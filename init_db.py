import os
import mysql.connector
from urllib.parse import urlparse

def init_database():
    """Initialize database with SQL files on startup"""
    mysql_url = os.getenv('MYSQL_URL')
    if not mysql_url:
        print("MYSQL_URL not set, skipping database initialization")
        return
    
    parsed = urlparse(mysql_url)
    
    try:
        conn = mysql.connector.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/')
        )
        cursor = conn.cursor()
        
        # Read and execute main_tables.sql
        with open('main_tables.sql', 'r') as f:
            sql = f.read()
            for statement in sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)
        
        # Read and execute stupify_data (2).sql
        with open('stupify_data (2).sql', 'r') as f:
            sql = f.read()
            for statement in sql.split(';'):
                if statement.strip():
                    cursor.execute(statement)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")

if __name__ == "__main__":
    init_database()
