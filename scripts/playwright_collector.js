// ============================================================================
// Health/Fitness Content Data Collector — Playwright Automation
// ============================================================================
//
// Collects search result data and screenshots from Google and YouTube for
// health/fitness related search terms. Designed for academic research.
//
// To run:
// 1. cd scripts
// 2. npm install
// 3. npx playwright install chromium
// 4. node playwright_collector.js
//
// Output:
//   ../data/csv/google_results.csv   — 50 Google search results
//   ../data/csv/youtube_results.csv  — 50 YouTube video results
//   ../data/screenshots/google/      — WEB-01.png through WEB-50.png
//   ../data/screenshots/youtube/     — YT-01.png through YT-50.png
//
// Notes:
//   - Uses incognito browsing (fresh context, no cookies)
//   - Viewport: 1920x1080, geolocation: US, language: en-US
//   - Resumable: skips screenshots that already exist on disk
//   - Robust: logs errors and continues if individual pages fail
//
// ============================================================================

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const SEARCH_TERMS = [
  'how to start exercising',
  'best exercises to lose weight',
  'strength training for beginners',
  'physical activity guidelines',
  'home workout routine',
];

const RESULTS_PER_TERM = 10;

// Directories (resolved relative to this script's location)
const BASE_DIR = path.resolve(__dirname, '..');
const GOOGLE_SCREENSHOT_DIR = path.join(BASE_DIR, 'data', 'screenshots', 'google');
const YOUTUBE_SCREENSHOT_DIR = path.join(BASE_DIR, 'data', 'screenshots', 'youtube');
const CSV_DIR = path.join(BASE_DIR, 'data', 'csv');

// Timing (milliseconds)
const DELAY_BETWEEN_SEARCHES_MIN = 2000;
const DELAY_BETWEEN_SEARCHES_MAX = 5000;
const DELAY_BETWEEN_PAGES_MIN = 1000;
const DELAY_BETWEEN_PAGES_MAX = 3000;
const PAGE_TIMEOUT = 30000; // 30 seconds

// ---------------------------------------------------------------------------
// Utility helpers
// ---------------------------------------------------------------------------

