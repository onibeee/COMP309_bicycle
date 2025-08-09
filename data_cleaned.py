######################################################################
# In this script:
# - drop unwanted columns
# - fill missing value
# - observe STATUS values (esp UNKNOWN)
#   (UNKNOWN likely related to PROPERY - FOUND => neither stolen or recovered, dropped)
######################################################################

import pandas as pd
import numpy as np
pd.set_option('display.max_columns',30) # set the maximum width
# Load the dataset in a dataframe object 
df = pd.read_csv('C:\COMP309\group\Bicycle_Thefts_Open_Data_Aug.csv')
# Explore the data check the column values
df.shape
df.dtypes
print(df.columns.values)
print (df.head())
print (df.info())
# Check for missing values
print(df.isnull().sum())
#or
print(len(df) - df.count())

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


#####################################################
# drop columns: REPORT_, OBJECTID, EVENT_UNIQUE_ID
#####################################################
df_cleaned = df.copy()  # preserve original df

report_cols = [col for col in df.columns if col.startswith('REPORT_')]
df_cleaned.drop(columns=report_cols, errors='ignore', inplace=True)
df_cleaned.drop(columns=['OBJECTID', 'EVENT_UNIQUE_ID', 'x', 'y', 'NEIGHBOURHOOD_158', 'NEIGHBOURHOOD_140'], errors='ignore', inplace=True)
df_cleaned.dtypes


"""
Explore again
"""

############################
# fill missing value
############################
#Check for missing values for included columns
print(df_cleaned.isnull().sum())
#or
print(len(df_cleaned) - df.count())
print(df_cleaned['BIKE_MAKE'].unique())
print(df_cleaned['BIKE_MODEL'].unique())
print(df_cleaned['BIKE_COLOUR'].unique())

print(df_cleaned['BIKE_MAKE'].value_counts())
print(df_cleaned['BIKE_MODEL'].value_counts())
print(df_cleaned['BIKE_COLOUR'].value_counts())
print(df_cleaned['HOOD_158'].value_counts())

# fill with median() for numeric fields
df_cleaned['BIKE_SPEED'].fillna(df_cleaned['BIKE_SPEED'].median(),inplace=True)
df_cleaned.isnull().sum()

df_cleaned['BIKE_COST'].fillna(df_cleaned['BIKE_COST'].median(),inplace=True)
df_cleaned.isnull().sum()

# fill with "UNKNOWN" for others
missing_categorical_cols = ['BIKE_MAKE', 'BIKE_MODEL', 'BIKE_COLOUR']
df_cleaned[missing_categorical_cols] = df_cleaned[missing_categorical_cols].fillna("UNKNOWN")
df_cleaned.isnull().sum()



#################################
# Process categorical columns
#################################
# assess categorical columns
categorical_cols = df_cleaned.select_dtypes(include='object').columns
print(categorical_cols)
for col in categorical_cols:
    unique_count = df_cleaned[col].nunique()
    print(f"{col}: {unique_count}")

# drop 'OCC_DATE', 'LOCATION_TYPE', 'BIKE_MODEL', 'HOOD_140'
drop_cat_cols = ['OCC_DATE', 'LOCATION_TYPE', 'BIKE_MODEL', 'HOOD_140']
df_encoded = df_cleaned.drop(columns=drop_cat_cols)

# keep top 20 and the remaining label as 'other' then one-hot
import pandas as pd

def group_top_n_categories(df, column_name, n=20, other_label='other'):
    top_n = df[column_name].value_counts().nlargest(n).index
    df[column_name] = df[column_name].where(df[column_name].isin(top_n), other_label)
    return df

df_encoded.dtypes
df_encoded = group_top_n_categories(df_encoded, 'PRIMARY_OFFENCE', n=20)   
df_encoded = group_top_n_categories(df_encoded, 'BIKE_MAKE', n=20)   
df_encoded = group_top_n_categories(df_encoded, 'BIKE_COLOUR', n=20)   
df_encoded = group_top_n_categories(df_encoded, 'HOOD_158', n=20)

# expand column values
encode_cols = ['PRIMARY_OFFENCE','OCC_MONTH','OCC_DOW','DIVISION','PREMISES_TYPE','BIKE_MAKE','BIKE_TYPE','BIKE_COLOUR','HOOD_158']
for col in encode_cols:
    cat_list='var'+'_'+col
    print(cat_list)         
    # creat columns based on values
    # cat_list = pd.get_dummies(data_rita_b['job'], prefix='job')
    cat_list = pd.get_dummies(df_encoded[col], prefix=col)
    df_tmp = df_encoded.join(cat_list)
    df_encoded = df_tmp

df_encoded.drop(columns=encode_cols, inplace=True)
df_encoded.head()

#################################
# assess STATUS column
#################################
df_encoded['STATUS'].value_counts()
# create a field to indicate if the record is unknown
# then observre the what UNKNOWN mean
df_encoded = df_encoded.copy()
df_encoded['IS_UNKNOWN'] = (df_encoded['STATUS'] == 'UNKNOWN').astype(int)
# correlate again after encoding
#status_corr_before_encoded = df_cleaned.corr(numeric_only=True)['IS_UNKNOWN'].sort_values(ascending=False)
#print(status_corr_before_encoded)

status_corr_after_encoded = df_encoded.corr(numeric_only=True)['IS_UNKNOWN'].sort_values(ascending=False)
print(status_corr_after_encoded)

df_encoded = df_encoded[df_encoded['STATUS'] != 'UNKNOWN']
