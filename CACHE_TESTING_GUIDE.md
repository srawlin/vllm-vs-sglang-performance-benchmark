# vLLM Cache Testing Guide

## Understanding vLLM Prefix Caching

**What is it?**
vLLM caches the KV (key-value) states from attention computations. When a new request shares a prefix with a previous request, vLLM reuses the cached states instead of recomputing them.

**Why it matters:**
- 10-20% faster TTFT for cached requests
- Huge benefits for RAG workloads (shared context)
- Critical for production cost/performance

## ❌ Common Mistake: Clearing Cache Between Tests

**WRONG Approach:**
```bash
# This defeats the purpose!
./run_with_cache_clear.sh vllm cache_reuse "1 10 50"
```

**Why it's wrong:**
- Cache warmup happens WITHIN a test (request 1 → request 80)
- Clearing between tests means you never see the benefit
- You're measuring "no cache" performance repeatedly

## ✅ Correct Cache Testing Strategy

### Test 1: Measure Cache Warmup Effect ⭐

**Goal:** See how cache improves performance as it warms up

```bash
# Let cache warm up naturally - DON'T clear!
./run_remote_benchmark.sh vllm cache_reuse "1"
```

**Expected behavior:**
```
Request 1:  450ms (cold - no cache)
Request 2:  420ms (starting to cache)
Request 3:  390ms (warming up)
Request 4+: 380ms (fully warm, 15% faster!)
```

**Analyze results:**
```bash
# Download results
./download_results.sh

# Analyze cache warmup
source bin/activate
python analyze_cache_warmup.py --results-dir results_from_vastai
```

### Test 2: Cache Persistence Across Concurrency Levels

**Goal:** Verify cache helps at different load levels

```bash
# Single session - cache accumulates!
./run_remote_benchmark.sh vllm cache_reuse "1 10 50"
```

**What happens:**
```
Concurrency 1:
  Request 1:      450ms (cold)
  Requests 2-100: 380ms (warm) ← Cache warming up

Concurrency 10:
  ALL requests:   380ms (already warm!) ← Cache persisted!

Concurrency 50:
  ALL requests:   385ms (still warm, slight contention)
```

**Key insight:** Cache built during c=1 helps c=10 and c=50 tests!

### Test 3: Compare Different Test Scenarios (Clear BETWEEN)

**Goal:** Measure cold start for different workload types

```bash
# Clear between DIFFERENT tests, not within same test
./clear_cache.sh
./run_remote_benchmark.sh vllm cache_reuse "1"

./clear_cache.sh
./run_remote_benchmark.sh vllm long_rag "1"

./clear_cache.sh
./run_remote_benchmark.sh vllm xl_rag "1"
```

**Why clear here:**
- Different tests have different prefixes
- We want clean comparison of cold start behavior
- Each test still shows warmup internally

### Test 4: Cache vs No-Cache Comparison

**Goal:** Quantify cache benefit

```bash
# Warm cache test
./run_remote_benchmark.sh vllm cache_reuse "1"
# Analyze: Average TTFT of requests 2-80 = 380ms

# Cold cache test (restart vLLM for each request - extreme!)
# Would need custom script, not recommended for normal testing
```

## 📊 Comprehensive Cache Test Suite

```bash
# 1. Deploy and prepare
./deploy_to_vastai.sh

# 2. Test cache warmup (sequential, low concurrency)
echo "=== Test 1: Cache Warmup ==="
./run_remote_benchmark.sh vllm cache_reuse "1"

# 3. Test cache under load (DON'T clear - cache persists!)
echo "=== Test 2: Cache at Different Loads ==="
./run_remote_benchmark.sh vllm cache_reuse "10 20 50"

# 4. Compare with non-cache test (different prefixes)
echo "=== Test 3: Regular RAG (different prefixes, less cache reuse) ==="
./clear_cache.sh
./run_remote_benchmark.sh vllm long_rag "1 10"

# 5. Download and analyze
./download_results.sh
cp -r results_from_vastai/* results/

# 6. Analyze cache warmup
source bin/activate
python analyze_cache_warmup.py --results-dir results

# 7. Generate full report
python analyze.py --results-dir results --plot
```

## 🔬 Advanced: Manual Cache Analysis

If you want to see raw per-request timing:

```bash
# SSH to Vast.ai
ssh -p $SSH_PORT -i ~/.ssh/vastai_ed25519 root@YOUR_VASTAI_IP
cd /workspace/llm-benchmark
source venv/bin/activate

# Run test
python benchmark.py \
  --server-url "http://localhost:8000" \
  --api-key "$VLLM_API_KEY" \
  --model "deepseek-ai/DeepSeek-R1-Distill-Llama-8B" \
  --framework vllm \
  --test-file data/cache_reuse.json \
  --concurrency 1 \
  --output-dir results

# Analyze per-request timing
python3 << 'EOF'
import json
import glob

files = glob.glob('results/vllm_cache_reuse_c1_*_raw.json')
latest = sorted(files)[-1]

with open(latest) as f:
    data = json.load(f)

print("Request-by-request TTFT:")
for i in range(min(30, len(data))):
    ttft_ms = data[i]['ttft'] * 1000
    print(f"Request {i+1:3d}: {ttft_ms:6.1f}ms")
EOF
```


## 🐛 Troubleshooting Cache Issues

### Problem: No cache speedup visible

**Check 1: Is prefix caching enabled?**
```bash
ssh -p $SSH_PORT -i ~/.ssh/vastai_ed25519 root@YOUR_VASTAI_IP
ps aux | grep vllm
# Look for: --enable-prefix-caching
```

**Check 2: Are requests sharing prefixes?**
```bash
# Verify test data has shared prefix
python3 << 'EOF'
import json
data = json.load(open('data/cache_reuse.json'))
prefix1 = data[0]['prompt'][:100]
prefix2 = data[1]['prompt'][:100]
print(f"Match: {prefix1 == prefix2}")
print(f"Prefix: {prefix1}")
EOF
```

**Check 3: Is cache TTL too short?**
- vLLM cache has a TTL (time-to-live)
- If requests are too slow, cache might expire
- Run with lower concurrency (c=1) first

### Problem: Cache speedup decreases at high concurrency

**Expected behavior:**
```
c=1:   15% speedup (baseline)
c=10:  14% speedup (still good)
c=50:  10% speedup (cache contention)
c=100: 8% speedup  (more contention)
```

This is normal - high concurrency causes cache eviction.

## 📝 Summary: When to Clear Cache

| Scenario | Clear Cache? | Why |
|----------|--------------|-----|
| **Within a single test** | ❌ NO | You want to see warmup effect |
| **Between concurrency levels** | ❌ NO | Cache persistence is realistic |
| **Between different test files** | ✅ YES | Avoid cross-contamination |
| **Between test runs (same file)** | ⚠️ MAYBE | Depends on what you're measuring |
| **Testing cold start behavior** | ✅ YES | Simulating first request |

## 🚀 Quick Start

```bash
# Best practice: Test cache warmup without clearing
./run_remote_benchmark.sh vllm cache_reuse "1"
./download_results.sh
source bin/activate
python analyze_cache_warmup.py
```

You'll see exactly how cache improves performance! 📈
