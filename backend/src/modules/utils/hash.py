import hashlib

# Compute file hash
# def compute_hash(file_path):
#     return hashlib.sha256(file_path.encode()).hexdigest()



def compute_hash(file_path, algorithm='sha256'):
    """
    Hashes the contents of a file using the specified algorithm.

    Args:
        file_path (str): The path to the file to hash.
        algorithm (str): The hashing algorithm to use (e.g., 'md5', 'sha1', 'sha256').

    Returns:
        str: The hexadecimal digest of the file's hash.
    """
    try:
        # Create a hash object based on the algorithm
        hash_func = hashlib.new(algorithm)
        
        # Open the file in binary mode and read in chunks
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):  # Read in 8KB chunks
                hash_func.update(chunk)
        
        # Return the hexadecimal digest of the hash
        return hash_func.hexdigest()
    except FileNotFoundError:
        return f"Error: File not found - {file_path}"
    except ValueError:
        return f"Error: Invalid hashing algorithm - {algorithm}"