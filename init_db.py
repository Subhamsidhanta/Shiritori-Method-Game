#!/usr/bin/env python3
"""
Database initialization script for Shiritori Method Game
Run this to create database tables if they don't exist
"""

import os
import sys
from app import app, db, GameScore

def init_database():
    """Initialize the database with all tables"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if we can connect and query
            count = GameScore.query.count()
            print(f"📊 Current scores in database: {count}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating database tables: {e}")
            return False

if __name__ == '__main__':
    print("🚀 Initializing Shiritori Method Game Database...")
    print("=" * 50)
    
    # Show configuration
    db_url = app.config['SQLALCHEMY_DATABASE_URI']
    if 'postgresql' in db_url:
        print("🗄️  Using PostgreSQL Database")
    else:
        print("🗄️  Using SQLite Database (Development)")
    
    print(f"📍 Database URL: {db_url[:50]}...")
    print("=" * 50)
    
    if init_database():
        print("🎉 Database initialization complete!")
        sys.exit(0)
    else:
        print("💥 Database initialization failed!")
        sys.exit(1)