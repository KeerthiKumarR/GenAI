"""
File Organizer Script using pathlib and shutil
Organizes messy_data directory by sorting files into subfolders based on file extension.
"""

from pathlib import Path
import shutil


def organize_directory(directory_path: Path):
    target_dir = Path(directory_path).resolve()

    if not target_dir.exists() or not target_dir.is_dir():
        print(f"Error: Directory '{target_dir}' does not exist.")
        return

    print(f"📂 Organizing directory: {target_dir}\n")

    moved_count = 0

    for item in target_dir.iterdir():
        # Only process files in the top level of messy_data (ignore directories & hidden files like .DS_Store)
        if item.is_file():
            # Skip hidden files and macOS system metadata like .DS_Store
            if item.name.startswith("."):
                continue

            # Get extension without the leading dot (e.g., 'pdf', 'png', 'txt')
            ext = item.suffix.lower().lstrip(".")

            # Categorize files without extension into 'others'
            folder_name = ext if ext else "others"

            # Create destination folder using pathlib
            dest_dir = target_dir / folder_name
            dest_dir.mkdir(parents=True, exist_ok=True)

            dest_path = dest_dir / item.name

            # Move file using shutil
            shutil.move(str(item), str(dest_path))
            print(f"  ✓ Moved '{item.name}' -> '{folder_name}/'")
            moved_count += 1

    print(f"\n🎉 Successfully organized {moved_count} file(s) into subdirectories!")


if __name__ == "__main__":
    messy_data_dir = Path(__file__).parent / "messy_data"
    organize_directory(messy_data_dir)
