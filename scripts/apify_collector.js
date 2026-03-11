// ============================================================================
// Unified Data Collector — Apify API
// ============================================================================
//
// Collects search result data from all 4 platforms using Apify actors:
//   1. Google Search  → apify/google-search-scraper
//   2. YouTube Search → streamers/youtube-scraper
//   3. TikTok Search  → clockworks/tiktok-scraper
//   4. Instagram      → apify/instagram-hashtag-scraper
//
// Usage:
//   1. cd scripts
//   2. npm install
//   3. node apify_collector.js
//
// Output:
//   ../data/csv/google_results.csv    (50 rows)
//   ../data/csv/youtube_results.csv   (50 rows)
//   ../data/csv/tiktok_results.csv    (50 rows)
//   ../data/csv/instagram_results.csv (50 rows)
//   ../data/csv/master_dataset.csv    (200 rows merged)
//
// ============================================================================

const { ApifyClient } = require('apify-client');
const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const APIFY_TOKEN = process.env.APIFY_TOKEN || 'YOUR_APIFY_TOKEN_HERE';

const SEARCH_TERMS = [
  'how to start exercising',
  'best exercises to lose weight',
  'strength training for beginners',
  'physical activity guidelines',
  'home workout routine',
];

const RESULTS_PER_TERM = 10;

// Instagram hashtag versions of search terms (Instagram searches by hashtag)
const INSTAGRAM_HASHTAGS = [
  'howtostarexercising',
  'bestexercisestolooseweight',
  'strengthtrainingforbeginners',
  'physicalactivityguidelines',
  'homeworkoutroutine',
];

// Backup hashtags if primary ones return too few results
const INSTAGRAM_BACKUP_HASHTAGS = [
  'startexercising',
  'weightlossworkout',
  'beginnerstrengthtraining',
  'exerciseguidelines',
  'homeworkout',
];

const BASE_DIR = path.resolve(__dirname, '..');
const CSV_DIR = path.join(BASE_DIR, 'data', 'csv');

const client = new ApifyClient({ token: APIFY_TOKEN });

// ---------------------------------------------------------------------------
// Utility helpers
// ---------------------------------------------------------------------------

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function timestamp() {
  return new Date().toISOString().replace('T', ' ').replace(/\.\d+Z/, '');
}

function log(msg) {
  console.log(`[${timestamp()}] ${msg}`);
}

function logError(msg) {
  console.error(`[${timestamp()}] ERROR: ${msg}`);
}

function csvEscape(value) {
  if (value === null || value === undefined) return '';
  const str = String(value).replace(/\r?\n/g, ' ').trim();
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return '"' + str.replace(/"/g, '""') + '"';
  }
  return str;
}

function writeCsv(filePath, rows, columns) {
  const header = columns.join(',');
  const lines = rows.map((row) =>
    columns.map((col) => csvEscape(row[col])).join(',')
  );
  fs.writeFileSync(filePath, [header, ...lines].join('\n'), 'utf-8');
  log(`  Wrote ${rows.length} rows to ${path.basename(filePath)}`);
}

function pad(n) {
  return String(n).padStart(2, '0');
}

function parseCsvFromContent(content) {
  const lines = content.split('\n').filter((l) => l.trim());
  if (lines.length < 2) return [];
  const headers = lines[0].split(',').map((h) => h.trim());
  const rows = [];
  for (let i = 1; i < lines.length; i++) {
    const vals = lines[i].split(',');
    const row = {};
    headers.forEach((h, idx) => { row[h] = (vals[idx] || '').trim(); });
    rows.push(row);
  }
  return rows;
}

// ---------------------------------------------------------------------------
// 1. Google Search Collection
// ---------------------------------------------------------------------------

