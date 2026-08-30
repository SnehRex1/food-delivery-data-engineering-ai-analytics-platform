import os
import json

import pandas as pd
import streamlit as st
import snowflake.connector

from google import genai
from google.genai import types
from dotenv import load_dotenv


# ============================================================
# Load Environment Variables
# ============================================================

load_dotenv()


# ============================================================
# Configuration
# ============================================================

MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


FORBIDDEN_WORDS = [
    "drop",
    "delete",
    "truncate",
    "alter",
    "update",
    "insert",
    "create",
    "replace",
    "grant",
    "revoke",
]


EXAMPLE_QUESTIONS = [
    "Top 10 cities by GMV",
    "Which cuisine has the most orders?",
    "Average delivery time by city, worst first",
    "What is the cancel rate by payment method?",
    "Top 10 restaurants by revenue",
    "Which food items generate the most revenue?",
]


# ============================================================
# Gemini Client
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# Snowflake Schema
# ============================================================

SCHEMA = """
Tables available in the FOOD_DELIVERY.MARTS schema.

Use bare table names only.
Do NOT use database or schema prefixes.

------------------------------------------------------------
FCT_ORDERS
------------------------------------------------------------

FCT_ORDERS(
    order_id,
    order_date,
    customer_id,
    restaurant_id,
    city,
    cuisine,
    payment_method,
    order_status,
    is_delivered,
    sales_amount,
    discount,
    delivery_fee,
    gst,
    customer_rating,
    delivery_time_min
)


------------------------------------------------------------
FACT_ORDER_ITEMS
------------------------------------------------------------

FACT_ORDER_ITEMS(
    order_item_id,
    order_id,
    food_id,
    quantity,
    unit_price,
    item_amount
)


------------------------------------------------------------
DIM_CUSTOMER
------------------------------------------------------------

DIM_CUSTOMER(
    customer_id,
    customer_name,
    age,
    age_segment,
    gender,
    city
)


------------------------------------------------------------
DIM_DATE
------------------------------------------------------------

DIM_DATE(
    date_day,
    year,
    month,
    month_name,
    day_name,
    is_weekend
)


------------------------------------------------------------
DIM_FOOD
------------------------------------------------------------

DIM_FOOD(
    food_id,
    food_name,
    category,
    price
)


------------------------------------------------------------
DIM_RESTAURANTS
------------------------------------------------------------

DIM_RESTAURANTS(
    restaurant_id,
    restaurant_name,
    city,
    cuisine,
    rating,
    cost_for_two
)


------------------------------------------------------------
MART_DAILY_CITY_REVENUE
------------------------------------------------------------

MART_DAILY_CITY_REVENUNE(
    order_date,
    city,
    orders,
    cancel_rate,
    gmv,
    aov
)


------------------------------------------------------------
MART_RESTAURANT_PERFORMANCE
------------------------------------------------------------

MART_RESTAURANT_PERFORMANCE(
    restaurant_id,
    restaurant_name,
    city,
    cuisine,
    orders,
    revenue,
    avg_customer_rating,
    cancel_rate
)


------------------------------------------------------------
MART_DELIVERY_SLA
------------------------------------------------------------

MART_DELIVERY_SLA(
    city,
    order_hour,
    delivered_orders,
    p50_delivery_min,
    late_rate
)


IMPORTANT BUSINESS RULES:

1. GMV means delivered revenue.

2. Prefer MART_DAILY_CITY_REVENUNE when answering
   city-level GMV, revenue, order, AOV, or cancellation
   questions.

3. Prefer MART_RESTAURANT_PERFORMANCE when answering
   restaurant-level performance questions.

4. Prefer MART_DELIVERY_SLA when answering delivery-time,
   SLA, late-delivery, or delivery-performance questions.

5. Use FCT_ORDERS when detailed order-level analysis is
   required.

6. Use FACT_ORDER_ITEMS when analyzing individual food items,
   quantities, prices, or order-item revenue.

7. Use DIM_CUSTOMER for customer demographic information.

8. Use DIM_RESTAURANTS for restaurant attributes.

9. Use DIM_FOOD for food/menu attributes.

10. Use DIM_DATE for calendar/date-related analysis.

11. Do not invent tables or columns.

12. Use Snowflake SQL syntax.
"""


# ============================================================
# Gemini System Prompt
# ============================================================