/** Return a random integer between min and max (inclusive). */
function randInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/** Sleep for a random duration between min and max ms. */
function randomDelay(min, max) {
  const ms = randInt(min, max);
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** Sleep for exactly ms milliseconds. */
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** Pad a number to two digits: 1 -> "01", 12 -> "12". */
function pad(n) {
  return String(n).padStart(2, '0');
}

/** Ensure a directory exists (recursive). */
function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

/** Check whether a file already exists on disk. */
function fileExists(filePath) {
  return fs.existsSync(filePath);
}

/** Escape a value for CSV (wrap in quotes, escape internal quotes). */
function csvEscape(value) {
  if (value === null || value === undefined) return '';
  const str = String(value).replace(/\r?\n/g, ' ').trim();
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return '"' + str.replace(/"/g, '""') + '"';
  }
  return str;
}

/** Write an array of objects to a CSV file. */
function writeCsv(filePath, rows, columns) {
  const header = columns.join(',');
  const lines = rows.map((row) =>
    columns.map((col) => csvEscape(row[col])).join(',')
  );
  fs.writeFileSync(filePath, [header, ...lines].join('\n'), 'utf-8');
  console.log(`  [CSV] Wrote ${rows.length} rows to ${filePath}`);
}

/** Timestamp string for log messages. */
function timestamp() {
  return new Date().toISOString().replace('T', ' ').replace(/\.\d+Z/, '');
}

function log(msg) {
  console.log(`[${timestamp()}] ${msg}`);
}

function logError(msg) {
  console.error(`[${timestamp()}] ERROR: ${msg}`);
}

// ---------------------------------------------------------------------------
// Browser context factory
// ---------------------------------------------------------------------------

/**
 * Launch Chromium and return a fresh incognito browser context configured
 * for US English, 1920x1080, with geolocation set to the United States.
 */
async function createBrowserContext() {
  const browser = await chromium.launch({
    headless: false, // Set to true for headless operation
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
    timezoneId: 'America/New_York',
    geolocation: { latitude: 37.7749, longitude: -122.4194 }, // San Francisco, US
    permissions: ['geolocation'],
    userAgent:
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
      '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  });

  return { browser, context };
}

// ---------------------------------------------------------------------------
// Google: consent / cookie popup handler
// ---------------------------------------------------------------------------

/**
 * Dismiss the Google cookie-consent dialog if it appears.
 * Tries several known button selectors used across Google domains.
 */
async function handleGoogleConsent(page) {
  try {
    // Wait briefly for the consent dialog to appear
    await page.waitForTimeout(1500);

    // Try various known consent button selectors
    const selectors = [
      'button:has-text("Reject all")',
      'button:has-text("Reject All")',
      'button:has-text("I agree")',
      'button:has-text("Accept all")',
      '#W0wltc',                          // "Reject all" button ID on some Google pages
      '[aria-label="Reject all"]',
      'button[id="L2AGLb"]',              // "I agree" button ID
      'form[action*="consent"] button',   // Generic consent form button
    ];

    for (const sel of selectors) {
      const btn = page.locator(sel).first();
      if (await btn.isVisible({ timeout: 500 }).catch(() => false)) {
        await btn.click();
        log('  Dismissed Google consent popup');
        await page.waitForTimeout(1000);
        return;
      }
    }
  } catch {
    // No consent popup — that is fine.
  }
}

// ---------------------------------------------------------------------------
// Google: extract organic search results from the SERP
// ---------------------------------------------------------------------------

/**
 * Extract organic results from Google's search results page.
 * Skips ads, "People also ask", and featured snippets.
 * Returns up to `count` results.
 */
async function extractGoogleResults(page, count) {
  return page.evaluate((cnt) => {
    const results = [];

    // Google organic result containers — each <div class="g"> with an <a> and <h3>
    const allG = document.querySelectorAll('div.g');

    for (const g of allG) {
      if (results.length >= cnt) break;

      // Skip ads (sponsored results have data-ad-* attributes or class "uEierd")
      if (g.closest('[data-text-ad]') || g.closest('.uEierd') || g.closest('#tads')) {
        continue;
      }

      // Skip "People also ask" sections
      if (g.closest('[data-sgrd]') || g.closest('.related-question-pair')) {
        continue;
      }

      const anchor = g.querySelector('a[href]');
      const heading = g.querySelector('h3');

      if (!anchor || !heading) continue;

      const url = anchor.href;
      // Skip Google's own internal links and vertical results
      if (!url || url.startsWith('https://www.google.com') || url.startsWith('/search')) {
        continue;
      }

      // Snippet: look for the description span inside the result
      let snippet = '';
      // Common snippet containers
      const snippetEl =
        g.querySelector('[data-sncf]') ||
        g.querySelector('.VwiC3b') ||
        g.querySelector('[style="-webkit-line-clamp:2"]') ||
        g.querySelector('.lEBKkf span') ||
        g.querySelector('.IsZvec');
      if (snippetEl) {
        snippet = snippetEl.innerText.trim();
      }

      results.push({
        url: url,
        title: heading.innerText.trim(),
        snippet: snippet,
      });
    }

    return results.slice(0, cnt);
  }, count);
}

// ---------------------------------------------------------------------------
// Google: extract metadata from an individual web page
// ---------------------------------------------------------------------------

/**
 * Navigate to a URL and attempt to extract author, date published, and page title.
 * Takes a full-page screenshot if it does not already exist.
 */
async function extractWebPageMeta(page, url, screenshotPath) {
  const meta = {
    author: '',
    datePublished: '',
    pageTitle: '',
    error: '',
  };

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: PAGE_TIMEOUT });
    await page.waitForTimeout(1500); // let JS render

    meta.pageTitle = await page.title();

    // Extract structured metadata from the page
    const extracted = await page.evaluate(() => {
      let author = '';
      let datePublished = '';

      // --- Author -----------------------------------------------------------
      // 1. <meta name="author" content="...">
      const metaAuthor = document.querySelector('meta[name="author"]');
      if (metaAuthor) author = metaAuthor.content;

      // 2. Schema.org JSON-LD
      if (!author) {
        const ldScripts = document.querySelectorAll('script[type="application/ld+json"]');
        for (const s of ldScripts) {
          try {
            const data = JSON.parse(s.textContent);
            const items = Array.isArray(data) ? data : [data];
            for (const item of items) {
              if (item.author) {
                const a = Array.isArray(item.author) ? item.author[0] : item.author;
                author = typeof a === 'string' ? a : a.name || '';
                if (author) break;
              }
            }
          } catch { /* ignore malformed JSON-LD */ }
          if (author) break;
        }
      }

      // 3. Common byline CSS patterns
      if (!author) {
        const bylineSelectors = [
          '[class*="byline"]',
          '[class*="author"]',
          '[rel="author"]',
          '[itemprop="author"]',
          '.post-author',
          '.entry-author',
          '.article-author',
          'a[href*="/author/"]',
        ];
        for (const sel of bylineSelectors) {
          const el = document.querySelector(sel);
          if (el && el.innerText && el.innerText.trim().length < 100) {
            author = el.innerText.trim();
            break;
          }
        }
      }

      // --- Date Published ---------------------------------------------------
      // 1. <meta property="article:published_time">
      const metaDate =
        document.querySelector('meta[property="article:published_time"]') ||
        document.querySelector('meta[name="date"]') ||
        document.querySelector('meta[name="publish-date"]') ||
        document.querySelector('meta[name="DC.date.issued"]') ||
        document.querySelector('meta[property="og:article:published_time"]');
      if (metaDate) datePublished = metaDate.content;

      // 2. Schema.org JSON-LD datePublished
      if (!datePublished) {
        const ldScripts = document.querySelectorAll('script[type="application/ld+json"]');
        for (const s of ldScripts) {
          try {
            const data = JSON.parse(s.textContent);
            const items = Array.isArray(data) ? data : [data];
            for (const item of items) {
              if (item.datePublished) {
                datePublished = item.datePublished;
                break;
              }
            }
          } catch { /* ignore */ }
          if (datePublished) break;
        }
      }

      // 3. <time> element
      if (!datePublished) {
        const timeEl = document.querySelector('time[datetime]');
        if (timeEl) datePublished = timeEl.getAttribute('datetime');
      }

      return { author, datePublished };
    });

    meta.author = extracted.author;
    meta.datePublished = extracted.datePublished;

    // Take screenshot if not already saved (resumable)
    if (!fileExists(screenshotPath)) {
      await page.screenshot({ path: screenshotPath, fullPage: true }).catch((err) => {
        logError(`Screenshot failed for ${url}: ${err.message}`);
      });
    }
  } catch (err) {
    meta.error = err.message;
    logError(`Failed to load ${url}: ${err.message}`);
  }

  return meta;
}

