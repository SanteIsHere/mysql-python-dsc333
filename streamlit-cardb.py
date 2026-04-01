# Streamlit application that interfaces with cars database
# running locally in MySQL

import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import pandas as pd
import os
import matplotlib.pyplot as plt

load_dotenv()


def connect_to_db():
    # DB_PASSWORD must be defined in .env.
    pw = os.environ.get("DB_PASSWORD")

    # Connect to DB
    mydb = mysql.connector.connect(
        host="localhost", user="root", password=pw, database="cardb"
    )

    # Return database connection and cursor object for executing queries
    return mydb, mydb.cursor()


def close_connection(db, cursor):
    cursor.close()
    db.close()


def get_user_selections():
    with st.form(key="my_form"):
        retail_range = st.slider("Retail price ($)", 0, 100000, (20000, 50000))
        min_mpg = st.slider(
            "Minimum fuel efficiency (highway - mpg)", 0, 55, 20)
        car_type = st.radio(
            "Car type", ("Sedan", "Wagon", "SUV", "Sports Car"))
        submitted = st.form_submit_button(label="Process")
        # Add a text input for make of car
        car_make = st.text_input("Enter the make of the car, e.g 'Toyota'")
        car_type_avg_gas = st.selectbox(
            "Car type", ("Sedan", "Wagon", "SUV", "Sports Car")
        )

        if submitted:
            # Use user provided inputs
            return retail_range, min_mpg, car_type, car_make, car_type_avg_gas
        else:
            # Send default values
            return ((20000, 50000), 20, "Sedan", "Toyota", "Sedan")


def exec_query(retail_range, min_mpg, car_type, car_make, cursor):
    # SQL query is broken down into multiple f strings for readibility.
    # f strings are concatenated automatically because of parenthesization.
    min_p, max_p = retail_range
    query = (
        f"SELECT Name, `Retail Price`, `Highway Miles Per Gallon`, Type"
        f" FROM cars WHERE `Retail Price` BETWEEN {min_p} AND {max_p}"
        f" AND `Highway Miles Per Gallon` > {min_mpg}"
        f" AND Type = '{car_type}'"
        f" AND Name LIKE '%{car_make}%'"
    )
    print(query)
    # Execute the SQL query
    cursor.execute(query)

    # Put results in a DataFrame
    columns = [desc[0] for desc in cursor.description]
    results_df = pd.DataFrame(cursor.fetchall(), columns=columns)
    return results_df


def query_avg_gas(car_make, type_sel, cursor):
    # Write the query using input car type
    query = (
        f"SELECT SUBSTRING_INDEX(Name, ' ', 1) AS Make, "
        f"AVG(`Highway Miles Per Gallon`) AS Avg_MPG "
        f"FROM cars "
        f"WHERE Type = '{type_sel}' "
        f"GROUP BY Make"
    )
    # Output query
    print(f"Avg. gas query: '{query}'")

    # Execute the query
    cursor.execute(query)

    # Put results in a DataFrame
    columns = [desc[0] for desc in cursor.description]
    results_df = pd.DataFrame(cursor.fetchall(), columns=columns)
    return results_df


def main():
    st.title("Car database")
    db, cursor = connect_to_db()
    # Add new input car_make. And car type selection for avg. gas
    retail_range, min_mpg, car_type, car_make, car_type_avg_gas = get_user_selections()
    results = exec_query(retail_range, min_mpg, car_type, car_make, cursor)
    avg_gas = query_avg_gas(car_make, car_type_avg_gas, cursor)
    st.markdown("---")
    st.subheader("Matches")
    st.dataframe(results, width=900, height=300)

    # --- Matplotlib Graph Generation ---
    # Create the figure and axis
    fig, ax = plt.subplots()

    # Generate horizontal bar graph (Make on Y, Avg_MPG on X)
    ax.barh(
        avg_gas["Make"],
        avg_gas["Avg_MPG"],
        edgecolor=["orange", "green", "red"],
        color="white",
    )

    # Set the x-axis label to match the sketch
    ax.set_xlabel("Average mpg (highway)")

    # Render the plot in Streamlit
    st.pyplot(fig)

    close_connection(db, cursor)


if __name__ == "__main__":
    main()
