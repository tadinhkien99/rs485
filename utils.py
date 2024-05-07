import os
import time


def create_directory(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def delete_old_pictures(folder, days=7):
    now = time.time()
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        if os.stat(filepath).st_mtime < now - days * 86400:
            os.remove(filepath)


