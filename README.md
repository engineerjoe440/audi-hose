<img src="https://raw.githubusercontent.com/engineerjoe440/audi-hose/main/logo/audihose-logo.png" width="250" alt="logo" align="right">

# audi-hose

Connecting audiences to the creators they love with easy audio.

## Installation

AudiHose is built to be run in a [Docker](https://docs.docker.com/get-started/overview/)
[container](https://www.redhat.com/en/topics/containers/whats-a-linux-container).
The easiest way to get AudiHose started is to use a [docker-compose](https://docs.docker.com/compose/)
configuration to define the parameters for your application to use. Here's an
example:

```yaml
version: "3.9"

# AudiHose Example Configuration
services:
  audihose:
    image: ghcr.io/engineerjoe440/audi-hose:main
    ports:
      - 8082:80
    restart: unless-stopped
    environment:
      # Optional Configuration Parameters
      # - APPLICATION_SITE_URL: https://audihose.example.com
      # - APPLICATION_STORAGE_PATH: ./recordings
      # - SMTP_SERVER: smtp.example.com
      # - SMTP_PORT: 587
      # - SMTP_STARTTLS: true
      # - SMTP_USERNAME: audihoseemail
      # - SMTP_PASSWORD: <insert your smtp password here>
      # - SMTP_FROM_ADDRESS: audihose@example.com
      # - NTFY_SERVER: https://ntfy.example.com
      # - NTFY_TOPIC: audihose
      # - NTFY_TOKEN: <insert your token here>
    volumes:
      - ./config:/server/config
      - ./recordings:/server/recordings
```

## Setup

:warning: TODO

---

## Development

### Linking frontend and backend (React/FastAPI)

Developing Audi-Hose should be relatively simple. It falls into a few general
steps. Install the `npm` dependencies, build the frontend, install the `python`
dependencies, then run the backend.

With some minor modifications made to the FastAPI configuration,
[this guide on using Flask and React](https://blog.learningdollars.com/2019/11/29/how-to-serve-a-reactapp-with-a-flask-server/)
was used to develop the link between the two ecosystems.

### Installing Frontend (`npm`) Dependencies

1. `cd` to the `frontend/` folder.
2. Run the command: `yarn install` (requires [yarn](https://classic.yarnpkg.com/lang/en/docs/install/))

### Building Frontend

1. `cd` to the `frontend/` folder.
2. Run the command `yarn build`. This will generate all of the Javascript/CSS
files needed in the `backend/audihose/static/react/` folder, and the `index.html`
in `backend/audihose/templates/`.

### Installing Backend (`python`) Dependencies

1. Create a Python Virtual Environment with `python3 -m venv venv`.
2. Activate the virtual environment.
3. Run the command `pip install -r backend/requirements.txt`

### Run the Application

1. `cd` to the `backend/` folder.
2. Run the command: `uvicorn audihose.main:app --reload --host 0.0.0.0`. This
will expose the application on all interfaces on the computer running the app.
This will allow you to test the app from other local devices.

