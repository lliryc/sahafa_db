from prefect import flow, task
from typing import List
import httpx
import boto3  # Added boto3 import
from prefect_aws import AwsCredentials
import os
import json
from datetime import datetime
from prefect.context import get_run_context
import subprocess
import threading
import tempfile
from datetime import timedelta
from dirwatcher import DirWatcher
from watchdog.events import FileSystemEvent
import time
import uuid

aws_credentials_block = AwsCredentials.load("minio-local2")


def stream_output(pipe, output_type):
    for line in iter(pipe.readline, b''):
        if line == "":
          continue
        print(f"{output_type}: {line.strip()}")
    pipe.close()

@task(name="Recording task")
def recording_task(url: str, duration_minutes: int, 
                   country_code: str, city_code: str, 
                   radio_station_id: str, program_id: str, 
                   start_timestamp: datetime, output_folder: str):
    """
    """
    # create time delta from duration minutes
    duration = timedelta(minutes=duration_minutes)
    duration_str = str(duration)

    output_file_prefix = f"{country_code}_{city_code}_{radio_station_id}_{program_id}_{start_timestamp.strftime('%Y%m%d%H%M%S%z')}"
    # ffmpeg command
    ffmpeg_command = [
        "ffmpeg", "-i", url,
        "-reconnect_at_eof", "1",
        "-reconnect_streamed", "1",
        "-reconnect_delay_max", "120",
        "-icy", "1",
        "-err_detect", "ignore_err",
        "-acodec", "libopus",
        "-cutoff", "12000",
        "-ab", "32k",
        "-compression_level", "10",
        "-t", duration_str,
        "-frame_duration", "60",
        "-f", "segment",
        "-segment_time", "05:00.0",
        "-segment_atclocktime", "1",
        "-strftime", "1",
        f"{output_file_prefix}_%Y%m%d%H%M%S%z.opus"
    ]
    
    print(f"Executing command: {' '.join(ffmpeg_command)}")

    process = subprocess.Popen(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=output_folder)

    # Create threads to read stdout and stderr
    stdout_thread = threading.Thread(target=stream_output, args=(process.stdout, "STDOUT"))
    stderr_thread = threading.Thread(target=stream_output, args=(process.stderr, "STDERR"))

    # Start the threads
    stdout_thread.start()
    stderr_thread.start()

    # Wait for the process to complete
    process.wait()

    # Wait for the threads to complete
    stdout_thread.join()
    stderr_thread.join()

    if process.returncode != 0:
        print("ffmpeg failed.")
    else:
        print("ffmpeg succeeded.")

current_file = ''
        
def on_created(event: FileSystemEvent, country_code: str, city_code: str, media_id: str, program_id: str, datetime_tz: str):
  global current_file  # Declare current_file as global
  print(f"Event: {event}")
  
  if (current_file != '' and event is not None and event.src_path is not None and event.src_path.endswith(".opus") and current_file != event.src_path) \
    or (event is None and current_file != ''):    
    # compose folder path
    month_folder = datetime_tz[:6]
    day_folder = datetime_tz[:8]
    folder_path = f"{country_code}/{city_code}/{media_id}/{program_id}/{month_folder}/{day_folder}/{datetime_tz}"
    # extract filename with  from event.src_path
    filename = os.path.basename(current_file)
    # compose full path
    full_path = f"{folder_path}/{filename}"
    s3_client = boto3.client('s3',
        aws_access_key_id=aws_credentials_block.aws_access_key_id,
        aws_secret_access_key=aws_credentials_block.aws_secret_access_key.get_secret_value())
        
    with open(current_file, "rb") as f:  
      s3_client.put_object(
          Bucket='recordings',
          Key=full_path,  # Save file in 'az' folder
          Body=f.read() # binary data from .opus file    
      )
    
    print(f"File {filename} has been saved to {full_path} in 'recordings' bucket.")
  
  
  if event.src_path is not None and event.src_path.endswith(".opus"):
    current_file = event.src_path 
  else:
    current_file = ''

@flow(name="Test flow")
def test_flow():
    print(f"{os.getcwd()}")

@flow(name="Recording flow")
def recording_flow(path: str, program_key: str): 
    """
    """
    meta_path = os.path.join(path, "meta.json")
    guide_path = os.path.join(path, "guide.json")
    
    #get country code 
    path = path.rstrip("/")
    cnt_cty_pair = path.split("/")[-1]
    [country_code, city_code]= cnt_cty_pair.split("-")
    
    #get the meta
    with open(meta_path, "r") as f:
        meta = json.load(f)
        
    # get guide
    with open(guide_path, "r") as f:
        guide = json.load(f)
    
    # get the url from the meta
    source_url = meta.get("url")
    if not source_url:
        raise ValueError(f"Source url not found in the meta")
    
    # get the program_key from the guide
    program = guide.get(program_key)
    if not program:
        raise ValueError(f"Program key {program_key} not found in the guide")
      
    media_id = program.get("media_id")
    if not media_id:
        raise ValueError(f"Media id not found in the program")
    
    program_id = program.get("program_id")
    if not program_id:
        raise ValueError(f"Program id not found in the program")
    
    duration_minutes = program.get("duration_minutes")
    if not duration_minutes:
        raise ValueError(f"Duration minutes not found in the program")
      
    flow_run_context = get_run_context()
    flow_run = flow_run_context.flow_run
    expected_start = flow_run.expected_start_time
    
    # Create a temporary directory for the output
    # extract YYYYMM from expected_start
    yyyymm = expected_start.strftime("%Y%m")
    yyyymmdd = expected_start.strftime("%Y%m%d")
    # full string with timezone
    datetime_tz = expected_start.strftime("%Y%m%d%H%M%S%z")
    
    with tempfile.TemporaryDirectory() as output_folder:
        # Start the watcher in a separate process
        with DirWatcher(output_folder, on_created=lambda event: on_created(event, country_code, city_code, media_id, program_id, datetime_tz)) as watcher:
            # Call the recording task with the temporary output folder
            recording_task(source_url, duration_minutes, country_code, city_code, media_id, program_id, expected_start, output_folder)
            time.sleep(3)
        on_created(None, country_code, city_code, media_id, program_id, datetime_tz)
          


# run the flow!
if __name__=="__main__":
    recording_flow("media_guides/ae/ae-az/ad-radio", "ad-radio-studio1")