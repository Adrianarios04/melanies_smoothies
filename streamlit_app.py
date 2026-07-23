# Import Python packages
import streamlit as st
import requests
import pandas as pd
from snowflake.snowpark.functions import col

# Get the current Snowflake session
cnx = st.connection("snowflake")
session = cnx.session()

# App title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")

st.write("Choose the fruits you want in your custom Smoothie!")

# Text input for customer name
name_on_order = st.text_input("Name on Smoothie:")

st.write("The name on your Smoothie will be:", name_on_order)

# Get fruit options from the Snowflake table
my_dataframe = session.table(
    "SMOOTHIES.PUBLIC.FRUIT_OPTIONS"
).select(
    col("FRUIT_NAME"),
    col("SEARCH_ON")
)

# These lines are only for testing, so they remain commented
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

# Convert the Snowpark DataFrame to a Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Convert the fruit-name column to a list
fruit_options = pd_df["FRUIT_NAME"].tolist()

# Multiselect widget with a maximum of five fruits
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# Build and display the order
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # Find the value recognized by the nutrition API
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        # Testing message — keep commented
        # st.write(
        #     "The search value for ",
        #     fruit_chosen,
        #     " is ",
        #     search_on,
        #     "."
        # )

        st.subheader(fruit_chosen + " Nutrition Information")

        # Request the selected fruit's nutrition information
        smoothiefroot_response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    # Submit-order button
    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        my_insert_stmt = """
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS
                (INGREDIENTS, NAME_ON_ORDER)
            VALUES (?, ?)
        """

        session.sql(
            my_insert_stmt,
            params=[
                ingredients_string.strip(),
                name_on_order
            ]
        ).collect()

        st.success(
            "Your Smoothie is ordered, " + name_on_order + "!",
            icon="✅"
        )

