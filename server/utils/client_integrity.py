import hashlib
import os

def calculate_file_hash(file_path, hash_algorithm="sha256"):
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

def hash_files_in_directory(directory_path, hash_algorithm="sha256"):
    file_hashes = {}
    
    try:
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            if os.path.isfile(file_path):
                #TODO check subdirectories
                file_hash = calculate_file_hash(file_path, hash_algorithm)
                file_hashes[filename] = file_hash
    except Exception as e:
        print(f"Error reading directory: {str(e)}")
    
    return file_hashes

directory_path = '/home/vini/code/VPeron/SOC/api_siem/client'
hash_algorithm = 'sha256'

file_hashes = hash_files_in_directory(directory_path, hash_algorithm)

if file_hashes:
    for filename, file_hash in file_hashes.items():
        print(f'{filename}: {file_hash}')
else:
    print("No files found in the directory.")


# needs to move to a separate file
current_client = """
siem_client.py: b69c2e4cfe444572568e89f7d8cdaf86677e730e5e7d4e378595c18238c58d00
client.py: 3fe7fd34b637b9ce2799b5549ba9a5efda8a98a19670aa2edf5d2a22d000e443
custom_logger.py: 1279862e5dbafd189cf8cb373206d0aff4ee7c7d0c6904cbf7683bb9f9bb9508
client_init.py: e9e15e52b68479a54ea52f4ee72d942d609facf8016b5fcbb8e86f941177dcc6
"""