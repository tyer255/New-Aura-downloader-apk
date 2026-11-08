const fs = require('fs');
const simpleIcons = require('simple-icons');

const icons = {
  'youtube': 'siYoutube',
  'instagram': 'siInstagram',
  'tiktok': 'siTiktok',
  'facebook': 'siFacebook',
  'reddit': 'siReddit',
  'pinterest': 'siPinterest',
  'x': 'siX',
  'linkedin': 'siLinkedin'
};

if (!fs.existsSync('/workspace/app/src/main/res/drawable')) {
  fs.mkdirSync('/workspace/app/src/main/res/drawable', { recursive: true });
}

for (const [name, siName] of Object.entries(icons)) {
  const icon = simpleIcons[siName];
  if (!icon) {
    console.log('Not found: ' + siName);
    continue;
  }
  const xml = `<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FFFFFFFF"
        android:pathData="${icon.path}" />
</vector>
`;
  fs.writeFileSync(`/workspace/app/src/main/res/drawable/ic_${name}.xml`, xml);
}
console.log('Drawables generated.');
