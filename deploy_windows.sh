# should be used in windows systems but i havent bothered to update for windows since i run linux for the most part now

mkdir "./deploy"
robocopy ./control ./deploy /e
pscp -r -pw $RPI_PASS ./deploy easternspork@192.168.1.146:/home/easternspork/