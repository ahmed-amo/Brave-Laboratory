import joblib
import numpy as np

# Load the trained model from the file
log_reg = joblib.load("/home/adam/Documents/Python-Django Development/Brave-Lab/IA_modeles/model-diabete/pythonProject2/trained_model_for_diabetes.pkl")

arr = np.array([1.0,37.0,0.0,0.0,1.0,36.87,8.8,160.0])
reshaped_arr = arr.reshape(1, -1)

# Load the scaler used fon training
scaler = joblib.load("/home/adam/Documents/Python-Django Development/Brave-Lab/IA_modeles/model-diabete/pythonProject2/scaler_for_diabetes.pkl")
arr_scaled = scaler.transform(reshaped_arr)

re = log_reg.predict(arr_scaled)