async function collectGoogle() {
  log('=== Starting Google Search Collection ===');

  const rows = [];
  let itemNum = 0;

  for (const term of SEARCH_TERMS) {
    log(`  Searching Google: "${term}"...`);

    const input = {
      queries: term,
      countryCode: 'us',
      languageCode: 'en',
      resultsPerPage: 20,
      maxPagesPerQuery: 2, // Fetch 2 pages to get enough organic results
      mobileResults: false,
      includeUnfilteredResults: false,
      saveHtml: false,
      saveHtmlToKeyValueStore: false,
    };

    const run = await client.actor('apify/google-search-scraper').call(input);
    const { items } = await client.dataset(run.defaultDatasetId).listItems();

    // Collect all organic results across pages for this term
    const allOrganic = [];
    for (const page of items) {
      const organicResults = page.organicResults || [];
      allOrganic.push(...organicResults);
    }

    log(`    Got ${allOrganic.length} organic results across ${items.length} page(s)`);

    // Deduplicate by URL (same result might appear on both pages)
    const seen = new Set();
    const unique = [];
    for (const r of allOrganic) {
      const url = r.url || '';
      if (url && !seen.has(url)) {
        seen.add(url);
        unique.push(r);
      }
    }

    // Take top 10
    const top = unique.slice(0, RESULTS_PER_TERM);
    for (let i = 0; i < top.length; i++) {
      itemNum++;
      const r = top[i];
      rows.push({
        Item_ID: `WEB-${pad(itemNum)}`,
        Platform: 'Website',
        Search_Term: term,
        URL: r.url || '',
        Title_Caption: r.title || '',
        Creator_Name: r.displayedUrl || '',
        Creator_Credentials: '',
        Date_Posted: '',
        Views: '',
        Likes: '',
        Shares: '',
        Comments: '',
        Creator_Type: '',
        Content_Format: 'Text article',
        Snippet: r.description || '',
        Position: r.position || i + 1,
      });
    }

    log(`    Collected ${top.length} results for "${term}" (running total: ${rows.length})`);
  }

  log(`  Collected ${rows.length} Google results total`);
  return rows;
}

// ---------------------------------------------------------------------------
// 2. YouTube Search Collection
// ---------------------------------------------------------------------------

async function collectYouTube() {
  log('=== Starting YouTube Search Collection ===');

  const rows = [];
  let itemNum = 0;

  // Run separate searches per term (like TikTok) to ensure 10 results each
  for (let termIdx = 0; termIdx < SEARCH_TERMS.length; termIdx++) {
    const term = SEARCH_TERMS[termIdx];
    log(`  Searching YouTube for: "${term}" (${termIdx + 1}/${SEARCH_TERMS.length})`);

    const input = {
      searchKeywords: term,
      maxResults: RESULTS_PER_TERM,
      maxResultsShorts: 0,
      maxResultStreams: 0,
    };

    try {
      const run = await client.actor('streamers/youtube-scraper').call(input);
      const { items } = await client.dataset(run.defaultDatasetId).listItems();
      log(`    Got ${items.length} results`);

      const limited = items.slice(0, RESULTS_PER_TERM);
      for (const v of limited) {
        itemNum++;

      // Parse engagement metrics (handle various field names)
      const views = v.viewCount || v.views || v.viewCountText || '';
      const likes = v.likes || v.likeCount || '';
      const comments = v.commentsCount || v.commentCount || v.numberOfComments || '';

      // Parse duration to determine content format
      const durationSec = v.duration || v.lengthSeconds || 0;
      let contentFormat = 'Long video (>5min)';
      if (durationSec && durationSec < 60) contentFormat = 'Short video (<60s)';
      else if (durationSec && durationSec <= 300) contentFormat = 'Long video (>5min)';

      rows.push({
        Item_ID: `YT-${pad(itemNum)}`,
        Platform: 'YouTube',
        Search_Term: term,
        URL: v.url || v.videoUrl || (v.id ? `https://www.youtube.com/watch?v=${v.id}` : ''),
        Title_Caption: v.title || '',
        Creator_Name: v.channelName || v.channelTitle || v.author || '',
        Creator_Credentials: '',
        Date_Posted: v.date || v.uploadDate || v.publishedAt || '',
        Views: typeof views === 'number' ? views : String(views).replace(/[^0-9]/g, ''),
        Likes: typeof likes === 'number' ? likes : String(likes).replace(/[^0-9]/g, ''),
        Shares: '',
        Comments: typeof comments === 'number' ? comments : String(comments).replace(/[^0-9]/g, ''),
        Creator_Type: '',
        Content_Format: contentFormat,
        Subscribers: v.subscriberCount || v.subscriberCountText || '',
        Duration: v.duration || v.lengthText || '',
        Description: (v.description || v.text || '').substring(0, 500),
      });
      }
    } catch (err) {
      logError(`  YouTube search failed for "${term}": ${err.message}`);
    }
  }

  log(`  Collected ${rows.length} YouTube results`);
  return rows;
}

// ---------------------------------------------------------------------------
// 3. TikTok Search Collection
// ---------------------------------------------------------------------------

