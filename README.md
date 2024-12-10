# mlv2

## Dev

- `uv sync`
- `uv pip install -e .`
- Restart VSCode for `pytest` to work
- Docker up
  - `docker compose -f ./docker/docker-compose-dev.yml --env-file ./.env.dev up -d --force-recreate`
- Docker down (with volume)
  - `docker compose -f ./docker/docker-compose-dev.yml --env-file ./.env.dev down -v`

## Test

- `docker compose -f ./docker-compose-test.yml --env-file ./.env.test up -d --force-recreate --build`

## Deploy

- `gcloud config set project PROJECT_ID`
- `gcloud builds submit --config cloudbuild-dev.yml .`
