import os
import json
import sqlite3
from typing import List, Dict
from discord.ext import commands
from core.config import DATA_DIR
from core.logger import get_server_logger
from rapidfuzz import fuzz

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class ServerDatabase:
    def __init__(self, server_id):
        self.server_id = server_id
        self.server_dir = os.path.join(DATA_DIR, str(server_id))
        self.serverLogger = get_server_logger(self.server_id)

        if not os.path.exists(self.server_dir):
            os.makedirs(self.server_dir)

        self.db_path = os.path.join(self.server_dir, "server_data.db")
        self.db = sqlite3.connect(self.db_path, check_same_thread=False)
        self.db.row_factory = sqlite3.Row

        self._init_tables()
        self._watcher_cache = self._load_watcher_cache()

    def _init_tables(self):
        with self.db:
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS downloads (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    links TEXT
                )
            ''')
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    name TEXT PRIMARY KEY,
                    tag TEXT,
                    links TEXT
                )
            ''')
            self.db.execute('''
                CREATE TABLE IF NOT EXISTS watchers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    reply TEXT NOT NULL
                )
            ''')

            self.db.execute("CREATE INDEX IF NOT EXISTS idx_downloads_name ON downloads(name)")
            self.db.execute("CREATE INDEX IF NOT EXISTS idx_downloads_id ON downloads(id)")
            self.db.execute("CREATE INDEX IF NOT EXISTS idx_videos_name ON videos(name)")
            self.db.execute("CREATE INDEX IF NOT EXISTS idx_videos_tag ON videos(tag)")
            self.db.execute("CREATE INDEX IF NOT EXISTS idx_watchers_question ON watchers(question)")

    def update_download_database(self, id: str, name, channel, link):
        id = id.upper()
        cur = self.db.execute("SELECT links FROM downloads WHERE id = ?", (id,))
        row = cur.fetchone()

        with self.db:
            if row:
                links = json.loads(row["links"])
                links[channel] = link
                self.db.execute(
                    "UPDATE downloads SET name = ?, links = ? WHERE id = ?",
                    (name, json.dumps(links), id)
                )
            else:
                links = {channel: link}
                self.db.execute(
                    "INSERT INTO downloads (id, name, links) VALUES (?, ?, ?)",
                    (id, name, json.dumps(links))
                )

    def update_video_database(self, name, channel, link, tag):
        cur = self.db.execute("SELECT links FROM videos WHERE name = ?", (name,))
        row = cur.fetchone()

        with self.db:
            if row:
                links = json.loads(row["links"])
                links[channel] = link
                self.db.execute(
                    "UPDATE videos SET tag = ?, links = ? WHERE name = ?",
                    (tag, json.dumps(links), name)
                )
            else:
                links = {channel: link}
                self.db.execute(
                    "INSERT INTO videos (name, tag, links) VALUES (?, ?, ?)",
                    (name, tag, json.dumps(links))
                )

    def get_download_entry(self, id):
        row = self.db.execute("SELECT name, links FROM downloads WHERE id = ?", (id.upper(),)).fetchone()
        if row:
            return row["name"], json.loads(row["links"])
        return None, None

    def get_video_entry(self, name):
        row = self.db.execute("SELECT tag, links FROM videos WHERE name = ?", (name,)).fetchone()
        if row:
            return row["tag"], json.loads(row["links"])
        return None

    def get_download_ids(self, count):
        rows = self.db.execute("SELECT id FROM downloads ORDER BY rowid DESC LIMIT ?", (count,)).fetchall()
        return [row["id"] for row in rows]

    def get_matching_download_ids(self, count, query=None):
        if query:
            like = f"%{query.lower()}%"
            rows = self.db.execute(
                "SELECT id FROM downloads WHERE LOWER(id) LIKE ? ORDER BY rowid DESC LIMIT ?",
                (like, count)
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT id FROM downloads ORDER BY rowid DESC LIMIT ?", (count,)
            ).fetchall()
        return [row["id"] for row in rows]

    def get_download_names(self, count, query=None, percentage=0):
        if query:
            like = f"%{query.lower()}%"
            rows = self.db.execute(
                "SELECT name FROM downloads WHERE LOWER(name) LIKE ? ORDER BY rowid DESC LIMIT 500",
                (like,)
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT name FROM downloads ORDER BY rowid DESC LIMIT ?", (count,)
            ).fetchall()

        names = [row["name"] for row in rows]

        if query:
            query = query.lower()
            scored = [(name, fuzz.ratio(query, name.lower())) for name in names]
            filtered = sorted(
                [name for name, score in scored if score >= percentage],
                key=lambda x: -fuzz.ratio(query, x.lower())
            )
            return filtered[:count]

        return names[:count]

    def get_download_id_names(self, count, query=None, percentage=0):
        if query:
            like = f"%{query.lower()}%"
            rows = self.db.execute(
                "SELECT id, name FROM downloads WHERE LOWER(id) LIKE ? OR LOWER(name) LIKE ? ORDER BY rowid DESC LIMIT 500",
                (like, like)
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT id, name FROM downloads ORDER BY rowid DESC LIMIT ?", (count,)
            ).fetchall()

        results = [(row["id"], row["name"]) for row in rows]

        if query:
            query = query.lower()
            def score(row):
                id_score = 100 if query in row[0].lower() else 0
                name_score = fuzz.ratio(query, row[1].lower())
                return max(id_score, name_score)

            scored = [(id, name, score((id, name))) for id, name in results]
            filtered = [(id, name) for id, name, s in sorted(scored, key=lambda x: -x[2]) if s >= percentage]
            return filtered[:count]

        return results[:count]

    def get_video_names(self, count, query=None, percentage=0):
        if query:
            like = f"%{query.lower()}%"
            rows = self.db.execute(
                "SELECT name FROM videos WHERE LOWER(name) LIKE ? ORDER BY rowid DESC LIMIT 500",
                (like,)
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT name FROM videos ORDER BY rowid DESC LIMIT ?", (count,)
            ).fetchall()

        names = [row["name"] for row in rows]

        if query:
            query = query.lower()
            scored = [(name, fuzz.ratio(query, name.lower())) for name in names]
            filtered = sorted(
                [name for name, score in scored if score >= percentage],
                key=lambda x: -fuzz.ratio(query, x.lower())
            )
            return filtered[:count]

        return names[:count]

    def get_matching_videos(self, count, query=None, percentage=50):
        if query:
            like = f"%{query.lower()}%"
            rows = self.db.execute(
                "SELECT name, tag, links FROM videos WHERE LOWER(name) LIKE ? ORDER BY rowid DESC LIMIT 500",
                (like,)
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT name, tag, links FROM videos ORDER BY rowid DESC LIMIT ?", (count,)
            ).fetchall()

        if not query:
            return [dict(row) for row in rows]

        query = query.lower()
        def score(row):
            name = row["name"].lower()
            if query in name:
                return 100
            return fuzz.partial_ratio(query, name)

        scored = [(dict(row), score(row)) for row in rows]
        filtered = sorted(
            [r for r, s in scored if s >= percentage],
            key=lambda r: -fuzz.partial_ratio(query, r["name"].lower())
        )
        return filtered[:count]

    def get_matching_downloads(self, count, query=None, percentage=50):
        if query:
            like = f"%{query.lower()}%"
            rows = self.db.execute(
                "SELECT id, name, links FROM downloads WHERE LOWER(id) LIKE ? OR LOWER(name) LIKE ? ORDER BY rowid DESC LIMIT 500",
                (like, like)
            ).fetchall()
        else:
            rows = self.db.execute(
                "SELECT id, name, links FROM downloads ORDER BY rowid DESC LIMIT ?", (count,)
            ).fetchall()

        if not query:
            return [dict(id=row["id"], name=row["name"], links=json.loads(row["links"])) for row in rows]

        query = query.lower()
        def score(row):
            id_val = row["id"].lower()
            name_val = row["name"].lower()
            if query in id_val or query in name_val:
                return 100
            return max(fuzz.partial_ratio(query, id_val), fuzz.partial_ratio(query, name_val))

        scored = [(row, score(row)) for row in rows]
        filtered = sorted(
            [r for r, s in scored if s >= percentage],
            key=lambda r: -max(fuzz.partial_ratio(query, r["id"].lower()), fuzz.partial_ratio(query, r["name"].lower()))
        )
        return [dict(id=r["id"], name=r["name"], links=json.loads(r["links"])) for r in filtered[:count]]

    def _load_watcher_cache(self) -> List[Dict]:
        cur = self.db.execute("SELECT id, question, reply FROM watchers ORDER BY id ASC")
        watchers = []
        for row in cur:
            watchers.append({
                "id": row["id"],
                "question": row["question"],
                "reply": row["reply"]
            })
        return watchers

    def get_watchers(self) -> List[Dict]:
        return self._watcher_cache

    def add_watcher(self, question: str, reply: str) -> int:
        with self.db:
            cur = self.db.execute(
                "INSERT INTO watchers (question, reply) VALUES (?, ?)",
                (question, reply)
            )
            new_id = cur.lastrowid
        self._watcher_cache = self._load_watcher_cache()
        return new_id

    def update_watcher(self, watcher_id: int, question: str, reply: str) -> bool:
        with self.db:
            cur = self.db.execute(
                "UPDATE watchers SET question = ?, reply = ? WHERE id = ?",
                (question, reply, watcher_id)
            )
            updated = cur.rowcount > 0
        if updated:
            self._watcher_cache = self._load_watcher_cache()
        return updated

    def remove_watcher(self, watcher_id: int) -> bool:
        with self.db:
            cur = self.db.execute("DELETE FROM watchers WHERE id = ?", (watcher_id,))
            removed = cur.rowcount > 0
        if removed:
            self._watcher_cache = self._load_watcher_cache()
        return removed
    
    def list_watchers(self, page=1, page_size=10):
        """
        Returns a paginated list of watchers for this server.
        """
        offset = (page - 1) * page_size
        query = """
            SELECT id, question, reply
            FROM watchers
            WHERE server_id = ?
            ORDER BY id ASC
            LIMIT ? OFFSET ?
        """
        with self.db:
            cur = self.db.execute(query, (self.server_id, page_size, offset))
            rows = cur.fetchall()

        return [
            {"id": row[0], "question": row[1], "reply": row[2]}
            for row in rows
        ]

# Singleton instances per server
_servers = {}

def get_server_database(server_id):
    if not server_id:
        raise commands.NoPrivateMessage("This command cannot be used in private messages.")
    if server_id not in _servers:
        _servers[server_id] = ServerDatabase(server_id)
    return _servers[server_id]