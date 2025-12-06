#!/bin/bash
# Run benchmarks with cache clearing between tests
# Ensures isolated, cold-cache measurements

set -e

# Configuration - Update these for your Vast.ai instance
SSH_HOST="${VASTAI_HOST:-root@YOUR_VASTAI_IP}"
SSH_PORT="${VASTAI_PORT:-22}"
SSH_KEY="~/.ssh/vastai_ed25519"
REMOTE_DIR="/workspace/llm-benchmark"

FRAMEWORK="${1:-vllm}"
TEST_NAME="${2:-medium_chat}"
CONCURRENCY_LEVELS="${3:-1 10 50}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Benchmark with Cache Clearing${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Framework: ${GREEN}$FRAMEWORK${NC}"
echo -e "Test: ${GREEN}$TEST_NAME${NC}"
echo -e "Concurrency levels: ${GREEN}$CONCURRENCY_LEVELS${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Function to clear cache
clear_cache() {
    echo -e "${YELLOW}Clearing vLLM cache...${NC}"

    ssh -p $SSH_PORT -i $SSH_KEY $SSH_HOST "
        # Use supervisorctl to restart vLLM (Vast.ai setup)
        if command -v supervisorctl &> /dev/null; then
            echo 'Restarting vLLM via supervisorctl...'
            supervisorctl restart vllm

            echo 'Waiting for vLLM to start...'
            sleep 15

            # Check if vLLM is responding
            for i in {1..30}; do
                if curl -s http://localhost:8000/v1/models > /dev/null 2>&1; then
                    echo 'vLLM is ready!'
                    break
                fi
                echo \"Waiting for vLLM... (\$i/30)\"
                sleep 2
            done
        else
            # Fallback: kill and let supervisor restart
            echo 'Killing vLLM process (supervisor will restart)...'
            VLLM_PID=\$(ps aux | grep 'vllm serve' | grep -v grep | awk '{print \$2}' | head -1)
            if [ -n \"\$VLLM_PID\" ]; then
                kill \$VLLM_PID
                sleep 15

                for i in {1..30}; do
                    if curl -s http://localhost:8000/v1/models > /dev/null 2>&1; then
                        echo 'vLLM is ready!'
                        break
                    fi
                    sleep 2
                done
            fi
        fi
    "

    echo -e "${GREEN}✓ Cache cleared${NC}\n"
    sleep 3
}

# Function to run a single benchmark
run_single_benchmark() {
    local concurrency=$1

    echo -e "${BLUE}Running test with concurrency=$concurrency${NC}"

    ssh -p $SSH_PORT -i $SSH_KEY $SSH_HOST "cd $REMOTE_DIR && bash -c '
        source venv/bin/activate

        python benchmark.py \
            --server-url \"http://localhost:8000\" \
            --api-key \"\${VLLM_API_KEY:-your-vllm-api-key-here}\" \
            --model \"deepseek-ai/DeepSeek-R1-Distill-Llama-8B\" \
            --framework \"$FRAMEWORK\" \
            --test-file \"data/${TEST_NAME}.json\" \
            --concurrency $concurrency \
            --output-dir results \
            --timeout 300
    '"

    echo -e "${GREEN}✓ Test complete (concurrency=$concurrency)${NC}\n"
}

# Run benchmarks with cache clearing between each
COUNTER=0
for concurrency in $CONCURRENCY_LEVELS; do
    COUNTER=$((COUNTER + 1))

    echo -e "${YELLOW}=== Test $COUNTER: Concurrency=$concurrency ===${NC}\n"

    # Clear cache before each test (except the first)
    if [ $COUNTER -gt 1 ]; then
        clear_cache
    fi

    # Run benchmark
    run_single_benchmark $concurrency

    sleep 2
done

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}✓ All tests complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "\nCache was cleared between each test for isolated measurements."
echo -e "\nDownload results:"
echo -e "  ${BLUE}./download_results.sh${NC}"
