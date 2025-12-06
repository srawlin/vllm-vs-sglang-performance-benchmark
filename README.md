# LLM Inference Benchmark Suite

A comprehensive benchmarking toolkit for comparing LLM serving frameworks (vLLM, SGLang, TensorRT-LLM) on the same hardware.

## Features

- **Framework-agnostic**: Works with any OpenAI-compatible API
- **Comprehensive metrics**: TTFT, TPOT, throughput, latency percentiles
- **Concurrency testing**: Test performance under various load levels
- **Cache testing**: Evaluate prefix caching effectiveness
- **Automated analysis**: Generate reports and comparison visualizations
- **Reusable test data**: Consistent test scenarios across frameworks

## Quick Start

### 1. Configure Environment (Important!)

**Before running benchmarks**, configure your environment variables:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual credentials
nano .env

# Source the environment
source .env
```

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

### 2. Install Dependencies

```bash
cd llm-benchmark
pip install -r requirements.txt
```

### 3. Generate Test Data

```bash
python test_data.py
```

This creates test prompts of various sizes in `./data/`:
- `short_chat.json` - 32 token prompts (100 samples)
- `medium_chat.json` - 512 token prompts (100 samples)
- `long_rag.json` - 2048 token prompts (50 samples)
- `xl_rag.json` - 8192 token prompts (20 samples)
- `cache_reuse.json` - Prefix caching test (80 samples)

### 4. Run Benchmark

#### Test vLLM

```bash
python benchmark.py \
  --server-url "http://localhost:8000" \
  --api-key "your-vllm-api-key-here" \
  --model "deepseek-ai/DeepSeek-R1-Distill-Llama-8B" \
  --framework vllm \
  --test-file data/medium_chat.json \
  --concurrency 1 10 50 \
  --output-dir results
```

#### Test SGLang (after switching servers)

```bash
python benchmark.py \
  --server-url "https://your-sglang-instance.trycloudflare.com" \
  --api-key "YOUR_SGLANG_TOKEN" \
  --model "deepseek-ai/DeepSeek-R1-Distill-Llama-8B" \
  --framework sglang \
  --test-file data/medium_chat.json \
  --concurrency 1 10 50 \
  --output-dir results
```

### 5. Analyze Results

```bash
python analyze.py --results-dir results --plot
```

This generates:
- `benchmark_report.md` - Comprehensive comparison report
- `throughput_comparison.png` - Throughput vs concurrency plot
- `latency_comparison.png` - TTFT and TPOT comparison plots

## Benchmark Workflow

### Complete Test Suite

Run all test scenarios to get comprehensive comparison:

```bash
# 1. Generate test data
python test_data.py

