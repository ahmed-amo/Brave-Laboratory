import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

#this model i made it to predict the anemia based on data set with multi features

#the bath for the data set part1 for training and testing at the same time
#path : "../../../Anemia_Prediction_part1.csv"
df = pd.read_csv("C:/Users/pc/Downloads/Anemia_Prediction_part1.csv") 
print(df)

# spliting the data and its label
x = df.drop(columns='TEST')
y = df['TEST']

# spliting the data -train data , -test data
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.1, random_state=21)

print(x_test)

# scale the input "data" (mean normalisation, ..)
scaler = StandardScaler()
x_train_scaled = scaler.fit_transform(x_train)
x_test_scaled = scaler.transform(x_test)

# Save the scaler used for training to a file
 
joblib.dump(scaler, "scaler.pkl")

# training a model
log_reg = LogisticRegression(random_state=0).fit(x_train_scaled, y_train)

print(log_reg.predict(x_train_scaled))
print(log_reg.score(x_test_scaled, y_test))

# Save the trained model to a file
joblib.dump(log_reg, "trained_model.pkl")
