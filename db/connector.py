import mysql.connector
from mysql.connector import pooling
import sqlite3
import importlib.util
import typer
from pathlib import Path

class DBConnector:
    """Base class for database connectors"""
    def __init__(self, profile):
        self.profile = profile
        self.connection = None
        self._transaction = False
    
    def __enter__(self):
        """Context manager entry"""
        if not self.connection:
            self.connect()
        self._transaction = True
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.connection:
            if exc_type is None and self._transaction:
                self.connection.commit()
            else:
                self.connection.rollback()
            self._transaction = False
    
    def connect(self, password=None):
        """Connect to the database"""
        raise NotImplementedError("Subclasses must implement connect()")
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query(self, query):
        """Execute a SQL query and return results"""
        raise NotImplementedError("Subclasses must implement execute_query()")
    
    def get_schema(self, force_refresh=False):
        """Get the database schema"""
        raise NotImplementedError("Subclasses must implement get_schema()")
    
    @staticmethod
    def create_connector(profile):
        """Factory method to create the appropriate connector based on profile type"""
        db_type = profile.get('type', 'MySQL')
        if db_type == "MySQL":
            return MySQLConnector(profile)
        elif db_type == "PostgreSQL":
            return PostgreSQLConnector(profile)
        elif db_type == "SQLite":
            return SQLiteConnector(profile)
        else:
            raise ValueError(f"Unsupported database type: {db_type}")

class MySQLConnector(DBConnector):
    """MySQL database connector"""
    def __init__(self, profile):
        super().__init__(profile)
        self.pool = None

    def connect(self, password=None):
        """Connect to MySQL database"""
        if password is None:
            password = self.profile.get('password', '')
        
        if not self.pool:
            self.pool = pooling.MySQLConnectionPool(
                pool_name = "nlsql_pool",
                pool_size = 5,
                host = self.profile.get('host', 'localhost'),
                port = int(self.profile.get('port', 3306)),
                user = self.profile.get('username', 'root'),
                password = password,
                database = self.profile.get('database', '')
            )
        self.connection = self.pool.get_connection()
        return self.connection
    
    def execute_query(self, query, auto_commit=True):
        """Execute a SQL query and return results"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute(query)
        
        # Get column names
        columns = [column[0] for column in cursor.description] if cursor.description else []
        
        # Fetch results
        results = cursor.fetchall()
        
        if auto_commit and not self._transaction:
            self.connection.commit()
        
        cursor.close()
        return results, columns
    
    def get_schema(self, force_refresh=False):
        """Get the database schema"""
        from db.schema import get_schema
        return get_schema(self, force_refresh)

class PostgreSQLConnector(DBConnector):
    """PostgreSQL database connector"""
    def __init__(self, profile):
        super().__init__(profile)
        # Check if psycopg2 is installed
        if importlib.util.find_spec("psycopg2") is None:
            typer.echo("PostgreSQL support requires psycopg2. Install with: pip install psycopg2-binary")
            raise typer.Exit(1)
    
    def connect(self, password=None):
        """Connect to PostgreSQL database"""
        import psycopg2
        
        if password is None:
            password = self.profile.get('password', '')
        
        if not self.connection:
            self.connection = psycopg2.connect(
                host=self.profile.get('host', 'localhost'),
                port=int(self.profile.get('port', 5432)),
                user=self.profile.get('username', 'postgres'),
                password=password,
                dbname=self.profile.get('database', '')
            )
        
        return self.connection
    
    def execute_query(self, query, auto_commit=True):
        """Execute a SQL query and return results with transaction management"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Fetch results
            results = cursor.fetchall()
            
            if auto_commit:
                self.connection.commit()
            
            return results, columns
        except Exception as e:
            if auto_commit:
                self.connection.rollback()
            raise e
        finally:
            cursor.close()
    
    def get_schema(self, force_refresh=False):
        """Get the database schema (placeholder)"""
        # This would need a PostgreSQL-specific implementation
        return {"tables": ["users", "orders", "products"]}

class SQLiteConnector(DBConnector):
    """SQLite database connector"""
    def __init__(self, profile):
        super().__init__(profile)
    
    def connect(self, password=None):
        """Connect to SQLite database"""
        db_path = self.profile.get('database', ':memory:')
        
        if not self.connection:
            self.connection = sqlite3.connect(db_path)
        
        return self.connection
    
    def execute_query(self, query):
        """Execute a SQL query and return results"""
        if not self.connection:
            self.connect()
        
        cursor = self.connection.cursor()
        cursor.execute(query)
        
        # Get column names
        columns = [description[0] for description in cursor.description] if cursor.description else []
        
        # Fetch results
        results = cursor.fetchall()
        
        cursor.close()
        return results, columns
    
    def get_schema(self, force_refresh=False):
        """Get the database schema (placeholder)"""
        # This would need a SQLite-specific implementation
        return {"tables": ["users", "orders", "products"]}