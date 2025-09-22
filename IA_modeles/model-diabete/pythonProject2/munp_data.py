#import pandas as pd
#
#df = pd.read_csv("C:/Users/pc/Desktop/Atelie/datasets/diabetes_prediction_dataset.csv")
##print(df.head())      # Display the first few rows of the DataFrame
##print(df.shape)       # Get the dimensions of the DataFrame (rows, columns)
##print(df.info())      # Get information about the DataFrame
##print(df.describe())  # Statistical summary of the DataFrame
#
##column_values = df['smoking_history'].unique()
#
## Replace specific values in a column with a new float value
##df['smoking_history'] = df['smoking_history'].replace({'never': 0.0})
##df['smoking_history'] = df['smoking_history'].replace({'No Info': 1.0})
##df['smoking_history'] = df['smoking_history'].replace({'former': 2.0})
##df['smoking_history'] = df['smoking_history'].replace({'not current': 3.0})
##df['smoking_history'] = df['smoking_history'].replace({'ever': 4.0})
##df['smoking_history'] = df['smoking_history'].replace({'current': 5.0})
#
#
#
#column_values = df['gender'].unique()
#print(column_values)
## Count the occurrences of specific values in the 'gender' column
#value_counts = df['gender'].value_counts()
#print(value_counts)
## Delete rows with a specific value in the 'gender' column
#df = df[df['gender'] != 'Other']
## change male to "0.0" , female to "1.0"
#df['gender'] = df['gender'].replace({'Male': 0.0})
#df['gender'] = df['gender'].replace({'Female': 1.0})
## Count the occurrences of specific values in the 'gender' column
#value_counts1 = df['gender'].value_counts()
#print(value_counts1)
#
#
## Select columns with the 'int' data type
#int_columns = df.select_dtypes(include='int')
##print(int_columns.columns)
#
## Convert the data type of integer columns to float
#df[int_columns.columns] = df[int_columns.columns].astype(float)
## Print the updated DataFrame
##print(df.dtypes)
#
#
#df.to_csv("C:/Users/pc/Desktop/Atelie/datasets/diabetes_prediction_dataset.csv", index=False)
#print(df)