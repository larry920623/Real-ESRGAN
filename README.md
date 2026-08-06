
# Scalable AI Super Resolution Engine

A distributed microservices architecture designed to provide decoupled and scalable image super-resolution capabilities. This project transforms a heavy AI inference script into a robust, production-ready system utilizing asynchronous task queues and hardware-optimized execution.

##  Features

* **Distributed Microservices Architecture:** Completely decouples the API gateway from the GPU-intensive inference workload.
* **Non-Blocking API:** Utilizes FastAPI's native asynchronous support to provide instant task ID generation upon image upload without freezing the server.
* **Reliable Task Queuing:** Implements Redis as an in-memory message broker to prevent GPU exhaustion during simultaneous user requests.
* **Hardware Optimization (Tiling Strategy):** Specifically engineered to bypass VRAM Out-of-Memory (OOM) limitations on hardware like the 8GB RTX 2060 by processing high-resolution (e.g., 4K) images in smaller chunks.
* **DevOps & CI/CD Pipeline:** Fully containerized via Docker to guarantee environment consistency, paired with GitHub Actions for automated code quality checks (Flake8) and Docker Hub image delivery.

##  System Architecture

The system consists of three main isolated components communicating over a Docker bridge network:

1. **FastAPI (Web):** The entry point for client requests (Image Uploads and Status Polling).
2. **Redis Queue:** The message broker that holds pending inference tasks.
3. **Celery Worker (GPU):** A dedicated background worker executing PyTorch / Real-ESRGAN inference, utilizing NVIDIA GPU passthrough.

*Note: The Web and Worker containers share a mounted volume (`/data_shared`) for efficient image file transfer, avoiding heavy I/O payloads through the message broker*.

##  Tech Stack

* **AI Engine:** PyTorch, Real-ESRGAN (Generative Adversarial Network)
* **API Gateway:** FastAPI (Python)
* **Message Broker:** Redis
* **Task Queue:** Celery
* **Containerization & Deployment:** Docker, Docker Compose

##  Prerequisites

To run this system locally, ensure your machine has the following installed:

* Docker & Docker Compose
* NVIDIA GPU Driver
* NVIDIA Container Toolkit (essential for GPU passthrough to the worker container)

##  Quick Start

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/scalable-ai-super-resolution.git
cd scalable-ai-super-resolution

```

**2. Start the microservices**
Build and start the system in detached mode:

```bash
docker-compose up -d --build

```

**3. Access the API**
Once the containers are running (verify with `docker ps`), navigate to the interactive API documentation:

* **Swagger UI:** `http://<YOUR_HOST_IP>:8002/docs`

##  API Usage Workflow

1. **Submit an Image:** Send a `POST` request to `/process-image` with your image file. The API will immediately return a JSON response containing a unique `task_id` and a `processing` status.
2. **Poll Status:** Send a `GET` request to `/tasks/{task_id}` to check the completion status.
3. **Download Result:** Once the status is `success`, the response will include a `download_url` to retrieve the upscaled, high-resolution image.

##  Future Optimizations

* **Global Access:** Implement Cloudflare Tunnel or Nginx for secure HTTPS public access.
* **Horizontal Scaling:** Transition to Kubernetes (K8s) to automatically scale the number of Celery workers based on the current Redis queue length.
* **Frontend Integration:** Develop a React Web UI for concurrent task visualization and a better user experience.

Hackmd : https://hackmd.io/@larry920623/HJ5-9bs_Wg