// ---------------------------------------------------------------------------
// YouTube: consent popup handler
// ---------------------------------------------------------------------------

async function handleYouTubeConsent(page) {
  try {
    await page.waitForTimeout(2000);

    const selectors = [
      'button:has-text("Reject all")',
      'button:has-text("Reject the use of cookies")',
      'button:has-text("Accept all")',
      'button[aria-label="Reject all"]',
      'button[aria-label="Reject the use of cookies and other data for the purposes described"]',
      'tp-yt-paper-dialog button.yt-spec-button-shape-next--call-to-action',
    ];

    for (const sel of selectors) {
      const btn = page.locator(sel).first();
      if (await btn.isVisible({ timeout: 800 }).catch(() => false)) {
        await btn.click();
        log('  Dismissed YouTube consent popup');
        await page.waitForTimeout(1500);
        return;
      }
    }
  } catch {
    // No consent popup.
  }
}

// ---------------------------------------------------------------------------
// YouTube: extract video results from search page
// ---------------------------------------------------------------------------

/**
 * Extract video results from YouTube search results page.
 * Skips ads and grouped Shorts shelves.
 * Returns up to `count` results.
 */
async function extractYouTubeSearchResults(page, count) {
  // Scroll down a few times to ensure enough results are loaded
  for (let i = 0; i < 5; i++) {
    await page.evaluate(() => window.scrollBy(0, 800));
    await page.waitForTimeout(800);
  }
  // Scroll back to top
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(500);

  return page.evaluate((cnt) => {
    const results = [];

    // YouTube renders video results as <ytd-video-renderer> elements
    const videoRenderers = document.querySelectorAll('ytd-video-renderer');

    for (const renderer of videoRenderers) {
      if (results.length >= cnt) break;

      // Skip ads — ad renderers have a different tag or contain ad badges
      if (renderer.querySelector('[class*="ad-badge"]') || renderer.closest('ytd-promoted-video-renderer')) {
        continue;
      }

      // Title and URL
      const titleLink = renderer.querySelector('#video-title');
      if (!titleLink) continue;

      const url = titleLink.href;
      const title = titleLink.textContent.trim();

      if (!url || !url.includes('/watch')) continue;

      // Channel name
      const channelEl =
        renderer.querySelector('#channel-name a') ||
        renderer.querySelector('ytd-channel-name a') ||
        renderer.querySelector('.ytd-channel-name a');
      const channelName = channelEl ? channelEl.textContent.trim() : '';

      // Metadata line (views, date)
      const metaLines = renderer.querySelectorAll('#metadata-line span.inline-metadata-item, #metadata-line span');
      let viewsText = '';
      let dateText = '';
      if (metaLines.length >= 1) viewsText = metaLines[0]?.textContent?.trim() || '';
      if (metaLines.length >= 2) dateText = metaLines[1]?.textContent?.trim() || '';

      // Duration — badge overlay
      const durationEl =
        renderer.querySelector('ytd-thumbnail-overlay-time-status-renderer span') ||
        renderer.querySelector('span.ytd-thumbnail-overlay-time-status-renderer') ||
        renderer.querySelector('#overlays span');
      const duration = durationEl ? durationEl.textContent.trim() : '';

      // Description snippet
      const descEl = renderer.querySelector('#description-text') || renderer.querySelector('.metadata-snippet-text');
      const description = descEl ? descEl.textContent.trim() : '';

      results.push({
        url,
        title,
        channelName,
        views: viewsText,
        uploadDate: dateText,
        duration,
        description,
      });
    }

    return results.slice(0, cnt);
  }, count);
}

