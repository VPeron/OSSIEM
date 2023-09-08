import sqlite3
import json
import os

from flask import Flask, request, jsonify, render_template

from utils.setup_db_tables import create_tables


app = Flask(__name__)

with open("server_conf.json", "r") as config_file:
    server_config = json.load(config_file)
    
DB_NAME = server_config["db_name"]
HOST = server_config["host"]
PORT = server_config["port"]
SERVER_INTERFACE = server_config["net_interface"]
HASH_ALGO = server_config["hash_algorithm"]
CLIENT_CHECKSUMS = server_config["client_checksums"]


# CONFIGURATION
@app.route("/get_server_configuration", methods=["GET"])
def get_server_configuration():
    """a server endpoint for clients to fetch config info"""
    if SERVER_INTERFACE and HOST and HASH_ALGO:
        return jsonify({
            "interface": SERVER_INTERFACE, 
            "server_ip": HOST, 
            "hash_algorithm": HASH_ALGO
             }), 200
    else:
        return jsonify({"error": "server not fully configured"}), 400

# LOGS
@app.route("/submit_log", methods=["POST"])
def submit_log():
    """general log submission endpoint"""
    data = request.get_json()
    # columns
    client_name = data.get("client_name")
    log_type = data.get("log_type")
    log_data = data.get("log_data")

    if log_type and log_data:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO logs (client_name, log_type, log_data) VALUES (?, ?, ?)", 
                (client_name, log_type, log_data)
                )
        except sqlite3.IntegrityError:
            print("Duplicate entry, skipping insertion.")
        conn.commit()
        conn.close()
        return jsonify({"message": "Log submitted successfully"}), 200
    else:
        return jsonify({"error": "Log type and data are required"}), 400


@app.route("/view_logs", methods=["GET"])
def view_logs():
    """serves database logs table to the endpoint"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY id DESC")
    logs = cursor.fetchall()
    conn.close()
    return render_template("logs.html", logs=logs)


# MEMORY USAGE
@app.route("/submit_memory_usage", methods=["POST"])
def submit_memory_usage():
    """submit converted memory usage data to the database"""
    data = request.get_json()
    client_name = data.get("client_name")
    mem_total = data.get("total")  / (1024 ** 3)
    mem_available = data.get("available")  / (1024 ** 3)
    mem_used = data.get("used")  / (1024 ** 3)
    mem_free = data.get("free")  / (1024 ** 3)
    mem_use_percent = data.get("usage_percent")

    if mem_total and mem_available:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO memory_usage (client_name, total, available, used, free, usage_percent) VALUES (?, ?, ?, ?, ?, ?)",
                (client_name, mem_total, mem_available, mem_used, mem_free, mem_use_percent)
                )
        except sqlite3.IntegrityError:
            print("Duplicate entry, skipping insertion.")
        conn.commit()
        conn.close()
        return jsonify({"message": "log submitted successfully"}), 200
    else:
        return jsonify({"error": "log data required"}), 400


@app.route("/view_memory_usage", methods=["GET"])
def view_memory_usage():
    """serves database memory_usage table to the endpoint"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM memory_usage ORDER BY id DESC")
    mem_use = cursor.fetchall()
    conn.close()
    return render_template("memory_usage.html", mem_use=mem_use)

# client reports
@app.route("/client_reports", methods=["POST"])
def client_reports():
    """client reports"""
    data = request.get_json()
    # columns
    client_ip = data.get("client_ip")
    status = data.get("status")
    log_data = data.get("log_data")

    if client_ip and log_data:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO client (client_ip, status, log_data) VALUES (?, ?, ?)", (client_ip, status, log_data))
        conn.commit()
        conn.close()
        return jsonify({"message": "report log submitted successfully"}), 200
    else:
        return jsonify({"error": "client report error"}), 400
    
# client checksum
@app.route("/check_client_integrity", methods=["POST"])
def check_client_integrity():
    """check_client_integrity"""
    data = request.get_json()
    # columns
    client_logger_file = data.get("custom_logger.py")
    client_main = data.get("client.py")
    client_initializer = data.get("client_init.py")
    client_integrity_checker = data.get("utils/client_integritiy.py")
    client_sys_monitor = data.get("utils/system_monitor.py")
        
    checksum_list = {
        "client.py": False,
        "customer_logger.py": False,
        "client_init.py": False,
        "utils/system_monitor.py": False,
        "utils/client_integritiy.py": False,       
    }
    
    #logger
    if client_logger_file == CLIENT_CHECKSUMS["logger"]:
        checksum_list["customer_logger.py"] = True
    #main
    if client_main == CLIENT_CHECKSUMS["client"]:
        checksum_list["client.py"] = True
    #main
    if client_initializer == CLIENT_CHECKSUMS["client_init"]:
        checksum_list["client_init.py"] = True
    #sysmonitor
    if client_sys_monitor == CLIENT_CHECKSUMS["system_monitor"]:
        checksum_list["utils/system_monitor.py"] = True
    #integrity check
    if client_integrity_checker == CLIENT_CHECKSUMS["client_integritiy"]:
        checksum_list["utils/client_integritiy.py"] = True
    
    print(checksum_list)
    if all(checksum_list.values()):
        return {"verified": True}
    return {"verified": False}


if __name__ == "__main__":
    if not os.path.exists(DB_NAME):
        create_tables()
    app.run(host=HOST, port=PORT)