import os
import sys
import hashlib
import shutil
import time


def calculate_md5(file_path):
    with open(file_path, 'rb') as file:
        md5_hash = hashlib.md5()
        while chunk := file.read(8192):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def sync_folders(source_path, replica_path, log_file_path):
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"Synchronization started at {time.ctime()}\n")

        for root, dirs, files in os.walk(source_path):
            for file in files:
                source_file_path = os.path.join(root, file)
                replica_file_path = os.path.join(replica_path, os.path.relpath(source_file_path, source_path))

                source_file_md5 = calculate_md5(source_file_path)

                if not os.path.exists(replica_file_path) or calculate_md5(replica_file_path) != source_file_md5:
                    shutil.copy2(source_file_path, replica_file_path)
                    log_file.write(f"Copied file: {source_file_path} -> {replica_file_path}\n")

        for root, dirs, files in os.walk(replica_path, topdown=False):
            for dir in dirs:
                replica_dir_path = os.path.join(root, dir)
                source_dir_path = os.path.join(source_path, os.path.relpath(replica_dir_path, replica_path))

                if not os.path.exists(source_dir_path):
                    shutil.rmtree(replica_dir_path)
                    log_file.write(f"Removed directory: {replica_dir_path}\n")

        log_file.write(f"Synchronization completed at {time.ctime()}\n")


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Usage: python sync_folders.py source_folder replica_folder log_file")
        sys.exit(1)

    source_folder = sys.argv[1]
    replica_folder = sys.argv[2]
    log_file = sys.argv[3]

    interval_seconds = 60

    while True:
        sync_folders(source_folder, replica_folder, log_file)
        time.sleep(interval_seconds)
