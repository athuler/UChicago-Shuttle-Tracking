[![Better Stack Badge](https://uptime.betterstack.com/status-badges/v2/monitor/15u11.svg)](https://status.andreithuler.com)
# UChicago Shuttle Tracking

 
## Secrets

In the same repository as `run.py`, create a `secret.py` in the following format:

``` python
DB_HOST = ""
DB_NAME = ""
DB_USER = ""
DB_PASS = ""
```

## Virtual Machine Management

This program runs in a Linux-based Google Gloud VM. Below are the steps for how to initially configure it as well as to start it.

### Initial Setup

1. Create and enter a Python virtual environment
2. Install the package: `pip install git+https://github.com/athuler/UChicago-Shuttle-Tracking@main`
1. Upload `run.py` and `secret.py` to the VM
2. Create `run.sh` containing the following:

``` bash
source venv/bin/activate
python3 run.py
```

5. Exit the virtual environment

### Starting up the VM:

Note: run this outside of any virtual environments

``` bash
screen
source run.sh
```

### Reconnect to the VM:

``` bash
screen -d -r
```