// ---------------------------------------------------------------------------
// YouTube: extract detailed video metadata from a video page
// ---------------------------------------------------------------------------

/**
 * Navigate to a YouTube video page and extract detailed metadata:
 * like count, comment count, subscriber count, full upload date, and description.
 */
async function extractYouTubeVideoMeta(page, videoUrl) {
  const meta = {
    likes: '',
    comments: '',
    subscribers: '',
    fullDate: '',
    fullDescription: '',
    error: '',
  };

  try {
    await page.goto(videoUrl, { waitUntil: 'domcontentloaded', timeout: PAGE_TIMEOUT });
    await page.waitForTimeout(3000); // YouTube needs time for dynamic rendering

    // Dismiss any consent popup on the video page
    await handleYouTubeConsent(page);

    // Try to expand the description by clicking "...more" if present
    try {
      const moreBtn = page.locator('tp-yt-paper-button#expand, #expand.button, tp-yt-paper-button#more, #description-inline-expander [truncated] button, #expand').first();
      if (await moreBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
        await moreBtn.click();
        await page.waitForTimeout(1000);
      }
    } catch { /* no expand button */ }

    // Extract metadata from the video page
    const extracted = await page.evaluate(() => {
      let likes = '';
      let comments = '';
      let subscribers = '';
      let fullDate = '';
      let fullDescription = '';

      // --- Like count -------------------------------------------------------
      // The like button typically shows the count in its aria-label or text
      const likeBtn = document.querySelector(
        'button[aria-label*="like this video"],' +
        'like-button-view-model button,' +
        '#top-level-buttons-computed button:first-child,' +
        'ytd-toggle-button-renderer:first-child button,' +
        'segmented-like-dislike-button-view-model button:first-child'
      );
      if (likeBtn) {
        const ariaLabel = likeBtn.getAttribute('aria-label') || '';
        // e.g. "like this video along with 12,345 other people"
        const likeMatch = ariaLabel.match(/([\d,.\sKkMm]+)/);
        if (likeMatch) {
          likes = likeMatch[1].trim();
        }
        if (!likes) {
          // Try text content of the button
          const btnText = likeBtn.textContent.trim();
          if (/^[\d,.\sKkMm]+$/.test(btnText)) likes = btnText;
        }
      }
      // Fallback: look for the formatted like string near the like button
      if (!likes) {
        const likeSel = document.querySelector(
          '#segmented-like-button button,' +
          'ytd-menu-renderer button:first-child'
        );
        if (likeSel) {
          const txt = likeSel.textContent.trim();
          if (/[\d]/.test(txt) && txt.length < 20) likes = txt;
        }
      }

      // --- Comment count ----------------------------------------------------
      const commentsHeader = document.querySelector('#count .count-text, #comments #count, h2#count');
      if (commentsHeader) {
        const match = commentsHeader.textContent.match(/([\d,.\s]+)/);
        if (match) comments = match[1].trim();
      }

      // --- Subscriber count -------------------------------------------------
      const subEl = document.querySelector('#owner-sub-count, yt-formatted-string#owner-sub-count');
      if (subEl) {
        subscribers = subEl.textContent.trim();
      }

      // --- Upload date ------------------------------------------------------
      // Primary info: "date-text" or "info-strings"
      const dateEl = document.querySelector(
        '#info-strings yt-formatted-string,' +
        'span.bold[style*="max-width"],' +
        '#info-container yt-formatted-string'
      );
      if (dateEl) {
        fullDate = dateEl.textContent.trim();
      }
      // Fallback: look for "Published on" or date in the description area
      if (!fullDate) {
        const descInfo = document.querySelector('#description-inner #info, #info #date');
        if (descInfo) fullDate = descInfo.textContent.trim();
      }

      // --- Description ------------------------------------------------------
      const descEl = document.querySelector(
        '#description-inner #attributed-snippet-text,' +
        '#description yt-attributed-string,' +
        '#description-text,' +
        'ytd-text-inline-expander #attributed-snippet-text'
      );
      if (descEl) {
        fullDescription = descEl.textContent.trim().substring(0, 500);
      }

      return { likes, comments, subscribers, fullDate, fullDescription };
    });

    meta.likes = extracted.likes;
    meta.comments = extracted.comments;
    meta.subscribers = extracted.subscribers;
    meta.fullDate = extracted.fullDate;
    meta.fullDescription = extracted.fullDescription;
  } catch (err) {
    meta.error = err.message;
    logError(`Failed to extract YouTube video meta from ${videoUrl}: ${err.message}`);
  }

  return meta;
}

