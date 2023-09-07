# API based OSSIEM
tested systems: linux

### Goal: 

        an open source basic SIEM system for home users with multiple linux devices

### trajectory

**Stack**: Python >= 3.8, *docker*(eng), streamlit(dashboard), telegrambot (alerts)

- define system confinements

        The idea is to setup a basic but modular initial system with a barebone, if that
        initial functionality and actual utility in terms of security and build from there.

- setup server and database

        The basic communication between server and client is setup via a Flask API. Server 
        logs are stored in a SQLite3 database but the client also produces some .log files
        and stores it in its own directory.

- setup client and configuration files

        the client directory, with the exception of the configuration file should be hashed
        as means for the server to verify the client hasn't been tampered with. The same
        portion of the client directory can be 'compiled'.

- setup server and client via docker with a streamlit dashboard (TODO)
- setup telegram alerts (TODO)


```
.
├── README.md
├── requirements.txt
├── feat_dev
│   ├── get_local_conf.py
│   ├── logs_watchdog.py
│   ├── re_log_search.py
│   ├── setup_tables.py
│   ├── siem_client.py
│   └── sniffer.py
├── client
│   ├── client_conf.json
│   ├── client_init.py
│   ├── client.py
│   ├── custom_logger.py
│   └── utils
│       ├── client_integritiy.py
│       └── system_monitor.py
└── server
    ├── server_conf.json
    ├── server.py
    ├── siem_database.db
    ├── templates
    │   ├── logs.html
    │   └── memory_usage.html
    └── utils
        ├── client_integrity.py
        ├── encryption.py
        └── setup_db_tables.py

```


# Server
Flask API that can post and get logs from & to sqlitedb

- scan clients for open ports and services
        run vulnerability check
- scan the actual applications for vulnerabilities?
- checksum client files to verify integrity

        the question here is how to keep the server maintainable
        in terms of processing power efficiency. A similar question
        hangs for the client but in a more severe manner since it may
        need multiple servers/listeners runnning simultaneously.
        - how does wazuh, snort etc do it without hindering the
        hosts processing power?

# Client

Monitors folders for changes via the python library
watchdog on /var/log/auth.log for example - trigger classifies
new entry into one of the following or none and sends 
the data to the server via an api call. Add more paths like /etc/passwd

research sensitve paths to monitor

    - boot up time
    - shutdown time
    - failed login attempts (TODO)
    - sudo commands
    - ssh logs
    - ftp logs (TODO?)
    start auth.log monitor for changes

May also have a socket listening for file transfers?

    - scan the source
    - scan the file

Network traffic (TODO: scapy)

    - dns resolve records
    - http connections
    - transfer volume analysis once enough data is gathered (1 week?)
    - get actual ssh/ftp/smb logs

client.conf:

    - client interaction is needed before first run

Client must run at user level


# Dashboard
- logs.html

        renders a view of all logs in the database
        
        This will likely shift to a streamlit app
        - prep data for dashboard viz

# Configuration

    A json file is provided for each server and client side individually
    in their respective directories.


## TODO

- Encryption
    - in transit
    - lock the db

- Authentication: 
    client needs to confirm somehow the client file is legit
    perhaps a file checksum could work
    1. checksum all staticfiles' hashes added up (client)
    - checklist pwd files
    - exclude conf and db and create a hash from the rest


# REFERENCES

a non-exhaustive list of possible IOCs to consider implementing:

    Unusual Login Activity:
        Multiple failed login attempts.
        Successful logins from unusual locations or at unusual times.
        Repeated login failures for the same account.

    Anomalous File Access:
        Unexpected access to sensitive files or directories.
        Changes to critical system files.
        Unusual file permission changes.

    Malware Signatures:
        Detecting known malware signatures in file hashes or patterns.
        Anomalous process behavior that may indicate the presence of malware.

    Network Traffic Anomalies:
        Unusual network connections, such as connections to known malicious IP addresses or domains.
        Large data transfers to/from unexpected locations.
        Port scans or network reconnaissance.

    Unauthorized Access or Privilege Escalation:
        Detection of unauthorized access to sensitive systems or data.
        Unusual privilege escalation activities.

    Suspicious Processes and System Calls:
        Monitoring for processes or system calls associated with known attacks or exploits.
        Detecting shellcode execution or suspicious API calls.

    Abnormal Resource Usage:
        Unusual spikes in CPU, memory, or disk usage.
        Processes that consume more resources than usual.

    Registry or Configuration Changes:
        Unauthorized changes to system registries or configuration files.
        Changes to startup scripts or cron jobs.

    Web Server and Application Logs:
        Analyzing web server logs for signs of SQL injection, XSS attacks, or other web-based attacks.
        Monitoring for unusual or excessive web traffic patterns.

    Email and Messaging Logs:
        Detecting phishing attempts or suspicious email attachments.
        Monitoring for email traffic to known malicious domains.

    DNS Queries and Resolutions:
        Detecting unusual DNS queries or responses.
        Monitoring for DNS requests to malicious domains.

    Authentication and Authorization Logs:
        Unusual access requests or changes to user roles and permissions.

    Endpoint Security Alerts:
        Alerts from antivirus, intrusion detection systems (IDS), or endpoint protection solutions.