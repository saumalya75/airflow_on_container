from airflow.sensors.base_sensor_operator import BaseSensorOperator
from hooks.custom_s3_minio_hook import CustomS3MinioHook
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException
import json, traceback, sys

def _trigger_file_to_xcom(hook, key, bucket, task_instance, task_key):
    source_file_details = hook.read_key(key, bucket)
    if source_file_details:
        source_file_details_json = json.loads(source_file_details)
        for key in source_file_details_json:
            task_instance.xcom_push(
                key=task_key + '__' + key
                , value = source_file_details_json[key]
                # , task_ids = task_key
            )
        print("Source file details are pushed to XCOM.")
    else:
        print("No data present in source file. Nothing to push to XCOM.")

class CustomS3Sensor(object):
    def __new__(cls, from_xcom = False, *args, **kwargs):
        if from_xcom:
            return S3SensorFromXcom(*args, **kwargs)
        else:
            return S3SensorFromProvidedValue(*args, **kwargs)


class S3SensorFromProvidedValue(BaseSensorOperator):

    @apply_defaults
    def __init__(self,
        conn_type:str = '',
        endpoint_url:str = 'http://127.0.0.1:9000',
        bucket_name:str = 'default_bucket',
        identifier:str = 'default_ind',
        wildcard_match:bool = False,
        aws_conn_id='',
        verify=None,
        remove_on_detection=True,
        xcom_task_id_key:str = '1234',
        refresh_xcom:bool = True,
        *args,
        **kwargs
    ):
        self.conn_type = conn_type
        self.endpoint_url = endpoint_url
        self.bucket_name = bucket_name
        self.identifier = identifier
        self.wildcard_match = wildcard_match
        self.aws_conn_id = aws_conn_id
        self.verify = verify
        self.remove_on_detection = remove_on_detection
        self.xcom_task_id_key = xcom_task_id_key
        self.refresh_xcom = refresh_xcom
        super().__init__(*args, **kwargs)

    def poke(self, context):
        try:
            """
                This sensor reads the trigger file.
                It also puts the values provided in trigger file on xcomm.
            """
            task_instance = context['task_instance']
            hook = CustomS3MinioHook(conn_type=self.conn_type, endpoint_url=self.endpoint_url, aws_conn_id=self.aws_conn_id, verify=self.verify)
            print(f"Connection Type: {self.conn_type}")
            print("Check for :" + self.bucket_name + "/" + self.identifier)
            if self.wildcard_match:
                presence = hook.check_for_wildcard_key(self.identifier, self.bucket_name)
                if presence and self.refresh_xcom:
                    trigger_file = hook.get_wildcard_key(self.identifier, self.bucket_name)
                    if type(trigger_file) == list:
                        trigger_file = trigger_file[0].key
                    else:
                        trigger_file = trigger_file.key
                    _trigger_file_to_xcom(
                        hook=hook
                        , key=trigger_file
                        , bucket=self.bucket_name
                        , task_instance=task_instance
                        , task_key=self.xcom_task_id_key
                    )
                return presence
            else:
                presence = hook.check_for_key(self.identifier, self.bucket_name)
                if presence and self.refresh_xcom:
                    _trigger_file_to_xcom(
                        hook=hook
                        , key=trigger_file
                        , bucket=self.bucket_name
                        , task_instance=task_instance
                        , task_key=self.xcom_task_id_key
                    )
                return presence
        except Exception as e:
            print("Something went wrong while poking: " + str(e))
            print('~' * 100)
            print(traceback.print_exc(file=sys.stdout))
            print('~' * 100)
            raise

class S3SensorFromXcom(S3SensorFromProvidedValue):

    @apply_defaults
    def __init__(self, xcom_source_task_id='', xcom_key='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not xcom_key or not xcom_source_task_id:
            raise AirflowException("Providing XCOM source task name and key is mandatory for while ``from_xcom`` is set to True.")
        self.xcom_task_id = xcom_source_task_id
        self.xcom_key = xcom_key

    @staticmethod
    def _extract_xcom_data(task_instance, xcom_task_id, xcom_key):
        return task_instance.xcom_pull(xcom_task_id, key=xcom_key)

    def poke(self, context):
        try:
            """
                This sensor reads the trigger file.
                It also puts the values provided in trigger file on xcomm.
            """
            task_instance = context['task_instance']
            self.bucket_name = self._extract_xcom_data(task_instance, self.xcom_task_id, self.xcom_key + "__bucket")
            self.identifier = self._extract_xcom_data(task_instance, self.xcom_task_id, self.xcom_key + "__prefix") \
                + '/' \
                + self._extract_xcom_data(task_instance, self.xcom_task_id, self.xcom_key + "__key")
            hook = CustomS3MinioHook(conn_type=self.conn_type, endpoint_url=self.endpoint_url, aws_conn_id=self.aws_conn_id, verify=self.verify)
            print(f"Connection Type: {self.conn_type}")
            print("Check for :" + self.bucket_name + "/" + self.identifier)
            if self.wildcard_match:
                presence = hook.check_for_wildcard_key(self.identifier, self.bucket_name)
                if presence and self.refresh_xcom:
                    trigger_file = hook.get_wildcard_key(self.identifier, self.bucket_name)
                    if type(trigger_file) == list:
                        trigger_file = trigger_file[0].key
                    else:
                        trigger_file = trigger_file.key
                    _trigger_file_to_xcom(
                        hook=hook
                        , key=trigger_file
                        , bucket=self.bucket_name
                        , task_instance=task_instance
                        , task_key=self.xcom_task_id_key
                    )
                return presence
            else:
                presence = hook.check_for_key(self.identifier, self.bucket_name)
                if presence and self.refresh_xcom:
                    _trigger_file_to_xcom(
                        hook=hook
                        , key=trigger_file
                        , bucket=self.bucket_name
                        , task_instance=task_instance
                        , task_key=self.xcom_task_id_key
                    )
                return presence
        except Exception as e:
            print("Something went wrong while poking: " + str(e))
            print('~' * 100)
            print(traceback.print_exc(file=sys.stdout))
            print('~' * 100)
            raise