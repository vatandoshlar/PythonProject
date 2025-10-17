#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Database Migration Script
This script migrates the bot from JSON file storage to SQLite database
"""

import os
import sys
from database import init_database, migrate_json_to_database, backup_json_data

def main():
    print("🗄️ Starting database migration...")
    print("=" * 50)
    
    try:
        # Step 1: Initialize database
        print("📊 Step 1: Initializing database...")
        init_database()
        print("✅ Database initialized successfully")
        
        # Step 2: Backup existing JSON data
        print("\n💾 Step 2: Creating backup of existing data...")
        backup_file = backup_json_data()
        if backup_file:
            print(f"✅ Backup created: {backup_file}")
        else:
            print("ℹ️ No existing JSON data found")
        
        # Step 3: Migrate data
        print("\n🔄 Step 3: Migrating data to database...")
        migrate_json_to_database()
        print("✅ Data migration completed successfully")
        
        # Step 4: Verify migration
        print("\n🔍 Step 4: Verifying migration...")
        from db_functions import get_database_stats
        stats = get_database_stats()
        print(f"📊 Migration Results:")
        print(f"   Total Users: {stats['total']}")
        print(f"   Complete: {stats['complete']}")
        print(f"   Incomplete: {stats['incomplete']}")
        print(f"   Old Format: {stats['old_format']}")
        
        print("\n🎉 Database migration completed successfully!")
        print("=" * 50)
        print("📝 Next steps:")
        print("1. Test the bots with the new database")
        print("2. Verify all functions work correctly")
        print("3. Keep the backup file safe")
        print("4. The bots will now use SQLite database instead of JSON")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("💾 Your original data is safe in the backup file")
        sys.exit(1)

if __name__ == "__main__":
    main()
