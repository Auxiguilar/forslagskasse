# 1st stage: Install dependencies
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder

WORKDIR /app

ENV UV_PROJECT_ENVIRONMENT=/app/.venv

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project


# 2nd stage: Run the application
FROM python:3.12-slim-bookworm

ARG APP_UID=1000
ARG APP_GID=1000
RUN groupadd --gid "$APP_GID" appuser \
	&& useradd --uid "$APP_UID" --gid appuser --create-home appuser

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY --chown=appuser:appuser . .

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONFAULTHANDLER=1

RUN mkdir -p /app/media/vedlegg && chown -R appuser:appuser /app/media
RUN mkdir -p /app/staticfiles && chown -R appuser:appuser /app/staticfiles

USER appuser

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]