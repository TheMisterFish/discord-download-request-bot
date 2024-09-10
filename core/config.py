import json
import os

DATA_DIR = 'data'

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

CONFIG_FILE = os.path.join(DATA_DIR, 'config.json')

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            'cooldown': {
                'limit': 1,
                'timeout': 3
            },
            'admin_always_download': True,
            'link_channels': {},
            'allowed_channels': {},
            'ignored_users': {},
        }
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config, bot=None):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4, sort_keys=True)

def create_config():
    save_config(load_config())