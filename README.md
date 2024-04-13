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
      # - SITE_URL: https://audihose.example.com
```

## Setup

:warning: TODO

---

## Development

### Linking frontend and backend (React/FastAPI):
With some minor modifications made to the FastAPI configuration,
[this guide on using Flask and React](https://blog.learningdollars.com/2019/11/29/how-to-serve-a-reactapp-with-a-flask-server/)
was used to develop the link between the two ecosystems.
