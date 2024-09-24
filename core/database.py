import os
import json
import pandas as pd
from fuzzywuzzy import fuzz
import re
from discord.ext import commands

from core.config import DATA_DIR
from core.logger import get_server_logger

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class ServerDatabase:
    def __init__(self, server_id):
        self.server_id = server_id
        self.server_dir = os.path.join(DATA_DIR, str(server_id))
        self.serverLogger = get_server_logger(self.server_id)
        
        if not os.path.exists(self.server_dir):
            os.makedirs(self.server_dir)

        self.download_db_file = os.path.join(self.server_dir, 'download_database.csv')
        self.video_db_file = os.path.join(self.server_dir, 'video_database.csv')

        self.download_db = self._load_or_create_df(self.download_db_file, ['id', 'name', 'links'])
        self.video_db = self._load_or_create_df(self.video_db_file, ['name', 'tag', 'links'])

    def _load_or_create_df(self, file_path, columns):
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            df['links'] = df['links'].apply(json.loads)
        else:
            df = pd.DataFrame(columns=columns)
        return df

    def _save_df(self, df, file_path):
        df_to_save = df.copy()
        df_to_save['links'] = df_to_save['links'].apply(json.dumps)
        df_to_save.to_csv(file_path, index=False)

    def update_download_database(self, id: str, name, channel, link):
        id = id.upper()
        existing_entry = self.download_db[self.download_db['id'] == id]

        if not existing_entry.empty:
            links = existing_entry['links'].iloc[0]
            links[channel] = link
            self.download_db.loc[self.download_db['id'] == id, 'name'] = name
            self.download_db.loc[self.download_db['id'] == id, 'links'] = [links]
            self.serverLogger.logger.info(f"Server {self.server_id}: Updated existing entry to link database: ID={id}, Name={name}, Channel={channel}")
        else:
            links = {channel: link}
            new_entry = pd.DataFrame({'id': [id], 'name': [name], 'links': [links]})
            self.download_db = pd.concat([self.download_db, new_entry], ignore_index=True)
            self.serverLogger.logger.info(f"Server {self.server_id}: Added new entry to link database: ID={id}, Name={name}, Channel={channel}")

        self._save_df(self.download_db, self.download_db_file)

    def update_video_database(self, name, channel, link, tag):
        existing_entry = self.video_db[self.video_db['name'] == name]

        if not existing_entry.empty:
            links = existing_entry['links'].iloc[0]
            links[channel] = link
            self.video_db.loc[self.video_db['name'] == name, 'tag'] = tag
            self.video_db.loc[self.video_db['name'] == name, 'links'] = [links]
            self.serverLogger.logger.info(f"Server {self.server_id}: Updated existing entry to video database: Name={name}, Channel={channel}")
        else:
            links = {channel: link}
            new_entry = pd.DataFrame({'name': [name], 'tag': [tag], 'links': [links]})
            self.video_db = pd.concat([self.video_db, new_entry], ignore_index=True)
            self.serverLogger.logger.info(f"Server {self.server_id}: Added new entry to video database: Name={name}, Channel={channel}")

        self._save_df(self.video_db, self.video_db_file)

    def get_download_entry(self, id):
        entry = self.download_db[self.download_db['id'] == id]
        return (entry['name'].iloc[0], entry['links'].iloc[0]) if not entry.empty else (None, None)

    def get_video_entry(self, name):
        entry = self.video_db[self.video_db['name'] == name]
        return (entry['tag'].iloc[0], entry['links'].iloc[0]) if not entry.empty else None

    def get_download_ids(self, count):
        return self.download_db['id'].tail(count).tolist()

    def get_matching_download_ids(self, count, query=None):
        if query:
            matched = self.download_db[self.download_db['id'].str.lower().str.contains(query.lower())]
            return matched['id'].head(count).tolist()
        else:
            return self.download_db['id'].tail(count).tolist()

    def get_download_names(self, count, query=None, percentage=0):
        if query:
            matched = self.download_db.apply(lambda row: fuzz.ratio(query.lower(), row['name'].lower()), axis=1)
            matched = self.download_db[matched >= percentage].sort_values(by='name', key=lambda x: matched[x.index], ascending=False)
            return matched['name'].head(count).tolist()
        else:
            return self.download_db['name'].tail(count).tolist()
        
    def get_download_id_names(self, count, query=None, percentage=0):
        if not query:
            result = self.download_db.tail(count)
            return list(zip(result['id'], result['name']))

        query = query.lower()

        def match_score(row):
            name_score = fuzz.ratio(query, row['name'].lower())
            id_score = 100 if query in row['id'].lower() else 0
            return max(name_score, id_score)

        self.download_db['score'] = self.download_db.apply(match_score, axis=1)
        matched = self.download_db[self.download_db['score'] >= percentage].sort_values(by='score', ascending=False)

        result = matched.head(count)
        return list(zip(result['id'], result['name']))

    def get_video_names(self, count, query=None, percentage=0):
        if query:
            matched = self.video_db.apply(lambda row: fuzz.ratio(query.lower(), row['name'].lower()), axis=1)
            matched = self.video_db[matched >= percentage].sort_values(by='name', key=lambda x: matched[x.index], ascending=False)
            return matched['name'].head(count).tolist()
        else:
            return self.video_db['name'].tail(count).tolist()

    def get_matching_videos(self, count, query=None, percentage=50):
        if not query:
            return self.video_db.tail(count).to_dict('records')

        query = query.lower()

        def match_score(row):
            name = row['name'].lower()
            
            if query in name:
                return 100
            
            name_score = fuzz.partial_ratio(query, name)
            return name_score

        matched = self.video_db.apply(match_score, axis=1)
        matched = self.video_db[matched >= percentage].sort_values(by='name', key=lambda x: matched[x.index], ascending=False)
        return matched.head(count).to_dict('records')

    def get_matching_downloads(self, count, query=None, percentage=50):
        if not query:
            return self.download_db.tail(count).to_dict('records')

        query = query.lower().strip()

        def match_score(row):
            name = row['name'].lower()
            id = str(row['id']).lower()
            
            if query == name or query == id:
                return 200 
            
            if query in name or query in id:
                return 100
            
            name_score = fuzz.ratio(query, name)
            id_score = fuzz.ratio(query, id)
            return max(name_score, id_score)

        self.download_db['score'] = self.download_db.apply(match_score, axis=1)
        matched = self.download_db[self.download_db['score'] >= percentage].sort_values(by='score', ascending=False)
        
        exact_matches = matched[matched['score'] == 200]
        if not exact_matches.empty:
            return exact_matches.head(1).to_dict('records')
        
        return matched.head(count).to_dict('records')

# Dictionary to store database instances for each server
server_databases = {}

def get_server_database(server_id):
    if not server_id:
        raise commands.NoPrivateMessage("This command cannot be used in private messages.")
    if server_id not in server_databases:
        server_databases[server_id] = ServerDatabase(server_id)
    return server_databases[server_id]
