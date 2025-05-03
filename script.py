import os
import platform

# Detect the operating system and set the base directory
if platform.system() == "Windows":
    base_dir = r'd:\projects\vibe-code-hackaton'
elif platform.system() == "Darwin":  # macOS
    base_dir = '/Users/your_username/projects/vibe-code-hackaton'
else:
    raise OSError("Unsupported operating system")

# Create 10 folders with 3 subfolders each
for i in range(1, 11):
    folder_name = f'apartment_{i}'
    folder_path = os.path.join(base_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)  # Create the main folder
    
    # Create subfolders for room numbers
    for j in range(1, 4):
        subfolder_name = f'room_{j}'
        subfolder_path = os.path.join(folder_path, subfolder_name)
        os.makedirs(subfolder_path, exist_ok=True)

print("Folders and subfolders created successfully.")