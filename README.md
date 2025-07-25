# NetLab

NetLab is a web-based network topology simulator that allows users to create, visualize, and interact with virtual network environments. It combines a Vue.js frontend with a Python Flask backend to provide a seamless and interactive experience for network experimentation and learning.

## Credits

The backend of this project builds upon the work of **[JanBdot](https://github.com/JanBdot/NetLabBuilder)** in the NetLabBuilder project. We extend our gratitude for the foundational network topology and container management infrastructure that made this project possible.

## Features

- **Interactive Topology Creation:** Easily create and configure network topologies such as rings, stars, trees and meshes.
- **Real-time Visualization:** View your network topology in real-time with a dynamic graph.
- **Embedded Terminal:** Access and interact with the command line of each node in your topology directly from your browser.
- **PCAP Analysis:** Capture and analyze network traffic with the integrated PCAP viewer.
- **Extensible Architecture:** The project is designed to be easily extensible with new topologies and features.

## Tech Stack

**Frontend:**

- [Vue.js](https://vuejs.org/)
- [Vue Router](https://router.vuejs.org/)
- [Vuex](https://vuex.vuejs.org/)
- [D3.js](https://d3js.org/)
- [PrimeVue](https://www.primefaces.org/primevue/)

**Backend:**

- [Flask](https://flask.palletsprojects.com/en/2.3.x/)
- [Docker](https://www.docker.com/)

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/en/)
- [Python 3](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/florinm03/NetLab.git
    cd NetLab
    ```

2.  **Install frontend dependencies:**

    ```bash
    cd Frontend
    npm install
    ```

3.  **Install backend dependencies:**

    ```bash
    cd ../Backend/NetLabBuilder
    python3 -m venv nlb-venv
    source nlb-venv/bin/activate
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Make sure Docker is running and start the database container:**

    ```bash
    cd Backend/NetLabBuilder
    chmod +x start_pcap_database.sh
    ./start_pcap_database.sh
    ```

2.  **Start the backend server:**

    ```bash
    cd Backend/NetLabBuilder
    source nlb-venv/bin/activate
    python src/net_lab_builder/app.py
    ```

3.  **Start the frontend development server:**

    ```bash
    cd Frontend
    npm run dev
    ```


