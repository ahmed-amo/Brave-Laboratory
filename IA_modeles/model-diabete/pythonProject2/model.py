import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

#this model i made it to predict the anemia based on data set with multi features

#the bath for the data set part1 for training and testing at the same time
#path : "../../../diabetes_prediction_dataset_part1.csv"
df = pd.read_csv("C:/Users/pc/Desktop/Atelie/datasets/diabetes_prediction_dataset_part1.csv")
print(df)

# spliting the data and its label
x = df.drop(columns='diabetes')
y = df['diabetes']

# spliting the data -train data , -test data
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=21)

print(x_test)

# scale the input "data" (mean normalisation, ..)
scaler_for_diabetes = StandardScaler()
x_train_scaled = scaler_for_diabetes.fit_transform(x_train)
x_test_scaled = scaler_for_diabetes.transform(x_test)

# Save the scaler used for training to a file
joblib.dump(scaler_for_diabetes, "scaler_for_diabetes.pkl")


# training a model
log_reg = LogisticRegression(random_state=0).fit(x_train_scaled, y_train)

print(log_reg.predict(x_train_scaled))
print(log_reg.score(x_test_scaled, y_test))

# Save the trained model to a file
joblib.dump(log_reg, "trained_model_for_diabetes.pkl")
