# Set the base image version as a build argument
ARG PYTHON_BASE=3.12-slim

# Build stage
FROM python:$PYTHON_BASE AS builder

# Install PDM
RUN pip install -U pdm
# Disable update check
ENV PDM_CHECK_UPDATE=false

# Set the working directory and install dependencies into the local packages directory
WORKDIR /app
COPY . .
RUN pdm init -n 
RUN pdm install --prod 
# --no-editable

# Run stage
FROM python:$PYTHON_BASE

# Copy the virtual environment from the build stage
COPY --from=builder /app/.venv/ /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

# Create a non-root user for security
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Set the working directory
WORKDIR /app

# Copy the application source code
COPY --chown=appuser:appuser . .


# Command to run the application using PDM
CMD [ "fastapi", "run", "/app/src/server/main.py", "--port", "8080"]
