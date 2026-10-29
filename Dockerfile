# Imagem do Farol para usar a CLI sem instalar uv nem Node.js:
#   docker run --rm -v "$PWD:/repo" ghcr.io/islan-max/farol revisar
FROM node:22-bookworm-slim AS node
FROM ghcr.io/astral-sh/uv:0.13.6 AS uv

FROM python:3.12-slim-bookworm AS build
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src
# Instala o Farol (sem as dependências de desenvolvimento), fixado pelo uv.lock.
RUN uv sync --locked --no-dev --no-editable

FROM python:3.12-slim-bookworm
LABEL org.opencontainers.image.title="Farol" \
      org.opencontainers.image.description="Revisão de pull request que ensina, em português do Brasil" \
      org.opencontainers.image.source="https://github.com/islan-max/farol" \
      org.opencontainers.image.url="https://islan-max.github.io/farol/" \
      org.opencontainers.image.licenses="MIT"

# git (o `farol revisar` lê o diff) e Node.js (ESLint, para JavaScript e TypeScript).
RUN apt-get update \
 && apt-get install -y --no-install-recommends git ca-certificates \
 && rm -rf /var/lib/apt/lists/* \
 && git config --system --add safe.directory '*'
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
 && node --version && npm --version

COPY --from=build /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH" \
    FAROL_CACHE=/opt/farol-cache

# O ESLint fixado é instalado agora (npm ci --ignore-scripts), para não baixar a cada execução.
RUN python -c "from farol.analise.eslint import preparar; print(preparar())" \
 && chmod -R a+rX /opt/farol-cache

RUN useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin farol
USER farol
WORKDIR /repo
ENTRYPOINT ["farol"]
CMD ["--help"]
