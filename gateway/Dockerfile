FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt
COPY app.py /app/gateway.py

EXPOSE 8080
CMD ["python","-m","uvicorn","gateway:app","--host","0.0.0.0","--port","8080"]

