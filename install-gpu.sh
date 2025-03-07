#!/bin/bash

# Enable error handling and debugging
set -e
set -x

# Logging configuration
LOG_FILE="install_script.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Script started at $(date)"
echo "Current working directory: $(pwd)"
echo "OSTYPE: $OSTYPE"

# Determine the operating system and set package manager
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        ID=${ID,,}  # Convert to lowercase for consistency
        VERSION_ID=${VERSION_ID%%.*}  # Get major version only
        case "$ID" in
            ubuntu|debian)
                PACKAGE_MANAGER="apt-get"
                ;;
            centos|rhel|fedora|rocky|almalinux)
                PACKAGE_MANAGER="yum"
                ;;
            *)
                echo "Unsupported Linux distribution: $ID $VERSION_ID"
                exit 1
                ;;
        esac
    else
        echo "Unable to determine the Linux distribution."
        exit 1
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PACKAGE_MANAGER="brew"
    if ! command -v brew &> /dev/null; then
        echo "Homebrew is not installed. Please install Homebrew and try again."
        exit 1
    fi
else
    echo "Unsupported operating system. This script is designed for Linux and macOS."
    exit 1
fi

# Install curl if not already installed
if ! command -v curl &> /dev/null; then
    echo "Installing curl..."
    if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        brew install curl
    else
        sudo $PACKAGE_MANAGER install -y curl
    fi
fi

# Check if Docker is already installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Installing Docker..."
    if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        brew install --cask docker
    else
        sudo $PACKAGE_MANAGER update
        sudo $PACKAGE_MANAGER install -y ca-certificates curl gnupg

        if [ "$ID" == "ubuntu" ] || [ "$ID" == "debian" ]; then
            # Create the directory for Docker's GPG key
            sudo install -m 0755 -d /etc/apt/keyrings

            # Download Docker's GPG key and save it
            curl -fsSL https://download.docker.com/linux/$ID/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

            # Set the correct permissions for the GPG key
            sudo chmod a+r /etc/apt/keyrings/docker.gpg

            # Add Docker's repository to Apt sources
            echo \
              "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$ID \
              $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
              sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

            # Update the package list and install Docker
            sudo $PACKAGE_MANAGER update
        elif [ "$ID" == "fedora" ]; then
            # Ensure dnf-plugins-core is installed
            if ! command -v dnf config-manager &> /dev/null; then
                echo "Installing dnf-plugins-core..."
                sudo dnf install -y dnf-plugins-core
            fi

            # Add Docker's repository for Fedora
            echo "Adding Docker's repository..."
            # sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo

            # Install Docker
            echo "Installing Docker..."
            sudo tee /etc/yum.repos.d/docker-ce.repo <<EOF
[docker-ce-stable]
name=Docker CE Stable - \$basearch
baseurl=https://download.docker.com/linux/fedora/\$releasever/\$basearch/stable
enabled=1
gpgcheck=1
gpgkey=https://download.docker.com/linux/fedora/gpg
EOF
            sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        fi

        # Add your user to the Docker group
        sudo usermod -a -G docker $USER
        # Apply group changes without requiring a logout
        # sudo newgrp docker
    fi
else
    echo "Docker is already installed. Skipping Docker installation."
fi

# Ensure Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Docker is not running. Attempting to start Docker..."
    if sudo systemctl start docker; then
        echo "Docker started successfully."
        # Optionally, enable Docker to start on boot
        sudo systemctl enable docker
    else
        echo "Error: Failed to start Docker. Please check the Docker service status manually."
        exit 1
    fi
fi

# Verify Docker is running
if docker info > /dev/null 2>&1; then
    echo "Docker is running."
else
    echo "Error: Docker is still not running. Please investigate and try again."
    exit 1
fi

# Verify Docker installation
docker --version

# Install Docker Compose Plugin
if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Installing Docker Compose Plugin..."
    if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        brew install docker-compose
    else
        if [ "$ID" == "ubuntu" ] || [ "$ID" == "debian" ]; then
            sudo $PACKAGE_MANAGER update
            sudo $PACKAGE_MANAGER install -y docker-compose-plugin
        elif [ "$ID" == "centos" ] || [ "$ID" == "rhel" ] || [ "$ID" == "fedora" ]; then
            sudo $PACKAGE_MANAGER update
            sudo $PACKAGE_MANAGER install -y docker-compose-plugin
        else
            echo "Unsupported distribution for Docker Compose installation."
            exit 1
        fi
    fi
else
    echo "Docker Compose is already installed. Skipping installation."
