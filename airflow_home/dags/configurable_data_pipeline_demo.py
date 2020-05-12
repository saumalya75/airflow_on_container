"""
Code that goes along with the Airflow located at:
http://airflow.readthedocs.org/en/latest/tutorial.html
"""
from airflow import DAG
from airflow.models import Variable
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.sensors import CustomS3Sensor
from airflow.operators import CustomFileProcessingOperator
from pathlib import Path
from datetime import datetime, timedelta
import json, traceback, sys, os, pprint


try:
    CONFIG_FILE_NAME = "dag_configuration_demo.json"
    CONFIG_DB_KEY = "configurable_data_pipeline_demo_config"

    config_file = Path(__file__).with_name(CONFIG_FILE_NAME)
    with config_file.open() as config_data:
        pipeline_config = json.loads(config_data.read())
    
    def _say_hello(account, file_name):
        print(f'Saying Hello from {file_name} file of {account} account!')

    def _get_timedelta(unit, value):
        if unit.upper() == "DAYS":
            return timedelta(days=value)
        if unit.upper() == "MONTHS":
            return timedelta(months=value)
        if unit.upper() == "YEARS":
            return timedelta(years=value)
        if unit.upper() == "HOURS":
            return timedelta(hours=value)
        if unit.upper() == "MINUTES":
            return timedelta(minutes=value)
        if unit.upper() == "SECONDS":
            return timedelta(seconds=value)
except Exception as e:
    print("Something went wrong while reading the dag configuration: " + str(e))
    print("~" * 100)
    traceback.print_exc(file=sys.stdout)
    print("~" * 100)

try:
    dag_config = pipeline_config['dag']
    if dag_config['schedule_interval_unit'] and dag_config['schedule_interval_val']:
        dag_config['schedule_interval'] = _get_timedelta(
            dag_config['schedule_interval_unit']
            , dag_config['schedule_interval_val']
        )
        del(dag_config['schedule_interval_unit'])
        del(dag_config['schedule_interval_val'])
    else:
        dag_config['schedule_interval'] = _get_timedelta('days', 1)

    default_args = pipeline_config['dag']['default_args']
    default_args = default_args
    default_args['start_date'] = datetime(
        default_args['start_date']['year'],
        default_args['start_date']['month'],
        default_args['start_date']['day']
    )
    if default_args['retry_delay_unit'] and default_args['retry_delay_val']:
        default_args['retry_delay'] = _get_timedelta(
            default_args['retry_delay_unit']
            , default_args['retry_delay_val']
        )
        del(default_args['retry_delay_unit'])
        del(default_args['retry_delay_val'])
    else:
        default_args['retry_delay'] = _get_timedelta('seconds', 30)
except Exception as e:
    print("Something went wrong while refactoring the dag configuration: " + str(e))
    print("Please ensure proper structure is maintained in configuration files.")
    print("~" * 100)
    traceback.print_exc(file=sys.stdout)
    print("~" * 100)

# default_args = {
#     "owner": "saumalya",
#     "depends_on_past": False,
#     "start_date": datetime(2020, 5, 8),
#     "email": ["digi.hogwarts.2020@gmail.com"],
#     "email_on_failure": False,
#     "email_on_retry": False,
#     "retries": 1,
#     "retry_delay": timedelta(minutes=1)
# }

try:
    config = Variable.setdefault(
        CONFIG_DB_KEY
        , json.loads(json.dumps(dag_config, default=str))
        , deserialize_json=True
    )
except Exception as e:
    print("Something went wrong while trying to set default variables during run time: " + str(e))
    print("~" * 100)
    traceback.print_exc(file=sys.stdout)
    print("~" * 100)

with DAG(**dag_config) as dag:
    # Declare pipeline start and end task
    start_task = DummyOperator(task_id='pipeline_start')
    end_task = DummyOperator(task_id='pipeline_end')

    for account_details in pipeline_config['task_details']['accounts']:
        #Declare Account Start and End Task
        if account_details['runable']:
            acct_start_task = DummyOperator(task_id=account_details['account_id'] + '_start')
            acct_start_task.set_upstream(start_task)
            acct_end_task = DummyOperator(task_id=account_details['account_id'] + '_end')
            for file_details in account_details['files']:
                if file_details['runable']:
                    minio_sensor = CustomS3Sensor(
                        task_id=file_details['file_id'] + "_minio_sensor"
                        , poke_interval=10
                        , retry_delay=timedelta(seconds=25)
                        , xcom_task_id_key=file_details['file_id'] + "_minio_sensor_xcom_key"
                        , refresh_xcom=True
                        , conn_type="minio"
                        , endpoint_url="http://minio:9000"
                        , bucket_name="airflow"
                        , identifier=file_details['trigger_prefix'] + "/" + file_details['trigger_identifier'] + datetime.now().strftime("%Y%m%d") + ".txt"
                        , wildcard_match=False
                        , dag=dag
                    )

                    s3_sensor = CustomS3Sensor(
                        task_id=file_details['file_id'] + "_s3_sensor"
                        , poke_interval=10
                        , retry_delay=timedelta(seconds=25)
                        , xcom_task_id_key=file_details['file_id'] + "_s3_sensor_xcom_key"
                        , refresh_xcom=False
                        , conn_type="aws"
                        , wildcard_match=False
                        , from_xcom=True
                        , xcom_source_task_id=file_details['file_id'] + "_minio_sensor"
                        , xcom_key=file_details['file_id'] + "_minio_sensor_xcom_key"
                        , dag=dag
                    )

                    data_processor = CustomFileProcessingOperator(
                        task_id=file_details['file_id'] + "_data_processor"
                        , xcom_task_id_key=file_details['file_id'] + "_data_processor_xcom_key"
                        , xcom_source_task_id=file_details['file_id'] + "_minio_sensor"
                        , xcom_key=file_details['file_id'] + "_minio_sensor_xcom_key"
                        , source_bed_type="aws"
                        , source_conn_id="aws_default"
                        , dag=dag
                    )

                    minio_sensor.set_upstream(acct_start_task)
                    s3_sensor.set_upstream(minio_sensor)
                    data_processor.set_upstream(s3_sensor)
                    acct_end_task.set_upstream(data_processor)
            end_task.set_upstream(acct_end_task)