// ---------------------------------------------------------------------------
// Main: Google collection
// ---------------------------------------------------------------------------

async function collectGoogleResults() {
  log('=== Starting Google Search Collection ===');
  ensureDir(GOOGLE_SCREENSHOT_DIR);
  ensureDir(CSV_DIR);

  const { browser, context } = await createBrowserContext();
  const allResults = [];
  let globalIndex = 0; // 0-based, used to compute WEB-XX IDs

  try {
    const page = await context.newPage();
    page.setDefaultTimeout(PAGE_TIMEOUT);

    for (let termIdx = 0; termIdx < SEARCH_TERMS.length; termIdx++) {
      const term = SEARCH_TERMS[termIdx];
      log(`\n--- Google Search ${termIdx + 1}/${SEARCH_TERMS.length}: "${term}" ---`);

      // Navigate to Google
      await page.goto('https://www.google.com/?hl=en&gl=us', {
        waitUntil: 'domcontentloaded',
        timeout: PAGE_TIMEOUT,
      });

      // Handle cookie consent on first visit
      if (termIdx === 0) {
        await handleGoogleConsent(page);
      }

      // Type the search query and press Enter
      try {
        const searchBox = page.locator('textarea[name="q"], input[name="q"]').first();
        await searchBox.fill(term);
        await searchBox.press('Enter');
        await page.waitForSelector('div.g', { timeout: 15000 });
      } catch (err) {
        logError(`Could not perform search for "${term}": ${err.message}`);
        // Assign empty results for this term
        for (let i = 0; i < RESULTS_PER_TERM; i++) {
          globalIndex++;
          allResults.push({
            Item_ID: `WEB-${pad(globalIndex)}`,
            Platform: 'Google',
            Search_Term: term,
            URL: '',
            Title: '',
            Creator_Name: '',
            Date_Posted: '',
            Snippet: '',
            Position: i + 1,
          });
        }
        await randomDelay(DELAY_BETWEEN_SEARCHES_MIN, DELAY_BETWEEN_SEARCHES_MAX);
        continue;
      }

      // Handle consent that might appear after first search
      await handleGoogleConsent(page);

      // Take a screenshot of the search results page
      const serpScreenshot = path.join(GOOGLE_SCREENSHOT_DIR, `SERP-${pad(termIdx + 1)}.png`);
      if (!fileExists(serpScreenshot)) {
        await page.screenshot({ path: serpScreenshot, fullPage: false });
        log(`  Saved SERP screenshot: SERP-${pad(termIdx + 1)}.png`);
      }

      // Extract organic results
      const organicResults = await extractGoogleResults(page, RESULTS_PER_TERM);
      log(`  Found ${organicResults.length} organic results`);

      // Visit each result page for metadata + screenshot
      for (let i = 0; i < RESULTS_PER_TERM; i++) {
        globalIndex++;
        const itemId = `WEB-${pad(globalIndex)}`;

        if (i >= organicResults.length) {
          // Fewer results than expected
          log(`  ${itemId}: No result at position ${i + 1} (only ${organicResults.length} found)`);
          allResults.push({
            Item_ID: itemId,
            Platform: 'Google',
            Search_Term: term,
            URL: '',
            Title: '',
            Creator_Name: '',
            Date_Posted: '',
            Snippet: '',
            Position: i + 1,
          });
          continue;
        }

        const result = organicResults[i];
        log(`  ${itemId}: Visiting ${result.url}`);

        const screenshotPath = path.join(GOOGLE_SCREENSHOT_DIR, `${itemId}.png`);

        // Open a new page for visiting the result (keeps SERP page intact)
        const resultPage = await context.newPage();
        resultPage.setDefaultTimeout(PAGE_TIMEOUT);

        const pageMeta = await extractWebPageMetaOnPage(resultPage, result.url, screenshotPath);

        await resultPage.close();

        allResults.push({
          Item_ID: itemId,
          Platform: 'Google',
          Search_Term: term,
          URL: result.url,
          Title: pageMeta.pageTitle || result.title,
          Creator_Name: pageMeta.author,
          Date_Posted: pageMeta.datePublished,
          Snippet: result.snippet,
          Position: i + 1,
        });

        // Random delay between page loads
        await randomDelay(DELAY_BETWEEN_PAGES_MIN, DELAY_BETWEEN_PAGES_MAX);
      }

      // Random delay between searches
      if (termIdx < SEARCH_TERMS.length - 1) {
        log('  Waiting before next search...');
        await randomDelay(DELAY_BETWEEN_SEARCHES_MIN, DELAY_BETWEEN_SEARCHES_MAX);
      }
    }
  } catch (err) {
    logError(`Google collection fatal error: ${err.message}`);
  } finally {
    await browser.close();
  }

  // Write CSV
  const csvPath = path.join(CSV_DIR, 'google_results.csv');
  writeCsv(csvPath, allResults, [
    'Item_ID', 'Platform', 'Search_Term', 'URL', 'Title',
    'Creator_Name', 'Date_Posted', 'Snippet', 'Position',
  ]);

  log(`=== Google collection complete: ${allResults.length} results ===\n`);
  return allResults;
}

