"""
Database Migration Script for Certificate Generation System
Updates the database schema to support the full-featured version
"""

import sqlite3
import os

def migrate_database(database_path="certificates.db"):
    """Migrate database to support full features"""
    
    print("🔄 Migrating database schema...")
    
    # Check if database exists
    if not os.path.exists(database_path):
        print("❌ Database not found. Please run the basic system first.")
        return False
    
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    try:
        # Check current schema
        cursor.execute("PRAGMA table_info(certificates)")
        columns = [column[1] for column in cursor.fetchall()]
        
        print(f"📋 Current columns: {columns}")
        
        # Add missing columns if they don't exist
        if 'qr_code_data' not in columns:
            print("➕ Adding qr_code_data column...")
            cursor.execute("ALTER TABLE certificates ADD COLUMN qr_code_data TEXT")
        
        if 'file_path' not in columns:
            print("➕ Adding file_path column...")
            cursor.execute("ALTER TABLE certificates ADD COLUMN file_path TEXT")
        
        # Update existing records with default values
        cursor.execute("UPDATE certificates SET qr_code_data = '' WHERE qr_code_data IS NULL")
        cursor.execute("UPDATE certificates SET file_path = '' WHERE file_path IS NULL")
        
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Show updated schema
        cursor.execute("PRAGMA table_info(certificates)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"📋 Updated columns: {columns}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def backup_database(database_path="certificates.db"):
    """Create a backup of the database"""
    if os.path.exists(database_path):
        backup_path = f"{database_path}.backup"
        import shutil
        shutil.copy2(database_path, backup_path)
        print(f"💾 Database backed up to: {backup_path}")
        return backup_path
    return None

if __name__ == "__main__":
    print("🔧 Certificate Database Migration Tool")
    print("=" * 50)
    
    # Create backup
    backup_path = backup_database()
    
    # Run migration
    success = migrate_database()
    
    if success:
        print("\n🎉 Migration completed! You can now use the full PDF+QR system.")
        print("📝 Run: python certificate_generator.py")
    else:
        print("\n⚠️ Migration failed. Your original database is safe.")
        if backup_path:
            print(f"💾 Backup available at: {backup_path}")