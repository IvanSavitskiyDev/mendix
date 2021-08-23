## MENDIX Test Project

This project includes solving problem of merging and downloading a log file. 
When solving this problem, the logic is as follows:


* Receiving parameters start_date/end_date on 
POST /initial method and validation these params.
* If everything is fine with the parameters, 
run the merge_s3_files celery task.
* Connect to s3, check the occurrences of the sample of dates.
* Create a merge file using the task ID as the name for log file,
 it help us to check celery task sate in /download method.
* In GET /download method check celery task state (PENDING, SUCCESS, etc). 
* Download the result file.

## Usage

### Run docker

```bash
docker-compose build
docker-compose up
```