async function collectTikTok() {
  log('=== Starting TikTok Search Collection ===');

  const rows = [];
  let itemNum = 0;

  // Run separate searches per term to track which term produced which results
  for (let termIdx = 0; termIdx < SEARCH_TERMS.length; termIdx++) {
    const term = SEARCH_TERMS[termIdx];
    log(`  Searching TikTok for: "${term}" (${termIdx + 1}/${SEARCH_TERMS.length})`);

    const input = {
      searchQueries: [term],
      resultsPerPage: RESULTS_PER_TERM,
      shouldDownloadVideos: false,
      shouldDownloadCovers: false,
      shouldDownloadSubtitles: false,
      shouldDownloadSlideshowImages: false,
    };

    try {
      const run = await client.actor('clockworks/tiktok-scraper').call(input);
      const { items } = await client.dataset(run.defaultDatasetId).listItems();
      log(`    Got ${items.length} results`);

      const limited = items.slice(0, RESULTS_PER_TERM);
      for (const v of limited) {
        itemNum++;
        const authorMeta = v.authorMeta || v.author || {};
        const stats = v.stats || v.videoMeta || {};

        rows.push({
          Item_ID: `TT-${pad(itemNum)}`,
          Platform: 'TikTok',
          Search_Term: term,
          URL: v.webVideoUrl || v.url || v.videoUrl || '',
          Title_Caption: (v.text || v.desc || v.description || '').substring(0, 500),
          Creator_Name: authorMeta.nickName || authorMeta.name || authorMeta.nickname || v.authorName || '',
          Creator_Credentials: authorMeta.signature || authorMeta.bio || '',
          Date_Posted: v.createTimeISO || v.createTime || '',
          Views: stats.playCount || stats.plays || v.playCount || v.views || '',
          Likes: stats.diggCount || stats.likes || v.diggCount || v.likes || '',
          Shares: stats.shareCount || stats.shares || v.shareCount || '',
          Comments: stats.commentCount || stats.comments || v.commentCount || '',
          Creator_Type: '',
          Content_Format: 'Short video (<60s)',
          Author_Verified: authorMeta.verified || false,
          Author_Followers: authorMeta.fans || authorMeta.followers || '',
        });
      }
    } catch (err) {
      logError(`  TikTok search failed for "${term}": ${err.message}`);
    }
  }

  log(`  Collected ${rows.length} TikTok results`);
  return rows;
}

// ---------------------------------------------------------------------------
// 4. Instagram Search Collection
// ---------------------------------------------------------------------------

