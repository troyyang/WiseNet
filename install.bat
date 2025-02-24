@echo off
:: Enable error handling and logging
setlocal enabledelayedexpansion
set LOG_FILE=install_script.log
call :log "Script started at %DATE% %TIME%"
call :log "Current working directory: %CD%"

:: Determine the operating system
set OS_TYPE=Windows
call :log "Operating System: %OS_TYPE%"


call :log "Load environment variables from .env file"
:: Load environment variables from .env file
if exist .env (
    call :log ".env file found. Loading environment variables..."
    for /f "tokens=1,2 delims==" %%A in (.env) do (
        set %%A=%%B
    )
) else (
    call :log ".env file not found. Please create it and try again."
    exit /b 1
)

:: Translate ${VARIABLE} to %VARIABLE% for all required variables
set REQUIRED_VARS=NEO4J_DIR WISENET_DATA_DIR OLLAMA_DIR
for %%V in (%REQUIRED_VARS%) do (
    call :replace_env_syntax "!%%V!"
    set %%V=!output!
    call :log "Translated %%V: !%%V!"
)

:: Validate required environment variables
for %%V in (%REQUIRED_VARS%) do (
    if not defined %%V (
        call :log "%%V environment variable is not set. Please set it in the .env file."
        exit /b 1
    )
)

:: Check if Docker is installed
where docker >nul 2>&1
if %ERRORLEVEL% equ 0 (
    call :log "Docker is already installed. Skipping Docker installation."
) else (
    call :log "Docker is not installed. Installing Docker..."
    call :install_docker
)

:: Ensure Docker is running
docker info >nul 2>&1
if %ERRORLEVEL% equ 0 (
    call :log "Docker is running."
) else (
    call :log "Docker is not running. Attempting to start Docker..."
    net start docker
    if %ERRORLEVEL% equ 0 (
        call :log "Docker started successfully."
    ) else (
        call :log "Error: Failed to start Docker. Please check the Docker service status manually."
        exit /b 1
    )
)

:: Verify Docker installation
docker --version
if %ERRORLEVEL% neq 0 (
    call :log "Error: Docker installation verification failed."
    exit /b 1
)

:: Check if Docker Compose is installed
docker compose version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    call :log "Docker Compose is already installed. Skipping installation."
) else (
    call :log "Docker Compose is not installed. Installing Docker Compose..."
    call :install_docker_compose
)

:: Verify Docker Compose installation
docker compose version
if %ERRORLEVEL% neq 0 (
    call :log "Error: Docker Compose installation verification failed."
    exit /b 1
)

:: Pull required Docker images
set IMAGES=python:3.10.12 node:18
for %%I in (%IMAGES%) do (
    call :pull_image %%I
)

:: Create and configure directories
call :create_and_configure_dir "%NEO4J_DIR%\data"
call :create_and_configure_dir "%NEO4J_DIR%\logs"
call :create_and_configure_dir "%OLLAMA_DIR%"
call :create_and_configure_dir "%WISENET_DATA_DIR%\app\data\spacy_models"
call :create_and_configure_dir "%WISENET_DATA_DIR%\app\data\logs"
call :create_and_configure_dir "%WISENET_DATA_DIR%\app\data\upload"
call :create_and_configure_dir "%WISENET_DATA_DIR%\app\cache"

:: Check and install spaCy models
call :check_and_install_spacy_model "en_core_web_lg-3.8.0" "en_core_web_lg-3.8.0.tar.gz" "https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0.tar.gz"
call :check_and_install_spacy_model "zh_core_web_lg-3.8.0" "zh_core_web_lg-3.8.0.tar.gz" "https://github.com/explosion/spacy-models/releases/download/zh_core_web_lg-3.8.0/zh_core_web_lg-3.8.0.tar.gz"

:: Start the containers
call :log "Starting the containers..."
docker compose up -d
call :log "Containers started."

:: Install Ollama models
call :check_and_install_model "llama3.1"
call :check_and_install_model "wizardlm2"
docker exec -it ollama ollama list

