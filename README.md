# NetLab

NetLab is a web-based network topology simulator that allows users to create, visualize, and interact with virtual network environments. It combines a Vue.js frontend with a Python Flask backend to provide a seamless and interactive experience for network experimentation and learning.

## Features

- **Interactive Topology Creation:** Easily create and configure network topologies such as rings, stars, and meshes.
- **Real-time Visualization:** View your network topology in real-time with a dynamic and interactive graph.
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
    cd Prototyp/NetLabFrontend
    npm install
    ```

3.  **Install backend dependencies:**

    ```bash
    cd ../Backend/NetLabBuilder
    pip install -r requirements.txt
    ```

### Running the Application

1.  **Start the backend server:**

    ```bash
    cd Prototyp/Backend/NetLabBuilder
    ```

2.  **Start the frontend development server:**

    ```bash
    cd Prototyp/NetLabFrontend
    npm run dev
    ```

3.  **Open your browser** and navigate to the URL provided by the Vite development server (usually `http://localhost:5173`).
