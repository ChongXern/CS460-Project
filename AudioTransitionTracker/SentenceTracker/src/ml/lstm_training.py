import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_curve, auc

data_train = np.load('../../data/npz/fullstop_prediction_train_cleaned.npz')
X_train = data_train['X_train']
X_train = np.squeeze(X_train, axis=-1)
y_train = data_train['y_train']

X_train = (X_train - X_train.min()) / (X_train.max() - X_train.min())
y_train = y_train.reshape(-1, 1)

X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], X_train.shape[2])

data_test = np.load('../../data/npz/fullstop_prediction_test_cleaned.npz')
X_test = data_test['X_test']
X_test = np.squeeze(X_test, axis=-1)
y_test = data_test['y_test']

X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], X_test.shape[2])

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train.reshape(-1, X_train.shape[2]))
X_test = scaler.transform(X_test.reshape(-1, X_test.shape[2]))
X_train = X_train.reshape(-1, 648, 1025)
X_test = X_test.reshape(-1, 648, 1025)

model = Sequential([
    Input(shape=(X_train.shape[1], X_train.shape[2])),
    LSTM(64, return_sequences=False),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dropout(0.3),
    Dense(1, activation='sigmoid')
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])

model.summary()

model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))

y_pred = (model.predict(X_test) > 0.5).astype("int32")
print(classification_report(y_test, y_pred))

fpr, tpr, thresholds = roc_curve(y_test, y_pred)
roc_auc = auc(fpr, tpr)
print(f"AUC: {roc_auc:.4f}")