/**
 * Navigate to a URL in the given page, extract metadata, and take a screenshot.
 * This is a version of extractWebPageMeta that accepts a page object.
 */
async function extractWebPageMetaOnPage(page, url, screenshotPath) {
  const meta = {
    author: '',
    datePublished: '',
    pageTitle: '',
    error: '',
  };

  try {
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: PAGE_TIMEOUT });
    await page.waitForTimeout(1500);

    meta.pageTitle = await page.title();

    // Extract structured metadata
    const extracted = await page.evaluate(() => {
      let author = '';
      let datePublished = '';

      // --- Author -----------------------------------------------------------
      const metaAuthor = document.querySelector('meta[name="author"]');
      if (metaAuthor) author = metaAuthor.content;

      if (!author) {
        const ldScripts = document.querySelectorAll('script[type="application/ld+json"]');
        for (const s of ldScripts) {
          try {
            const data = JSON.parse(s.textContent);
            const items = Array.isArray(data) ? data : [data];
            for (const item of items) {
              if (item.author) {
                const a = Array.isArray(item.author) ? item.author[0] : item.author;
                author = typeof a === 'string' ? a : a.name || '';
                if (author) break;
              }
            }
          } catch { /* ignore */ }
          if (author) break;
        }
      }

      if (!author) {
        const bylineSelectors = [
          '[class*="byline"]', '[class*="author"]', '[rel="author"]',
          '[itemprop="author"]', '.post-author', '.entry-author',
          '.article-author', 'a[href*="/author/"]',
        ];
        for (const sel of bylineSelectors) {
          const el = document.querySelector(sel);
          if (el && el.innerText && el.innerText.trim().length < 100) {
            author = el.innerText.trim();
            break;
          }
        }
      }

      // --- Date Published ---------------------------------------------------
      const metaDate =
        document.querySelector('meta[property="article:published_time"]') ||
        document.querySelector('meta[name="date"]') ||
        document.querySelector('meta[name="publish-date"]') ||
        document.querySelector('meta[name="DC.date.issued"]') ||
        document.querySelector('meta[property="og:article:published_time"]');
      if (metaDate) datePublished = metaDate.content;

      if (!datePublished) {
        const ldScripts = document.querySelectorAll('script[type="application/ld+json"]');
        for (const s of ldScripts) {
          try {
            const data = JSON.parse(s.textContent);
            const items = Array.isArray(data) ? data : [data];
            for (const item of items) {
              if (item.datePublished) {
                datePublished = item.datePublished;
                break;
              }
            }
          } catch { /* ignore */ }
          if (datePublished) break;
        }
      }

      if (!datePublished) {
        const timeEl = document.querySelector('time[datetime]');
        if (timeEl) datePublished = timeEl.getAttribute('datetime');
      }

      return { author, datePublished };
    });

    meta.author = extracted.author;
    meta.datePublished = extracted.datePublished;

    // Take full-page screenshot (resumable — skip if it exists)
    if (!fileExists(screenshotPath)) {
      await page.screenshot({ path: screenshotPath, fullPage: true }).catch((err) => {
        logError(`Screenshot failed for ${url}: ${err.message}`);
      });
      log(`    Saved screenshot: ${path.basename(screenshotPath)}`);
    } else {
      log(`    Screenshot already exists: ${path.basename(screenshotPath)} (skipped)`);
    }
  } catch (err) {
    meta.error = err.message;
    logError(`Failed to load ${url}: ${err.message}`);
  }

  return meta;
}

