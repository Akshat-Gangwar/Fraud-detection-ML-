# Fraud-detection-ML-
This project was made by me for a Machine Learning internship .
This project streams data using Apache Kafka to a real time simulation and detects fraud.
It highlights, counts and alerts via email if a fraudulent transaction is detected.

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Akshat-Gangwar/Fraud-detection-ML-.git
   cd fraud-detection
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start Kafka and Zookeeper:**  
   You can use the provided `docker-compose.yml`:
   ```bash
   docker-compose up
   ```

4. **Train the model (optional):**
   ```bash
   python train_model.py
   ```

5. **Start the producer, consumer, and dashboard:**
   - Producer: `python producer.py`
   - Consumer: `python consumer.py`
   - Dashboard: `python dashboard.py`

## Usage

- The **producer** sends transaction data to Kafka.
- The **consumer** receives data, applies the ML model, and stores results.
- The **dashboard** visualizes the latest transactions and fraud predictions.

## Docker Instructions

To run the entire stack using Docker Compose:
```bash
docker-compose up
```
This will start Kafka, Zookeeper, and any other services defined in `docker-compose.yml`.

## Requirements

- Python 3.7+
- See `requirements.txt` for Python dependencies
- Docker & Docker Compose (for containerized setup)


---

