FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install .
CMD ["sahafa_db"]
