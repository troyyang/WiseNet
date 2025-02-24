#!/bin/sh

# Check if we are on a Debian or Ubuntu system
if command -v apt-get >/dev/null 2>&1; then
    # Update the package list
    apt-get update
    # Install curl, -y option means auto confirm installation
    apt-get install -y curl
fi

# Start the Ollama server in the background
/usr/bin/ollama serve &

# Wait for Ollama to become available
echo "Waiting for Ollama server to start..."
until ollama list >/dev/null 2>&1; do
  sleep 2
done

echo "Ollama server is running!"

# Check if models are specified
if [ -z "$OLLAMA_MODELS" ]; then
  echo "Error: No models specified in OLLAMA_MODELS environment variable."
  exit 1
fi

# Pull each model and output progress to Docker logs
for model in $OLLAMA_MODELS; do
  echo "Pulling model: $model"
  
  # Run ollama pull and capture output
  if ! ollama pull "$model"; then
    echo "Failed to pull model: $model"
    exit 1
  fi
done

echo "All models pulled successfully."

# Keep the server running
wait