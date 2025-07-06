import os
import shutil
import stat
import time

# === CONFIGURATION ===
FILE_EXTENSION = ".txt"  # Change this to your desired file type
OVERWRITE_EXISTING = True  # Set to False to skip existing files
# =====================

# Destination = folder where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DESTINATION_FOLDER = SCRIPT_DIR

def remove_readonly(func, path, exc_info):
    """Helper to handle read-only files on Windows."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def get_all_windows_drives():
    """Get valid Windows drive letters (C:\, D:\, etc.)"""
    drives = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)
    return drives

def find_and_copy_files():
    print("🚀 Starting global file search...")
    print(f"📁 Target extension: {FILE_EXTENSION}")
    print(f"💾 Destination: {DESTINATION_FOLDER}\n")

    count = 0
    skipped = 0
    total_size = 0

    # Create destination folder if needed
    os.makedirs(DESTINATION_FOLDER, exist_ok=True)

    # Determine search roots based on OS
    if os.name == 'nt':
        roots = get_all_windows_drives()
    else:
        roots = ['/']

    # Search all drives/roots
    for root_path in roots:
        print(f"🔍 Searching in: {root_path}")
        try:
            for root, dirs, files in os.walk(root_path, topdown=True, onerror=None, followlinks=False):
                for filename in files:
                    try:
                        if filename.lower().endswith(FILE_EXTENSION.lower()):
                            src_path = os.path.join(root, filename)
                            dest_path = os.path.join(DESTINATION_FOLDER, filename)

                            # Handle duplicate filenames
                            base, ext = os.path.splitext(filename)
                            counter = 1
                            while os.path.exists(dest_path) and not OVERWRITE_EXISTING:
                                dest_path = os.path.join(DESTINATION_FOLDER, f"{base}_{counter}{ext}")
                                counter += 1

                            # Try to remove read-only flag on Windows
                            if os.path.exists(dest_path):
                                os.chmod(dest_path, stat.S_IWRITE)

                            # Copy file
                            shutil.copy2(src_path, dest_path)
                            file_size = os.path.getsize(src_path)
                            count += 1
                            total_size += file_size
                            print(f"✅ Copied: {filename} ({file_size / 1024:.2f} KB)")

                    except PermissionError:
                        print(f"⚠️  Skipped (Permission denied): {filename}")
                        skipped += 1
                    except Exception as e:
                        print(f"⚠️  Skipped (Error: {e}): {filename}")
                        skipped += 1
        except Exception as e:
            print(f"🚫 Cannot access path: {root_path} ({e})")

    # Final Summary
    print("\n==========================")
    print(f"Total files copied: {count}")
    print(f"Total size copied: {total_size / (1024 * 1024):.2f} MB")
    print(f"Total skipped: {skipped}")
    print("==========================")

if __name__ == "__main__":
    start_time = time.time()
    find_and_copy_files()
    duration = time.time() - start_time
    print(f"🏁 Operation complete in {duration:.2f} seconds")
    input("Press Enter to exit...")