fi

# Verify Docker Compose installation
docker compose version

# Function to check if an image exists locally and pull it if missing
pull_image() {
    local image_name=$1
    if ! docker image inspect "$image_name" > /dev/null 2>&1; then
        echo "$image_name not found locally. Pulling..."
        if ! docker pull "$image_name"; then
            echo "Error: Failed to pull $image_name. Check your internet connection or Docker settings."
            exit 1
        fi
    else
        echo "$image_name already exists locally. Skipping pull."
    fi
}

# Ensure Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# List of required images
IMAGES=("python:3.10.12" "node:18")

# Check and pull images if needed
for IMAGE in "${IMAGES[@]}"; do
    pull_image "$IMAGE"
done

echo "Image pull process completed successfully."

# Check if NVIDIA Container Toolkit is installed (Linux only)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Detect package manager (APT for Debian/Ubuntu, DNF for Fedora)
    if command -v apt &> /dev/null; then
        PACKAGE_MANAGER="apt"
        NVIDIA_REPO_URL="https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list"
        NVIDIA_GPG_KEY_URL="https://nvidia.github.io/libnvidia-container/gpgkey"
    elif command -v dnf &> /dev/null; then
        PACKAGE_MANAGER="dnf"
        NVIDIA_REPO_URL="https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo"
        NVIDIA_GPG_KEY_URL="https://nvidia.github.io/libnvidia-container/gpgkey"
    else
        echo "Unsupported package manager. Exiting."
        exit 1
    fi

    # Install NVIDIA Container Toolkit if not installed
    if ! command -v nvidia-container-toolkit &> /dev/null; then
        echo "NVIDIA Container Toolkit is not installed. Installing..."

        if [[ "$PACKAGE_MANAGER" == "apt" ]]; then
            # Add NVIDIA GPG key and repository for APT-based systems
            curl -fsSL "$NVIDIA_GPG_KEY_URL" | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
              && curl -s -L "$NVIDIA_REPO_URL" | \
                sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
                sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list > /dev/null
        elif [[ "$PACKAGE_MANAGER" == "dnf" ]]; then
            # Ensure dnf-plugins-core is installed
            if ! command -v dnf config-manager &> /dev/null; then
                echo "Installing dnf-plugins-core..."
                sudo dnf install -y dnf-plugins-core
            fi
            # Add NVIDIA repository for Fedora-based systems
            # sudo dnf config-manager --add-repo "$NVIDIA_REPO_URL"
            sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo <<EOF
[nvidia-container-toolkit]
name=NVIDIA Container Toolkit
baseurl=https://nvidia.github.io/libnvidia-container/stable/rpm/$basearch
enabled=1
gpgcheck=1
gpgkey=https://nvidia.github.io/libnvidia-container/gpgkey
EOF
        fi

        # Update package lists and install the toolkit
        sudo $PACKAGE_MANAGER update -y
        sudo $PACKAGE_MANAGER install -y nvidia-container-toolkit || { echo "Failed to install NVIDIA Container Toolkit"; exit 1; }
    else
        echo "NVIDIA Container Toolkit is already installed. Skipping installation."
    fi

    # Ensure NVIDIA runtime is configured
    if ! docker info | grep -iq "nvidia"; then
        echo "Configuring NVIDIA runtime for Docker..."
        sudo nvidia-ctk runtime configure --runtime=docker || { echo "Failed to configure NVIDIA runtime"; exit 1; }
        sudo systemctl restart docker || { echo "Failed to restart Docker service"; exit 1; }
    else
        echo "NVIDIA runtime is already configured."
    fi

    # Configure Docker to use NVIDIA runtime
    echo "Configuring Docker daemon to use NVIDIA runtime..."
    if ! cat /etc/docker/daemon.json | grep -q "nvidia"; then
        echo "please update /etc/docker/daemon.json, adding the following:"
        echo "    \"runtimes\": {
            \"nvidia\": {
                \"path\": \"nvidia-container-runtime\",
                \"runtimeArgs\": []
            }
        }"
        #     sudo tee /etc/docker/daemon.json <<EOF > /dev/null
    # {
    #     "runtimes": {
    #         "nvidia": {
    #             "path": "nvidia-container-runtime",
    #             "runtimeArgs": []
    #         }
    #     }
    # }
    # EOF
        echo "and restart Docker"
        exit 1

    fi    

    # Verify GPU access with Docker
    echo "Verifying GPU access..."
    if docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi; then
        echo "GPU is accessible inside Docker."
    else
        echo "Error: GPU is not accessible inside Docker. Please check your NVIDIA driver and Docker configuration."
        echo "Try running: sudo systemctl restart docker && sudo systemctl restart nvidia-container-toolkit"
        exit 1
    fi
