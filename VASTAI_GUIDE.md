# Running Benchmarks on Vast.ai (Zero Network Latency)

This guide shows how to run benchmarks directly on your Vast.ai instance for accurate, production-grade results without network latency contamination.

## Why Run on Vast.ai?

**Problem with local testing:**
```
Your Mac → Internet → Cloudflare → Vast.ai → vLLM
         [~2000ms total latency]
```

**Solution - Run locally on Vast.ai:**
```
Vast.ai → localhost → vLLM
        [~1ms latency]
```

This gives you **2000× lower latency** and results comparable to published benchmarks.

## Quick Start

### 1. Deploy Benchmark Suite

```bash
# Make scripts executable
chmod +x *.sh

# Deploy to Vast.ai (one-time setup)
./deploy_to_vastai.sh
```

This will:
- ✓ Upload benchmark code to `/workspace/llm-benchmark/`
- ✓ Install Python dependencies
- ✓ Generate test data
- ✓ Verify vLLM is running

### 2. Run Benchmarks

**Option A: Run remotely (easiest)**
```bash
# Run a single test
./run_remote_benchmark.sh vllm medium_chat "1 5 10 20 50"

# Test different scenarios
./run_remote_benchmark.sh vllm short_chat "1 10 50"
./run_remote_benchmark.sh vllm long_rag "1 5 10"
./run_remote_benchmark.sh vllm cache_reuse "1 10"
```

**Option B: SSH in and run manually (full control)**
```bash
# Connect to Vast.ai (replace with your instance IP)
ssh -p $SSH_PORT -i ~/.ssh/vastai_ed25519 root@YOUR_VASTAI_IP

# Navigate to benchmark directory
cd /workspace/llm-benchmark

# Activate Python environment
source venv/bin/activate

# Run comprehensive test suite
./run_local_benchmark.sh

# Or run individual tests
python benchmark.py \
  --server-url "http://localhost:8000" \
  --api-key "$VLLM_API_KEY" \
  --model "deepseek-ai/DeepSeek-R1-Distill-Llama-8B" \
  --framework vllm \
  --test-file data/medium_chat.json \
  --concurrency 1 5 10 50 100 \
  --output-dir results
```

### 3. Download Results

```bash
# Download all results to local machine
./download_results.sh

# Results will be in ./results_from_vastai/
```

### 4. Analyze Results

**Option A: Analyze on Vast.ai**
```bash
ssh -p $SSH_PORT -i ~/.ssh/vastai_ed25519 root@YOUR_VASTAI_IP
cd /workspace/llm-benchmark
source venv/bin/activate
python analyze.py --results-dir results --plot
cat results/benchmark_report.md
```

**Option B: Analyze locally**
```bash
cp -r results_from_vastai/* results/
source bin/activate
python analyze.py --results-dir results --plot
cat results/benchmark_report.md
```

## Testing Multiple Frameworks

### vLLM (Current Setup)
```bash
./run_remote_benchmark.sh vllm medium_chat "1 10 50 100"
```

### SGLang (After switching)
```bash
# 1. Stop vLLM on Vast.ai
# 2. Start SGLang on same instance
# 3. Run benchmarks
export SGLANG_API_KEY="your_sglang_token"
./run_remote_benchmark.sh sglang medium_chat "1 10 50 100"
```

### TensorRT-LLM
```bash
export TENSORRT_API_KEY="your_token"
./run_remote_benchmark.sh tensorrt medium_chat "1 10 50 100"
```

## Complete Benchmark Suite

Run all tests across all scenarios:

```bash
# SSH into Vast.ai
ssh -p $SSH_PORT -i ~/.ssh/vastai_ed25519 root@YOUR_VASTAI_IP
cd /workspace/llm-benchmark
source venv/bin/activate

# Run comprehensive suite
for test in short_chat medium_chat long_rag xl_rag code_short code_medium cache_reuse; do
  echo "Running $test..."
  python benchmark.py \
    --server-url "http://localhost:8000" \
    --api-key "$VLLM_API_KEY" \
    --model "deepseek-ai/DeepSeek-R1-Distill-Llama-8B" \
    --framework vllm \
    --test-file "data/${test}.json" \
    --concurrency 1 5 10 20 50 100 \
    --output-dir results
  sleep 5
done

# Analyze all results
python analyze.py --results-dir results --plot
```

