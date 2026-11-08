import re

with open('app/src/main/AndroidManifest.xml', 'r') as f:
    content = f.read()

if 'REQUEST_INSTALL_PACKAGES' not in content:
    target = '<uses-permission android:name="android.permission.INTERNET" />'
    replace = '<uses-permission android:name="android.permission.INTERNET" />\n    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />'
    content = content.replace(target, replace)
    
    # Also add provider
    if '<provider' not in content:
        provider_xml = """
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.provider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/provider_paths" />
        </provider>"""
        content = content.replace('</application>', provider_xml + '\n    </application>')

    with open('app/src/main/AndroidManifest.xml', 'w') as f:
        f.write(content)
    print("Manifest patched")
else:
    print("Already patched")
