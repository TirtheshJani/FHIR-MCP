FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uv
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN uv pip install --system .
COPY examples/synthea_patients.json.gz /data/synthea.json.gz
EXPOSE 8000
CMD ["python", "-m", "fhir_mcp", "--transport", "sse", "--port", "8000", "--bundle", "/data/synthea.json.gz"]
