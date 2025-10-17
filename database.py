#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime

# Database file path
DB_FILE = 'bot_database.db'

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Initialize database with required tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                language_code VARCHAR(10),
                registration_date DATETIME,
                registration_status VARCHAR(20) DEFAULT 'incomplete',
                completion_date DATETIME,
                last_updated DATETIME,
                added_manually BOOLEAN DEFAULT FALSE,
                added_by_admin BIGINT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create user_details table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT NOT NULL,
                fullname VARCHAR(255),
                country VARCHAR(255),
                city VARCHAR(255),
                birthdate VARCHAR(255),
                phone VARCHAR(255),
                workplace VARCHAR(255),
                specialty VARCHAR(255),
                education VARCHAR(255),
                nomination VARCHAR(255),
                current_step VARCHAR(50),
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        
        # Create user_files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id BIGINT NOT NULL,
                file_id VARCHAR(255),
                file_type VARCHAR(50),
                file_name VARCHAR(255),
                upload_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_user_id ON users(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_status ON users(registration_status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_details_user_id ON user_details(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_files_user_id ON user_files(user_id)")
        
        conn.commit()
        print("✅ Database initialized successfully")

def backup_json_data():
    """Create backup of existing JSON data"""
    import json
    from datetime import datetime
    
    backup_file = f"registered_users_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    if os.path.exists('registered_users.json'):
        with open('registered_users.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON data backed up to {backup_file}")
        return backup_file
    else:
        print("⚠️ No existing JSON data found")
        return None

def migrate_json_to_database():
    """Migrate existing JSON data to database"""
    import json
    
    if not os.path.exists('registered_users.json'):
        print("⚠️ No JSON data to migrate")
        return
    
    # Backup existing data
    backup_file = backup_json_data()
    
    try:
        with open('registered_users.json', 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for user in json_data:
                # Insert user data
                cursor.execute("""
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, language_code,
                     registration_date, registration_status, completion_date, last_updated,
                     added_manually, added_by_admin)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.get('user_id'),
                    user.get('username', 'Username yo\'q'),
                    user.get('first_name', ''),
                    user.get('last_name', ''),
                    user.get('language_code', ''),
                    user.get('registration_date'),
                    user.get('registration_status', 'incomplete'),
                    user.get('completion_date'),
                    user.get('last_updated', user.get('registration_date')),
                    user.get('added_manually', False),
                    user.get('added_by_admin')
                ))
                
                # Insert user details
                cursor.execute("""
                    INSERT OR REPLACE INTO user_details 
                    (user_id, fullname, country, city, birthdate, phone, workplace,
                     specialty, education, nomination, current_step)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.get('user_id'),
                    user.get('fullname', ''),
                    user.get('country', ''),
                    user.get('city', ''),
                    user.get('birthdate', ''),
                    user.get('phone', ''),
                    user.get('workplace', ''),
                    user.get('specialty', ''),
                    user.get('education', ''),
                    user.get('nomination', ''),
                    user.get('current_step', '')
                ))
                
                # Insert file data if exists
                if user.get('file'):
                    file_data = user.get('file', {})
                    cursor.execute("""
                        INSERT OR REPLACE INTO user_files 
                        (user_id, file_id, file_type, file_name)
                        VALUES (?, ?, ?, ?)
                    """, (
                        user.get('user_id'),
                        file_data.get('file_id', ''),
                        file_data.get('file_type', ''),
                        file_data.get('file_name', '')
                    ))
            
            conn.commit()
            print(f"✅ Successfully migrated {len(json_data)} users to database")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if backup_file:
            print(f"💾 Backup available at: {backup_file}")
        raise e

if __name__ == "__main__":
    # Initialize database and migrate data
    init_database()
    migrate_json_to_database()
