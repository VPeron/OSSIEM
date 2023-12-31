# OS SIEM


### Goal: 

        an open source basic SIEM system for home users with multiple linux devices

### trajectory

**Stack**: Python >= 3.8, docker*(eng), streamlit(dashboard), telegrambot (alerts)
NOTE: Docker may screw subprocess system calls, specially on client side

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
- setup alerts (TODO)


```
.
├── README.md
├── requirements.txt
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

    - user interaction is needed before first run

Client must run at user level?


# Dashboard
- logs.html

        renders a view of all logs in the database
        
        This will likely shift to a streamlit app
        - prep data for dashboard viz

# Configuration

    A json file is needed for each server and client side individually
    in their respective directories. 
server_conf.json (template)

```
{
    "host" : "0.0.0.0",
    "port" : 5000,
    "db_name" : "siem_database.db",
    "net_interface" : "",
    "host_ip" : "",
    "hash_algorithm": "sha256",
    "client_checksums": {
        "client": "",
        "logger": "",
        "client_init": "",
        "system_monitor": "",
        "client_integritiy": ""
    }
}
```
client_conf.json (template)

```
{
    "client_init": "false",
    "server_ip": "",
    "port": 5000,
    "client_name": "",
    "net_interface": "",
    "host_ip": "",
    "client_filepath": "",
    "hash_algorithm": "sha256"
}
```
The client_init loads the interface, host_ip and hash algorithm from the server directly on first run.
name and server_ip need user interaction or server preconfig on distribution.

## TODO

- Encryption
    - in transit
    - lock the db

- Authentication: 
    client needs to confirm somehow the client file is legit
    perhaps a file checksum could work
    - checklist pwd files
    - exclude conf and db and create a hash from the rest
- Authorization:
    - client needs to authorized to only perform predefined
    actions via api calls.

- Dependencies:
    split server/client dependencies

- Tests
    unittest should be ok for now


# REFERENCES

tested systems: Ubuntu 22.04.2