where curl >nul 2>&1
if %ERRORLEVEL% neq 0 (
    call :log "Error: curl is not installed. Please install curl and try again."
    exit /b 1
)

:: Init graph database
call :log "Initializing graph database..."
curl http://localhost:%API_PORT%/api/graph/initialize`
if %ERRORLEVEL% neq 0 (
    call :log "Error: Failed to initialize graph database."
    exit /b 1
)
call :log "Graph database initialized."

:: Log script completion
call :log "Script finished at %DATE% %TIME%"
exit /b 0

:: Functions
:log
echo %DATE% %TIME% - %* >> %LOG_FILE%
echo %*
exit /b 0

:replace_env_syntax
set "input=%~1"
set "output=!input:${=%%!"
set "output=!output:}=%%!"
exit /b 0


:install_docker
call :log "Installing Docker..."
call :log "Please install Docker Desktop manually from https://www.docker.com/products/docker-desktop"
exit /b 0

:install_docker_compose
call :log "Installing Docker Compose..."
call :log "Please ensure Docker Compose is installed with Docker Desktop."
exit /b 0

:pull_image
set IMAGE_NAME=%1
call :log "Checking if image %IMAGE_NAME% exists locally..."
docker image inspect %IMAGE_NAME% >nul 2>&1
if %ERRORLEVEL% equ 0 (
    call :log "Image %IMAGE_NAME% already exists locally. Skipping pull."
) else (
    call :log "Image %IMAGE_NAME% not found locally. Pulling..."
    docker pull %IMAGE_NAME%
    if %ERRORLEVEL% neq 0 (
        call :log "Error: Failed to pull %IMAGE_NAME%. Check your internet connection or Docker settings."
        exit /b 1
    )
)
exit /b 0

:create_and_configure_dir
set DIR=%~1
set DIR=%DIR:/=\%  &:: Convert slashes to backslashes
if not exist "%DIR%" (
    call :log "Creating directory: %DIR%"
    mkdir "%DIR%"
    if %ERRORLEVEL% neq 0 (
        call :log "Failed to create directory: %DIR%"
        exit /b 1
    )
) else (
    call :log "Directory %DIR% already exists. Skipping creation."
)
exit /b 0

:check_and_install_spacy_model
set MODEL_NAME=%1
set MODEL_FILE=%2
set MODEL_URL=%3
if exist "%WISENET_DATA_DIR%\app\data\spacy_models\%MODEL_NAME%" (
    call :log "spaCy model '%MODEL_NAME%' is already installed. Skipping download and installation."
) else (
    call :log "spaCy model '%MODEL_NAME%' is not installed. Downloading and installing..."
    curl -o "%WISENET_DATA_DIR%\app\data\spacy_models\%MODEL_FILE%" "%MODEL_URL%"
    if %ERRORLEVEL% neq 0 (
        call :log "Failed to download spaCy model '%MODEL_NAME%'."
        exit /b 1
    )
    call :log "Extracting the spaCy model '%MODEL_NAME%'..."
    tar -xzvf "%WISENET_DATA_DIR%\app\data\spacy_models\%MODEL_FILE%" -C "%WISENET_DATA_DIR%\app\data\spacy_models"
    del "%WISENET_DATA_DIR%\app\data\spacy_models\%MODEL_FILE%"
    call :log "spaCy model '%MODEL_NAME%' installed successfully."
)
exit /b 0

:check_and_install_model
set MODEL_NAME=%1
call :log "Checking if model '%MODEL_NAME%' is installed..."
docker exec -it ollama ollama list | findstr /i "%MODEL_NAME%" >nul
if %ERRORLEVEL% equ 0 (
    call :log "Model '%MODEL_NAME%' is already installed. Skipping installation."
) else (
    call :log "Model '%MODEL_NAME%' is not installed. Installing..."
    docker exec -it ollama ollama pull %MODEL_NAME%
    if %ERRORLEVEL% neq 0 (
        call :log "Error: Failed to install model '%MODEL_NAME%'."
        exit /b 1
    )
)
exit /b 0