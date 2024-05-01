
docker-compose -f ./artifacts/docker-compose.yaml up -d

sleep 5
python3 api.py

