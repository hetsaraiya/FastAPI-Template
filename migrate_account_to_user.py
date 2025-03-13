#!/usr/bin/env python
"""
Helper script to run the Account to User migration
"""
import os
import subprocess
import sys

def run_migration():
    """
    Run the Alembic migration to convert Account table to User table
    """
    print("Running migration to convert 'account' table to 'user' table...")
    
    try:
        # Run alembic upgrade to latest version
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        print("Migration completed successfully!")
        print("The 'account' table has been migrated to 'user' table.")
        
    except subprocess.CalledProcessError as e:
        print(f"Error running migration: {e}")
        sys.exit(1)
        
    print("\nMigration complete! Make sure to update any remaining code references from 'account' to 'user'.")

if __name__ == "__main__":
    run_migration()