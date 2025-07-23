import streamlit as st
import pandas as pd
import joblib
from kafka import KafkaConsumer, KafkaProducer
import json
from sklearn.preprocessing import LabelEncoder
import time

st.set_page_config(page_title="Fraud Detection Dashboard", layout="wide")

# Sidebar
st.sidebar.title("ℹ️ About")
st.sidebar.info(
    """
    **Real-Time Credit Card Fraud Detection**
    
    - Powered by Kafka, scikit-learn, and Streamlit
    - Shows live predictions and alerts for fraudulent transactions
    """
)
if st.sidebar.button("🔄 Refresh Dashboard"):
    st.experimental_rerun()

# Add a button to simulate a fraud
if st.sidebar.button("🚨 Simulate Fraudulent Transaction"):
    producer = KafkaProducer(
        bootstrap_servers='localhost:9092',
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    fraudulent_transaction = {
        "Unnamed: 0": 5727826,
        "step": 399,
        "type": "TRANSFER",
        "amount": 1442075.9,
        "nameOrig": "C2041824507",
        "oldbalanceOrg": 1442075.9,
        "newbalanceOrig": 0.0,
        "nameDest": "C1842704131",
        "oldbalanceDest": 0.0,
        "newbalanceDest": 0.0,
        "isFraud": 1,
        "isFlaggedFraud": 0
    }
    producer.send('transactions', value=fraudulent_transaction)
    producer.flush()
    st.sidebar.success("Simulated fraudulent transaction sent!")

# Header
st.markdown("""
    <h1 style='text-align: center;'>💳 Real-Time Credit Card Fraud Detection</h1>
    <h4 style='text-align: center; color: gray;'>Monitor transactions and get instant fraud alerts</h4>
    <hr>
    """, unsafe_allow_html=True)

# Load model
model = joblib.load('final_model_5.bin')

# LabelEncoder for 'type'
type_classes = ['CASH_IN', 'CASH_OUT', 'DEBIT', 'PAYMENT', 'TRANSFER']
le = LabelEncoder()
le.fit(type_classes)

cols_to_drop = ['Unnamed: 0', 'nameOrig', 'nameDest', 'isFraud', 'isFlaggedFraud']

# Kafka consumer
consumer = KafkaConsumer(
    'transactions',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='fraud-dashboard-group',
    consumer_timeout_ms=1000
)

# Streamlit state
if 'data' not in st.session_state:
    st.session_state['data'] = []
if 'fraud_count' not in st.session_state:
    st.session_state['fraud_count'] = 0
if 'total_count' not in st.session_state:
    st.session_state['total_count'] = 0
if 'last_fraud_alert' not in st.session_state:
    st.session_state['last_fraud_alert'] = None

# --- Static Layout Placeholders ---
metrics_placeholder = st.empty()
alert_placeholder = st.empty()
table_placeholder = st.empty()

# --- Render static layout ONCE ---
with metrics_placeholder:
    col1, col2 = st.columns(2)
    total_metric = col1.metric("Total Transactions", st.session_state['total_count'])
    fraud_metric = col2.metric("Fraudulent Transactions", st.session_state['fraud_count'])
with alert_placeholder:
    if st.session_state['last_fraud_alert']:
        st.warning(st.session_state['last_fraud_alert'])

# Main polling loop
while True:
    for message in consumer.poll(timeout_ms=1000, max_records=10).values():
        for record in message:
            transaction = record.value
            X = pd.DataFrame([transaction])
            for col in cols_to_drop:
                if col in X.columns:
                    X = X.drop(col, axis=1)
            if 'type' in X.columns:
                X['type'] = le.transform(X['type'])
            prediction = model.predict(X)[0]
            result = 'FRAUD' if prediction == 1 else 'NOT FRAUD'
            # Print transaction and prediction for debugging
            print(f"Transaction: {transaction}\nPrediction: {result}\n---")
            transaction_display = transaction.copy()
            transaction_display['Prediction'] = result
            st.session_state['data'].append(transaction_display)
            st.session_state['total_count'] += 1
            if result == 'FRAUD':
                st.session_state['fraud_count'] += 1
                # Show fake email alert in Streamlit
                alert_msg = f"""
                === EMAIL ALERT ===\nSubject: FRAUD ALERT: Suspicious Transaction Detected\nBody: Fraudulent transaction detected:\n{json.dumps(transaction, indent=2)}\n==================
                """
                st.session_state['last_fraud_alert'] = alert_msg
    # Show only the last 50 transactions
    df = pd.DataFrame(st.session_state['data'][-50:])
    # Highlight fraud rows
    def highlight_fraud(row):
        color = 'background-color: #ffcccc' if row['Prediction'] == 'FRAUD' else ''
        return [color]*len(row)
    # --- Update metrics and alert in their placeholders ---
    with metrics_placeholder:
        col1, col2 = st.columns(2)
        col1.metric("Total Transactions", st.session_state['total_count'])
        col2.metric("Fraudulent Transactions", st.session_state['fraud_count'])
    with alert_placeholder:
        alert_placeholder.empty()
        if st.session_state['last_fraud_alert']:
            st.warning(st.session_state['last_fraud_alert'])
    # Only one table rendered here
    with table_placeholder:
        table_placeholder.empty()
        st.markdown("<br>", unsafe_allow_html=True)
        if not df.empty:
            st.dataframe(df.style.apply(highlight_fraud, axis=1), height=500)
        else:
            st.info("No transactions yet.")
    time.sleep(1) 