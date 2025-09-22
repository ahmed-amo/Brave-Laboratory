import joblib
import numpy as np

# Load the trained model from the file
log_reg = joblib.load("/home/adam/Documents/Python-Django Development/Brave-Lab/IA_modeles/model-diabete/pythonProject2/trained_model_for_diabetes.pkl")

arr = np.array([1.0, 37.0, 0.0, 0.0, 1.0, 36.87, 8.8, 160.0])
reshaped_arr = arr.reshape(1, -1)

# Load the scaler used for training
scaler = joblib.load("/home/adam/Documents/Python-Django Development/Brave-Lab/IA_modeles/model-diabete/pythonProject2/scaler_for_diabetes.pkl")
arr_scaled = scaler.transform(reshaped_arr)

# Make predictions and get probabilities
predictions = log_reg.predict(arr_scaled)
probabilities = log_reg.predict_proba(arr_scaled)


# Extract the probability for the positive class (class 1)
positive_probability = probabilities[0, 1]

# Convert the probability to percentage
positive_percentage = positive_probability * 100

print("Predictions:", predictions)
print("Positive Probability:", positive_probability)
print("Positive Percentage:", positive_percentage, "%")
