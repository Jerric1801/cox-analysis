# Cox's Bazar Disaster Simulator App

This application is designed to streamline evacuation planning in response to the Rohingya Refugee crisis in Cox's Bazar. Leveraging Flask, Pandas, NetworkX, and Folium, it simulates optimized routes to improve emergency response and evacuation efficiency.


## Prerequisites

- Docker
- Poetry

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/cox-analysis.git
cd cox-analysis
```

### 2. Install Poetry
If you don't have Poetry installed, you can install it using the following command:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Add Poetry to your PATH by adding the following line to your shell configuration file (~/.bash_profile, ~/.bashrc, or ~/.zshrc):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Reload your shell configuration:

```bash
source ~/.bash_profile  # or ~/.bashrc or ~/.zshrc
```

### 3. Generate poetry.lock
Navigate to the app directory and generate the poetry.lock file:

```bash
cd app
poetry lock
cd ..
```

### 4. Build and Run the Docker Container

Run the following script to build and run the container: 

```bash
./start.sh
```

### 5. Access the Application

Open your web browser and navigate to:

```bash
http://localhost:3001
```

### 6. Stopping the Application
To stop and remove the Docker container, run the following script:

```bash
./stop.sh
```
