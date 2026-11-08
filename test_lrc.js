const lrcText = "[00:19.51] Line 1\n[00:24.13] Line 2";
const timeRegex = /\[(\d{1,3}):(\d{1,2})(?:[:.](\d{1,3}))?\]/g;
let match;
while ((match = timeRegex.exec(lrcText)) !== null) {
    const min = parseInt(match[1]);
    const sec = parseInt(match[2]);
    const fracStr = match[3] || "";
    let ms = 0;
    if (fracStr.length === 1) ms = parseInt(fracStr) * 100;
    else if (fracStr.length === 2) ms = parseInt(fracStr) * 10;
    else if (fracStr.length === 3) ms = parseInt(fracStr);
    const timeMs = min * 60000 + sec * 1000 + ms;
    console.log("Time:", timeMs);
}
