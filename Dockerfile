FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src/ src/

RUN pip install --no-cache-dir .

EXPOSE 8000

WORKDIR /app

CMD ["python", "-c", "from mcp_sweden.server import mcp; mcp.run(transport='http', host='0.0.0.0', port=8000)"]
