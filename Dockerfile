FROM ghcr.io/astral-sh/uv:python3.13-bookworm AS base

ARG USERNAME="mcp"
ARG USER_UID=1001
ARG USER_GID=1001

RUN addgroup --gid $USER_GID $USERNAME && \
    adduser --uid $USER_UID --gid $USER_GID --home /home/$USERNAME --shell /bin/bash $USERNAME && \
    chown -R $USERNAME:$USERNAME /home/$USERNAME


FROM base AS builder

USER $USERNAME
ENV HOME_DIR=/home/$USERNAME

ENV NODE_VERSION=22.14.0
ENV NVM_DIR=${HOME_DIR}/.nvm

# Install node
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash && \
    . ${NVM_DIR}/nvm.sh && \
    nvm install $NODE_VERSION && \
    nvm alias default $NODE_VERSION

USER root

WORKDIR ${HOME_DIR}/app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN mkdir -p ${HOME_DIR}/.cache/uv && chown -R $USERNAME:$USERNAME ${HOME_DIR}
RUN --mount=type=cache,target=${HOME_DIR}/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . .
RUN --mount=type=cache,target=${HOME_DIR}/.cache/uv \
    uv sync --frozen --no-dev


FROM base AS runtime

USER $USERNAME
ENV HOME_DIR=/home/$USERNAME

ENV NODE_VERSION=22.14.0
ENV NVM_DIR=${HOME_DIR}/.nvm

COPY --from=builder ${HOME_DIR} ${HOME_DIR}

ENV PATH=${NVM_DIR}/versions/node/v${NODE_VERSION}/bin:$PATH
ENV PATH=${HOME_DIR}/app/.venv/bin:$PATH 

WORKDIR ${HOME_DIR}/app

CMD ["uv", "run", "main.py"]

