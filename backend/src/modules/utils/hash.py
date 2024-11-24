import hashlib

# Compute file hash
def compute_hash(file_path):
    return hashlib.sha256(file_path.encode()).hexdigest()