# 2. Test vLLM across all scenarios
for test in data/*.json; do
  python benchmark.py \
    --server-url "$VLLM_URL" \
    --api-key "$VLLM_TOKEN" \
    --model "$MODEL_NAME" \
    --framework vllm \
    --test-file "$test" \
    --concurrency 1 10 50 100 \
    --output-dir results
  sleep 10
done

# 3. Switch to SGLang server and repeat
for test in data/*.json; do
  python benchmark.py \
    --server-url "$SGLANG_URL" \
    --api-key "$SGLANG_TOKEN" \
    --model "$MODEL_NAME" \
    --framework sglang \
    --test-file "$test" \
    --concurrency 1 10 50 100 \
    --output-dir results
  sleep 10
done

# 4. Generate analysis
python analyze.py --results-dir results --plot
```

## Test Scenarios Explained

### Short Chat (`short_chat.json`)
- **Size**: ~32 tokens
- **Use case**: Quick Q&A, chat messages
- **Key metric**: TTFT (responsiveness)

### Medium Chat (`medium_chat.json`)
- **Size**: ~512 tokens
- **Use case**: Document summaries, moderate context
- **Key metrics**: TTFT, throughput balance

### Long RAG (`long_rag.json`)
- **Size**: ~2048 tokens
- **Use case**: RAG with context, document Q&A
- **Key metrics**: Throughput, TPOT stability

### XL RAG (`xl_rag.json`)
- **Size**: ~8192 tokens
- **Use case**: Full document analysis, long context
- **Key metrics**: Memory efficiency, throughput

### Cache Reuse (`cache_reuse.json`)
- **Special**: Shared 2000-token prefix, different suffixes
- **Use case**: Testing prefix caching effectiveness
- **Key metrics**: Cache hit rate, latency reduction

## Understanding the Metrics

### TTFT (Time to First Token)
- **What**: How quickly the model starts responding
- **Importance**: User-perceived responsiveness
- **Good value**: <100ms for chat, <500ms for long context

### TPOT (Time Per Output Token)
- **What**: Average time to generate each token
- **Importance**: Streaming smoothness
- **Good value**: <10ms for smooth streaming

### Throughput (tokens/second)
- **What**: Total tokens generated per second
- **Importance**: System capacity, cost efficiency
- **Good value**: Depends on model size (100+ for 8B models)

### Concurrency Scaling
- **What**: Performance as concurrent requests increase
- **Importance**: Real-world production capacity
- **Good behavior**: Throughput increases linearly, TTFT stays stable

## Output Files

### Raw Results
`{framework}_{test}_{timestamp}_raw.json`
- Complete data for every request
- Useful for detailed analysis and debugging

### Summary Results
`{framework}_{test}_{timestamp}_summary.json`
- Aggregated statistics
- Used by analyzer for comparisons

### Reports
`benchmark_report.md`
- Executive summary
- Full comparison tables
- Per-test analysis
- Recommendations by use case

## Advanced Usage

### Custom Test Data

Create your own test JSON:

```json
[
  {
    "id": "test_001",
    "prompt": "Your custom prompt here",
    "type": "chat",
    "target_tokens": 512,
    "max_tokens": 128
  }
]
```

### Testing Cache Performance

The `cache_reuse.json` test specifically measures prefix caching:
- First request: Cold cache (baseline)
- Subsequent requests: Warm cache (should be faster)
- Calculate speedup: `(cold_time - warm_time) / cold_time * 100%`

Expected improvements:
- vLLM: 13-20% faster
- TensorRT-LLM: 20-35% faster
- SGLang: 2-6× faster (best for RAG workloads)

### Multi-GPU Testing

Ensure your server is configured with tensor parallelism:

**vLLM**:
```bash
--tensor-parallel-size 2
```

**SGLang**:
```bash
--tp 2
```

Then compare single GPU vs TP=2 throughput to measure scaling efficiency.

## Troubleshooting

### SSL Certificate Errors
The benchmark uses `ssl=False` for self-signed certs. If you still get errors, verify your server URL is correct.

### Timeout Errors
Increase timeout for large prompts:
```bash
--timeout 600  # 10 minutes
```

### Memory Errors
Reduce concurrency or prompt size:
```bash
--concurrency 1 5 10  # Lower concurrency
```

### No Results
Check that:
1. Server URL is accessible
2. API key is correct
3. Model name matches server configuration

## Hardware Specs

For reproducible results, document your hardware:

```
GPU: 2x NVIDIA H100 SXM (80GB each)
CPU: [Your CPU]
RAM: [Your RAM]
Framework versions:
  - vLLM: [version]
  - SGLang: [version]
  - TensorRT-LLM: [version]
```

## Example Results

After running benchmarks, your `results/` directory will contain:

```
results/
├── vllm_medium_chat_c1_20251205_143022_summary.json
├── vllm_medium_chat_c1_20251205_143022_raw.json
├── vllm_medium_chat_c10_20251205_143125_summary.json
├── vllm_medium_chat_c10_20251205_143125_raw.json
├── sglang_medium_chat_c1_20251205_150022_summary.json
├── sglang_medium_chat_c1_20251205_150022_raw.json
├── benchmark_report.md
├── throughput_comparison.png
└── latency_comparison.png
```

## Contributing

To add new test scenarios:
1. Edit `test_data.py` to add new prompt generators
2. Run `python test_data.py` to regenerate data
3. Benchmark with your new test files

## License

MIT
