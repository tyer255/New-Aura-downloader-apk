const https = require('https');
https.get('https://aura-downloader-yg40.onrender.com/api/spotify-resolve?trackId=0wHYuCTWPntEgWiUVED4wB&title=Aarzu&artist=Noor&artists=Noor%2CKhan%2CMadhurxo&durationMs=187567&isrc=', (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => console.log(data));
});
