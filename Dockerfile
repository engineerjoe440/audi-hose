# Build the frontend
FROM node:latest AS uibuilder

WORKDIR /uibuild

COPY ./frontend /uibuild

RUN yarn install
RUN yarn build

# Runtime image
FROM python:3.12

WORKDIR /server

# Install backend dependencies
COPY ./requirements.txt /server/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /server/requirements.txt

# Copy backend source
COPY ./audihose /server/audihose

# Copy built frontend assets into FastAPI expected locations
COPY --from=uibuilder /audihose/static/react /server/audihose/static/react
COPY --from=uibuilder /audihose/templates/index.html /server/audihose/templates/index.html

CMD ["uvicorn", "audihose.main:app", "--host", "0.0.0.0", "--port", "80", "--forwarded-allow-ips", "*"]

