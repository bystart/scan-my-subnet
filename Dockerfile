FROM docker.1ms.run/python:3.11-slim-bookworm

WORKDIR /app


RUN sed -i \
      -e 's|http://deb.debian.org|https://mirrors.aliyun.com|g' \
      -e 's|http://security.debian.org|https://mirrors.aliyun.com|g' \
      /etc/apt/sources.list.d/debian.sources

RUN apt-get update && \
    apt-get install -y --no-install-recommends iputils-ping && \
    rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.doubanio.com/simple/

COPY app/ ./app/
COPY static/ ./static/

RUN mkdir -p /app/data

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
