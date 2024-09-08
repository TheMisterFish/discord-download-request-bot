import json
import os

DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')
DATABASE_FILE = os.path.join(DATA_DIR, 'database.csv')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {'link_channels': [], 'ignored_users': []}
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)