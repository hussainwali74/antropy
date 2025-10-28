FROM python:3.14-slim

# INSTALL uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /app

# install the app deps
WORKDIR /app

RUN uv sync --frozen --no-cache

# run the app

CMD ["/app/.venv/bin/fastapi", "run", "main.py", "--port", "80", "--host", "0.0.0.0"]