// ---------------------------------------------------------------------------
// Main: YouTube collection
// ---------------------------------------------------------------------------

async function collectYouTubeResults() {
  log('=== Starting YouTube Search Collection ===');
  ensureDir(YOUTUBE_SCREENSHOT_DIR);
  ensureDir(CSV_DIR);

  const { browser, context } = await createBrowserContext();
  const allResults = [];
  let globalIndex = 0;

  try {
    const page = await context.newPage();
    page.setDefaultTimeout(PAGE_TIMEOUT);

    for (let termIdx = 0; termIdx < SEARCH_TERMS.length; termIdx++) {
      const term = SEARCH_TERMS[termIdx];
      log(`\n--- YouTube Search ${termIdx + 1}/${SEARCH_TERMS.length}: "${term}" ---`);

      // Navigate to YouTube
      await page.goto('https://www.youtube.com', {
        waitUntil: 'domcontentloaded',
        timeout: PAGE_TIMEOUT,
      });

      // Handle consent popup on first visit
      if (termIdx === 0) {
        await handleYouTubeConsent(page);
      }

      // Type search query
      try {
        const searchBox = page.locator('input#search, input[name="search_query"]').first();
        await searchBox.click();
        await searchBox.fill(term);
        await searchBox.press('Enter');

        // Wait for video results to load
        await page.waitForSelector('ytd-video-renderer', { timeout: 15000 });
        await page.waitForTimeout(2000); // Extra time for rendering
      } catch (err) {
        logError(`Could not perform YouTube search for "${term}": ${err.message}`);
        for (let i = 0; i < RESULTS_PER_TERM; i++) {
          globalIndex++;
          allResults.push({
            Item_ID: `YT-${pad(globalIndex)}`,
            Platform: 'YouTube',
            Search_Term: term,
            URL: '',
            Title: '',
            Creator_Name: '',
            Views: '',
            Likes: '',
            Comments: '',
            Date_Posted: '',
            Duration: '',
            Subscribers: '',
            Description: '',
          });
        }
        await randomDelay(DELAY_BETWEEN_SEARCHES_MIN, DELAY_BETWEEN_SEARCHES_MAX);
        continue;
      }

      // Take a screenshot of the search results page
      const serpScreenshot = path.join(YOUTUBE_SCREENSHOT_DIR, `YT-SERP-${pad(termIdx + 1)}.png`);
      if (!fileExists(serpScreenshot)) {
        await page.screenshot({ path: serpScreenshot, fullPage: false });
        log(`  Saved SERP screenshot: YT-SERP-${pad(termIdx + 1)}.png`);
      }

      // Extract video results from search page
      const videoResults = await extractYouTubeSearchResults(page, RESULTS_PER_TERM);
      log(`  Found ${videoResults.length} video results`);

      // Visit each video page for detailed metadata + screenshot
      for (let i = 0; i < RESULTS_PER_TERM; i++) {
        globalIndex++;
        const itemId = `YT-${pad(globalIndex)}`;

        if (i >= videoResults.length) {
          log(`  ${itemId}: No result at position ${i + 1} (only ${videoResults.length} found)`);
          allResults.push({
            Item_ID: itemId,
            Platform: 'YouTube',
            Search_Term: term,
            URL: '',
            Title: '',
            Creator_Name: '',
            Views: '',
            Likes: '',
            Comments: '',
            Date_Posted: '',
            Duration: '',
            Subscribers: '',
            Description: '',
          });
          continue;
        }

        const video = videoResults[i];
        log(`  ${itemId}: Visiting ${video.url}`);

        const screenshotPath = path.join(YOUTUBE_SCREENSHOT_DIR, `${itemId}.png`);

        // Open video page in a new tab
        const videoPage = await context.newPage();
        videoPage.setDefaultTimeout(PAGE_TIMEOUT);

        const videoMeta = await extractYouTubeVideoMeta(videoPage, video.url);

        // Take screenshot of the video page (resumable)
        if (!fileExists(screenshotPath)) {
          try {
            await videoPage.screenshot({ path: screenshotPath, fullPage: false });
            log(`    Saved screenshot: ${itemId}.png`);
          } catch (err) {
            logError(`Screenshot failed for ${video.url}: ${err.message}`);
          }
        } else {
          log(`    Screenshot already exists: ${itemId}.png (skipped)`);
        }

        await videoPage.close();

        allResults.push({
          Item_ID: itemId,
          Platform: 'YouTube',
          Search_Term: term,
          URL: video.url,
          Title: video.title,
          Creator_Name: video.channelName,
          Views: video.views || '',
          Likes: videoMeta.likes || '',
          Comments: videoMeta.comments || '',
          Date_Posted: videoMeta.fullDate || video.uploadDate || '',
          Duration: video.duration || '',
          Subscribers: videoMeta.subscribers || '',
          Description: videoMeta.fullDescription || video.description || '',
        });

        // Random delay between page loads
        await randomDelay(DELAY_BETWEEN_PAGES_MIN, DELAY_BETWEEN_PAGES_MAX);
      }

      // Random delay between searches
      if (termIdx < SEARCH_TERMS.length - 1) {
        log('  Waiting before next search...');
        await randomDelay(DELAY_BETWEEN_SEARCHES_MIN, DELAY_BETWEEN_SEARCHES_MAX);
      }
    }
  } catch (err) {
    logError(`YouTube collection fatal error: ${err.message}`);
  } finally {
    await browser.close();
  }

  // Write CSV
  const csvPath = path.join(CSV_DIR, 'youtube_results.csv');
  writeCsv(csvPath, allResults, [
    'Item_ID', 'Platform', 'Search_Term', 'URL', 'Title',
    'Creator_Name', 'Views', 'Likes', 'Comments', 'Date_Posted',
    'Duration', 'Subscribers', 'Description',
  ]);

  log(`=== YouTube collection complete: ${allResults.length} results ===\n`);
  return allResults;
}

