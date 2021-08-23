import logging
from datetime import datetime
from time import sleep

from botocore.client import ClientError

from asyncworker.awsclient.awsclient import AWSClient
from asyncworker.celery import app

logger = logging.getLogger(__name__)


@app.task
def merge_s3_files(result):
    """Async task to download files from S3, merge them and upload the result.

    The lines in the merged file should be ordered.
    """
    # create s3 connection
    s3_connect = AWSClient().connect()

    my_bucket = s3_connect.Bucket("logs")
    start_date = result["start_date"]
    end_date = result["end_date"]
    file_names = [i.key for i in my_bucket.objects.all()]

    # sort files in list
    file_names.sort()

    # check border dates
    if (
        datetime.strptime(start_date, "%Y-%m-%d").date()
        < datetime.strptime(file_names[0][:10], "%Y-%m-%d").date()
    ):
        logger.exception("No files satisfying the request dates")

        return None

    if (
        datetime.strptime(end_date, "%Y-%m-%d").date()
        > datetime.strptime(file_names[-1][:10], "%Y-%m-%d").date()
    ):
        logger.exception("No files satisfying the request dates")

        return None

    # find the first and last files in our selection
    start_file_index = [
        index for index, file in enumerate(file_names) if start_date in file
    ][0]
    end_file_index = [
        index for index, file in enumerate(file_names) if end_date in file
    ][-1]

    # get list of right files
    result_files_list = [
        file for file in list(file_names)[start_file_index : end_file_index + 1]
    ]

    # create s3 client
    s3_client = AWSClient().client()

    # start collect oll lines
    output = []
    for file in result_files_list:
        body = s3_client.get_object(Bucket="logs", Key=file)["Body"].iter_lines()
        for line in body:
            # # for testing purpose to slow down creation - uncomment next line
            # sleep(0.1)
            output.append(line.decode("utf-8"))

    # sort result
    output = sorted(output, key=lambda x: x[:19])

    # result_filename the same as task_id for check task state via /download/{download_id}
    result_filename = str(merge_s3_files.request.id)
    outputbody = "\t".join(output) + "\n"

    # guarantee the presence of a 'results' bucket
    try:
        s3_connect.meta.client.head_bucket(Bucket="results")
    except ClientError:
        s3_connect.create_bucket(Bucket="results")

    # put object
    s3_client.put_object(
        Bucket="results", Key=f"{result_filename}.log", Body=outputbody
    )
    return result_filename