SYSTEM_PROMPT = f"""
You are an expert Snowflake SQL analyst for a food-delivery
data platform.

Your task is to convert the user's natural-language question
into ONE SQL query.

The SQL will be executed directly against Snowflake.

RULES:

1. Generate SELECT queries only.

2. WITH queries are allowed as long as they ultimately
   produce a SELECT result.

3. Never modify, delete, insert, update, create, alter,
   replace, grant, or revoke anything.

4. Use bare table names only.

   Correct:
       FROM FCT_ORDERS

   Incorrect:
       FROM FOOD_DELIVERY.MARTS.FCT_ORDERS

5. Do not use database or schema prefixes.

6. Tables are available in the FOOD_DELIVERY.MARTS schema.

7. Add LIMIT 100 or less unless the question specifically
   asks for a single aggregate value.

8. Use appropriate aggregation such as SUM, AVG, COUNT,
   COUNT DISTINCT, etc.

9. Use ORDER BY when the question asks for rankings such as
   top, highest, lowest, worst, best, etc.

10. Use the appropriate MART_ table whenever it directly
    answers the question.

11. Do not invent tables or columns.

12. Return ONLY valid JSON in exactly this format:

{{
    "sql": "your SQL query here"
}}

Available schema and business definitions:

{SCHEMA}
"""


# ============================================================
# Snowflake Connection
# ============================================================

@st.cache_resource
def get_connection():

    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database="FOOD_DELIVERY",
        schema="MARTS",
        role="DBT_ROLE",
    )


# ============================================================
# Generate SQL using Gemini
# ============================================================

def generate_sql(question):

    response = client.models.generate_content(
        model=MODEL,
        contents=question,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            temperature=0,
            response_mime_type="application/json",
        ),
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty response."
        )

    answer = json.loads(response.text)

    if "sql" not in answer:
        raise ValueError(
            "Gemini response does not contain a 'sql' field."
        )

    sql = answer["sql"]

    # Remove accidental database/schema prefixes
    sql = (
        sql
        .replace(
            "FOOD_DELIVERY.MARTS.",
            ""
        )
        .replace(
            "FOOD_DELIVERY.",
            ""
        )
        .replace(
            "ZOMATO.MARTS.",
            ""
        )
        .replace(
            "ZOMATO.",
            ""
        )
    )

    return sql.strip().rstrip(";")


# ============================================================
# SQL Safety Check
# ============================================================

def is_safe(sql):

    lowered = sql.lower().strip()

    # --------------------------------------------------------
    # Only SELECT / WITH queries
    # --------------------------------------------------------

    if not (
        lowered.startswith("select")
        or lowered.startswith("with")
    ):
        return False

    # --------------------------------------------------------
    # Block destructive/modifying SQL commands
    # --------------------------------------------------------

    for word in FORBIDDEN_WORDS:

        if word in lowered:
            return False

    return True


# ============================================================
# Execute Query
# ============================================================

def run_query(sql):

    conn = get_connection()

    cursor = conn.cursor()

    try:

        return cursor.execute(
            sql
        ).fetch_pandas_all()

    finally:

        cursor.close()


# ============================================================
# Streamlit UI
# ============================================================

st.title(
    "Chat with your Food Delivery Data"
)

st.caption(
    f"Ask in English → {MODEL} generates SQL → "
    "Snowflake executes it"
)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.header(
        "Example Questions"
    )

    for q in EXAMPLE_QUESTIONS:

        st.markdown(
            f"- {q}"
        )


# ============================================================
# Question Input
# ============================================================

question = st.text_input(
    "Enter your question here",
    placeholder=(
        "e.g. Top 10 restaurants by revenue in Bangalore"
    ),
)


# ============================================================
# Process Question
# ============================================================

if question:

    try:

        # ----------------------------------------------------
        # Generate SQL
        # ----------------------------------------------------

        sql = generate_sql(
            question
        )

        st.subheader(
            "Generated SQL"
        )

        st.code(
            sql,
            language="sql"
        )


        # ----------------------------------------------------
        # Safety Check
        # ----------------------------------------------------

        if not is_safe(sql):

            st.error(
                "The generated SQL is not safe to run. "
                "Only SELECT queries are allowed."
            )

        else:

            # ------------------------------------------------
            # Execute SQL
            # ------------------------------------------------

            df = run_query(
                sql
            )


            # ------------------------------------------------
            # Display Result
            # ------------------------------------------------

            st.success(
                f"{len(df)} rows returned"
            )

            st.dataframe(
                df,
                hide_index=True
            )


            # ------------------------------------------------
            # Simple Chart
            # ------------------------------------------------

            if (
                len(df.columns) == 2
                and pd.api.types.is_numeric_dtype(
                    df.iloc[:, 1]
                )
            ):

                st.subheader(
                    "Visualization"
                )

                st.bar_chart(
                    df,
                    x=df.columns[0],
                    y=df.columns[1]
                )


    except json.JSONDecodeError:

        st.error(
            "Gemini returned an invalid JSON response."
        )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )