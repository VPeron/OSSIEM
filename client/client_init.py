import json
import socket
import psutil
import requests

from custom_logger import setup_custom_logger

with open('client_conf.json', 'r') as config_file:
    client_config = json.load(config_file)
    

SERVER_IP = client_config["server_ip"]
SERVER_PORT = client_config["port"]
SERVER_URL = f"http://{SERVER_IP}:{SERVER_PORT}"
SERVER_INTERFACE_ENDPOINT = "/get_server_interface"

#init_logger = setup_custom_logger("client_init")

def get_server_interface():
    server_interface_url = SERVER_URL + SERVER_INTERFACE_ENDPOINT
    try:
        response = requests.get(server_interface_url)
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
        print(f"Error: {e}")
        return None

def start_up_conf_check(file_path):
    # open client configuration file and write client's internal 
    # ip, on the same interface as the server, to the conf file 
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        data["net_interface"] = get_server_interface()["interface"]
        if not data["net_interface"]:
            #init_logger.info(f"Server Interface not found")
            return
        if data["host_ip"] == "":
            internal_ip = get_internal_ip(data["net_interface"])
            if internal_ip:
                data["host_ip"] = internal_ip
                data["client_init"] = "true"

    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)
        #init_logger.info(f"Client: {internal_ip} config updated with server interface")


