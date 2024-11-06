# mlv2

## Dev

- `pdm install`
- `docker compose -f ./docker/docker-compose-dev.yml --env-file ./.env.dev up -d`

## Test

- `docker compose --env-file ./.env.test up -d --force-recreate --build`

## Deploy

- `gcloud config set project PROJECT_ID`
- `gcloud builds submit --config cloudbuild-dev.yml .`
