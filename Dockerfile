FROM python:3.12-slim

WORKDIR /app
COPY ./backend /app/backend
COPY ./frontend /app/frontend
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .

# 對外暴露端口
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

