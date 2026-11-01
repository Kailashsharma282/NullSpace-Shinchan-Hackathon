const fs = require('fs');
const path = require('path');
const puppeteer = require('../frontend/node_modules/puppeteer-core');

const delay = (ms) => new Promise(r => setTimeout(r, ms));

async function run() {
  const chromePath = fs.existsSync('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe')
    ? 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    : 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe';

  console.log('Using browser binary:', chromePath);

  const browser = await puppeteer.launch({
    executablePath: chromePath,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 950 });

  console.log('Navigating to http://127.0.0.1:8080...');
  await page.goto('http://127.0.0.1:8080', { waitUntil: 'networkidle2' });

  // Pre-load demo via API to guarantee active dataset
  console.log('Loading demo dataset...');
  await page.evaluate(async () => {
    await fetch('/api/demo/load', { method: 'POST' });
  });
  await page.reload({ waitUntil: 'networkidle2' });
  await delay(2500);

  const screenshotDir = path.join(__dirname, '..', 'docs', 'screenshots');
  const artifactDir = 'C:\\Users\\kaila\\.gemini\\antigravity\\brain\\139c2371-8f84-46d5-8b71-884de8583d6e';

  if (!fs.existsSync(screenshotDir)) fs.mkdirSync(screenshotDir, { recursive: true });

  // 1. Dashboard / Overview Screenshot
  console.log('Capturing Dashboard Overview screenshot...');
  const dashPath = path.join(screenshotDir, 'dashboard.png');
  await page.screenshot({ path: dashPath });
  fs.copyFileSync(dashPath, path.join(artifactDir, 'dashboard.png'));

  // 2. Dark Spots View
  console.log('Navigating to Dark Spots tab...');
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const btn = btns.find(b => b.textContent && b.textContent.includes('Dark Spots'));
    if (btn) btn.click();
  });
  await delay(1500);
  const darkPath = path.join(screenshotDir, 'darkspots.png');
  await page.screenshot({ path: darkPath });
  fs.copyFileSync(darkPath, path.join(artifactDir, 'darkspots.png'));

  // 3. Contradictions View
  console.log('Navigating to Contradictions tab...');
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const btn = btns.find(b => b.textContent && b.textContent.includes('Contradictions'));
    if (btn) btn.click();
  });
  await delay(1500);
  const confPath = path.join(screenshotDir, 'contradictions.png');
  await page.screenshot({ path: confPath });
  fs.copyFileSync(confPath, path.join(artifactDir, 'contradictions.png'));

  // 4. Verification Checklist View
  console.log('Navigating to Verification Checklist tab...');
  await page.evaluate(() => {
    const btns = Array.from(document.querySelectorAll('button'));
    const btn = btns.find(b => b.textContent && b.textContent.includes('Verification Checklist'));
    if (btn) btn.click();
  });
  await delay(1500);
  const chkPath = path.join(screenshotDir, 'checklist.png');
  await page.screenshot({ path: chkPath });
  fs.copyFileSync(chkPath, path.join(artifactDir, 'checklist.png'));

  console.log('All E2E screenshots successfully captured and saved!');
  await browser.close();
}

run().catch((err) => {
  console.error('Error during E2E visual capture:', err);
  process.exit(1);
});
