FROM python:3.8.7-slim
VOLUME /golem/input /golem/output
ADD docker/.build/ /golem/entrypoint/
RUN chmod +x /golem/entrypoint/worker.py
WORKDIR /golem/entrypoint