import platform
import subprocess
import json
import re

import psutil
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from client_init import start_up_conf_check
from utils.custom_logger import setup_custom_logger
from utils.system_monitor import get_system_stats
from utils.client_integritiy import hash_files_in_directory


client_logger = setup_custom_logger("main_client")


client_config_file = "client_conf.json"
# load configuration file and check if it's complete
with open(client_config_file, 'r') as config_file:
    client_config = json.load(config_file)
    
    if client_config["client_init"] == "false":
        client_logger.info("client configuration")
        print('configuring client')
        config_file.close()
        start_up_conf_check(client_config_file)


SERVER_IP = client_config["server_ip"]
SERVER_PORT = client_config["port"]
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}"
CLIENT_NAME = client_config["client_name"]
CLIENT_PATH = client_config["client_filepath"]
HASH_ALGO = client_config["hash_algorithm"]
HOST_IP = client_config['host_ip']

# watchdog handler
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # triggers client workflow
        run_client()
        client_logger.info(f'File modified: {event.src_path}')
        

def collect_and_send_log(log_type, log_data):
    data = {
        'client_name': HOST_IP,
        'log_type': log_type,
        'log_data': log_data
    }
    submit_log_url = SERVER_URL + "/submit_log"
    try:
        response = requests.post(submit_log_url, json=data)
        if response.status_code != 200:
            client_logger.info(f'Client failed to submit {log_type} log | statuscode: {response.status_code}')
    except requests.exceptions.RequestException as e:
        client_logger.info('Error:', e)

def collect_system_logs():
    # Collect system-specific logs
    system = platform.system()
    if system == 'Linux':
        boot_time = subprocess.check_output(['uptime', '-s']).decode().strip()
        collect_and_send_log('system_boot_time', boot_time)
    else:
        print(f"{system} not supported")
        exit()

def search_log(log_path, search_pattern):
    # Read log file
    with open(log_path, 'r') as log_file:
        search_matches = []
        for line in log_file:
            # Search for the failed login pattern in each line
            match = re.search(search_pattern, line)
            if match:
                search_matches.append(line)
    
    if len(search_matches) > 0:
        return search_matches
    else: 
        return False

def filter_logs():
    keyword_search = ['sudo', r"authentication failure", 'ssh']
    try:
        for tag in keyword_search:
            results = search_log("/var/log/auth.log", tag)
            if results:
                for result in results:
                    collect_and_send_log(tag, result)
    except subprocess.CalledProcessError as e:
        sudo_log = "Error retrieving sudo log: " + str(e)
        collect_and_send_log('sudo commands', sudo_log)


# System Logs
def get_memory_usage():
    virtual_memory = psutil.virtual_memory()
    return {
        "total": virtual_memory.total,
        "available": virtual_memory.available,
        "used": virtual_memory.used,
        "free": virtual_memory.free,
        "percent": virtual_memory.percent
    }


def collect_and_send_memory_usage():
    memory_usage = get_memory_usage()
    data = {
        'client_name': HOST_IP,
        "total": round(int(memory_usage["total"]), 2),
        "available": round(int(memory_usage["available"]), 2),
        "used": round(int(memory_usage["used"]), 2),
        "free": round(int(memory_usage["free"]), 2),
        "percent": memory_usage["percent"]
    }
    submit_memory_usage_url = SERVER_URL + "/submit_memory_usage"
    try:
        response = requests.post(submit_memory_usage_url, json=data)
        if response.status_code != 200:
            client_logger.info(f'Client failed to submit Memory Usage log', response.status_code)
    except requests.exceptions.RequestException as e:
        client_logger.info('Error:', e)


def profile_client(status, log_data='None'):
    # update client action to server
    client_report = {
        "client_ip": HOST_IP,
        "status": status,
        'log_data': log_data
        }
    submit_log_url = SERVER_URL + "/client_reports"
    try:
        response = requests.post(submit_log_url, json=client_report)
        if response.status_code != 200:
            client_logger.info(f'Client submit error | statuscode: {response.status_code}')
    except requests.exceptions.RequestException as e:
        client_logger.info('Error:', e)


def submit_client_integriry():
    directory_path = CLIENT_PATH
    hash_algorithm = HASH_ALGO

    file_hashes = hash_files_in_directory(directory_path, hash_algorithm)
    client_integrity_url = SERVER_URL + "/check_client_integrity"
    try:
        response = requests.post(client_integrity_url, json=file_hashes)
        if response.status_code == 200:
            result = response.json()
            if result['verified']:
                return True
            return False
        else:
            client_logger.info(f'client integrity submit error | statuscode: {response.status_code}')
            return False
    except requests.exceptions.RequestException as e:
        client_logger.info('Error:', e)


def submit_client_processes():
    # Get a list of all running processes
    running_processes = []
    for process in psutil.process_iter(attrs=['pid', 'name', 'status']):
        
        process_info = process.info
        if process_info["status"] == "running":
            running_processes.append(process_info)
    
    proc_url = SERVER_URL + "/client_processes"
    procs_logged = 0
    
    for process in running_processes:
        proc_data = {
            "client_ip": HOST_IP,
            "PID": process["pid"],
            "process_name": process["name"],
            "process_status": process["status"],
        }
        try:
            response = requests.post(proc_url, json=proc_data)
            if response.status_code == 200:
                procs_logged += 1
            else:
                client_logger.info(f'client integrity submit error | statuscode: {response.status_code}')
        
        except requests.exceptions.RequestException as e:
            client_logger.info('Error:', e)
    return {"processes logged": procs_logged}

    

# start watchdog and listen for changes on log files
def watchdog_run(monitor_filepath):
    profile_client('listening', 'file change')
    client_logger.info('client listening: file change')
    event_handler = MyHandler()
    observer = Observer()
    observer.schedule(event_handler, path=monitor_filepath, recursive=True)
    observer.start()

    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    profile_client(f'{monitor_filepath} observer is idle')
    client_logger.info(f'{monitor_filepath} observer is idle')


def run_client():
    # run the client log collection cycle
    print("\nrunning client workflow\n")
    client_logger.info("Client run")
    
    profile_client('running', 'workflow')
    submit_client_processes()
    collect_and_send_memory_usage()
    collect_system_logs()
    filter_logs()
    print("workflow complete\n")
    

if __name__ == '__main__':
    client_logger.info("Starting client")
    integrity_response = submit_client_integriry()
    if integrity_response:
        get_system_stats()
        run_client()
        # start listener
        watchdog_run("/var/log/auth.log")
        #watchdog_run(".")
    else:
        print('checksum verification failed')

        
