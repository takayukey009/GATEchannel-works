const puppeteer = require('puppeteer');
const path = require('path');
const { PDFDocument } = require('pdf-lib');
const fs = require('fs');

(async () => {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();

    // PDF用紙サイズ (mm→px: 1mm = 96/25.4 px ≈ 3.7795px)
    const pdfWidthMM = 254;
    const pdfHeightMM = 142.875;
    const pxPerMm = 96 / 25.4;
    const widthPx = Math.round(pdfWidthMM * pxPerMm);
    const heightPx = Math.round(pdfHeightMM * pxPerMm);

    await page.setViewport({ width: widthPx, height: heightPx, deviceScaleFactor: 2 });

    const htmlPath = path.resolve(__dirname, 'sendagaya_scripts_tategaki.html');
    await page.goto('file:///' + htmlPath.replace(/\\/g, '/'), { waitUntil: 'load', timeout: 60000 });

    await page.evaluateHandle('document.fonts.ready');
    await new Promise(r => setTimeout(r, 2000));

    // ページ数を取得
    const pageCount = await page.evaluate(() => document.querySelectorAll('.page').length);
    console.log(`Found ${pageCount} pages. Capturing each as screenshot...`);

    // 全ページを非表示にするJSを注入
    await page.evaluate(() => {
        const style = document.createElement('style');
        style.id = 'capture-helper';
        style.textContent = `.page { display: none !important; } .page.active-capture { display: block !important; position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; z-index: 9999 !important; }`;
        document.head.appendChild(style);
    });

    // 1ページずつスクリーンショットを撮ってPDFに結合
    const mergedPdf = await PDFDocument.create();

    for (let i = 0; i < pageCount; i++) {
        // 現在のページだけアクティブにする
        await page.evaluate((idx) => {
            document.querySelectorAll('.page').forEach((p, j) => {
                p.classList.toggle('active-capture', j === idx);
            });
        }, i);

        await new Promise(r => setTimeout(r, 300));

        // スクリーンショットをPDFとして保存
        const screenshotBuffer = await page.screenshot({
            type: 'png',
            clip: { x: 0, y: 0, width: widthPx, height: heightPx },
        });

        // 画像をPDFページとして埋め込む
        const pngImage = await mergedPdf.embedPng(screenshotBuffer);

        // ページサイズをmm→pt (1mm = 2.83465pt)
        const ptPerMm = 2.83465;
        const pageWidthPt = pdfWidthMM * ptPerMm;
        const pageHeightPt = pdfHeightMM * ptPerMm;

        const pdfPage = mergedPdf.addPage([pageWidthPt, pageHeightPt]);
        pdfPage.drawImage(pngImage, {
            x: 0,
            y: 0,
            width: pageWidthPt,
            height: pageHeightPt,
        });

        console.log(`  Page ${i + 1}/${pageCount} captured.`);
    }

    const pdfBytes = await mergedPdf.save();
    const outputPath = path.resolve(__dirname, 'sendagaya_scripts_presentation.pdf');
    fs.writeFileSync(outputPath, pdfBytes);

    console.log(`PDF generated successfully! ${pageCount} pages, no blank pages.`);
    await browser.close();
})();
