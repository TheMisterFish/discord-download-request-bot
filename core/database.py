import csv
import json
import os

from core.config import DATABASE_FILE

def init_database():
    if not os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Name', 'Links'])

def update_database(id: str, name, channel, link):
    id = id.upper()
    rows = []
    updated = False
    with open(DATABASE_FILE, 'r') as f:
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
    
    with open(DATABASE_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)

def get_entry(id):
    with open(DATABASE_FILE, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == id:
                return row[1], json.loads(row[2])
    return None, None