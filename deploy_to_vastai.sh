#!/bin/bash
# Deploy and run benchmarks on Vast.ai instance
# This eliminates network latency for accurate results

set -e

# Configuration - Update these for your Vast.ai instance
SSH_HOST="${VASTAI_HOST:-root@YOUR_VASTAI_IP}"
SSH_PORT="${VASTAI_PORT:-22}"
SSH_KEY="~/.ssh/vastai_ed25519"
REMOTE_DIR="/workspace/llm-benchmark"
LOCAL_DIR="$(pwd)"


# Example port forwarding: ssh -p $SSH_PORT $SSH_HOST -L 8080:localhost:8080

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Vast.ai Benchmark Deployment Script${NC}"
echo -e "${BLUE}========================================${NC}"

# Function to run SSH commands
run_ssh() {
    ssh -p $SSH_PORT -i $SSH_KEY $SSH_HOST "$@"
}

# Function to copy files
copy_files() {
    rsync -avz -e "ssh -p $SSH_PORT -i $SSH_KEY" \
        --exclude='bin/' \
        --exclude='lib/' \
        --exclude='include/' \
        --exclude='__pycache__/' \
        --exclude='*.pyc' \
        --exclude='results/' \
        --exclude='.git/' \
        "$@"
}

# Step 1: Check connection
echo -e "\n${YELLOW}[1/6] Testing SSH connection...${NC}"
if run_ssh "echo 'Connection successful'"; then
    echo -e "${GREEN}✓ Connected to Vast.ai instance${NC}"
else
    echo -e "❌ Failed to connect. Check your SSH credentials."
    exit 1
fi

# Step 2: Create remote directory
echo -e "\n${YELLOW}[2/6] Creating remote directory...${NC}"
run_ssh "mkdir -p $REMOTE_DIR"
echo -e "${GREEN}✓ Remote directory created: $REMOTE_DIR${NC}"

# Step 3: Copy benchmark suite to server
echo -e "\n${YELLOW}[3/6] Uploading benchmark suite...${NC}"
copy_files \
    --progress \
    --exclude='venv/' \
    $LOCAL_DIR/ $SSH_HOST:$REMOTE_DIR/
echo -e "${GREEN}✓ Files uploaded${NC}"

# Step 4: Install dependencies on remote server
echo -e "\n${YELLOW}[4/6] Installing dependencies on remote server...${NC}"
run_ssh "cd $REMOTE_DIR && bash -c '
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo \"Installing Python 3...\"
        apt-get update
        apt-get install -y python3 python3-pip python3-venv
    fi

    # Create virtual environment
    echo \"Creating virtual environment...\"
    python3 -m venv venv

    # Install requirements
    echo \"Installing Python packages...\"
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt

    # Generate test data
    echo \"Generating test data...\"
    python test_data.py

    echo \"Setup complete!\"
'"
echo -e "${GREEN}✓ Dependencies installed and test data generated${NC}"

# Step 5: Check vLLM is running locally
echo -e "\n${YELLOW}[5/6] Checking vLLM server status...${NC}"
if run_ssh "curl -s http://localhost:8000/v1/models > /dev/null 2>&1"; then
    echo -e "${GREEN}✓ vLLM server is running on localhost:8000${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Could not reach vLLM on localhost:8000${NC}"
    echo -e "${YELLOW}  Make sure vLLM is running before executing benchmarks${NC}"
fi

# Step 6: Display next steps
echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo -e "${BLUE}========================================${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Run benchmarks remotely:"
echo -e "   ${BLUE}./run_remote_benchmark.sh vllm short_chat 1 5 10${NC}"
echo -e ""
echo -e "2. Or SSH in and run manually:"
echo -e "   ${BLUE}ssh -p $SSH_PORT -i $SSH_KEY $SSH_HOST${NC}"
echo -e "   ${BLUE}cd $REMOTE_DIR${NC}"
echo -e "   ${BLUE}source venv/bin/activate${NC}"
echo -e "   ${BLUE}./run_local_benchmark.sh${NC}"
echo -e ""
echo -e "3. Download results when complete:"
echo -e "   ${BLUE}./download_results.sh${NC}"
echo -e ""
echo -e "${GREEN}Results will be saved to: $REMOTE_DIR/results/${NC}"
