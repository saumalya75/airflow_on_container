import boto3
import os
import re

from airflow.exceptions import AirflowException
from airflow.hooks.S3_hook import S3Hook


class S3Creds(object):
    """S3 credentials"""
    def __init__(self, aws_access_key_id, aws_secret_access_key, endpoint_url='', region_name='us-east-1'):
        try:
            self.aws_access_key_id = aws_access_key_id
            self.aws_secret_access_key = aws_secret_access_key
            self.endpoint_url = endpoint_url
            self.region_name = region_name
        except Exception as e:
            raise AirflowException("Error while instantiating S3Creds object: " + str(e))

def _get_credentials_from_env(conn_type):
    try:
        if conn_type.upper() == 'MINIO':
            if (not os.getenv('MINIO_ACCESS_KEY', '')) or (not os.getenv('MINIO_SECRET_KEY', '')):
                raise AirflowException("To use minio type connection MINIO_ACCESS_KEY, MINIO_SECRET_KEY and MINIO_ENDPOINT_URL must be provided while creating the hook object or have to be declared in environment!")
            return S3Creds(
                aws_access_key_id = os.getenv('MINIO_ACCESS_KEY', ''),
                aws_secret_access_key = os.getenv('MINIO_SECRET_KEY', ''),
                endpoint_url = os.getenv('MINIO_ENDPOINT_URL', 'http://localhost:9000')
            )
        else:
            if (not os.getenv('AWS_ACCESS_KEY_ID', '')) or (not os.getenv('AWS_SECRET_ACCESS_KEY', '')):
                raise AirflowException("To use S3 hook without airflow connection AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be declared in environment!")
            return S3Creds(
                aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID', ''),
                aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY', '')
            )
    except Exception as e:
        raise AirflowException("Error while getting credentials from environment: " + str(e))


class CustomS3MinioHook(S3Hook):
    """Decision inerface between minio and AWS type connection."""
    def __new__(cls, *args, **kwargs):
        try:
            if kwargs.get('conn_type', '').upper() == 'MINIO':
                return CustomMinioHook(*args, **kwargs)
            elif not kwargs.get('aws_conn_id', ''):
                return CustomS3Hook(*args, **kwargs)
            else:
                return S3Hook(
                    aws_conn_id = kwargs.get('aws_conn_id', ''),
                    verify = kwargs.get('verify', '')
                    # region_name = kwargs.get('region_name', ''),
                    # config = kwargs.get('config', '')
                )
        except Exception as e:
            raise AirflowException("Error while creating s3Hook(CustomMinioHook or CustomS3Hook) object: " + str(e))


class CustomS3Hook(S3Hook):
    """Overridding some properties of s3 hook to support credentials from environment for AWS type connection."""
    def __init__(self, *args, **kwargs):
        try:
            s3_creds = _get_credentials_from_env('aws')
            self.aws_access_key_id = kwargs.get('aws_access_key_id', s3_creds.aws_access_key_id)
            self.aws_secret_access_key = kwargs.get('aws_secret_access_key', s3_creds.aws_secret_access_key)
            self.region_name = s3_creds.region_name = kwargs.get('region_name', 'us-east-1')
        except Exception as e:
            raise AirflowException("Error while initialising CustomS3Hook object: " + str(e))
    
    def get_client_type(self, client_type='s3'):
        try:
            return boto3.session.Session().client(
                client_type,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
        except Exception as e:
            raise AirflowException("Error while AWS type S3 client using environment variables: " + str(e))
    
    def get_resource_type(self, resource_type='s3'):
        try:
            return boto3.session.Session().resource(
                resource_type,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                region_name=self.region_name
            )
        except Exception as e:
            raise AirflowException("Error while AWS type resource using environment variables: " + str(e))


class CustomMinioHook(S3Hook):
    """Overridding some properties of s3 hook to support minio type connection."""
    def __init__(self, *args, **kwargs):
        try:
            s3_creds = _get_credentials_from_env('minio')
            self.aws_access_key_id = kwargs.get('aws_access_key_id', s3_creds.aws_access_key_id)
            self.aws_secret_access_key = kwargs.get('aws_secret_access_key', s3_creds.aws_secret_access_key)
            self.endpoint_url = kwargs.get('endpoint_url', s3_creds.endpoint_url)
        except Exception as e:
            raise AirflowException("Error while initializing CustomMinioHook object: " + str(e))

    @staticmethod
    def get_compiled_wildcard(wildcard):
        try:
            return re.compile(wildcard)
        except Exception as e:
            raise AirflowException("Error while compilling provided wildcard: " + str(e))

    def get_client_type(self, client_type='s3'):
        try:
            return boto3.session.Session().client(
                client_type,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                endpoint_url = self.endpoint_url
            )
        except Exception as e:
            raise AirflowException("Error while MINIO type client using environment variables: " + str(e))
    
    def get_resource_type(self, resource_type='s3'):
        try:
            return boto3.session.Session().resource(
                resource_type,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                endpoint_url = self.endpoint_url
            )
        except Exception as e:
            raise AirflowException("Error while MINIO type resource using environment variables: " + str(e))
    