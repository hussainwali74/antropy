setup django
uv run django-admin startproject config .
uv run python manage.py startapp core

---

# Neo4j with Docker Compose

This project runs a Neo4j graph database using Docker Compose.

The configuration uses a named volume (`neo4j-data`) to ensure your graph data is persisted even if the container is removed.

## Prerequisites

- Docker
- Docker Compose

## How to Use

1.  **Set Your Password**
    Create a file named `.env` in this directory and set your password:

    ```ini
    NEO4J_PASSWORD=your_super_secret_password
    ```

2.  **Start the Service**
    Run the following command to build and start the container in the background:

    ```bash
    docker-compose up -d
    ```

3.  **Stop the Service**
    To stop the container, run:
    ```bash
    docker-compose down
    ```

## Accessing Neo4j 🌐

- **Neo4j Browser**: Open your web browser to `http://localhost:7474`
- **Username**: `neo4j`
- **Password**: The password you set in the `.env` file.
