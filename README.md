# Neurond Sandbox

Neurond Sandbox is a flexible and powerful environment for executing code in isolated sessions using Docker or Kubernetes. It allows users to create, manage, and run code in various programming languages while providing a simple API for interaction.

## Features

- **Multi-Language Support**: Execute code in Python, Java, JavaScript, C++, Go, Ruby, and more.
- **Session Management**: Create, retrieve, and close sessions easily.
- **File Operations**: Copy files to and from the runtime environment.
- **Mounting**: Add mounts to sessions for persistent storage.
- **Configurable**: Customize Docker images and configurations for each session.

## Requirements

- Python 3.9 or higher
- FastAPI
- Docker or Kubernetes (depending on your choice of execution environment)
- Pydantic
- Uvicorn

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/phinx-orient/neurond-sandbox.git
   cd neurond-sandbox
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure Docker is running on your machine or configure Kubernetes as needed.

4. Create a `config.json` file in the root directory with the following structure:
   ```json
   {
       "SANDBOX_DOCKERFILE": "path/to/your/Dockerfile"
   }
   ```
The `SANDBOX_DOCKERFILE` folder contains the Dockerfile for the sandbox environment. You can pre-install essential packages, such as NumPy and Pandas, within this Dockerfile. This way, you won't need to install them again the first time you run the sandbox.

## Usage

### Starting the Server

To start the server using Docker Compose, create a `docker-compose.yml` file in the root directory with the following content:
```bash
docker compose up --build 
```

## Source
Clone and customize from https://github.com/vndee/llm-sandbox

