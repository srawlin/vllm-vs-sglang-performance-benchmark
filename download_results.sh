#!/bin/bash
# Download benchmark results from Vast.ai instance to local machine

set -e

# Configuration - Update these for your Vast.ai instance
SSH_HOST="${VASTAI_HOST:-root@YOUR_VASTAI_IP}"
SSH_PORT="${VASTAI_PORT:-22}"
SSH_KEY="~/.ssh/vastai_ed25519"
REMOTE_DIR="/workspace/llm-benchmark/results"
LOCAL_DIR="$(pwd)/results_from_vastai"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Downloading Results from Vast.ai${NC}"
echo -e "${BLUE}========================================${NC}"

# Create local results directory
mkdir -p "$LOCAL_DIR"

echo -e "\n${YELLOW}Downloading results...${NC}"

# Download results
rsync -avz -e "ssh -p $SSH_PORT -i $SSH_KEY" \
    --progress \
    $SSH_HOST:$REMOTE_DIR/ "$LOCAL_DIR/"

echo -e "\n${GREEN}✓ Results downloaded to: $LOCAL_DIR${NC}"

# Count files
JSON_COUNT=$(find "$LOCAL_DIR" -name "*.json" | wc -l)
PNG_COUNT=$(find "$LOCAL_DIR" -name "*.png" | wc -l)
MD_COUNT=$(find "$LOCAL_DIR" -name "*.md" | wc -l)

echo -e "\nDownloaded:"
echo -e "  ${GREEN}$JSON_COUNT${NC} JSON result files"
echo -e "  ${GREEN}$PNG_COUNT${NC} PNG plot files"
echo -e "  ${GREEN}$MD_COUNT${NC} Markdown reports"

# List summary files
echo -e "\n${YELLOW}Summary files:${NC}"
find "$LOCAL_DIR" -name "*_summary.json" -type f | sort | while read file; do
    echo -e "  ${BLUE}$(basename $file)${NC}"
done

# Check if report exists
if [ -f "$LOCAL_DIR/benchmark_report.md" ]; then
    echo -e "\n${GREEN}✓ Benchmark report available:${NC}"
    echo -e "  ${BLUE}$LOCAL_DIR/benchmark_report.md${NC}"
    echo -e "\nView report:"
    echo -e "  ${BLUE}cat $LOCAL_DIR/benchmark_report.md${NC}"
    echo -e "  or open in your editor"
fi

echo -e "\n${YELLOW}To analyze locally:${NC}"
echo -e "  1. Copy results to main results dir:"
echo -e "     ${BLUE}cp -r $LOCAL_DIR/* results/${NC}"
echo -e "  2. Run analysis:"
echo -e "     ${BLUE}source bin/activate && python analyze.py --results-dir results --plot${NC}"
