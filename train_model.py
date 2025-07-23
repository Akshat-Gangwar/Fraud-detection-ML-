import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, f1_score
import joblib

# Load data
csv_file = 'lastten.csv'
df = pd.read_csv(csv_file)

# Drop the first unnamed column (index)
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # or df.drop(df.columns[0], axis=1)

# Drop nameOrig and nameDest (IDs)
df = df.drop(['nameOrig', 'nameDest'], axis=1)

# Encode 'type' categorical feature
le = LabelEncoder()
df['type'] = le.fit_transform(df['type'])

# Features and target
target = 'isFraud'
X = df.drop([target, 'isFlaggedFraud'], axis=1)
y = df[target]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Logistic Regression
lr = LogisticRegression(max_iter=1000)
lr.fit(X_train, y_train)
y_pred_lr = lr.predict(X_test)
acc_lr = accuracy_score(y_test, y_pred_lr)
f1_lr = f1_score(y_test, y_pred_lr)
print('Logistic Regression:')
print(classification_report(y_test, y_pred_lr))

# Random Forest
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
y_pred_rf = rf.predict(X_test)
acc_rf = accuracy_score(y_test, y_pred_rf)
f1_rf = f1_score(y_test, y_pred_rf)
print('Random Forest:')
print(classification_report(y_test, y_pred_rf))

# Save the best model
if f1_rf >= f1_lr:
    print('Saving Random Forest model as final_model_5.bin')
    joblib.dump(rf, 'final_model_5.bin')
else:
    print('Saving Logistic Regression model as final_model_5.bin')
    joblib.dump(lr, 'final_model_5.bin') 