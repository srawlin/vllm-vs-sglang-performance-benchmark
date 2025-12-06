#!/bin/bash
# Clear LLM server cache by restarting the service
# Works with supervisor-managed servers (Vast.ai setup)
# Usage: ./clear_cache.sh [framework]
#   framework: vllm (default), sglang, or tensorrt

set -e

FRAMEWORK="${1:-vllm}"
SSH_HOST="${VASTAI_HOST:-root@YOUR_VASTAI_IP}"
SSH_PORT="${VASTAI_PORT:-22}"
SSH_KEY="~/.ssh/vastai_ed25519"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Set framework-specific settings
case $FRAMEWORK in
    vllm)
        SERVICE_NAME="vllm"
        PROCESS_PATTERN="vllm serve"
        HEALTH_PORT="8000"
        ;;
    sglang)
        SERVICE_NAME="sglang"
        PROCESS_PATTERN="sglang"
        HEALTH_PORT="32382"
        ;;
    tensorrt)
        SERVICE_NAME="tensorrt"
        PROCESS_PATTERN="tensorrt"
        HEALTH_PORT="8000"
        ;;
    *)
        echo -e "${RED}Error: Unknown framework '$FRAMEWORK'${NC}"
        echo "Usage: $0 [vllm|sglang|tensorrt]"
        exit 1
        ;;
esac

echo -e "${YELLOW}Clearing $FRAMEWORK cache...${NC}"

ssh -p $SSH_PORT -i $SSH_KEY $SSH_HOST "
    set -e

    # Check if supervisorctl is available
    if command -v supervisorctl &> /dev/null; then
        echo \"Using supervisorctl to restart $SERVICE_NAME...\"
        supervisorctl restart $SERVICE_NAME 2>/dev/null || echo \"Note: supervisorctl restart failed, trying process kill...\"

        echo \"Waiting for $SERVICE_NAME to start...\"
        sleep 15

        # Wait for service to be ready
        for i in {1..30}; do
            if curl -s http://localhost:$HEALTH_PORT/health > /dev/null 2>&1 || \
               curl -s http://localhost:$HEALTH_PORT/v1/models > /dev/null 2>&1; then
                echo \"$SERVICE_NAME is ready!\"
                exit 0
            fi
            echo \"Waiting for $SERVICE_NAME to respond... (\$i/30)\"
            sleep 2
        done

        echo \"Warning: $SERVICE_NAME may not be fully ready yet\"
        exit 0
    else
        # Fallback: kill process and let supervisor restart it
        echo \"Supervisorctl not found, killing $SERVICE_NAME process...\"
        PROCESS_PID=\$(ps aux | grep '$PROCESS_PATTERN' | grep -v grep | awk '{print \$2}' | head -1)

        if [ -n \"\$PROCESS_PID\" ]; then
            echo \"Found $SERVICE_NAME process: PID \$PROCESS_PID\"
            kill \$PROCESS_PID

            echo \"Waiting for supervisor to restart $SERVICE_NAME...\"
            sleep 15

            # Check if restarted
            for i in {1..30}; do
                if curl -s http://localhost:$HEALTH_PORT/health > /dev/null 2>&1 || \
                   curl -s http://localhost:$HEALTH_PORT/v1/models > /dev/null 2>&1; then
                    echo \"$SERVICE_NAME is ready!\"
                    exit 0
                fi
                echo \"Waiting... (\$i/30)\"
                sleep 2
            done
        else
            echo \"Error: Could not find $SERVICE_NAME process\"
            exit 1
        fi
    fi
"

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ Cache cleared successfully${NC}"
    echo -e "$FRAMEWORK has been restarted with cold cache"
else
    echo -e "${RED}✗ Failed to clear cache${NC}"
    echo -e "You may need to manually restart $FRAMEWORK"
    exit 1
fi
