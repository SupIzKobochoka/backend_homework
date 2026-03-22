pip install -r requirements.txt  # ставит зависимости
bash infra/create_topics.sh   # создаёт топики
docker compose up -d          # поднимает инфраструктуру
uvicorn main:app --reload --port 8003  # запускает API
