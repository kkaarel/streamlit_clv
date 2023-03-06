import pandas as pd
import streamlit as st
import numpy as np

##


# Load the data into a DataFrame
#data is from here https://www.kaggle.com/datasets/mashlyn/online-retail-ii-uci
df = pd.read_csv('./data/online_retail_II.csv')

#This is for bad quality data, there are zeros in customer id, like in real data
df['Customer ID'] = df['Customer ID'].fillna(0)
df['Customer ID'] = df['Customer ID'].replace([np.inf, -np.inf], 0)
df['Customer ID'] = df['Customer ID'].astype(int)

df = df[(df['Customer ID'] != 0) & (df['Customer ID'].notnull())]

#InvoiceDate to a data format 

df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# Calculate the total amount spent by each customer
total_amount_spent = df.groupby('Customer ID')['Quantity', 'Price'].apply(lambda x: (x['Quantity'] * x['Price']).sum()).reset_index(name='total_amount_spent')
#change customer id to a whole number

# Calculate the number of purchases made by each customer
num_purchases = df.groupby('Customer ID')['Invoice'].nunique().reset_index(name='num_purchases')

# Merge the total amount spent and number of purchases DataFrames
customer_data = pd.merge(total_amount_spent, num_purchases, on='Customer ID')


# Calculate the average purchase value for each customer
customer_data['avg_purchase_value'] = customer_data['total_amount_spent'] / customer_data['num_purchases']


# Calculate the average customer lifespan in days
customer_lifespan = df.groupby('Customer ID')['InvoiceDate'].apply(lambda x: (x.max() - x.min()).days).reset_index(name='customer_lifespan')


# Merge the customer lifespan data into the customer data DataFrame
customer_data = pd.merge(customer_data, customer_lifespan, on='Customer ID')

def format_metric(number):
    if number >= 1000000:
        return f'{number/1000000:.1f} M'
    elif number >= 10000:
        return f'{number/10000:.1f} K'
    else:
        return f'{number:.0f}'

st.title("Marketing tool")
# Custmers, Total spent, avegra purchase
col1, col2, col3 = st.columns(3)

col1.metric(label = "Customers",
 value = (customer_data['Customer ID'].nunique()),
)

col2.metric(label = "Avergae purchase value",
 value = (format_metric( (customer_data['total_amount_spent'].sum()) / (customer_data['Customer ID'].nunique()))),
)


col3.metric(label = "Avergae Customer Lifetime in days",
 value = (round((customer_data['customer_lifespan'].sum()) / (customer_data['Customer ID'].nunique()))),
)


#select your marketin cost 
marketing_cost = st.number_input('Total marketing costs', value=10000)

#select your number of customer

num_new_customers = st.number_input('Number of new customers', value=2000)

# Calculate the customer acquisition cost
st.write('Customer acquisition cost', marketing_cost / marketing_cost)

discount_rate = st.number_input('Discount amount', value=0.9)
# Calculate the customer lifetime value

customer_data['customer_lifetime_value'] = (customer_data['avg_purchase_value'] * customer_data['customer_lifespan']) / (1 + discount_rate) - marketing_cost / marketing_cost


st.table(customer_data)