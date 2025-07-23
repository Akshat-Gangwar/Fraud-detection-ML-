import json
from kafka import KafkaConsumer
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder
import time
import smtplib
from email.mime.text import MIMEText

def send_fraud_alert(transaction):
    sender = "akshat.gangwar132005@gmail.com" 
    receiver = "alert_email@gmail.com" 
    password = "**********"  

    subject = "FRAUD ALERT: Suspicious Transaction Detected"
    body = f"Fraudulent transaction detected:\n\n{transaction}"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print("Email alert sent!")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Load the trained model
model = joblib.load('final_model_5.bin')

# Recreate the LabelEncoder for 'type' as in training
type_classes = ['CASH_IN', 'CASH_OUT', 'DEBIT', 'PAYMENT', 'TRANSFER']
le = LabelEncoder()
le.fit(type_classes)

cols_to_drop = ['Unnamed: 0', 'nameOrig', 'nameDest', 'isFraud', 'isFlaggedFraud']

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='fraud-detector-group'
)

print("Listening for transactions...")

for message in consumer:
    transaction = message.value
    X = pd.DataFrame([transaction])
    for col in cols_to_drop:
        if col in X.columns:
            X = X.drop(col, axis=1)
    if 'type' in X.columns:
        X['type'] = le.transform(X['type'])
    prediction = model.predict(X)[0]
    result = 'FRAUD' if prediction == 1 else 'NOT FRAUD'
    print(f"Transaction: {transaction}\nPrediction: {result}\n---")
    if result == 'FRAUD':
        send_fraud_alert(transaction) 