fi


# Check if .env file exists and load environment variables
if [ -f ./.env ]; then
    if [ -r ./.env ]; then
        source ./.env
    else
        echo "You do not have permission to read the .env file. Please check the file permissions."
        exit 1
    fi
else
    echo ".env file not found. Please create it and try again."
    exit 1
fi

# Validate required environment variables
required_vars=("NEO4J_DIR" "WISENET_DATA_DIR" "OLLAMA_DIR")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "$var environment variable is not set. Please set it in the .env file."
        exit 1
    fi
done

# Function to create directory and set ownership and permissions
create_and_configure_dir() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        echo "Creating directory: $dir"
        mkdir -p "$dir" || { echo "Failed to create directory: $dir"; exit 1; }
    else
        echo "Directory $dir already exists. Skipping creation."
    fi
    echo "Setting ownership and permissions for directory: $dir"
    sudo chown -R $USER:$USER "$dir" || { echo "Failed to change ownership of directory: $dir"; exit 1; }
    sudo chmod -R 755 "$dir" || { echo "Failed to change permissions of directory: $dir"; exit 1; }
    echo "Directory $dir created and configured."
}

# Create and configure directories
create_and_configure_dir "$NEO4J_DIR/data"
create_and_configure_dir "$NEO4J_DIR/logs"
create_and_configure_dir "$OLLAMA_DIR"
create_and_configure_dir "$WISENET_DATA_DIR/app/data/spacy_models"
create_and_configure_dir "$WISENET_DATA_DIR/app/data/logs"
create_and_configure_dir "$WISENET_DATA_DIR/app/data/upload"
create_and_configure_dir "$WISENET_DATA_DIR/app/cache"

echo "Directories created and permissions set."

# Function to check if spaCy model is installed
export github_base_url="https://github.com"
# use github mirror url, refer to https://fcp7.com/github-mirror-daily-updates.html
# export github_base_url="https://bgithub.xyz"
check_and_install_spacy_model() {
    local model_name="$1"
    local model_file="$2"
    local model_url="$3"

    echo "Checking if spaCy model '$model_name' is installed..."

    if [ -d "$WISENET_DATA_DIR/app/data/spacy_models/$model_name" ]; then
        echo "spaCy model '$model_name' is already installed. Skipping download and installation."
    else
        echo "spaCy model '$model_name' is not installed. Downloading and installing..."
        wget "$model_url" -P "$WISENET_DATA_DIR/app/data/spacy_models"
        echo "Extracting the spaCy model '$model_name'..."
        tar -xzvf "$WISENET_DATA_DIR/app/data/spacy_models/$model_file" -C "$WISENET_DATA_DIR/app/data/spacy_models"
        rm "$WISENET_DATA_DIR/app/data/spacy_models/$model_file"
        echo "spaCy model '$model_name' installed successfully."
    fi
}

# Check and install spaCy models
check_and_install_spacy_model "en_core_web_lg-3.8.0" "en_core_web_lg-3.8.0.tar.gz" "$github_base_url/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0.tar.gz"
check_and_install_spacy_model "zh_core_web_lg-3.8.0" "zh_core_web_lg-3.8.0.tar.gz" "$github_base_url/explosion/spacy-models/releases/download/zh_core_web_lg-3.8.0/zh_core_web_lg-3.8.0.tar.gz"

echo "spaCy models are ready."

# Start the containers
echo "Starting the containers..."
# docker compose up -d
docker compose -f docker-compose-base-gpu.yml -f docker-compose.yml up -d
echo "Containers started."

# install ollama models
# Function to check if a model is installed
check_and_install_model() {
    local model_name="$1"
    echo "Checking if model '$model_name' is installed..."

    # Check if the model is already installed
    if docker exec -it ollama ollama list | grep -q "$model_name"; then
        echo "Model '$model_name' is already installed. Skipping installation."
    else
        echo "Model '$model_name' is not installed. Installing..."
        docker exec -it ollama ollama pull "$model_name"
        echo "Model '$model_name' installed successfully."
    fi
}

# Check and install models
check_and_install_model "llama3.1"
check_and_install_model "wizardlm2"
check_and_install_model "deepseek-r1:8b"
docker exec -it ollama ollama list

echo "All models checked and installed (if necessary)."

# Disable debugging
set +x

echo "Script finished at $(date)"
