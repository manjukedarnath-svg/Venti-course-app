const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto('file://' + __dirname + '/book.html', { waitUntil: 'networkidle' }); await pg.evaluate(() => document.fonts.ready);
  await pg.pdf({ path: __dirname + '/VentCourse Simulator Scenarios.pdf', format: 'A4', printBackground: true, preferCSSPageSize: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: '<div style="width:100%;font:7px monospace;letter-spacing:1px;color:#5E554B;padding:0 15mm;display:flex;justify-content:space-between;"><span>VENTCOURSE · SIMULATOR SCENARIO BOOK</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>' });
  await b.close(); })();
