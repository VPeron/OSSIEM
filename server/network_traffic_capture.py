import scapy.all as scapy
import sqlite3
import json


with open('server_conf.json', 'r') as conf_file:
    conf_data = json.load(conf_file)

DBNAME = conf_data["db_name"]
INTERFACE = conf_data["net_interface"]
TRAFFIC_LOGS = 'logs/captured_traffic.pcap'

class CustomSniffer:
    def __init__(self, interface, filter="", max_packets=None) -> None:
        self.interface = interface
        self.filter = filter
        self.max_packets = max_packets
        self.db_connection = sqlite3.connect(DBNAME)
        self.db_cursor = self.db_connection.cursor()
    
    def _process_network_traffic(self, packet):
        # process packet info
        if packet.haslayer(scapy.IP):
            src_ip = packet[scapy.IP].src
            dst_ip = packet[scapy.IP].dst
            protocol = packet[scapy.IP].proto
            timestamp = packet.time

            # insert packet summary into the database
            self.db_cursor.execute("INSERT INTO packets (src_ip, dst_ip, protocol, timestamp) VALUES (?, ?, ?, ?)",
                                    (src_ip, dst_ip, protocol, timestamp))
            self.db_connection.commit()

        # write to pcap
        scapy.wrpcap(TRAFFIC_LOGS, packet, append=True)

    def start_sniffer(self):
        # start traffic sniffing
        scapy.sniff(iface=self.interface, prn=self._process_network_traffic, filter=self.filter)
    
    def close(self):
        self.db_connection.close()

def traffic_sniffer():
    filters = {
        "all": "",
        "tcp": "tcp",
        "udp": "udp",
        "icmp": "icmp",
        "dns": "udp port 53",
    }
    max_packets = 1000
    session = CustomSniffer(INTERFACE, filters["all"])
    session.start_sniffer()
    session.close()

if __name__ == "__main__":
    traffic_sniffer()
