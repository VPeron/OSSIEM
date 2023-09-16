import scapy.all as scapy
import sqlite3
import os



class CustomSniffer:
    def __init__(self, interface, filter="", max_packets=None) -> None:
        self.interface = interface
        self.filter = filter
        self.max_packets = max_packets
        self.db_connection = sqlite3.connect('siem_database.db')
        self.db_cursor = self.db_connection.cursor()
        # check if db file exists first
        self.db_cursor.execute('''
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                src_ip TEXT,
                dst_ip TEXT,
                protocol TEXT,
                timestamp DATETIME
            )
        ''')
    
    def _process_network_traffic(self, packet):
        # Extract relevant information from the packet
        if packet.haslayer(scapy.IP):
            src_ip = packet[scapy.IP].src
            dst_ip = packet[scapy.IP].dst
            protocol = packet[scapy.IP].proto
            timestamp = packet.time

            # Insert packet summary into the database
            self.db_cursor.execute("INSERT INTO packets (src_ip, dst_ip, protocol, timestamp) VALUES (?, ?, ?, ?)",
                                    (src_ip, dst_ip, protocol, timestamp))
            self.db_connection.commit()

        # Save the full packet to a PCAP file
        #print(packet.summary())
        scapy.wrpcap('logs/captured_traffic.pcap', packet, append=True)

        # if self.max_packets and len(self.db_cursor.execute("SELECT id FROM packets").fetchall()) >= self.max_packets:
            # Stop sniffing after capturing a specified number of packets
            # raise KeyboardInterrupt

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
    session = CustomSniffer("wlp0s20f3", filters["all"], max_packets)
    session.start_sniffer()
    session.close()

if __name__ == "__main__":
    traffic_sniffer()