// ---------------------------------------------------------------------------
// Entry point
// ---------------------------------------------------------------------------

async function main() {
  log('============================================================');
  log('  Health/Fitness Content Data Collector');
  log('============================================================');
  log(`  Search terms: ${SEARCH_TERMS.length}`);
  log(`  Results per term: ${RESULTS_PER_TERM}`);
  log(`  Total expected: ${SEARCH_TERMS.length * RESULTS_PER_TERM} Google + ${SEARCH_TERMS.length * RESULTS_PER_TERM} YouTube`);
  log(`  Output dir: ${BASE_DIR}`);
  log('============================================================\n');

  const startTime = Date.now();

  // --- Phase 1: Google ---
  try {
    await collectGoogleResults();
  } catch (err) {
    logError(`Google phase failed: ${err.message}`);
  }

  // --- Phase 2: YouTube ---
  try {
    await collectYouTubeResults();
  } catch (err) {
    logError(`YouTube phase failed: ${err.message}`);
  }

  const elapsed = ((Date.now() - startTime) / 1000 / 60).toFixed(1);
  log('============================================================');
  log(`  Collection complete in ${elapsed} minutes`);
  log('============================================================');
}

// Run
main().catch((err) => {
  logError(`Fatal: ${err.message}`);
  process.exit(1);
});
