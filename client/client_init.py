import json
import socket
import psutil
import requests
import subprocess
from pathlib import Path

#from custom_logger import setup_custom_logger

with open('client_conf.json', 'r') as config_file:
    client_config = json.load(config_file)
    

SERVER_IP = client_config["server_ip"]
SERVER_PORT = client_config["port"]
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}"
SERVER_CONFIGURATION_ENDPOINT = "/get_server_configuration"

#init_logger = setup_custom_logger("client_init")

def get_client_local_path():
    try:
        get_client_local_path = subprocess.check_output(["pwd"], shell=True).decode("utf-8")
        if Path(get_client_local_path):
            return get_client_local_path.strip()
    except subprocess.CalledProcessError as e:
        client_path_search_error = "Error retrieving client path: " + str(e)
        return client_path_search_error
    

def get_server_configuration():
    server_configuration_url = SERVER_URL + SERVER_CONFIGURATION_ENDPOINT
    try:
        response = requests.get(server_configuration_url)
        if response.status_code == 200:
            #init_logger.info(f"StatusCode:{response.status_code} | get server interface")
            return response.json()
        else:
            #init_logger.info(f"StatusCode:{response.status_code} | get server interface error")
            return False
    except requests.exceptions.RequestException as e:
        #init_logger.info(f"StatusCode:{response.status_code} | get server interface error: {e}")
        print(e)

def get_internal_ip(interface_name):
    try:
        addresses = psutil.net_if_addrs()
        if interface_name in addresses:
            for address in addresses[interface_name]:
                if address.family == socket.AF_INET:  # IPv4 address
                    return address.address
        return None
    except Exception as e:
        print(f"Error: {e} bleh")
        return None

def start_up_conf_check(local_conf_file_path):
    # open client configuration file and write client's internal 
    # ip, on the same interface as the server, to the conf file 
    with open(local_conf_file_path, 'r') as json_file:
        data = json.load(json_file)
        server_data = get_server_configuration()
        data["net_interface"] = server_data["interface"]
        data["hash_algorithm"] = server_data["hash_algorithm"]
        if not data["net_interface"]:
            #init_logger.info(f"Server Interface not found")
            return
        if data["host_ip"] == "":
            internal_ip = get_internal_ip(data["net_interface"])
            if internal_ip:
                data["host_ip"] = internal_ip
                data["client_init"] = "true"
                data["client_filepath"] = get_client_local_path()

    with open(local_conf_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
        #init_logger.info(f"Client: {internal_ip} config updated with server interface")