async function collectInstagram() {
  log('=== Starting Instagram Search Collection ===');

  const rows = [];
  let itemNum = 0;

  for (let termIdx = 0; termIdx < SEARCH_TERMS.length; termIdx++) {
    const term = SEARCH_TERMS[termIdx];
    const hashtag = INSTAGRAM_HASHTAGS[termIdx];
    const backupHashtag = INSTAGRAM_BACKUP_HASHTAGS[termIdx];

    log(`  Searching Instagram hashtag #${hashtag} for: "${term}" (${termIdx + 1}/${SEARCH_TERMS.length})`);

    const input = {
      hashtags: [hashtag],
      resultsLimit: RESULTS_PER_TERM,
      resultsType: 'posts',
      searchType: 'hashtag',
    };

    try {
      const run = await client.actor('apify/instagram-hashtag-scraper').call(input);
      let { items } = await client.dataset(run.defaultDatasetId).listItems();
      // Filter out error objects (no post data, just tag page URLs)
      items = items.filter((item) => !item.error && (item.shortCode || item.id || item.caption));
      log(`    Got ${items.length} valid results from #${hashtag}`);

      // If not enough results, try backup hashtag
      if (items.length < RESULTS_PER_TERM) {
        log(`    Trying backup hashtag #${backupHashtag}...`);
        const backupInput = {
          hashtags: [backupHashtag],
          resultsLimit: RESULTS_PER_TERM - items.length,
          resultsType: 'posts',
          searchType: 'hashtag',
        };
        const backupRun = await client.actor('apify/instagram-hashtag-scraper').call(backupInput);
        const backupData = await client.dataset(backupRun.defaultDatasetId).listItems();
        items = items.concat(backupData.items || []);
        log(`    Total after backup: ${items.length} results`);
      }

      const limited = items.slice(0, RESULTS_PER_TERM);
      if (limited.length > 0) {
        log(`    Sample post keys: ${Object.keys(limited[0]).join(', ')}`);
        log(`    Sample URL field: ${limited[0].url}`);
        log(`    Sample shortCode field: ${limited[0].shortCode}`);
        log(`    Sample shortcode field: ${limited[0].shortcode}`);
      }
      for (const post of limited) {
        itemNum++;

        // Handle various field name patterns from Instagram scraper
        const caption = post.caption || post.text || post.alt || '';
        const owner = post.ownerUsername || post.owner?.username || post.username || '';
        const ownerName = post.ownerFullName || post.owner?.fullName || post.fullName || owner;

        // Determine content format
        let contentFormat = 'Image+caption';
        if (post.type === 'Video' || post.isVideo || post.videoUrl) {
          contentFormat = 'Short video (<60s)';
        } else if (post.type === 'Sidecar' || post.childPosts || post.sidecarChildren) {
          contentFormat = 'Carousel';
        }

        rows.push({
          Item_ID: `IG-${pad(itemNum)}`,
          Platform: 'Instagram',
          Search_Term: term,
          URL: post.url || (post.shortCode ? `https://www.instagram.com/p/${post.shortCode}/` : '') || (post.shortcode ? `https://www.instagram.com/p/${post.shortcode}/` : '') || post.inputUrl || '',
          Title_Caption: caption.substring(0, 500),
          Creator_Name: ownerName || owner,
          Creator_Credentials: '',
          Date_Posted: post.timestamp || post.takenAtTimestamp || post.date || '',
          Views: post.videoViewCount || post.videoPlayCount || '',
          Likes: post.likesCount || post.likes || post.likeCount || '',
          Shares: '',
          Comments: post.commentsCount || post.comments || post.commentCount || '',
          Creator_Type: '',
          Content_Format: contentFormat,
          Hashtags: (post.hashtags || []).join(', '),
        });
      }
    } catch (err) {
      logError(`  Instagram search failed for #${hashtag}: ${err.message}`);

      // Try the backup hashtag as primary
      try {
        log(`    Trying backup hashtag #${backupHashtag} as primary...`);
        const backupInput = {
          hashtags: [backupHashtag],
          resultsLimit: RESULTS_PER_TERM,
          resultsType: 'posts',
          searchType: 'hashtag',
        };
        const backupRun = await client.actor('apify/instagram-hashtag-scraper').call(backupInput);
        const { items: backupItems } = await client.dataset(backupRun.defaultDatasetId).listItems();
        log(`    Got ${backupItems.length} results from backup`);

        const limited = backupItems.slice(0, RESULTS_PER_TERM);
        for (const post of limited) {
          itemNum++;
          const caption = post.caption || post.text || post.alt || '';
          const owner = post.ownerUsername || post.owner?.username || post.username || '';

          let contentFormat = 'Image+caption';
          if (post.type === 'Video' || post.isVideo) contentFormat = 'Short video (<60s)';
          else if (post.type === 'Sidecar' || post.childPosts) contentFormat = 'Carousel';

          rows.push({
            Item_ID: `IG-${pad(itemNum)}`,
            Platform: 'Instagram',
            Search_Term: term,
            URL: post.url || `https://www.instagram.com/p/${post.shortcode}/`,
            Title_Caption: caption.substring(0, 500),
            Creator_Name: owner,
            Creator_Credentials: '',
            Date_Posted: post.timestamp || post.date || '',
            Views: post.videoViewCount || '',
            Likes: post.likesCount || post.likes || '',
            Shares: '',
            Comments: post.commentsCount || post.comments || '',
            Creator_Type: '',
            Content_Format: contentFormat,
            Hashtags: (post.hashtags || []).join(', '),
          });
        }
      } catch (err2) {
        logError(`  Backup hashtag also failed: ${err2.message}`);
      }
    }
  }

  log(`  Collected ${rows.length} Instagram results`);
  return rows;
}

// ---------------------------------------------------------------------------
// Master CSV merge
// ---------------------------------------------------------------------------

