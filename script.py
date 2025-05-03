import os

# Dynamically set the base directory to the script's location
base_dir = os.path.dirname(os.path.abspath(__file__))

# Create 10 folders without subfolders and do not recreate existing folders
for i in range(1, 11):
    folder_name = f'apartment_{i}'
    folder_path = os.path.join(base_dir, folder_name)
    
    # Check if the folder already exists
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)  # Create the main folder
        print(f"Created folder: {folder_path}")
    else:
        print(f"Folder already exists: {folder_path}")
    
    # Add a description.txt file inside the folder
    description_file_path = os.path.join(folder_path, "description.txt")
    if not os.path.exists(description_file_path):
        with open(description_file_path, "w") as file:
            file.write(f"This is the description for {folder_name}.")
        print(f"Created description.txt in: {folder_path}")
    else:
        print(f"description.txt already exists in: {folder_path}")

print("Folder creation process completed.")