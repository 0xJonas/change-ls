# syntax=docker/dockerfile:1
FROM python:3.8-bookworm

# Install node
ADD --checksum=sha256:05c08a107c50572ab39ce9e8663a2a2d696b5d262d5bd6f98d84b997ce932d9a https://nodejs.org/dist/v14.21.3/node-v14.21.3-linux-x64.tar.xz /setup/
RUN cd /setup && \
    tar -x -f node-v14.21.3-linux-x64.tar.xz --xz && \
    rm node-v14.21.3-linux-x64.tar.xz
ENV PATH "/setup/node-v14.21.3-linux-x64/bin/:${PATH}"

# Update npm to get npm exec
RUN npm install -g npm@9.9.1

# Install Python dependencies
COPY noxfile.py pyproject.toml /setup/
RUN cd /setup/ && \
    python3 -m pip install nox && \
    python3 -m nox --no-venv -s install_dev_dependencies && \
    rm noxfile.py pyproject.toml
