import numpy as np

def filter_invalid_data(X, y):
    valid_X = []
    valid_y = []

    for i, spectrogram in enumerate(X):
        if spectrogram is None or spectrogram.shape[0] == 0:  # Check for empty spectrogram
            continue  # Skip invalid data
        valid_X.append(spectrogram)
        valid_y.append(y[i])

    return np.array(valid_X), np.array(valid_y)

checkpoint = np.load("npz/fullstop_prediction_test.npz")
X = checkpoint["X"].tolist()
y = checkpoint["y"].tolist()

X_filtered, y_filtered = filter_invalid_data(X, y)

np.savez("npz/fullstop_prediction_test_filtered.npz", X=X_filtered, y=y_filtered)
