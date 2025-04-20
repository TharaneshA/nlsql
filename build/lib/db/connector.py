import mysql.connector
from mysql.connector import pooling

class MySQLConnector:
    def __init__(self, config):
        self.config = config
        self.pool = None

    def connect(self):
        if not self.pool:
            self.pool = pooling.MySQLConnectionPool(
                pool_name = "nlsql_pool",
                pool_size = 5,
                host = self.config.get('host', 'localhost'),
                user = self.config.get('user', 'root'),
                password = self.config.get('password', ''),
                database = self.config.get('database', '')
            )
        return self.pool.get_connection()

    def close(self):
        # Pool connections are managed automatically
        pass