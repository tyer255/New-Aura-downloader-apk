import os
import shutil

OLD_PACKAGE = "com.example"
NEW_PACKAGE = "com.auradownloader.app"
OLD_DIR = OLD_PACKAGE.replace('.', '/')
NEW_DIR = NEW_PACKAGE.replace('.', '/')

# 1. Move directories
src_base = "app/src/main/java"
old_path = os.path.join(src_base, OLD_DIR)
new_path = os.path.join(src_base, NEW_DIR)

if os.path.exists(old_path):
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    shutil.move(old_path, new_path)
    print(f"Moved {old_path} to {new_path}")

    # Remove empty parent dirs of old path if empty
    try:
        os.rmdir(os.path.join(src_base, "com/example"))
        os.rmdir(os.path.join(src_base, "com"))
    except:
        pass

# 2. Find and replace in files
def replace_in_file(filepath, old_str, new_str):
    with open(filepath, 'r') as f:
        content = f.read()
    if old_str in content:
        content = content.replace(old_str, new_str)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Replaced in {filepath}")

for root, _, files in os.walk('.'):
    for file in files:
        if file.endswith(('.kt', '.xml', '.kts', '.json')) and 'node_modules' not in root and '.gradle' not in root and 'build' not in root:
            filepath = os.path.join(root, file)
            replace_in_file(filepath, OLD_PACKAGE, NEW_PACKAGE)
            replace_in_file(filepath, "com.aistudio.auradownloader.yhjxqz", NEW_PACKAGE)

