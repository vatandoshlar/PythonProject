#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from database import get_db_connection
from datetime import datetime
import json

def save_user_data(user_id, user_data, status='incomplete'):
    """Save user data to database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Insert or update user
            cursor.execute("""
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, language_code,
                 registration_date, registration_status, completion_date, last_updated,
                 added_manually, added_by_admin)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                user_data.get('username', 'Username yo\'q'),
                user_data.get('first_name', ''),
                user_data.get('last_name', ''),
                user_data.get('language_code', ''),
                user_data.get('registration_date', datetime.now().strftime('%d.%m.%Y %H:%M:%S')),
                status,
                user_data.get('completion_date', datetime.now().strftime('%d.%m.%Y %H:%M:%S') if status == 'complete' else None),
                datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                user_data.get('added_manually', False),
                user_data.get('added_by_admin')
            ))
            
            # Insert or update user details
            cursor.execute("""
                INSERT OR REPLACE INTO user_details 
                (user_id, fullname, country, city, birthdate, phone, workplace,
                 specialty, education, nomination, current_step)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                user_data.get('fullname', ''),
                user_data.get('country', ''),
                user_data.get('city', ''),
                user_data.get('birthdate', ''),
                user_data.get('phone', ''),
                user_data.get('workplace', ''),
                user_data.get('specialty', ''),
                user_data.get('education', ''),
                user_data.get('nomination', ''),
                user_data.get('current_step', '')
            ))
            
            # Insert or update file data if exists
            if user_data.get('file'):
                file_data = user_data.get('file', {})
                cursor.execute("""
                    INSERT OR REPLACE INTO user_files 
                    (user_id, file_id, file_type, file_name)
                    VALUES (?, ?, ?, ?)
                """, (
                    user_id,
                    file_data.get('file_id', ''),
                    file_data.get('file_type', ''),
                    file_data.get('file_name', '')
                ))
            
            conn.commit()
            print(f"✅ User {user_id} saved to database with status: {status}")
            
    except Exception as e:
        print(f"❌ Error saving user data: {e}")
        raise e

def get_user_by_id(user_id):
    """Get user data by user_id"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.*, ud.fullname, ud.country, ud.city, ud.birthdate, ud.phone,
                       ud.workplace, ud.specialty, ud.education, ud.nomination, ud.current_step,
                       uf.file_id, uf.file_type, uf.file_name
                FROM users u
                LEFT JOIN user_details ud ON u.user_id = ud.user_id
                LEFT JOIN user_files uf ON u.user_id = uf.user_id
                WHERE u.user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
    except Exception as e:
        print(f"❌ Error getting user data: {e}")
        return None

def get_all_users():
    """Get all users from database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.*, ud.fullname, ud.country, ud.city, ud.birthdate, ud.phone,
                       ud.workplace, ud.specialty, ud.education, ud.nomination, ud.current_step,
                       uf.file_id, uf.file_type, uf.file_name
                FROM users u
                LEFT JOIN user_details ud ON u.user_id = ud.user_id
                LEFT JOIN user_files uf ON u.user_id = uf.user_id
                ORDER BY u.registration_date DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
    except Exception as e:
        print(f"❌ Error getting all users: {e}")
        return []

def get_incomplete_users():
    """Get users with incomplete registration"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.*, ud.fullname, ud.country, ud.city, ud.birthdate, ud.phone,
                       ud.workplace, ud.specialty, ud.education, ud.nomination, ud.current_step
                FROM users u
                LEFT JOIN user_details ud ON u.user_id = ud.user_id
                WHERE u.registration_status = 'incomplete'
                ORDER BY u.last_updated DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
    except Exception as e:
        print(f"❌ Error getting incomplete users: {e}")
        return []

def update_user_status(user_id, status, completion_date=None):
    """Update user registration status"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET registration_status = ?, completion_date = ?, last_updated = ?
                WHERE user_id = ?
            """, (status, completion_date, datetime.now().strftime('%d.%m.%Y %H:%M:%S'), user_id))
            
            conn.commit()
            print(f"✅ User {user_id} status updated to: {status}")
            
    except Exception as e:
        print(f"❌ Error updating user status: {e}")
        raise e

def save_partial_user_data(user_id, context_data, step_name):
    """Save partial user data during registration process"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user exists and get current status
            cursor.execute("SELECT registration_status FROM users WHERE user_id = ?", (user_id,))
            existing_user = cursor.fetchone()
            
            # Determine status - preserve 'complete' if already completed
            if existing_user and existing_user['registration_status'] == 'complete':
                status = 'complete'
            else:
                status = 'incomplete'
            
            # Update user basic info
            cursor.execute("""
                INSERT OR REPLACE INTO users 
                (user_id, username, first_name, last_name, language_code,
                 registration_date, registration_status, completion_date, last_updated,
                 added_manually, added_by_admin)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                context_data.get('username', 'Username yo\'q'),
                context_data.get('first_name', ''),
                context_data.get('last_name', ''),
                context_data.get('language_code', ''),
                context_data.get('registration_date', datetime.now().strftime('%d.%m.%Y %H:%M:%S')),
                status,
                context_data.get('completion_date') if status == 'complete' else None,
                datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                context_data.get('added_manually', False),
                context_data.get('added_by_admin')
            ))
            
            # Update user details
            cursor.execute("""
                INSERT OR REPLACE INTO user_details 
                (user_id, fullname, country, city, birthdate, phone, workplace,
                 specialty, education, nomination, current_step)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                context_data.get('fullname', ''),
                context_data.get('country', ''),
                context_data.get('city', ''),
                context_data.get('birthdate', ''),
                context_data.get('phone', ''),
                context_data.get('workplace', ''),
                context_data.get('specialty', ''),
                context_data.get('education', ''),
                context_data.get('nomination', ''),
                step_name
            ))
            
            conn.commit()
            print(f"✅ Partial data saved for user {user_id} at step: {step_name} (status: {status})")
            
    except Exception as e:
        print(f"❌ Error saving partial data: {e}")
        raise e

def get_database_stats():
    """Get database statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Total users
            cursor.execute("SELECT COUNT(*) as total FROM users")
            total = cursor.fetchone()['total']
            
            # Complete users
            cursor.execute("SELECT COUNT(*) as complete FROM users WHERE registration_status = 'complete'")
            complete = cursor.fetchone()['complete']
            
            # Incomplete users
            cursor.execute("SELECT COUNT(*) as incomplete FROM users WHERE registration_status = 'incomplete'")
            incomplete = cursor.fetchone()['incomplete']
            
            # Old format users (no registration_status)
            cursor.execute("SELECT COUNT(*) as old_format FROM users WHERE registration_status IS NULL")
            old_format = cursor.fetchone()['old_format']
            
            return {
                'total': total,
                'complete': complete,
                'incomplete': incomplete,
                'old_format': old_format
            }
            
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")
        return {'total': 0, 'complete': 0, 'incomplete': 0, 'old_format': 0}

def delete_user(user_id):
    """Delete user from database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            conn.commit()
            print(f"✅ User {user_id} deleted from database")
            
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        raise e
