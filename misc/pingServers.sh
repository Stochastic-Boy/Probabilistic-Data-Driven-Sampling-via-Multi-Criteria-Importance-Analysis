#!/bin/bash

# Check if at least two command-line arguments are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <start_ip> <end_ip>"
    exit 1
fi

start_ip="$1"
end_ip="$2"

# Validate IP addresses
if ! [[ $start_ip =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Invalid start IP address format."
    exit 1
fi

if ! [[ $end_ip =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "Invalid end IP address format."
    exit 1
fi

# Convert the last octet of start and end IPs to integers
start_octet="${start_ip##*.}"
end_octet="${end_ip##*.}"

# Iterate through the IP range and ping each IP address
for ((i = start_octet; i <= end_octet; i++))
do
    ip="${start_ip%.*}.$i"
    # Use the ping command with a count of 1 and a timeout of 2 seconds
    ping -c 1 -W 2 $ip > /dev/null 2>&1

    # Check the exit status of the ping command
    if [ $? -eq 0 ]; then
        echo "omsv21@$ip:4"
    fi
done
