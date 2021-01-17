# plex_tools.py

## Installation
1. Clone the repository
2. Install dependencies (`pip install plexapi==4.2.0`)

## Usage
```
$ python3 plex_tools.py -h
usage: plex_tools.py [-h] [--list] [--stats] [--sync] [--ignore IGNORE [IGNORE ...]] [-V] email password

positional arguments:
  email                 Email address
  password              Password

optional arguments:
  -h, --help            show this help message and exit
  --list                List all your Plex servers
  --stats               Return watch-time statistics
  --sync                Sync watched content across all servers (excluding ignored servers)
  --ignore IGNORE [IGNORE ...]
                        List of servers to ignore
  -V, --verbose         Enable verbose output
```