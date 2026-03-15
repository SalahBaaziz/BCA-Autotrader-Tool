# Autotrader Scrape Chrome Extension

This extension reads a clipboard image, runs OCR, parses key car details, opens an AutoTrader search, and analyzes the current results page.

## Local Installation
1. Open Chrome and go to `chrome://extensions`.
2. Enable `Developer mode`.
3. Click `Load unpacked`.
4. Select the folder:
   `/Users/salahbaaziz/Desktop/Projects/Autotrader Scrape/chrome extension`

## Usage
1. Copy a car listing screenshot to your clipboard.
2. Click the extension icon.
3. Click `Read Clipboard Image`, then `Parse Text`.
4. Click `Open Search` to load an AutoTrader search.
5. On the search results page, click `Analyze Current Page`.

## Files
- `manifest.json`: Extension configuration (MV3).
- `popup.html`: UI for OCR and analysis.
- `popup.js`: OCR + parsing + analysis logic.
- `content.js`: Scrapes prices and mileages from AutoTrader pages.
- `tesseract.min.js`, `tesseract-worker.js`, `tesseract-core.wasm`, `eng.traineddata.gz`: OCR runtime assets.