function writeMasterCsv(google, youtube, tiktok, instagram) {
  const masterColumns = [
    'Item_ID', 'Platform', 'Search_Term', 'URL', 'Title_Caption',
    'Creator_Name', 'Creator_Credentials', 'Date_Posted',
    'Views', 'Likes', 'Shares', 'Comments',
    'Creator_Type', 'Content_Format',
  ];

  const allRows = [...google, ...youtube, ...tiktok, ...instagram].map((row) => {
    const clean = {};
    for (const col of masterColumns) {
      clean[col] = row[col] || '';
    }
    return clean;
  });

  const masterPath = path.join(CSV_DIR, 'master_dataset.csv');
  writeCsv(masterPath, allRows, masterColumns);
  log(`  Master dataset: ${allRows.length} total rows`);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  ensureDir(CSV_DIR);

  console.log('');
  log('============================================================');
  log('  Unified Data Collector — Apify API');
  log('============================================================');
  log(`  Search terms: ${SEARCH_TERMS.length}`);
  log(`  Results per term: ${RESULTS_PER_TERM}`);
  log(`  Total expected: ${SEARCH_TERMS.length * RESULTS_PER_TERM * 4} items (4 platforms)`);
  log('============================================================');
  console.log('');

  // Shared columns for platform-specific CSVs
  const googleCols = [
    'Item_ID', 'Platform', 'Search_Term', 'URL', 'Title_Caption',
    'Creator_Name', 'Snippet', 'Position',
  ];
  const youtubeCols = [
    'Item_ID', 'Platform', 'Search_Term', 'URL', 'Title_Caption',
    'Creator_Name', 'Date_Posted', 'Views', 'Likes', 'Comments',
    'Content_Format', 'Subscribers', 'Duration', 'Description',
  ];
  const tiktokCols = [
    'Item_ID', 'Platform', 'Search_Term', 'URL', 'Title_Caption',
    'Creator_Name', 'Creator_Credentials', 'Date_Posted',
    'Views', 'Likes', 'Shares', 'Comments', 'Content_Format',
    'Author_Verified', 'Author_Followers',
  ];
  const instagramCols = [
    'Item_ID', 'Platform', 'Search_Term', 'URL', 'Title_Caption',
    'Creator_Name', 'Date_Posted',
    'Views', 'Likes', 'Comments', 'Content_Format', 'Hashtags',
  ];

  let googleRows = [];
  let youtubeRows = [];
  let tiktokRows = [];
  let instagramRows = [];

  // Check which platforms already have complete data (skip re-collection)
  const googleCsvPath = path.join(CSV_DIR, 'google_results.csv');
  const youtubeCsvPath = path.join(CSV_DIR, 'youtube_results.csv');
  const tiktokCsvPath = path.join(CSV_DIR, 'tiktok_results.csv');
  const instagramCsvPath = path.join(CSV_DIR, 'instagram_results.csv');

  // Google: reuse existing CSV if it has 50 rows
  if (fs.existsSync(googleCsvPath)) {
    const content = fs.readFileSync(googleCsvPath, 'utf-8');
    const lineCount = content.split('\n').filter(l => l.trim()).length - 1;
    if (lineCount >= 50) {
      log(`=== Google: Reusing existing CSV (${lineCount} rows) ===`);
      const parsed = parseCsvFromContent(content);
      googleRows = parsed.slice(0, 50);
    } else {
      try {
        googleRows = await collectGoogle();
        writeCsv(googleCsvPath, googleRows, googleCols);
      } catch (err) {
        logError(`Google collection failed: ${err.message}`);
      }
    }
  } else {
    try {
      googleRows = await collectGoogle();
      writeCsv(googleCsvPath, googleRows, googleCols);
    } catch (err) {
      logError(`Google collection failed: ${err.message}`);
    }
  }

  // YouTube: reuse existing CSV if it has 50 rows
  if (fs.existsSync(youtubeCsvPath)) {
    const content = fs.readFileSync(youtubeCsvPath, 'utf-8');
    const lineCount = content.split('\n').filter(l => l.trim()).length - 1;
    if (lineCount >= 50) {
      log(`=== YouTube: Reusing existing CSV (${lineCount} rows) ===`);
      const parsed = parseCsvFromContent(content);
      youtubeRows = parsed.slice(0, 50);
    } else {
      try {
        youtubeRows = await collectYouTube();
        writeCsv(youtubeCsvPath, youtubeRows, youtubeCols);
      } catch (err) {
        logError(`YouTube collection failed: ${err.message}`);
      }
    }
  } else {
    try {
      youtubeRows = await collectYouTube();
      writeCsv(youtubeCsvPath, youtubeRows, youtubeCols);
    } catch (err) {
      logError(`YouTube collection failed: ${err.message}`);
    }
  }

  // TikTok: reuse existing CSV if it has 50 rows
  if (fs.existsSync(tiktokCsvPath)) {
    const content = fs.readFileSync(tiktokCsvPath, 'utf-8');
    const lineCount = content.split('\n').filter(l => l.trim()).length - 1; // minus header
    if (lineCount >= 50) {
      log(`=== TikTok: Reusing existing CSV (${lineCount} rows) ===`);
      // Parse existing CSV into rows for master merge
      const lines = content.split('\n').filter(l => l.trim());
      const headers = lines[0].split(',');
      for (let i = 1; i <= Math.min(lineCount, 50); i++) {
        const vals = lines[i].split(',');
        const row = {};
        headers.forEach((h, idx) => { row[h.trim()] = (vals[idx] || '').trim(); });
        tiktokRows.push(row);
      }
    } else {
      try {
        tiktokRows = await collectTikTok();
        writeCsv(tiktokCsvPath, tiktokRows, tiktokCols);
      } catch (err) {
        logError(`TikTok collection failed: ${err.message}`);
      }
    }
  } else {
    try {
      tiktokRows = await collectTikTok();
      writeCsv(tiktokCsvPath, tiktokRows, tiktokCols);
    } catch (err) {
      logError(`TikTok collection failed: ${err.message}`);
    }
  }

  // Instagram: reuse existing CSV if it has 50 rows
  if (fs.existsSync(instagramCsvPath)) {
    const content = fs.readFileSync(instagramCsvPath, 'utf-8');
    const lineCount = content.split('\n').filter(l => l.trim()).length - 1;
    if (lineCount >= 50) {
      log(`=== Instagram: Reusing existing CSV (${lineCount} rows) ===`);
      const lines = content.split('\n').filter(l => l.trim());
      const headers = lines[0].split(',');
      for (let i = 1; i <= Math.min(lineCount, 50); i++) {
        const vals = lines[i].split(',');
        const row = {};
        headers.forEach((h, idx) => { row[h.trim()] = (vals[idx] || '').trim(); });
        instagramRows.push(row);
      }
    } else {
      try {
        instagramRows = await collectInstagram();
        writeCsv(instagramCsvPath, instagramRows, instagramCols);
      } catch (err) {
        logError(`Instagram collection failed: ${err.message}`);
      }
    }
  } else {
    try {
      instagramRows = await collectInstagram();
      writeCsv(instagramCsvPath, instagramRows, instagramCols);
    } catch (err) {
      logError(`Instagram collection failed: ${err.message}`);
    }
  }

  // Write master CSV
  writeMasterCsv(googleRows, youtubeRows, tiktokRows, instagramRows);

  // Summary
  console.log('');
  log('============================================================');
  log('  COLLECTION SUMMARY');
  log('============================================================');
  log(`  Google:    ${googleRows.length} / 50 items`);
  log(`  YouTube:   ${youtubeRows.length} / 50 items`);
  log(`  TikTok:    ${tiktokRows.length} / 50 items`);
  log(`  Instagram: ${instagramRows.length} / 50 items`);
  log(`  TOTAL:     ${googleRows.length + youtubeRows.length + tiktokRows.length + instagramRows.length} / 200 items`);
  log('============================================================');

  if (googleRows.length + youtubeRows.length + tiktokRows.length + instagramRows.length < 200) {
    log('');
    log('  NOTE: Some platforms returned fewer than 50 results.');
    log('  Check the individual CSV files and fill gaps manually.');
    log('  You may need to adjust hashtags for Instagram or');
    log('  verify your Apify account has sufficient credits.');
  }

  log('');
  log('  Output files:');
  log(`    ${path.join(CSV_DIR, 'google_results.csv')}`);
  log(`    ${path.join(CSV_DIR, 'youtube_results.csv')}`);
  log(`    ${path.join(CSV_DIR, 'tiktok_results.csv')}`);
  log(`    ${path.join(CSV_DIR, 'instagram_results.csv')}`);
  log(`    ${path.join(CSV_DIR, 'master_dataset.csv')}`);
  log('');
  log('  Next steps:');
  log('    1. Review each CSV for completeness');
  log('    2. Run the screenshot script: node screenshot_collector.js');
  log('    3. Import master_dataset.csv into your spreadsheet');
  log('    4. Begin DISCERN scoring');
  log('');
}

main().catch((err) => {
  logError(`Fatal error: ${err.message}`);
  console.error(err);
  process.exit(1);
});
