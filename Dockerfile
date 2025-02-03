FROM python:alpine3.8
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt 
EXPOSE 8080
CMD ["python3", "server.py"]