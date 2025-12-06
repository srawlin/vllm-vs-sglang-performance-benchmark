#!/bin/bash
# Run benchmarks locally on Vast.ai instance
# This script runs ON the Vast.ai server for zero network latency

set -e

# Get vLLM server info
VLLM_URL="http://localhost:8000"
API_KEY="${API_KEY:-token-abc123}"  # Default or from environment
MODEL_NAME="${MODEL_NAME:-deepseek-ai/DeepSeek-R1-Distill-Llama-8B}"
FRAMEWORK="${FRAMEWORK:-vllm}"

# Activate virtual environment
source venv/bin/activate

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Running LLM Benchmarks Locally${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Server: $VLLM_URL"
echo -e "Model: $MODEL_NAME"
echo -e "Framework: $FRAMEWORK"
echo -e "${BLUE}========================================${NC}\n"

# Test server connectivity
echo -e "${YELLOW}Testing server connectivity...${NC}"
if curl -s "$VLLM_URL/v1/models" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Server is reachable${NC}\n"
else
    echo -e "❌ Cannot reach server at $VLLM_URL"
    echo -e "Make sure vLLM is running locally"
    exit 1
fi

# Function to run a benchmark
run_benchmark() {
    local test_name=$1
    local concurrency=$2

    echo -e "${YELLOW}Running: $test_name (concurrency: $concurrency)${NC}"

    python benchmark.py \
        --server-url "$VLLM_URL" \
        --api-key "$API_KEY" \
        --model "$MODEL_NAME" \
        --framework "$FRAMEWORK" \
        --test-file "data/${test_name}.json" \
        --concurrency $concurrency \
        --output-dir results \
        --timeout 300

    echo -e "${GREEN}✓ Completed: $test_name${NC}\n"
    sleep 3
}

# Run comprehensive benchmark suite
echo -e "${BLUE}Starting benchmark suite...${NC}\n"

# Quick tests (low concurrency)
echo -e "${YELLOW}=== Phase 1: Latency Tests (Low Concurrency) ===${NC}"
run_benchmark "short_chat" "1 5"
run_benchmark "medium_chat" "1 5"

# Moderate load tests
echo -e "${YELLOW}=== Phase 2: Moderate Load Tests ===${NC}"
run_benchmark "short_chat" "10 20"
run_benchmark "medium_chat" "10 20"

# High concurrency tests
echo -e "${YELLOW}=== Phase 3: High Concurrency Tests ===${NC}"
run_benchmark "short_chat" "50"
run_benchmark "medium_chat" "50"

# Long context tests
echo -e "${YELLOW}=== Phase 4: Long Context Tests ===${NC}"
run_benchmark "long_rag" "1 5 10"

# Cache reuse test (critical for RAG)
echo -e "${YELLOW}=== Phase 5: Cache Reuse Test ===${NC}"
run_benchmark "cache_reuse" "1 10"

# Code generation test
echo -e "${YELLOW}=== Phase 6: Code Generation Tests ===${NC}"
run_benchmark "code_short" "1 10"

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✓ All benchmarks complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "\nResults saved in: ./results/"
echo -e "\nTo analyze results:"
echo -e "  ${BLUE}python analyze.py --results-dir results --plot${NC}"
echo -e "\nTo download results to local machine:"
echo -e "  ${BLUE}(From your local machine) ./download_results.sh${NC}"
