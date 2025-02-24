FROM python:3.10.12

# Set the working directory
WORKDIR /app
# Copy application code
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*
# Configure pip to use a mirror if you download slow
# RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
#     pip3 config set global.trusted-host "pypi.tuna.tsinghua.edu.cn mirrors.pku.edu.cn" && \
#     pip3 config set global.extra-index-url "https://mirrors.pku.edu.cn/pypi/web/simple"

# Install Poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=2.1.1
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s ${POETRY_HOME}/bin/poetry /usr/local/bin/poetry
ENV PATH="${POETRY_HOME}/bin:${PATH}"

# Add Poetry plugin for PyPI mirror
# RUN poetry self add poetry-plugin-pypi-mirror
# ENV POETRY_PYPI_MIRROR_URL=https://mirrors.aliyun.com/pypi/simple/
# ENV POETRY_PYPI_MIRROR_URL=https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
# Configure Poetry to not create virtual environments
RUN poetry config virtualenvs.create false

# Copy dependency files first to leverage Docker cache
COPY pyproject.toml poetry.lock ./

# Set the timeout for Poetry to 600 seconds
ENV POETRY_INSTALLER_MAX_WORKERS=10
ENV POETRY_HTTP_TIMEOUT=180
# Install dependencies
RUN poetry install --no-interaction --only main

RUN pip install --upgrade pip

# Install Babel
RUN pip install Babel
# Compile translations
RUN echo "Compiling translations..."
RUN pybabel compile -d translations
RUN echo "Translations compiled."

# Make entrypoint script executable
RUN chmod +x ./entrypoint.sh
# Make start.sh executable
RUN chmod +x ./start.sh

# Expose port
EXPOSE 8088
# Run the application
ENTRYPOINT ["./entrypoint.sh"]
CMD ["./start.sh"]