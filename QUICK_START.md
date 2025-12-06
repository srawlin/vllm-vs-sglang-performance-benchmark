# Quick Start Guide

## TL;DR - 3 Commands to Run Benchmarks

```bash
# 1. Deploy to Vast.ai (one-time setup)
./deploy_to_vastai.sh

# 2. Run benchmark
./run_remote_benchmark.sh vllm medium_chat "1 10 50"

# 3. Download results
./download_results.sh
```

## What You Get

- **Accurate TTFT**: ~50ms instead of ~2000ms (43× improvement)
- **No network latency**: Direct localhost connection
- **Production-grade results**: Comparable to published benchmarks
- **Ready to compare**: Same tests work for vLLM, SGLang, TensorRT-LLM

## SSH Connection
```
Host: root@YOUR_VASTAI_IP
Port: $SSH_PORT
Key: ~/.ssh/vastai_ed25519
```

## Full Workflow

### Test vLLM
```bash
./deploy_to_vastai.sh
./run_remote_benchmark.sh vllm short_chat "1 5 10 20"
./run_remote_benchmark.sh vllm medium_chat "1 10 50"
./run_remote_benchmark.sh vllm cache_reuse "1 10"
./download_results.sh
```

### Test SGLang (after switching on Vast.ai)
```bash
export SGLANG_API_KEY="your_token"
./run_remote_benchmark.sh sglang short_chat "1 5 10 20"
./run_remote_benchmark.sh sglang medium_chat "1 10 50"
./run_remote_benchmark.sh sglang cache_reuse "1 10"
./download_results.sh
```

### Compare Results
```bash
cp -r results_from_vastai/* results/
source bin/activate
python analyze.py --results-dir results --plot
cat results/benchmark_report.md
```

## Available Tests

- `short_chat` - 32 tokens, 100 samples (latency testing)
- `medium_chat` - 512 tokens, 100 samples (balanced)
- `long_rag` - 2048 tokens, 50 samples (RAG workloads)
- `xl_rag` - 8192 tokens, 20 samples (long context)
- `cache_reuse` - 2048 tokens, 80 samples (prefix caching)
- `code_short` - 128 tokens, 50 samples
- `code_medium` - 1024 tokens, 30 samples

## Example Output

```
📊 Benchmark Results Summary
────────────────────────────────────────────
Framework:        vllm
Test:             medium_chat_c50
Concurrency:      50
Duration:         45.23s

🎯 Request Stats:
  Successful:     100
  Success Rate:   100.0%

⚡ Latency:
  TTFT Mean:      52ms  ← Real performance!
  TTFT P95:       85ms
  TPOT Mean:      15ms

🚀 Throughput:
  Tokens/sec:     2847
  Requests/sec:   22.1
```

## Troubleshooting

**Can't connect?**
```bash
ssh -p $SSH_PORT -i ~/.ssh/vastai_ed25519 root@YOUR_VASTAI_IP "echo test"
```

**Re-deploy everything:**
```bash
./deploy_to_vastai.sh
```

**See full guide:**
```bash
cat VASTAI_GUIDE.md
```

---

**You're now running production-grade LLM benchmarks! 🚀**
