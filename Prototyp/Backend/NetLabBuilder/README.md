# NetLabBuilder

NetLabBuilder is a Python package that utilizes the Docker Python SDK to create and manage network environments.

## Installation
The installation guide is only tested for Linux (Ubuntu 21.04) and Windows 11 with WSL2 (Ubuntu 20.04).
### Prerequisites
- Python 3.8+
- pip 20+
- Docker 24
- Ubuntu: python-venv

### Installation Script
First clone this project and change directory to the project. Then run the setup script with the following command:

```bash
chmod +x setup.sh
./setup.sh
. nlb-venv/bin/activate
```	

This will create a virtual environment and install the required packages. The last command activates the virtual environment.

### Manual Installation
First clone this project and change directory to the project. Then run the following commands:

```bash
python3 -m venv nlb-venv
. nlb-venv/bin/activate
pip install -r requirements.txt
```

For Linux you might need to do some [post installation steps](https://docs.docker.com/engine/install/linux-postinstall/), if you freshly installed docker.

## Usage
There are four topology files in the `src/` folder that can be run with a command like this:

```bash
python3 src/<topology.py>
```

You should replace `<topology.py>` with the name of the topology file you want to run. The available topologies are:
- ring.py
- star.py
- tree.py
- mesh.py

Of course you can write your own topologies and run them with the same command.

In the future this code will be packaged as a Python package and will be available on PyPI. Then you can install it with `pip install netlabbuilder` and use it as a Python package.

### Pcap Files
The topologies will create pcap files in a docker volume. To find these files (e.g. to open with Wireshark) you can run the following command:

#### Linux

```bash
docker volume inspect pcap_data
```

The output will be something like this and you can find the pcap files in the `Mountpoint` directory:

```json
[
    {
        "CreatedAt": "2023-07-06T10:19:41Z",
        "Driver": "local",
        "Labels": null,
        "Mountpoint": "/var/lib/docker/volumes/pcap_data/_data",
        "Name": "pcap_data",
        "Options": null,
        "Scope": "local"
    }
]
```

#### Windows
For Windows there is still no reliable way to mount the volume to your Windows file system. For me with Docker Desktop and WSL2 I was able to find the pcap files in the following directory:

```bash
\\wsl$\docker-desktop-data\data\docker\volumes
```

If you have trouble finding your volumes in Windows, I refer to this [GitHub issue](https://github.com/microsoft/WSL/discussions/4176) or this [Blog post](https://dev.to/kim-ch/move-docker-desktop-data-distro-out-of-system-drive-4cg2).


## License
[MIT](https://choosealicense.com/licenses/mit/)
