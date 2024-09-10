import csv
import json
import os

from core.config import DATA_DIR
from core.logger import logger

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DOWNLOAD_DATABASE_FILE = os.path.join(DATA_DIR, 'download_database.csv')
VIDEO_DATABASE_FILE = os.path.join(DATA_DIR, 'video_database.csv')

def init_database():
    if not os.path.exists(DOWNLOAD_DATABASE_FILE):
        with open(DOWNLOAD_DATABASE_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Links'])

    if not os.path.exists(VIDEO_DATABASE_FILE):
        with open(VIDEO_DATABASE_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Tag', 'Links'])

def update_download_database(id: str, name, channel, link):
    id = id.upper()
    rows = []
    updated = False
    with open(DOWNLOAD_DATABASE_FILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == id:
                links = json.loads(row[2])
                links[channel] = link
                rows.append([id, name, json.dumps(links)])
                updated = True
            else:
                rows.append(row)
    
    if not updated:
        links = {channel: link}
        rows.append([id, name, json.dumps(links)])
        logger.info(f"Added new entry to link database: ID={id}, Name={name}, Channel={channel}")

    with open(DOWNLOAD_DATABASE_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def update_video_database(name, channel, link, tag):
    rows = []
    updated = False

    with open(VIDEO_DATABASE_FILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == name:
                links = json.loads(row[2])
                links[channel] = link
                rows.append([name, tag, json.dumps(links)])
                updated = True
            else:
                rows.append(row)
    
    if not updated:
        links = {channel: link}
        rows.append([name, tag, json.dumps(links)])
        logger.info(f"Added new entry to video database: Name={name}, Channel={channel}")

    with open(VIDEO_DATABASE_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)


def get_download_entry(id):
    with open(DOWNLOAD_DATABASE_FILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == id:
                return row[1], json.loads(row[2])
    return None, None

def get_video_entry(name):
    with open(VIDEO_DATABASE_FILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == name:
                return row[1], json.loads(row[2])
    return None