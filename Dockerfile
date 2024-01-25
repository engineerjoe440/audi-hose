# Build the Frontend
FROM node:latest AS uibuilder

WORKDIR /uibuild

COPY ./frontend /uibuild

RUN yarn install
RUN yarn run build

# Dockerfile for Audi-Hose
FROM python:3.12

WORKDIR /server

COPY ./backend /server

# Copy React Files
COPY --from=uibuilder /backend /server

RUN pip install --no-cache-dir --upgrade -r /server/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--log-config", "log_conf.yml", "--forwarded-allow-ips", "'*'"]

