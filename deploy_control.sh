
# Create the deploy directory
mkdir -p ./deploy

# Copy all files and directories from control to deploy, excluding the build folder
rsync -av --exclude='build' ./control/ ./deploy/

# Securely copy the deploy directory to the remote Raspberry Pi
scp -r ./deploy easternspork@192.168.1.146:/home/easternspork/