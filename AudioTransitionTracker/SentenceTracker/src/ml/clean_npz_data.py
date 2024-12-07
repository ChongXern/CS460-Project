import numpy as np

#data = np.load('../../data/npz/fullstop_prediction_train.npz')
data = np.load('../../data/npz/fullstop_prediction_test.npz')

print(data)

#sums = np.sum(data['X_train'], axis=(1, 2, 3))
sums = np.sum(data['X_test'], axis=(1, 2, 3))
zero_sum_indxs = np.where(sums == 0)[0]

print(f'Zero sum indices: {zero_sum_indxs}')

#X_train_cleaned = np.delete(data['X_train'], zero_sum_indxs, axis=0)
#y_train_cleaned = np.delete(data['y_train'], zero_sum_indxs, axis=0)
X_test_cleaned = np.delete(data['X_test'], zero_sum_indxs, axis=0)
y_test_cleaned = np.delete(data['y_test'], zero_sum_indxs, axis=0)

#np.savez('../../data/npz/fullstop_prediction_train_cleaned.npz', X_train=X_train_cleaned, y_train=y_train_cleaned)
np.savez('../../data/npz/fullstop_prediction_test_cleaned.npz', X_test=X_test_cleaned, y_test=y_test_cleaned)

