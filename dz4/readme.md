docker compose up -d          # поднимает инфраструктуру
bash infra/create_topics.sh   # создаёт топики
pip install -r requirements.txt  # ставит зависимости
uvicorn app.main:app --reload --port 8000  # запускает API
