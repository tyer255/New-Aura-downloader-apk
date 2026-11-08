const https = require('https');
const payload = JSON.stringify({ url: 'https://open.spotify.com/track/0wHYuCTWPntEgWiUVED4wB?si=0Zy-UpIKTmOrdHhjN_4gSw' });
const options = {
  hostname: 'aura-downloader-yg40.onrender.com',
  port: 443,
  path: '/api/download',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(payload)
  }
};
const req = https.request(options, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => console.log(data));
});
req.write(payload);
req.end();
