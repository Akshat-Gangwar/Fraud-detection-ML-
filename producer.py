import pandas as pd
import json
import time
from kafka import KafkaProducer

# Read the CSV file
csv_file = 'lastten.csv'
df = pd.read_csv(csv_file)

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

topic = 'transactions'

for idx, row in df.iterrows():
    message = row.to_dict()
    producer.send(topic, value=message)
    print(f"Sent: {message}")
    time.sleep(1)  # Simulate real-time by waiting 1 second

producer.flush()
producer.close() 