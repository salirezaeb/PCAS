# Fsched: A Function-as-a-Service Platform with Smart Cache Allocation

**Fsched** is a Function-as-a-Service (FaaS) platform that optimizes function execution by predicting and allocating the required Last Level Cache (LLC) for each function. The platform follows a **Master-Worker** architecture, where the **Master Node** manages function scheduling and LLC allocation, and the **Worker Nodes** execute the functions.

## Table of Contents

*   [Overview](#overview)
*   [Features](#features)
*   [Architecture](#architecture)
*   [Installation](#installation)
*   [Usage](#usage)
*   [Contributing](#contributing)
*   [License](#license)

## Overview

Fsched enhances performance in serverless computing by intelligently predicting and allocating LLC resources. The platform leverages a machine learning model to determine the LLC needs of each function, improving resource utilization and reducing cache misses. It operates in a **Master-Worker** structure, with the master node controlling task distribution and the worker nodes executing tasks efficiently.

## Features

*   **Master-Worker Architecture**: Distributed task scheduling and execution with Rust-based worker nodes and a Python-based master node.
*   **LLC Prediction**: A machine learning model forecasts the LLC requirements for each function before execution.
*   **Cluster Management**: Seamlessly add or remove worker nodes.
*   **Efficient Scheduling**: Dynamically assigns tasks to the most suitable worker node based on predicted LLC requirements.
*   **Scalability**: Add more worker nodes to handle higher workloads without degrading performance.

## Architecture

Fsched's architecture revolves around a **Master Node** and **Worker Nodes**.

### Master Node

The master node is responsible for managing the overall system and is composed of the following key modules:

1.  **Cluster Manager**: Manages worker nodes, including adding, removing, and monitoring nodes in the system.
2.  **Controller**: Acts as the central hub, handling incoming function requests, coordinating with the other modules, and ensuring tasks are processed.
3.  **Scheduler**: Schedules tasks on worker nodes based on LLC predictions and available resources.
4.  **Predictor**: Utilizes a machine learning model to predict the required LLC for each function, ensuring optimal scheduling and resource allocation.

### Worker Nodes

Worker nodes, implemented in Rust, execute functions that have been scheduled by the master node. They use the LLC allocated by the master node's prediction model to ensure efficient execution.

_(architecture diagram)_

## Installation

### Prerequisites

*   Python 3.x (for the master node)
*   Rust (for building the worker nodes)
*   Docker (optional, for containerized deployments)

### Steps

1.  **Clone the repository**:
    
    ```bash
    git clone https://github.com/Manni-MinM/fsched.git
    cd fsched
    ```
    
2.  **Master Node Setup (Python)**:
    
    Install the required dependencies for the Python master node:
    
    ```bash
    cd master
    pip install -r requirements.txt
    ```

3.  **Worker Node Setup (Rust)**:
    
    Navigate to the `worker` directory and build the worker nodes:
    
    ```bash
    cd worker
    cargo build --release
    ```

## Usage

### Running the Master Node

Start the master node to manage worker nodes and schedule tasks:

```bash
python master/main.py
```

This starts all four modules (Cluster Manager, Controller, Scheduler, and Predictor) and begins accepting function execution requests.

### Running Worker Nodes

On each worker node machine, run the following to start the worker:

```bash
./target/release/worker_node
```

The worker nodes will register with the master node and wait for tasks to execute.

### Example Function Submission

Submit a function to the master node for scheduling and execution:

```bash
curl -X POST http://<master-node-ip>:<port>/submit \
    -d '{"function_name": "my_function", "parameters": {"arg1": "value1"}}'
```

The master node will handle task scheduling, predict the LLC, and dispatch the task to the best-suited worker node.

## API Documentation

The Fsched master node exposes a RESTful API for task management, including the creation, benchmarking, and execution of tasks. Note that while the current implementation uses REST, there are plans to shift to an event-based system (e.g., RabbitMQ) in the future.

### Endpoints

1. **Create a New Task**
    
    *   **Endpoint**: `/controller/task/new`
    *   **Method**: `POST`
    *   **Description**: Uploads a new task file and returns a task ID.
    *   **Request Parameters**:
        *   `file` (multipart file)
    *   **Response**:
        *   200: Task ID for the newly created task.
        *   400: Error if no file is specified.
    
    **Example**:
    
    ```bash
    curl -X POST http://<master-node-ip>:<port>/controller/task/new \
    -F file=@/path/to/task/file
    ```
    
    **Response**:
    
    ```json
    {
        "task_id": "task123"
    }
    ```

2. **Run a Task**
    
    *   **Endpoint**: `/controller/task/run`
    *   **Method**: `POST`
    *   **Description**: Runs an existing task with the provided command, task ID, and input size. Checks if the task is ready for execution based on the input size.
    *   **Request Parameters** (JSON):
        *   `command`: Command to execute the task.
        *   `task_id`: ID of the task to run.
        *   `input_size`: Size of the input for the task.
    *   **Response**:
        *   200: Returns task execution status and execution mode.
        *   400: Error if required keys are missing.
    
    **Example**:
    
    ```bash
    curl -X POST http://<master-node-ip>:<port>/controller/task/run \
    -H "Content-Type: application/json" \
    -d '{"command": "run_cmd", "task_id": "task123", "input_size": 1024}'
    ```
    
    **Response**:
    
    ```json
    {
        "message": "Task is not yet ready for execution. Try benchmarking it with a specific input size"
    }
    ```

3. **Benchmark a Task**
    
    *   **Endpoint**: `/controller/task/benchmark`
    *   **Method**: `POST`
    *   **Description**: Benchmarks an existing task based on the provided command, task ID, and input size. This prepares the task for execution.
    *   **Request Parameters** (JSON):
        *   `command`: Command to benchmark the task.
        *   `task_id`: ID of the task to benchmark.
        *   `input_size`: Size of the input for the task.
    *   **Response**:
        *   200: Returns benchmark result and marks the task as ready for execution.
        *   400: Error if required keys are missing.
    
    **Example**:
    
    ```bash
    curl -X POST http://<master-node-ip>:<port>/controller/task/benchmark \
    -H "Content-Type: application/json" \
    -d '{"command": "bench_cmd", "task_id": "task123", "input_size": 1024}'
    ```
    
    **Response**:
    
    ```json
    {
        "message": "Benchmarking was successful and task is ready for execution",
        "exec_time": {
            "input_size": 1024,
            "time": "15ms"
        }
    }
    ```

### Notes

*   In the future, these endpoints will be transitioned to an event-based system using a message broker like RabbitMQ to facilitate asynchronous task handling.
*   For now, the REST API provides a simple and synchronous interface for task management and execution.

---

## Worker Management

The following endpoints allow for managing worker nodes in the Fsched platform. You can register new worker nodes and list the currently active ones.

1. **Register a New Worker Node**
    
    *   **Endpoint**: `/cluster/worker/add`
    *   **Method**: `POST`
    *   **Description**: Registers a new worker node with the master by specifying the worker's host address.
    *   **Request Parameters** (JSON):
        *   `host`: The IP address or hostname of the worker node.
    *   **Response**:
        *   200: Successfully added the worker node.
        *   400: Error if no host is specified.
        *   500: Error if the worker node is unresponsive.
    
    **Example**:
    
    ```bash
    curl -X POST http://<master-node-ip>:<port>/cluster/worker/add \
    -H "Content-Type: application/json" \
    -d '{"host": "192.168.1.10"}'
    ```
    
    **Response**:
    
    ```json
    {
        "message": "worker node successfully added"
    }
    ```

2. **List Registered Worker Nodes**
    
    *   **Endpoint**: `/cluster/workers`
    *   **Method**: `GET`
    *   **Description**: Retrieves the list of currently registered worker nodes.
    *   **Response**:
        *   200: Returns a list of registered worker nodes.
    
    **Example**:
    
    ```bash
    curl -X GET http://<master-node-ip>:<port>/cluster/workers
    ```
    
    **Response**:
    
    ```json
    {
        "workers": [
            {
                "id": "worker1",
                "host": "192.168.1.10"
            },
            {
                "id": "worker2",
                "host": "192.168.1.11"
            }
        ]
    }
    ```

## License

This project is licensed under the MIT License. See the LICENSE file for details.
