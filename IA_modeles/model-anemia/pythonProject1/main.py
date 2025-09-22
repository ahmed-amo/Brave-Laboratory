import joblib
import numpy as np

# Load the trained model from the file
log_reg = joblib.load("C:/Users/pc/PycharmProjects/pythonProject1/trained_model.pkl")

arr = np.array([60, 1, 4.08, 38.8, 95, 30.8, 32.4, 15.2, 7.1, 183, 12.6])
reshaped_arr = arr.reshape(1, -1)

# Load the scaler used for training
# the path for the scaler used to scale the training data so we use it to scale the input
scaler = joblib.load("C:/Users/pc/PycharmProjects/pythonProject1/scaler.pkl")
arr_scaled = scaler.transform(reshaped_arr)

print(log_reg.predict(arr_scaled))
