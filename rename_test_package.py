import os
import shutil

OLD_PACKAGE = "com.example"
NEW_PACKAGE = "com.auradownloader.app"
OLD_DIR = OLD_PACKAGE.replace('.', '/')
NEW_DIR = NEW_PACKAGE.replace('.', '/')

def move_dir(src_base):
    old_path = os.path.join(src_base, OLD_DIR)
    new_path = os.path.join(src_base, NEW_DIR)
    
    if os.path.exists(old_path):
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.move(old_path, new_path)
        print(f"Moved {old_path} to {new_path}")
        
        try:
            os.rmdir(os.path.join(src_base, "com/example"))
            os.rmdir(os.path.join(src_base, "com"))
        except:
            pass

move_dir("app/src/test/java")
move_dir("app/src/androidTest/java")
