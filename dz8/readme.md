pip install -r requirements.txt
docker compose up -d
bash client/create_topics.sh
uvicorn main:app --reload --port 8003

python workers/moderation_worker.py

pytest -m "not integration"
pytest -m integration
