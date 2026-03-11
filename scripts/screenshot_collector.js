// ============================================================================
// Screenshot Collector — Takes screenshots of all 200 URLs
// ============================================================================
//
// Reads URLs from the CSV files produced by apify_collector.js and visits
// each one with Playwright to take a full-page screenshot.
//
// Usage:
//   1. Run apify_collector.js first to generate the CSVs
//   2. node screenshot_collector.js
//
// Output:
//   ../data/screenshots/google/WEB-01.png  through WEB-50.png
//   ../data/screenshots/youtube/YT-01.png  through YT-50.png
//   ../data/screenshots/tiktok/TT-01.png   through TT-50.png
//   ../data/screenshots/instagram/IG-01.png through IG-50.png
//
// ============================================================================

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const BASE_DIR = path.resolve(__dirname, '..');
const CSV_DIR = path.join(BASE_DIR, 'data', 'csv');
const SCREENSHOT_BASE = path.join(BASE_DIR, 'data', 'screenshots');

const PAGE_TIMEOUT = 20000; // 20 seconds per page
const DELAY_BETWEEN_PAGES = 1500; // 1.5 sec between pages

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

function log(msg) {
  const ts = new Date().toISOString().replace('T', ' ').replace(/\.\d+Z/, '');
  console.log(`[${ts}] ${msg}`);
}

function parseCsv(filePath) {
  if (!fs.existsSync(filePath)) return [];
  const content = fs.readFileSync(filePath, 'utf-8');
  const lines = content.split('\n').filter((l) => l.trim());
  if (lines.length < 2) return [];

  const headers = lines[0].split(',').map((h) => h.trim());
  const rows = [];

  for (let i = 1; i < lines.length; i++) {
    // Simple CSV parsing (handles quoted fields)
    const values = [];
    let current = '';
    let inQuotes = false;
    for (const char of lines[i]) {
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        values.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    values.push(current.trim());

    const row = {};
    headers.forEach((h, idx) => {
      row[h] = values[idx] || '';
    });
    rows.push(row);
  }

  return rows;
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

// ---------------------------------------------------------------------------
// Screenshot logic
// ---------------------------------------------------------------------------

async function takeScreenshots(rows, screenshotDir, context) {
  ensureDir(screenshotDir);
  let success = 0;
  let failed = 0;

  for (const row of rows) {
    const itemId = row.Item_ID || row.item_id || '';
    const url = row.URL || row.url || '';

    if (!itemId || !url) {
      log(`  SKIP: Missing ID or URL`);
      failed++;
      continue;
    }

    const screenshotPath = path.join(screenshotDir, `${itemId}.png`);

    // Skip if already exists (resumable)
    if (fs.existsSync(screenshotPath)) {
      log(`  SKIP: ${itemId} (already exists)`);
      success++;
      continue;
    }

    const page = await context.newPage();
    try {
      log(`  Capturing ${itemId}: ${url.substring(0, 80)}...`);
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: PAGE_TIMEOUT });
      await sleep(2000); // Wait for content to render
      await page.screenshot({ path: screenshotPath, fullPage: false }); // viewport only
      success++;
    } catch (err) {
      log(`  FAIL: ${itemId} — ${err.message.substring(0, 100)}`);
      failed++;
    } finally {
      await page.close();
    }

    await sleep(DELAY_BETWEEN_PAGES);
  }

  return { success, failed };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  log('============================================================');
  log('  Screenshot Collector');
  log('============================================================');

  // Read all CSVs
  const platforms = [
    { file: 'google_results.csv', dir: 'google', label: 'Google' },
    { file: 'youtube_results.csv', dir: 'youtube', label: 'YouTube' },
    { file: 'tiktok_results.csv', dir: 'tiktok', label: 'TikTok' },
    { file: 'instagram_results.csv', dir: 'instagram', label: 'Instagram' },
  ];

  // Launch browser
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
    userAgent:
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
      '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
  });

  const summary = {};

  for (const platform of platforms) {
    const csvPath = path.join(CSV_DIR, platform.file);
    const rows = parseCsv(csvPath);

    if (rows.length === 0) {
      log(`\n  ${platform.label}: No CSV found or empty — skipping`);
      summary[platform.label] = { success: 0, failed: 0 };
      continue;
    }

    log(`\n=== ${platform.label}: ${rows.length} items ===`);
    const screenshotDir = path.join(SCREENSHOT_BASE, platform.dir);
    const result = await takeScreenshots(rows, screenshotDir, context);
    summary[platform.label] = result;
  }

  await browser.close();

  // Print summary
  log('\n============================================================');
  log('  SCREENSHOT SUMMARY');
  log('============================================================');
  let totalSuccess = 0;
  let totalFailed = 0;
  for (const [platform, result] of Object.entries(summary)) {
    log(`  ${platform}: ${result.success} captured, ${result.failed} failed`);
    totalSuccess += result.success;
    totalFailed += result.failed;
  }
  log(`  TOTAL: ${totalSuccess} captured, ${totalFailed} failed`);
  log('============================================================');
}

main().catch((err) => {
  console.error(`Fatal error: ${err.message}`);
  process.exit(1);
});
