FROM python:3.12-slim
ENV PYTHONUNBUFFERED True

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r  requirements.txt

ENV APP_HOME /root
WORKDIR $APP_HOME
COPY /app $APP_HOME/app

EXPOSE 8080
# main is in src/main.py. Run with fastapi production server
CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]

