# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Get the current Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write("Choose the fruits you want in your custom Smoothie!")

# Text input for customer name
name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_order)

# Get fruit options from Snowflake table
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col("FRUIT_NAME"))

# Convert Snowflake dataframe to list
fruit_options = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Multiselect widget with max 5 fruits
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# If ingredients are selected, build the order
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
                        values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered, " + name_on_order + "!", icon="✅") 

# New section to display SmoothieFruit nutrition information
import requests

smoothiefroot_response = requests.get(
    "https://my.smoothiefroot.com/api/fruit/watermelon"
)

st.text(smoothiefroot_response.json()) 

sf_df = st.dataframe(
    data=smoothiefroot_response.json(),
    use_container_width=True
)
