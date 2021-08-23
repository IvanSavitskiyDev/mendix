import logging
import tempfile
from celery.result import AsyncResult
from celery.states import UNREADY_STATES, EXCEPTION_STATES

from aiohttp import web

from marshmallow import ValidationError
import botocore

from asyncworker.tasks import merge_s3_files
from asyncworker.awsclient.awsclient import AWSClient
from ..serializers import DateRangeSerializer, DownloadIdSerializer


logger = logging.getLogger(__name__)


async def initiate(request):
    """This function is called when a POST request is made to /initiate.

    According to the assignment the expected POST input is:
    {
        "start_date": "<date in ISO8601 format>",
        "end_date": "<date in ISO8601 format>"
    }
    For example:
    {
        "start_date": "2021-01-01",
        "end_date": "2021-01-01"
    }
s
    The function should initiate the merging of files on S3 with names between
    the given dates. The actual merging should be offloaded to the async
    executor service.

    The return data is a download ID that the /download endpoint digests:
    {
        "download_id": "<id>"
    }
    For example:
    {
        "download_id": "b0952099-3536-4ea0-a613-98509f4087cd"
    }
    """
    # get data from request
    data = await request.json()

    # try to serialize it
    try:
        result = DateRangeSerializer().load(data)

    except ValidationError as err:
        logger.info(f" Validation error {err}")
        return web.HTTPBadRequest(reason='Validation error', text=str(err))

    # convert dates
    result['start_date'] = result['start_date'].strftime("%Y-%m-%d")
    result['end_date'] = result['end_date'].strftime("%Y-%m-%d")

    # run merge task
    task_result = merge_s3_files.delay(result)

    # catch missing date parameters in the bucket
    if task_result is None:
        return web.HTTPBadRequest(reason='Validation error', text='No files satisfying the request dates')

    logger.info("Task result is %s", task_result)
    return web.json_response({"download_id": str(task_result)})


async def download(request):
    """This function is called when a GET request is made to /download.
    According to the assignment this endpoint accepts the dowload ID as a URL
    parameter and returns the merged file for download if the merging is done.
    If the merging is not done yet, the appropriate HTTP code is returned, so
    the calling client can continue polling.
    """
    # get download_id from request
    download_id = request.match_info['download_id']

    # try to serialize download_id
    try:
        serialized_data = DownloadIdSerializer().load(data={'download_id': download_id})
        serialized_uuid = str(serialized_data['download_id'])
        serialized_filename = str(serialized_data['download_id']) + '.log'

    except ValidationError as err:
        logger.info(f" Validation error {err}")
        return web.HTTPBadRequest(reason='Validation error', text=str(err))

    # create s3 connection
    s3_connect = AWSClient().connect()

    # check celery task status
    task_state = AsyncResult(serialized_uuid).state

    if task_state in UNREADY_STATES:
        logger.info(f"Merge not yet complete, current status {task_state}")
        return web.json_response({"result": f"Merge not yet complete, current status {task_state}"})

    elif task_state in EXCEPTION_STATES:
        logger.exception(f"An error occurred while merging, current status {task_state}")
        return web.json_response({"result": f"An error occurred while merging, current status {task_state}"})

    # try to get current file and put it in response
    try:
        fd, path = tempfile.mkstemp()
        s3_connect.Bucket('results').download_file(serialized_filename, path)
        response = web.FileResponse(path=path, status=200, headers={
            'Content-Disposition': f'attrachment;filename={serialized_filename}'
      })
        response.content_type = 'application/octet-stream'
        return response

    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return web.HTTPNotFound()
        else:
            return web.HTTPBadRequest()


async def hello(request):
    """This function is called when a GET request is made to /hello.

    Just a dummy function mainly as an example used for the tests.
    """
    return web.json_response({"hello": "world!"})
