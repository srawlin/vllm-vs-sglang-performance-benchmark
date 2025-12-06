#!/bin/bash
# Run benchmarks remotely on Vast.ai instance
# Execute from your local machine

set -e

# Configuration - Update these for your Vast.ai instance
SSH_HOST="${VASTAI_HOST:-root@YOUR_VASTAI_IP}"
SSH_PORT="${VASTAI_PORT:-22}"
SSH_KEY="~/.ssh/vastai_ed25519"
REMOTE_DIR="/workspace/llm-benchmark"

# Parse arguments
FRAMEWORK="${1:-vllm}"
TEST_NAME="${2:-medium_chat}"
CONCURRENCY="${3:-1 5 10}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Remote Benchmark Execution${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Framework: ${GREEN}$FRAMEWORK${NC}"
echo -e "Test: ${GREEN}$TEST_NAME${NC}"
echo -e "Concurrency: ${GREEN}$CONCURRENCY${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Validate framework
if [[ ! "$FRAMEWORK" =~ ^(vllm|sglang|tensorrt|other)$ ]]; then
    echo -e "${RED}Error: Invalid framework. Use: vllm, sglang, tensorrt, or other${NC}"
    exit 1
fi

# Determine API key and port based on framework
case $FRAMEWORK in
    vllm)
        API_KEY="${VLLM_API_KEY:-your-vllm-api-key-here}"
        MODEL="deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
        SERVER_PORT="8000"
        echo -e "${YELLOW}Note: Set VLLM_API_KEY environment variable${NC}"
        ;;
    sglang)
        API_KEY="${SGLANG_API_KEY:-your-sglang-api-key-here}"
        MODEL="${SGLANG_MODEL:-deepseek-ai/DeepSeek-R1-Distill-Llama-8B}"
        SERVER_PORT="${SGLANG_PORT:-31836}"
        echo -e "${YELLOW}Note: Set SGLANG_API_KEY environment variable${NC}"
        echo -e "${YELLOW}Note: Using SGLang port $SERVER_PORT${NC}"
        ;;
    tensorrt)
        API_KEY="${TENSORRT_API_KEY:-your-tensorrt-api-key-here}"
        MODEL="${TENSORRT_MODEL:-deepseek-ai/DeepSeek-R1-Distill-Llama-8B}"
        SERVER_PORT="${TENSORRT_PORT:-8000}"
        echo -e "${YELLOW}Note: Set TENSORRT_API_KEY environment variable${NC}"
        ;;
    *)
        API_KEY="${API_KEY:-your-api-key-here}"
        MODEL="${MODEL:-deepseek-ai/DeepSeek-R1-Distill-Llama-8B}"
        SERVER_PORT="8000"
        ;;
esac

echo -e "${YELLOW}Running benchmark remotely...${NC}\n"

# Execute benchmark on remote server
ssh -p $SSH_PORT -i $SSH_KEY $SSH_HOST "cd $REMOTE_DIR && bash -c '
    source venv/bin/activate

    # Check if test file exists
    if [ ! -f \"data/${TEST_NAME}.json\" ]; then
        echo \"Error: Test file data/${TEST_NAME}.json not found\"
        echo \"Available tests:\"
        ls -1 data/*.json | xargs -n1 basename
        exit 1
    fi

    # Run the benchmark
    python benchmark.py \
        --server-url \"http://localhost:$SERVER_PORT\" \
        --api-key \"$API_KEY\" \
        --model \"$MODEL\" \
        --framework \"$FRAMEWORK\" \
        --test-file \"data/${TEST_NAME}.json\" \
        --concurrency $CONCURRENCY \
        --output-dir results \
        --timeout 300
'"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}✓ Benchmark completed successfully!${NC}"
    echo -e "\nTo download results:"
    echo -e "  ${BLUE}./download_results.sh${NC}"
    echo -e "\nTo analyze results:"
    echo -e "  ${BLUE}ssh -p $SSH_PORT -i $SSH_KEY $SSH_HOST 'cd $REMOTE_DIR && source venv/bin/activate && python analyze.py --results-dir results --plot'${NC}"
else
    echo -e "\n${RED}❌ Benchmark failed with exit code $EXIT_CODE${NC}"
    exit $EXIT_CODE
fi
