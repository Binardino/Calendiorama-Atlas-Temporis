# ---------------------------------------------------------------------------
# Stage 1 — builder
# Installs Poetry and all production dependencies into an in-project .venv.
# This stage is discarded after build — Poetry and pip never reach the final image.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

RUN pip install poetry

# Copy dependency manifests first so Docker can cache the install layer.
# poetry install only re-runs when pyproject.toml or poetry.lock changes,
# not on every code change.
COPY pyproject.toml poetry.lock ./

# in-project true: forces Poetry to create .venv inside /app instead of
# a random cache path, so COPY --from=builder can locate it in stage 2.
# --without dev: excludes pytest, ruff, black, mypy from the production image.
# --no-root: skips installing the project itself as a package (not needed here).
RUN poetry config virtualenvs.in-project true \
    && poetry install --without dev --no-root

# ---------------------------------------------------------------------------
# Stage 2 — runtime
# Copies only the compiled .venv and application code. No Poetry, no pip.
# Final image is ~2× lighter than a single-stage build.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy the virtualenv built in stage 1 — all dependencies, no build tools.
COPY --from=builder /app/.venv ./.venv

# Copy application source code.
COPY . .

# Prepend .venv/bin so python/gunicorn resolve to the virtualenv binaries.
ENV PATH="/app/.venv/bin:$PATH"

# Document the port Gunicorn listens on (consumed by docker-compose).
EXPOSE 8000

# workers=2: conservative default for a 1-CPU VM (rule of thumb: 2 × CPU + 1).
# create_app('production'): selects ProductionConfig (Redis cache, no debug).
ENTRYPOINT ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:create_app('production')"]