## Comparing Frameworks Side-by-Side

### Day 1: Test vLLM
```bash
# Deploy and test vLLM
./deploy_to_vastai.sh
./run_remote_benchmark.sh vllm medium_chat "1 10 50 100"
./run_remote_benchmark.sh vllm cache_reuse "1 10"
./download_results.sh
```

### Day 2: Test SGLang
```bash
# On Vast.ai: Stop vLLM, start SGLang
# Then from local machine:
export SGLANG_API_KEY="your_token"
./run_remote_benchmark.sh sglang medium_chat "1 10 50 100"
./run_remote_benchmark.sh sglang cache_reuse "1 10"
./download_results.sh
```

### Day 3: Compare Results
```bash
# All results are now in results_from_vastai/
cp -r results_from_vastai/* results/
source bin/activate
python analyze.py --results-dir results --plot

# View report
cat results/benchmark_report.md
open results/throughput_comparison.png
open results/latency_comparison.png
```

## Expected Performance Improvements

Running on Vast.ai vs your local Mac:

| Metric | Local (Mac) | Remote (Vast.ai) | Improvement |
|--------|-------------|------------------|-------------|
| **TTFT** | 2170ms | ~50ms | **43× faster** |
| **Network overhead** | ~2000ms | ~1ms | **2000× lower** |
| **Throughput** | Same | Same | No change |
| **Result accuracy** | ❌ Contaminated | ✅ Accurate | - |

## Available Test Scenarios

| Test | Description | Prompt Size | Count | Best For |
|------|-------------|-------------|-------|----------|
| `short_chat` | Quick Q&A | 32 tokens | 100 | Latency testing |
| `medium_chat` | Standard chat | 512 tokens | 100 | Balanced testing |
| `long_rag` | RAG with context | 2048 tokens | 50 | Context handling |
| `xl_rag` | Full documents | 8192 tokens | 20 | Long context |
| `code_short` | Quick code tasks | 128 tokens | 50 | Code generation |
| `code_medium` | Complex code | 1024 tokens | 30 | Code reasoning |
| `cache_reuse` | **Prefix caching** | 2048 tokens | 80 | Cache efficiency |

## Troubleshooting

### Can't connect to SSH
```bash
# Test connection
ssh -p $SSH_PORT -i ~/.ssh/vastai_ed25519 root@YOUR_VASTAI_IP "echo 'Connected'"

# Check SSH key permissions
chmod 600 ~/.ssh/vastai_ed25519
```

### vLLM not responding on localhost
```bash
# SSH into Vast.ai and check vLLM status
ssh -p $SSH_PORT -i ~/.ssh/vastai_ed25519 root@YOUR_VASTAI_IP
curl http://localhost:8000/v1/models

# Check vLLM logs
docker ps
docker logs <vllm_container_id>
```

### Python dependencies missing
```bash
# Re-run deployment
./deploy_to_vastai.sh
```

### API key errors
The benchmark auto-detects localhost and may not need a token. If you get auth errors:
```bash
# Find the actual token on Vast.ai
ssh -p $SSH_PORT -i ~/.ssh/vastai_ed25519 root@YOUR_VASTAI_IP
env | grep TOKEN
```

## Cost Optimization

**Estimated costs (Vast.ai 2x H100 SXM):**
- GPU instance: ~$2-4/hour
- Benchmark runtime: ~30-60 minutes per framework
- Total per framework: ~$1-4

**Tips:**
1. Run all tests in one session
2. Stop instance immediately after downloading results
3. Use lower concurrency for initial testing

## Next Steps

1. **Deploy**: `./deploy_to_vastai.sh`
2. **Run vLLM tests**: `./run_remote_benchmark.sh vllm medium_chat "1 10 50"`
3. **Download**: `./download_results.sh`
4. **Switch to SGLang** on Vast.ai
5. **Run SGLang tests**: `./run_remote_benchmark.sh sglang medium_chat "1 10 50"`
6. **Compare**: `python analyze.py --results-dir results --plot`

You'll have production-grade, peer-reviewed quality benchmark results! 🚀
