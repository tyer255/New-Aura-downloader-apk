const https = require("https");
const query = "Rick Astley Never Gonna Give You Up";
const encoded = encodeURIComponent(query);
https.get("https://www.youtube.com/results?search_query=" + encoded, (res) => {
    let data = "";
    res.on("data", chunk => data += chunk);
    res.on("end", () => {
        const match = data.match(/"videoId":"([a-zA-Z0-9_-]{11})"/);
        console.log("Video ID: " + (match ? match[1] : "not found"));
    });
});
