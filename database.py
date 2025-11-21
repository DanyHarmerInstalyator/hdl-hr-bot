# database.py
import sqlite3
import json
from datetime import datetime
from pathlib import Path

class Database:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        Path("data").mkdir(exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            # Таблица пользователей
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    current_stage INTEGER DEFAULT 1
                )
            ''')
            
            # Таблица прогресса
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_progress (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    stage INTEGER,
                    completed_tasks TEXT,
                    pending_tasks TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица завершенных этапов
            conn.execute('''
                CREATE TABLE IF NOT EXISTS completed_stages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    stage INTEGER,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица админов
            conn.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
    
    def get_user_stage(self, user_id: int) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT current_stage FROM users WHERE user_id = ?", 
                (user_id,)
            )
            result = cursor.fetchone()
            return result[0] if result else 1
    
    def set_user_stage(self, user_id: int, stage: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE users SET current_stage = ? WHERE user_id = ?",
                (stage, user_id)
            )
    
    def mark_stage_completed(self, user_id: int, stage: int):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO completed_stages (user_id, stage, completed_at)
                VALUES (?, ?, ?)
            ''', (user_id, stage, datetime.now()))
    
    def get_completed_stages(self, user_id: int) -> list:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT stage, completed_at FROM completed_stages WHERE user_id = ? ORDER BY stage",
                (user_id,)
            )
            return cursor.fetchall()
    
    def save_current_progress(self, user_id: int, stage: int, completed_tasks: list, pending_tasks: list):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO user_progress (user_id, stage, completed_tasks, pending_tasks)
                VALUES (?, ?, ?, ?)
            ''', (
                user_id, 
                stage, 
                json.dumps(completed_tasks, ensure_ascii=False),
                json.dumps(pending_tasks, ensure_ascii=False)
            ))
    
    def get_current_progress(self, user_id: int, stage: int) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT completed_tasks, pending_tasks FROM user_progress WHERE user_id = ? AND stage = ?",
                (user_id, stage)
            )
            result = cursor.fetchone()
            if result:
                return {
                    'completed_tasks': json.loads(result[0]) if result[0] else [],
                    'pending_tasks': json.loads(result[1]) if result[1] else []
                }
            return {'completed_tasks': [], 'pending_tasks': []}
    
    def get_all_users(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT u.user_id, u.username, u.first_name, u.last_name, 
                       u.current_stage, u.created_at,
                       COUNT(cs.stage) as completed_stages
                FROM users u
                LEFT JOIN completed_stages cs ON u.user_id = cs.user_id
                WHERE u.current_stage IS NOT NULL
                GROUP BY u.user_id
                ORDER BY u.created_at DESC
            ''')
            return cursor.fetchall()
    
    def add_admin(self, user_id: int, username: str = None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO admins (user_id, username)
                VALUES (?, ?)
            ''', (user_id, username))
    
    def is_admin(self, user_id: int) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM admins WHERE user_id = ?",
                (user_id,)
            )
            return cursor.fetchone() is not None

# Создаем глобальный экземпляр базы данных
db = Database()