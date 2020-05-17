import sys
sys.path.insert(0,"/usr/local/airflow")
sys.path.insert(0,"/usr/local/app")
from airflow.plugins_manager import AirflowPlugin
from sensors.custom_s3_sensor import CustomS3Sensor
from operators.custom_file_load_operator import CustomFileProcessingOperator


# Defining the plugin class
class CustomPlugin(AirflowPlugin):
    name = "custom_plugin"
    sensors = [CustomS3Sensor]
    operators = [CustomFileProcessingOperator]