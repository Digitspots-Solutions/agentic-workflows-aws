FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim
WORKDIR /app

# All environment variables in one layer
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    AWS_REGION=us-east-1 \
    AWS_DEFAULT_REGION=us-east-1



COPY requirements.txt requirements.txt
# Install from requirements file
RUN uv pip install -r requirements.txt




RUN uv pip install aws-opentelemetry-distro==0.12.2


# Signal that this is running in Docker for host binding logic
ENV DOCKER_CONTAINER=1

# Copy entire project BEFORE switching to non-root user (respecting .dockerignore)
COPY . .

# Create non-root user
RUN useradd -m -u 1000 bedrock_agentcore

# Set proper permissions for all files
RUN chown -R bedrock_agentcore:bedrock_agentcore /app && \
    chmod -R 755 /app && \
    find /app -type f -name "*.py" -exec chmod 644 {} \;

USER bedrock_agentcore

EXPOSE 9000
EXPOSE 8000
EXPOSE 8080

# Use the full module path

CMD ["opentelemetry-instrument", "python", "-m", "lautech_agentcore"]
