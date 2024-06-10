import boto3
import os
import datetime
import time
 
group_names = ["<YOUR_CLOUDWATCH_LOG_GROUPS>"]
destination_bucket = "<YOUR_BUCKET_NAME>"
prefix_name = "rds-logs"
scrap_interval = 10

def get_time_duration(intervel):
    current_time = datetime.datetime.now()
    end_date = current_time - datetime.timedelta(days=-1)
    start_date = (current_time - datetime.timedelta(days=0)) - datetime.timedelta(minutes=intervel)

    from_date = int(start_date.timestamp() * 1000)
    to_date = int(end_date.timestamp() * 1000)

    return (from_date, to_date, start_date)


def lambda_handler(event, context):
    response = None
    client = boto3.client('logs')
    from_date, to_date, start_date = get_time_duration(scrap_interval)
    bucket_prefix = os.path.join(prefix_name, start_date.strftime('%Y{0}%m{0}%d').format("-"))

    for group_name in group_names:
        time.sleep(10)
        response = client.create_export_task(
            logGroupName=group_name,
            fromTime=from_date,
            to=to_date,
            destination=destination_bucket,
            destinationPrefix=os.path.join(bucket_prefix, os.path.basename(group_name))
        )
    return response