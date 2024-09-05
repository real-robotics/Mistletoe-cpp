#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo ".env file not found!"
    exit 1
fi

# Ensure PASSWORD is set
if [ -z "$PASSWORD" ]; then
    echo "PASSWORD not set in .env file!"
    exit 1
fi

# Define variables
INTERMEDIATE_HOST="10.42.0.1"
FINAL_HOST="192.168.1.100"
INTERMEDIATE_DEST="/home/orangepi"
FINAL_DEST="/home/easternspork"
INTERMEDIATE_USER="orangepi"
FINAL_USER="easternspork"
COMPUTE_FOLDER="compute"
CONTROL_FOLDER="control"
EXCLUDE_FOLDER="build"

# Copy compute folder to the intermediate host
echo "Copying $COMPUTE_FOLDER to $INTERMEDIATE_HOST..."
sshpass -p "$PASSWORD" scp -r "$COMPUTE_FOLDER" "$INTERMEDIATE_USER@$INTERMEDIATE_HOST:$INTERMEDIATE_DEST"

# Check if the copy was successful
if [ $? -ne 0 ]; then
    echo "Failed to copy $COMPUTE_FOLDER to $INTERMEDIATE_HOST"
    exit 1
fi

# Copy control folder to the intermediate host, excluding the build folder
echo "Copying $CONTROL_FOLDER to $INTERMEDIATE_HOST, excluding $EXCLUDE_FOLDER..."
sshpass -p "$PASSWORD" rsync -av --exclude="$EXCLUDE_FOLDER" "$CONTROL_FOLDER/" "$INTERMEDIATE_USER@$INTERMEDIATE_HOST:$INTERMEDIATE_DEST/$CONTROL_FOLDER"

# Check if the copy was successful
if [ $? -ne 0 ]; then
    echo "Failed to copy $CONTROL_FOLDER to $INTERMEDIATE_HOST"
    exit 1
fi

# Copy control folder from the intermediate host to the final destination
echo "Copying $CONTROL_FOLDER from $INTERMEDIATE_HOST to $FINAL_HOST..."
sshpass -p "$PASSWORD" ssh "$INTERMEDIATE_USER@$INTERMEDIATE_HOST" "sshpass -p '$PASSWORD' scp -r $INTERMEDIATE_DEST/$CONTROL_FOLDER $FINAL_USER@$FINAL_HOST:$FINAL_DEST"

# Check if the copy was successful
if [ $? -ne 0 ]; then
    echo "Failed to copy $CONTROL_FOLDER to $FINAL_HOST"
    exit 1
fi

# Delete control folder from the intermediate host
echo "Deleting $CONTROL_FOLDER from $INTERMEDIATE_HOST..."
sshpass -p "$PASSWORD" ssh "$INTERMEDIATE_USER@$INTERMEDIATE_HOST" "rm -rf $INTERMEDIATE_DEST/$CONTROL_FOLDER"

# SSH into the final host and clean and build the project
echo "Building project on $FINAL_HOST..."
sshpass -p "$PASSWORD" ssh "$INTERMEDIATE_USER@$INTERMEDIATE_HOST" "sshpass -p '$PASSWORD' ssh -t $FINAL_USER@$FINAL_HOST 'cd $FINAL_DEST/control; sh build.sh'"

echo "Deployment and build completed successfully."

# Restart services
echo "Restarting services..."
# sshpass -p "$PASSWORD" ssh "$INTERMEDIATE_USER@$INTERMEDIATE_HOST" "sudo -S systemctl restart mistletoe-compute.service"
# sshpass -p "$PASSWORD" ssh "$INTERMEDIATE_USER@$INTERMEDIATE_HOST" "sshpass -p '$PASSWORD' ssh $FINAL_USER@$FINAL_HOST 'sudo -S systemctl restart mistletoe-control.service'"
