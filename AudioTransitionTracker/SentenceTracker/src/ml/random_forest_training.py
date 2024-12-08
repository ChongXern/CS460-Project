import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_curve, auc
from sklearn.preprocessing import StandardScaler

# Load training data
data_train = np.load('../../data/npz/fullstop_prediction_train_cleaned.npz')
X_train = data_train['X_train']
y_train = data_train['y_train']

# Flatten spectrogram data for Random Forests (samples x features)
X_train_flattened = X_train.reshape(X_train.shape[0], -1)  # Flatten each spectrogram
y_train = y_train.ravel()  # Flatten the target to a 1D array

# Normalize features (this is optional but often improves performance)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_flattened)

# Load testing data
data_test = np.load('../../data/npz/fullstop_prediction_test_cleaned.npz')
X_test = data_test['X_test']
y_test = data_test['y_test']

# Flatten the test data as well
X_test_flattened = X_test.reshape(X_test.shape[0], -1)

# Normalize the test data using the same scaler as for the training data
X_test_scaled = scaler.transform(X_test_flattened)

# Initialize Random Forest model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)

# Train the model
rf_model.fit(X_train_scaled, y_train)

# Make predictions on the test data
y_pred = rf_model.predict(X_test_scaled)

# Print classification report
print(classification_report(y_test, y_pred))

# Calculate AUC
fpr, tpr, thresholds = roc_curve(y_test, rf_model.predict_proba(X_test_scaled)[:, 1])
roc_auc = auc(fpr, tpr)
print(f"AUC: {roc_auc}")

# Optionally, you can also visualize the ROC curve
import matplotlib.pyplot as plt
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
