import os
import numpy as np
import pandas as pd
import streamlit as st
import snowflake.connector

from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()


# ============================================================
# Configuration
# ============================================================

EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-001"
)

CHAT_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

NEW_REVIEWS = 100
TOP_K = 5

CACHE_FILE = "review_embeddings.parquet"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=GEMINI_API_KEY)


# ============================================================
# Snowflake
# ============================================================

def read_reviews_from_snowflake():

    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

    query = f"""
        SELECT
            REVIEW_ID,
            CITY,
            RATING,
            COMMENT
        FROM FOOD_DELIVERY.STAGING.STG_REVIEWS
        SAMPLE ({NEW_REVIEWS} ROWS)
    """

    df = conn.cursor().execute(query).fetch_pandas_all()

    conn.close()

    df.columns = [col.lower() for col in df.columns]

    return df


# ============================================================
# Gemini Embeddings
# ============================================================

def embed(texts):

    embeddings = []

    for text in texts:

        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
        )

        embeddings.append(response.embeddings[0].values)

    return embeddings


# ============================================================
# Load reviews + create embeddings
# ============================================================

@st.cache_data()
def load_reviews():

    if os.path.exists(CACHE_FILE):
        return pd.read_parquet(CACHE_FILE)

    df = read_reviews_from_snowflake()

    df["embedding"] = embed(
        df["comment"].fillna("").tolist()
    )

    df.to_parquet(CACHE_FILE)

    return df


# ============================================================
# Streamlit UI
# ============================================================

st.title("Chat with your Food Delivery App Reviews")

st.caption(
    f"Searching {NEW_REVIEWS} reviews, "
    f"answering with {CHAT_MODEL}"
)


# ============================================================
# Cosine similarity
# ============================================================

def cosine_similarity(vec_a, vec_b):

    return np.dot(vec_a, vec_b) / (
        np.linalg.norm(vec_a) *
        np.linalg.norm(vec_b)
    )


# ============================================================
# Find relevant reviews
# ============================================================

def find_similar_reviews(question, df):

    question_vector = embed([question])[0]

    scores = []

    for review_vector in df["embedding"]:

        scores.append(
            cosine_similarity(
                question_vector,
                review_vector
            )
        )

    df = df.copy()

    df["score"] = scores

    return df.nlargest(TOP_K, "score")


# ============================================================
# Gemini RAG generation
# ============================================================

def ask_llm(question, top_reviews):

    context = ""

    for _, row in top_reviews.iterrows():

        context += (
            f"({row['city']}, "
            f"{row['rating']} stars) "
            f"{row['comment']}\n"
        )

    system_prompt = """
You are an AI assistant for a food-delivery analytics platform.

Answer ONLY using the customer reviews provided in the context.

Be concise and factual.

If the provided reviews do not contain enough information
to answer the question, say that the available reviews
do not contain enough information.

Do not invent facts.
"""

    user_prompt = f"""
Question:
{question}

Customer Reviews:
{context}
"""

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2,
        ),
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return response.text


# ============================================================
# Application
# ============================================================

review_df = load_reviews()

question = st.text_input(
    "Ask a question about your reviews:",
    placeholder=(
        "e.g. What are the most common complaints "
        "about delivery?"
    ),
)


if question:

    top_reviews = find_similar_reviews(
        question,
        review_df
    )

    answer = ask_llm(
        question,
        top_reviews
    )

    st.markdown("**Answer:**")

    st.write(answer)

    with st.expander(
        "Reviews used to build this answer"
    ):

        st.dataframe(
            top_reviews[
                ["city", "rating", "comment"]
            ],
            hide_index=True,
        )