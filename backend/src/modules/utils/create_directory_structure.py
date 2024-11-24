import os
import shutil

def create_directory_structure(base_path, files):
    """ Recursively create directories based on metadata. """
    # Clear the directory if it already exists
    # if os.path.exists(base_path):
    #     shutil.rmtree(base_path)
    
    # Create the base directory
    # os.makedirs(base_path, exist_ok=True)

    clear_directory(base_path)
    # Create all files
    for file in files:
        file_path = os.path.join(base_path, file.filename)
        directory_path = os.path.dirname(file_path)
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        file.save(os.path.join(file_path))

def clear_directory(directory_path: str):
    """
    Clears all files and subdirectories inside the given directory without deleting the directory itself.

    :param directory_path: Path to the directory to be cleared
    """
    for item in os.listdir(directory_path):
        item_path = os.path.join(directory_path, item)
        if os.path.isfile(item_path) or os.path.islink(item_path):  # Check if it's a file or symlink
            os.unlink(item_path)  # Remove the file or symlink
        elif os.path.isdir(item_path):  # Check if it's a directory
            shutil.rmtree(item_path)  # Recursively delete the directory