import pymysql
from pymysql.cursors import DictCursor
from config import Config
from dbutils.pooled_db import PooledDB

# We will initialize the pool when the app starts.
pool = None

def init_db_pool():
    global pool
    pool = PooledDB(
        creator=pymysql,
        maxconnections=20,
        mincached=2,
        maxcached=10,
        blocking=True,
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        port=Config.DB_PORT,
        cursorclass=DictCursor,
        autocommit=True,
        ssl={'ca': Config.DB_SSL_CA} if Config.DB_SSL_CA else None
    )
    return pool

def get_db_connection():
    global pool
    if pool is None:
        init_db_pool()
    return pool.connection()
