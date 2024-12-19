FROM python:3.9.15-slim

RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*  

ADD https://astral.sh/uv/0.5.10/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app
COPY . .
RUN uv sync --frozen --no-dev
CMD ["uv", "run", "streamlit", "run", "streamlit_app.py", "--server.port", "8601"]
