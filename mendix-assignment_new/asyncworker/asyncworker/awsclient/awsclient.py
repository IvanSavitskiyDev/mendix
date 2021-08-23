import boto3
from asyncworker.awsclient.settings import AWS_ACCESS_KEY, AWS_SECRET_ACCESS_KEY, AWS_HOST, AWS_PORT


class AWSClient:

    def __init__(self):
        self.access_key = AWS_ACCESS_KEY
        self.secret_access_key = AWS_SECRET_ACCESS_KEY
        self.url = f'http://{AWS_HOST}:{AWS_PORT}'

    def connect(self):
        return boto3.resource(
            's3',
            endpoint_url=self.url, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_access_key
        )

    def client(self):
        return boto3.client(
            's3',
            endpoint_url=self.url, aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_access_key
        )
