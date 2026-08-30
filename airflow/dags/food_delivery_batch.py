from datetime import datetime

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.standard.operators.bash import BashOperator


DBT = "/opt/airflow/dbt_venv/bin/dbt"
DBT_PROJECT = "/opt/airflow/dbt/food_delivery_dbt"


COPY_RAW = [
    "USE WAREHOUSE FD_WH",

    "COPY INTO RAW.RESTAURANTS FROM @FD_RAW_STAGE/restaurant/ ON_ERROR = 'CONTINUE'",

    "COPY INTO RAW.USERS FROM @FD_RAW_STAGE/users/ ON_ERROR = 'CONTINUE'",

    "COPY INTO RAW.FOOD FROM @FD_RAW_STAGE/food/ ON_ERROR = 'CONTINUE'",

    "COPY INTO RAW.MENU FROM @FD_RAW_STAGE/menu/ ON_ERROR = 'CONTINUE'",

    "COPY INTO RAW.ORDERS FROM @FD_RAW_STAGE/orders/ ON_ERROR = 'CONTINUE'",

    "COPY INTO RAW.ORDER_ITEMS FROM @FD_RAW_STAGE/order_items/ ON_ERROR = 'CONTINUE'",

    "COPY INTO RAW.REVIEWS FROM @FD_RAW_STAGE/reviews/ ON_ERROR = 'CONTINUE'",
]


with DAG(
    dag_id="food_delivery_batch",
    start_date=datetime(2023, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["food_delivery", "batch", "dbt"],
) as dag:

    reload_raw = SQLExecuteQueryOperator(
        task_id="reload_raw",
        conn_id="snowflake_default",
        sql=COPY_RAW,
        split_statements=True,
        autocommit=True,
    )

    dbt_build_core = BashOperator(
        task_id="dbt_build_core",
        bash_command=f"{DBT} build --project-dir {DBT_PROJECT} --profiles-dir {DBT_PROJECT}",
        
    )
    
    enrich_reviews = BashOperator(
        task_id="enrich_reviews",
        bash_command=f"python /opt/airflow/ai_layer/enrich_reviews.py",
    )

    dbt_build_ai = BashOperator(
        task_id = "dbt_build_ai",
        bash_command=f"{DBT} build --select tag:ai --project-dir {DBT_PROJECT} --profiles-dir {DBT_PROJECT}"
    )

    reload_raw >> dbt_build_core >> enrich_reviews >> dbt_build_ai

