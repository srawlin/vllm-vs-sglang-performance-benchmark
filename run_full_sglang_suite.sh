#!/bin/bash
# Complete SGLang benchmark suite for comparison report
# Generates all data needed for comprehensive analysis

set -e

FRAMEWORK="sglang"

echo "=========================================="
echo "SGLang Complete Benchmark Suite"
echo "=========================================="
echo "This will run ~15-20 tests (30-60 minutes)"
echo ""

# Verify we're ready
if [ ! -d "data" ]; then
    echo "Error: Run ./deploy_to_vastai.sh first"
    exit 1
fi

# Section 3: Latency Performance
echo ""
echo "=== SECTION 3: Latency Performance ==="
echo "Testing TTFT and TPOT across prompt sizes..."

echo "→ Short prompts (chat)..."
./run_remote_benchmark.sh $FRAMEWORK short_chat "1 5 10 20 50 100"

echo "→ Medium prompts (standard)..."
./run_remote_benchmark.sh $FRAMEWORK medium_chat "1 5 10 20 50 100"

# Section 4: Throughput Performance
echo ""
echo "=== SECTION 4: Throughput Performance ==="
echo "Testing scaling and saturation..."

echo "→ Throughput scaling test..."
./run_remote_benchmark.sh $FRAMEWORK medium_chat "1 10 20 50 100 150 200"

# Section 5: Cache Performance
echo ""
echo "=== SECTION 5: Cache Performance ==="
echo "Testing prefix caching effectiveness..."

echo "→ Cache warmup (sequential)..."
./run_remote_benchmark.sh $FRAMEWORK cache_reuse "1"

echo "→ Cache under concurrency..."
./run_remote_benchmark.sh $FRAMEWORK cache_reuse "10 20 50"

echo "→ Long context RAG..."
./run_remote_benchmark.sh $FRAMEWORK long_rag "1 5 10 20 50"

echo "→ Very long context RAG..."
./run_remote_benchmark.sh $FRAMEWORK xl_rag "1 5 10 20"

# Section 7: Workload-Specific
echo ""
echo "=== SECTION 7: Workload-Specific Tests ==="
echo "Testing different use cases..."

echo "→ Code generation (short)..."
./run_remote_benchmark.sh $FRAMEWORK code_short "1 10 50"

echo "→ Code generation (medium)..."
./run_remote_benchmark.sh $FRAMEWORK code_medium "1 10 50"

# Section 8: Stress Test
echo ""
echo "=== SECTION 8: Stability & Stress Test ==="
echo "Testing maximum load..."

echo "→ High concurrency stress..."
./run_remote_benchmark.sh $FRAMEWORK medium_chat "200 250"

# Download results
echo ""
echo "=== Downloading Results ==="
./download_results.sh

# Generate analysis
echo ""
echo "=== Generating Analysis ==="
cp -r results_from_vastai/* results/
source bin/activate

echo "→ Cache warmup analysis..."
python analyze_cache_warmup.py --results-dir results > results/cache_analysis_sglang.txt

echo "→ Full comparison report..."
python analyze.py --results-dir results --plot

echo ""
echo "=========================================="
echo "✓ SGLang Benchmark Suite Complete!"
echo "=========================================="
echo ""
echo "Results saved in:"
echo "  - results/benchmark_report.md (now includes SGLang + vLLM)"
echo "  - results/cache_analysis_sglang.txt"
echo "  - results/*.png (comparison charts)"
echo ""
echo "Next steps:"
echo "1. Review comparison: cat results/benchmark_report.md"
echo "2. View charts: open results/throughput_comparison.png"
echo "3. Update BENCHMARK_REPORT.md with SGLang data"
echo ""
echo "🎉 You now have complete vLLM vs SGLang comparison data!"
