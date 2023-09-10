import sqlite3
import json


with open('server_conf.json', 'r') as config_file:
    server_config = json.load(config_file)
    

DB_NAME = server_config["db_name"]


def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            client_name TEXT,
            log_type TEXT,
            log_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (client_name, log_type, log_data)
        )
    ''')
    #conn.commit()
    # processes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processes (
            id INTEGER PRIMARY KEY,
            client_ip TEXT,
            PID TEXT,
            process_name TEXT,
            process_status TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    # Memory Usage
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_usage (
            id INTEGER PRIMARY KEY,
            client_name TEXT,
            total TEXT,
            available TEXT,
            used TEXT,
            free TEXT,
            usage_percent TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    #conn.commit()
    # client_reports
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS client (
            id INTEGER PRIMARY KEY,
            client_ip TEXT,
            status TEXT,
            log_data TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()