FROM python:3.9.20-slim
COPY --from=ghcr.io/astral-sh/uv:0.5.10 /uv /uvx /bin/

RUN apt-get update && apt-get install -y curl

WORKDIR /app
COPY . .
RUN uv sync --frozen --no-dev
CMD ["uv", "run", "streamlit", "run", "streamlit_app.py", "--server.port", "8601"]
