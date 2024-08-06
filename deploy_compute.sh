# deprecated use deploy.sh

# Create the deploy directory
mkdir -p ./deploy

# Copy all files and directories from compute to deploy, excluding the build folder
rsync -av --exclude='build' ./compute/ ./deploy/

# Securely copy the deploy directory to the remote Raspberry Pi
scp -r ./deploy orangepi@192.168.1.147:/home/orangepi

