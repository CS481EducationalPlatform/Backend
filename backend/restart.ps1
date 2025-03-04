docker-compose down --volumes
Remove-Item -Path "logs/debug.log" -Force
docker-compose up --build