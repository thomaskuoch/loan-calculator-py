FROM python:3.10.14-slim
COPY --from=ghcr.io/astral-sh/uv:0.8.22 /uv /uvx /bin/

WORKDIR /app
COPY . .
RUN uv sync --frozen --no-dev
CMD ["uv", "run", "streamlit", "run", "streamlit_app.py", "--server.port", "8601"]
