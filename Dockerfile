FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/

RUN pip install --no-cache-dir .

EXPOSE 8000

WORKDIR /app/src
CMD ["fastmcp", "run", "mcp_sweden/server.py:mcp", "--transport", "http", "--port", "8000"]
