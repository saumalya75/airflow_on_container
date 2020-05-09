"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.sensors import CustomS3Sensor
from airflow.operators import CustomFileProcessingOperator
from datetime import datetime, timedelta

run_id = datetime.now().strftime('%Y%m%d%H%M%S')
default_args = {
    "owner": "saumalya",
    "depends_on_past": False,
    "start_date": datetime(2020, 5, 8),
    "email": ["digi.hogwarts.2020@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1)
}

dag = DAG(
    "data_pipeline_demo"
    , default_args=default_args
    , schedule_interval=timedelta(1)
)


minio_sensor = CustomS3Sensor(
    task_id="minio_sensor"
    , poke_interval=10
    , retry_delay=timedelta(seconds=25)
    , xcom_task_id_key="minio_sensor_xcom_key"
    , refresh_xcom=True
    , conn_type='minio'
    , endpoint_url='http://minio:9000'
    , bucket_name='airflow'
    , identifier=f'trigger/minio_*_trigger_{datetime.now().strftime("%Y%m%d")}.txt'
    , wildcard_match=True
    , dag=dag
)

s3_sensor = CustomS3Sensor(
    task_id='s3_sensor'
    , poke_interval=10
    , retry_delay=timedelta(seconds=25)
    , xcom_task_id_key="s3_sensor_xcom_key"
    , refresh_xcom=False
    , conn_type='aws'
    , wildcard_match=True
    , from_xcom=True
    , xcom_source_task_id="minio_sensor"
    , xcom_key="minio_sensor_xcom_key"
    , dag=dag
)

data_processor = CustomFileProcessingOperator(
    task_id='data_processor'
    , xcom_task_id_key="data_processor_xcom_key"
    , xcom_source_task_id="minio_sensor"
    , xcom_key="minio_sensor_xcom_key"
    , source_bed_type='aws'
    , source_conn_id='aws_default'
    , dag=dag
)

s3_sensor.set_upstream(minio_sensor)
data_processor.set_upstream(s3_sensor)
