mkdir "./deploy"
robocopy ./control ./deploy /e
pscp -r -pw $RPI_PASS ./deploy easternspork@192.168.1.146:/home/easternspork/