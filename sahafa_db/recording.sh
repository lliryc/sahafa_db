#!/bin/bash

# Default values
url=""
duration=""
country_code=""
city_code=""
radio_station_id=""
program_id=""
start_timestamp=""
output_folder=""

# Parse named parameters
while getopts u:d:c:y:r:p:s:o: flag
do
    case "${flag}" in
        u) url=${OPTARG};;
        d) duration=${OPTARG};;
        c) country_code=${OPTARG};;
        y) city_code=${OPTARG};;
        r) radio_station_id=${OPTARG};;
        p) program_id=${OPTARG};;
        s) start_timestamp=${OPTARG};;
        o) output_folder=${OPTARG};;
    esac
done

# Check if all required parameters are provided
if [ -z "$url" ] || [ -z "$duration" ] || [ -z "$country_code" ] || [ -z "$city_code" ] || [ -z "$radio_station_id" ] || [ -z "$program_id" ] || [ -z "$start_timestamp" ] || [ -z "$output_folder" ]; then
    echo "Usage: $0 -u <url> -d <duration> -c <country_code> -y <city_code> -r <radio_station_id> -p <program_id> -s <start_timestamp> -o <output_folder>"
    exit 1
fi

# Ensure the output folder exists
mkdir -p "$output_folder"

# Run ffmpeg command with provided parameters
ffmpeg -i "$url" -reconnect_at_eof 1 -reconnect_streamed 1 -reconnect_delay_max 120 -icy 1 -err_detect ignore_err -acodec libopus -cutoff 12000 -ab 32k -compression_level 10 -t "$duration" -frame_duration 60 -f segment -segment_time 05:0.0 -segment_atclocktime 1 -strftime 1 "${output_folder}/${country_code}_${city_code}_${radio_station_id}_${program_id}_${start_timestamp}_%Y%m%d%H%M%S%z.opus"