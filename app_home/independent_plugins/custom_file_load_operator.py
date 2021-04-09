from airflow.models.baseoperator import BaseOperator
from hooks.custom_s3_minio_hook import CustomS3MinioHook
from airflow.utils.decorators import apply_defaults
# Demo application integration imports
import myscript as ms
from myscript.run import check
from myscript import run as r


class CustomFileProcessingOperator(BaseOperator):
    """
        Currently this operator is not doing anything practically.
        We are just taking count of the source file and putting it on XCOM or demo purpose.
        But anyone can add logic to based on hteir reqirement. The configurations are structure will be similar.
    """

    @apply_defaults
    def __init__(self
        , xcom_task_id_key:str = 'data_processor_key'
        , xcom_source_task_id:str = ''
        , xcom_key:str = ''
        , source_bed_type:str = 'aws'
        , source_endpoint_url:str = ''
        , source_conn_id:str = 'aws_default'
        , source_verify:str = ''
        , *args
        , **kwargs
    ):
        super().__init__(*args, **kwargs)
        if (not len(xcom_key)) or (not len(xcom_source_task_id)):
            raise AirflowException("Providing XCOM source task name and key is mandatory for for this processing operator.")
        self.xcom_task_id_key = xcom_task_id_key
        self.xcom_task_id = xcom_source_task_id
        self.xcom_key = xcom_key
        self.source_bed_type = source_bed_type
        self.source_endpoint_url=source_endpoint_url
        self.source_conn_id=source_conn_id
        self.source_verify=source_verify

    @staticmethod
    def _extract_xcom_data(task_instance, xcom_task_id, xcom_key):
        return task_instance.xcom_pull(xcom_task_id, key=xcom_key)

    def execute(self, context):
        # Demo application integration prints
        print("*" * 50)
        print(check)
        print(r.check)
        print(ms.check)
        print('~' * 50)
        """File processing is implemented"""
        source_hook = CustomS3MinioHook(
            conn_type=self.source_bed_type
            , endpoint_url=self.source_endpoint_url
            , aws_conn_id=self.source_conn_id
            , verify=self.source_verify
        )
        print(f"Source Connection Type: {self.source_bed_type}")

        task_instance = context['task_instance']
        self.source_bucket_name = self._extract_xcom_data(task_instance, self.xcom_task_id, self.xcom_key + "__bucket")
        self.source_key = self._extract_xcom_data(task_instance, self.xcom_task_id, self.xcom_key + "__prefix") \
            + '/' \
            + self._extract_xcom_data(task_instance, self.xcom_task_id, self.xcom_key + "__key")
        source_data = source_hook.read_key(self.source_key, self.source_bucket_name)
        print(source_data)
        task_instance.xcom_push(
            key=self.xcom_task_id_key + '__row_count'
            , value = len(source_data.splitlines())
        )

        print("Execution complete!")