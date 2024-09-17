import json
import os
from core.logger import get_server_logger

DATA_DIR = 'data'

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def default_config():
    return {
        'cooldown': {
            'limit': 1,
            'timeout': 3
        },
        'admin_always_download': True,
        'download_channels': {},
        'video_channels': {},
        'allowed_channels': {},
        'ignored_users': {},
    }

def get_server_config_file(server_id):
    server_dir = os.path.join(DATA_DIR, str(server_id))
    if not os.path.exists(server_dir):
        os.makedirs(server_dir)
    return os.path.join(server_dir, 'config.json')

server_configs = {}

def load_config(server_id):
    if server_id in server_configs:
        return server_configs[server_id]

    config_file = get_server_config_file(server_id)
    if not os.path.exists(config_file):
        config = default_config()
    else:
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            serverLogger = get_server_logger(server_id)
            serverLogger.logger.error(f"Error loading config for server {server_id}: {e}")
            config = default_config()

    server_configs[server_id] = config
    return config

def save_config(server_id, config, bot=None):
    server_configs[server_id] = config
    config_file = get_server_config_file(server_id)
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4, sort_keys=True)
