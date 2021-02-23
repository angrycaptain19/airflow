import os
import requests
import json
import psycopg2 as pg
from datetime import date

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

def initialLoadStores():
    dbconnect = None
    try:
        dbconnect = pg.connect(
            database=os.environ['POSTGRESQLDATABASE'],
            user=os.environ['POSTGRESQLUSERNAME'],
            password=os.environ['POSTGRESQLPASSWORD'],
            host=os.environ['POSTGRESQLHOST'],
            port=os.environ['POSTGRESQLPORT']
        )

        cursor = dbconnect.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stores (
                id SERIAL,
                storenr INTEGER UNIQUE,
                close_date text,
                address varchar(255),
                warehousenr INTEGER,
                PRIMARY KEY (id)
            );

            TRUNCATE TABLE stores CASCADE;
        """
        )

        dbconnect.commit()

        with open("/opt/bitnami/airflow/dags/git-airflow/data/data/initial_load/stores.csv", 'r', encoding='unicode_escape') as reader:
            next(reader, None)
            for row in reader:
                cursor.execute("""
                    INSERT INTO stores(storenr, close_date, address, warehousenr)
                    VALUES ('{}', '{}', '{}', '{}')
                """.format(
                row.split(";")[0],
                row.split(";")[1],
                row.split(";")[2],
                row.split(";")[3])
                )
        dbconnect.commit()

        cursor.close()
    except (Exception, pg.DatabaseError) as error:
        print(error)

    finally:
        if dbconnect is not None:
            dbconnect.close()
            print('Connection to the database is closed')

def initialLoadEvents():
    dbconnect = None
    try:
        dbconnect = pg.connect(
            database=os.environ['POSTGRESQLDATABASE'],
            user=os.environ['POSTGRESQLUSERNAME'],
            password=os.environ['POSTGRESQLPASSWORD'],
            host=os.environ['POSTGRESQLHOST'],
            port=os.environ['POSTGRESQLPORT']
        )

        cursor = dbconnect.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL,
                storenr INTEGER,
                date text,
                customers INTEGER,
                PRIMARY KEY (id),
                FOREIGN KEY (storenr) REFERENCES stores (storenr)
            );

            TRUNCATE TABLE events CASCADE;
        """
        )

        dbconnect.commit()

        with open("/opt/bitnami/airflow/dags/git-airflow/data/data/initial_load/customer_number.csv", 'r', encoding='unicode_escape') as reader:
            next(reader, None)
            for row in reader:
                cursor.execute("""
                    INSERT INTO events(storenr, date, customers)
                    VALUES ('{}', '{}', '{}')
                """.format(
                row.split(",")[0],
                row.split(",")[1],
                row.split(",")[2])
                )
        dbconnect.commit()

        cursor.close()
    except (Exception, pg.DatabaseError) as error:
        print(error)

    finally:
        if dbconnect is not None:
            dbconnect.close()
            print('Connection to the database is closed')


default_args = {
    "owner": "airflow",
    "start_date": datetime.today() - timedelta(days=1)
}
dag = DAG(
    "initial_load_dag",
    default_args=default_args,
    schedule_interval=None,
    )
initialLoadStores = PythonOperator(
    task_id="initial_load_stores",
    python_callable=initialLoadStores,
    dag=dag,
    )
initialLoadEvents = PythonOperator(
    task_id="initial_load_events",
    python_callable=initialLoadEvents,
    dag=dag,
    )

initialLoadStores >> initialLoadEvents
