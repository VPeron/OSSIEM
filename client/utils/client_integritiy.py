import hashlib
import os
import json

with open("client_conf.json", "r") as conf_obj:
    data = json.load(conf_obj)

CLIENT_PATH = data["client_filepath"]
HASH_ALGO = data["hash_algorithm"]


def calculate_file_hash(file_path, hash_algorithm=HASH_ALGO):
    try:
        hasher = hashlib.new(hash_algorithm)
        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                hasher.update(data)
        return hasher.hexdigest()
    except Exception as e:
        return f"Error hashing {file_path}: {str(e)}"

def should_ignore_file_or_directory(name):
    # Define patterns for directories or files to ignore
    ignore_patterns = ["__pycache__", "client_conf.json", "client_init.log", "main_client.log"]
    for pattern in ignore_patterns:
        if pattern in name:
            return True
    return False

def hash_files_in_directory(directory_path, hash_algorithm=HASH_ALGO):
    file_hashes = {}
    
    try:
        for root, dirs, files in os.walk(directory_path):
            # Filter out directories or files to ignore
            dirs[:] = [d for d in dirs if not should_ignore_file_or_directory(d)]
            files[:] = [f for f in files if not should_ignore_file_or_directory(f)]
            
            for filename in files:
                file_path = os.path.join(root, filename)
                file_hash = calculate_file_hash(file_path, hash_algorithm)
                file_hashes[os.path.relpath(file_path, directory_path)] = file_hash
    except Exception as e:
        print(f"Error reading directory: {str(e)}")
    
    return file_hashes

if __name__ == "__main__":
    file_hashes = hash_files_in_directory(CLIENT_PATH, HASH_ALGO)

    if file_hashes:
        for filename, file_hash in file_hashes.items():
            print(f'{filename}: {file_hash}')
    else:
        print("No files found in the directory.")