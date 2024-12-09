import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_curve, auc
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

data_train = np.load('../../data/npz/fullstop_prediction_train_cleaned.npz')
X_train = data_train['X_train']
X_train = np.squeeze(X_train, axis=-1)
y_train = data_train['y_train']

# flatten spectogram data for sampling x features
X_train_flattened = X_train.reshape(X_train.shape[0], -1)
y_train = y_train.ravel()  #flatten target into 1d arr

# Normalise features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_flattened)

data_test = np.load('../../data/npz/fullstop_prediction_test_cleaned.npz')
X_test = data_test['X_test']
X_test = np.squeeze(X_test, axis=-1)
y_test = data_test['y_test']

X_test_flattened = X_test.reshape(X_test.shape[0], -1)

X_test_scaled = scaler.transform(X_test_flattened)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_scaled, y_train)

y_pred = rf_model.predict(X_test_scaled)

print(classification_report(y_test, y_pred))

# Calculate auc
fpr, tpr, thresholds = roc_curve(y_test, rf_model.predict_proba(X_test_scaled)[:, 1])
roc_auc = auc(fpr, tpr)
print(f"AUC: {roc_auc}")

plt.figure()
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend(loc="lower right")
plt.show()
