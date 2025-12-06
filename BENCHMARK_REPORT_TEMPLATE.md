# LLM Serving Framework Comparison Report

**Hardware:** 2× NVIDIA H100 SXM (80GB each)
**Model:** DeepSeek-R1-Distill-Llama-8B (8B parameters)
**Date:** [DATE]
**Frameworks Tested:** vLLM, SGLang, [TensorRT-LLM]

**Key Visualizations:**
- Chart 1: TTFT vs Concurrency (§3.1) - Responsiveness at scale
- Chart 2: Throughput vs Concurrency (§4.1) - System capacity
- Chart 3: Cache Warmup Curve (§5.1) - Cache effectiveness (key differentiator)

---

## 1. Executive Summary

### 1.1 Quick Recommendation Matrix

| Use Case | Recommended Framework | Key Reason |
|----------|----------------------|------------|
| Interactive Chat (High Concurrency) | [TBD] | [TBD] |
| RAG with Shared Context | [TBD] | [TBD] |
| Multi-User Production API | [TBD] | [TBD] |
| Agentic Workflows / Tool Use | [TBD] | [TBD] |
| Single-User Application | [TBD] | [TBD] |
| Batch Document Processing | [TBD] | [TBD] |
| Code Generation | [TBD] | [TBD] |

### 1.2 Performance Highlights

**Latency (TTFT) Winner:** [TBD]
- P95 TTFT: [X]ms at [Y] concurrency

**Throughput Winner:** [TBD]
- Peak: [X] tokens/sec at [Y] concurrency

**Cache Efficiency Winner:** [TBD]
- Speedup: [X]% (cold vs warm cache)

**Multi-GPU Scaling Winner:** [TBD]
- Scaling factor: [X]× (TP=2 vs TP=1)

**Best Overall for Production:** [TBD]

### 1.3 Cost Efficiency

_Based on H100 rental costs and measured throughput_

| Framework | Cost per 1M Tokens | Relative Efficiency |
|-----------|-------------------|---------------------|
| vLLM | $[TBD] | [TBD]× baseline |
| SGLang | $[TBD] | [TBD]× baseline |
| TensorRT-LLM | $[TBD] | [TBD]× baseline |

---

## 2. Test Methodology

### 2.1 Hardware Configuration

```
GPU: 2× NVIDIA H100 SXM (80GB VRAM each)
Total VRAM: 160GB
CPU: [TBD]
RAM: [TBD]
Interconnect: NVLink (for multi-GPU)
Tensor Parallelism: TP=2 (across both GPUs)
```

### 2.2 Software Configuration

| Framework | Version | Configuration |
|-----------|---------|---------------|
| vLLM | [TBD] | `--tensor-parallel-size 2 --enable-prefix-caching --max-model-len [TBD]` |
| SGLang | [TBD] | `--tp 2 --chunked-prefill-size [TBD] --mem-fraction-static [TBD]` |
| TensorRT-LLM | [TBD] | `--world_size 2 --enable_chunked_context` |

**Model:** DeepSeek-R1-Distill-Llama-8B
**Precision:** [TBD - FP16/BF16/INT8]
**Max Context Length:** [TBD]

### 2.3 Test Data

| Test Name | Prompt Size | Samples | Description | Use Case |
|-----------|-------------|---------|-------------|----------|
| `short_chat` | 32 tokens | 100 | Quick questions | Interactive chat |
| `medium_chat` | 512 tokens | 100 | Standard conversations | General purpose |
| `long_rag` | 2048 tokens | 50 | Document Q&A | RAG applications |
| `xl_rag` | 8192 tokens | 20 | Full documents | Long-context analysis |
| `cache_reuse` | 2048 tokens | 80 | Shared prefix testing | RAG with cache |
| `code_short` | 128 tokens | 50 | Code snippets | Code completion |
| `code_medium` | 1024 tokens | 30 | Complex code | Code generation |

**Data Quality:** Realistic technical content (no Lorem ipsum)
**Prefix Sharing (cache_reuse):** 2000-token shared context with 80 different questions

### 2.4 Concurrency Levels Tested

- **Low:** 1, 5, 10 (baseline, single-user)
- **Medium:** 20, 50 (typical production)
- **High:** 100, 150, 200 (stress testing)

### 2.5 Metrics Collected

**Latency Metrics:**
- TTFT (Time to First Token): User-perceived responsiveness
- TPOT (Time Per Output Token): Streaming smoothness
- End-to-end latency: Total request time
- Percentiles: P50, P95, P99

**Throughput Metrics:**
- Tokens per second: System capacity
- Requests per second: Concurrent request handling
- Scaling efficiency: Linear vs actual scaling

**Cache Metrics:**
- Cold cache baseline: First request performance
- Warm cache speedup: Subsequent request improvement
- Cache hit rate: Prefix reuse effectiveness
- Stabilization point: When cache fully warms

**Reliability Metrics:**
- Success rate: % of successful requests
- Error types: Categorization of failures
- Resource utilization: GPU memory, CPU usage

---

## 3. Latency Performance (Interactive Responsiveness)

### 3.1 Time to First Token (TTFT)

_Lower is better - measures how quickly the model starts responding_

#### TTFT by Concurrency Level

| Framework | c=1 | c=10 | c=50 | c=100 | Winner |
|-----------|-----|------|------|-------|--------|
| **vLLM** | [TBD]ms | [TBD]ms | [TBD]ms | [TBD]ms | - |
| **SGLang** | [TBD]ms | [TBD]ms | [TBD]ms | [TBD]ms | - |
| **TensorRT-LLM** | [TBD]ms | [TBD]ms | [TBD]ms | [TBD]ms | - |

_All values are P95 latencies_

#### TTFT by Prompt Size (c=10)

| Framework | Short (32t) | Medium (512t) | Long (2048t) | XL (8192t) |
|-----------|-------------|---------------|--------------|------------|
| **vLLM** | [TBD]ms | [TBD]ms | [TBD]ms | [TBD]ms |
| **SGLang** | [TBD]ms | [TBD]ms | [TBD]ms | [TBD]ms |
| **TensorRT-LLM** | [TBD]ms | [TBD]ms | [TBD]ms | [TBD]ms |

#### Chart: TTFT vs Concurrency
```
[INSERT CHART: Line graph showing TTFT (y-axis) vs Concurrency (x-axis) for all frameworks]
```

**Winner:** [TBD]
**Key Finding:** [TBD]

### 3.2 Time Per Output Token (TPOT)

_Lower is better - measures token generation speed and streaming smoothness_

#### TPOT Comparison

| Framework | Mean (ms) | P95 (ms) | Stability Score |
|-----------|-----------|----------|-----------------|
| **vLLM** | [TBD] | [TBD] | [TBD] |
| **SGLang** | [TBD] | [TBD] | [TBD] |
| **TensorRT-LLM** | [TBD] | [TBD] | [TBD] |

_Tested at concurrency=50, medium_chat workload_

**Winner:** [TBD]
**Key Finding:** [TBD]

### 3.3 End-to-End Latency Distribution

#### Latency Percentiles (c=50, medium_chat)

| Framework | P50 | P95 | P99 | Max |
|-----------|-----|-----|-----|-----|
| **vLLM** | [TBD]s | [TBD]s | [TBD]s | [TBD]s |
| **SGLang** | [TBD]s | [TBD]s | [TBD]s | [TBD]s |
| **TensorRT-LLM** | [TBD]s | [TBD]s | [TBD]s | [TBD]s |

**Key Finding:** [TBD - discuss tail latencies and consistency]

### 3.4 Latency Summary

**Best for Low-Latency Applications:** [TBD]
**Most Consistent Latency:** [TBD]
**Best Tail Latency (P99):** [TBD]

---

## 4. Throughput Performance (System Capacity)

### 4.1 Throughput Scaling with Concurrency

#### Tokens per Second by Concurrency

| Framework | c=1 | c=10 | c=50 | c=100 | c=200 | Peak |
|-----------|-----|------|------|-------|-------|------|
| **vLLM** | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] tok/s |
| **SGLang** | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] tok/s |
| **TensorRT-LLM** | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] | [TBD] tok/s |

#### Chart: Throughput Scaling
```
[INSERT CHART: Line graph showing throughput vs concurrency]
```

**Scaling Analysis:**
- **Linear scaling:** [TBD - which framework scales most linearly?]
- **Saturation point:** [TBD - at what concurrency does each saturate?]

### 4.2 Maximum Throughput Achieved

| Framework | Peak Throughput | At Concurrency | Efficiency |
|-----------|----------------|----------------|------------|
| **vLLM** | [TBD] tok/s | c=[TBD] | [TBD]% of theoretical |
| **SGLang** | [TBD] tok/s | c=[TBD] | [TBD]% of theoretical |
| **TensorRT-LLM** | [TBD] tok/s | c=[TBD] | [TBD]% of theoretical |

**Winner:** [TBD]
**Throughput Advantage:** [TBD]× over runner-up

### 4.3 Requests Per Second

#### RPS by Concurrency (medium_chat workload)

| Framework | c=10 | c=50 | c=100 | c=200 |
|-----------|------|------|-------|-------|
| **vLLM** | [TBD] | [TBD] | [TBD] | [TBD] |
| **SGLang** | [TBD] | [TBD] | [TBD] | [TBD] |
| **TensorRT-LLM** | [TBD] | [TBD] | [TBD] | [TBD] |

### 4.4 Throughput Summary

**Best for High-Throughput Production:** [TBD]
**Most Efficient Scaling:** [TBD]
**Maximum Concurrent Requests:** [TBD] (framework can handle [X] concurrent)

---

## 5. Cache Performance (Critical for RAG/Agents)

### 5.1 Prefix Cache Effectiveness

#### Cache Warmup Analysis

**Test:** `cache_reuse` - 80 requests with shared 2000-token prefix

| Framework | First Request (Cold) | Avg Subsequent (Warm) | Speedup | Winner |
|-----------|---------------------|----------------------|---------|--------|
| **vLLM** | [TBD]ms | [TBD]ms | [TBD]% | - |
| **SGLang** | [TBD]ms | [TBD]ms | [TBD]% | - |
| **TensorRT-LLM** | [TBD]ms | [TBD]ms | [TBD]% | - |

**Expected Range:**
- vLLM: 13-20% speedup
- SGLang: 100-600% speedup (up to 6× faster)
- TensorRT-LLM: 20-35% speedup

#### Chart: Cache Warmup Curve
```
[INSERT CHART: TTFT vs Request Number (1-80) showing cache warmup]
```

### 5.2 Cache Performance Under Load

#### Cache Speedup at Different Concurrency Levels

| Framework | c=1 Speedup | c=10 Speedup | c=50 Speedup | Cache Stability |
|-----------|-------------|--------------|--------------|-----------------|
| **vLLM** | [TBD]% | [TBD]% | [TBD]% | [TBD] |
| **SGLang** | [TBD]% | [TBD]% | [TBD]% | [TBD] |
| **TensorRT-LLM** | [TBD]% | [TBD]% | [TBD]% | [TBD] |

**Key Finding:** [TBD - does cache benefit persist under high load?]

### 5.3 RAG Workload Performance

#### Long Context with Repeated Queries (long_rag test)

| Framework | Cold Cache TTFT | Warm Cache TTFT | Throughput (warm) |
|-----------|----------------|-----------------|-------------------|
| **vLLM** | [TBD]ms | [TBD]ms | [TBD] tok/s |
| **SGLang** | [TBD]ms | [TBD]ms | [TBD] tok/s |
| **TensorRT-LLM** | [TBD]ms | [TBD]ms | [TBD] tok/s |

### 5.4 Cache Stabilization Point

**How many requests before cache is fully warm?**

| Framework | Stabilization Point | 90% of Max Speedup |
|-----------|--------------------|--------------------|
| **vLLM** | Request #[TBD] | Request #[TBD] |
| **SGLang** | Request #[TBD] | Request #[TBD] |
| **TensorRT-LLM** | Request #[TBD] | Request #[TBD] |

### 5.5 Cache Performance Summary

**Best Cache Efficiency:** [TBD]
**Most Important for:** RAG applications with repeated context, agentic workflows
**Key Differentiator:** [TBD - explain why this matters for production]

**Recommendation:**
- For RAG with >50% prefix reuse: Use [TBD]
- For diverse prompts: Use [TBD]

---

## 6. Multi-GPU Scaling (Tensor Parallelism TP=2)

### 6.1 Scaling Efficiency

**Theoretical:** 2× speedup with TP=2
**Realistic Target:** 1.8-1.9× (due to inter-GPU communication overhead)

#### TP=2 Scaling Factor

| Framework | TP=1 Baseline | TP=2 Actual | Scaling Factor | Efficiency |
|-----------|---------------|-------------|----------------|------------|
| **vLLM** | [TBD] tok/s | [TBD] tok/s | [TBD]× | [TBD]% |
| **SGLang** | [TBD] tok/s | [TBD] tok/s | [TBD]× | [TBD]% |
| **TensorRT-LLM** | [TBD] tok/s | [TBD] tok/s | [TBD]× | [TBD]% |

_Note: TP=1 baseline requires separate test run on single GPU_

### 6.2 Memory Distribution

#### GPU Memory Utilization per Device

| Framework | GPU 0 | GPU 1 | Balance | Total |
|-----------|-------|-------|---------|-------|
| **vLLM** | [TBD]GB | [TBD]GB | [TBD]% | [TBD]GB |
| **SGLang** | [TBD]GB | [TBD]GB | [TBD]% | [TBD]GB |
| **TensorRT-LLM** | [TBD]GB | [TBD]GB | [TBD]% | [TBD]GB |

### 6.3 Maximum Concurrent Requests (TP=2)

| Framework | Max Stable Concurrency | At What Cost |
|-----------|----------------------|--------------|
| **vLLM** | [TBD] | [TBD - latency impact] |
| **SGLang** | [TBD] | [TBD - latency impact] |
| **TensorRT-LLM** | [TBD] | [TBD - latency impact] |

### 6.4 Multi-GPU Summary

**Best Multi-GPU Scaling:** [TBD]
**Most Balanced Memory Use:** [TBD]
**Key Finding:** [TBD]

---

## 7. Workload-Specific Analysis

### 7.1 Short Prompts (Chat Applications)

**Test:** `short_chat` (32 tokens) at c=50

| Metric | vLLM | SGLang | TensorRT-LLM | Winner |
|--------|------|--------|--------------|--------|
| TTFT P95 | [TBD]ms | [TBD]ms | [TBD]ms | [TBD] |
| Throughput | [TBD] tok/s | [TBD] tok/s | [TBD] tok/s | [TBD] |
| Success Rate | [TBD]% | [TBD]% | [TBD]% | [TBD] |

**Best for Chat:** [TBD]
**Use Case:** Interactive chatbots, customer service, Q&A

### 7.2 Long Context (RAG Applications)

**Test:** `long_rag` (2048 tokens) at c=20

| Metric | vLLM | SGLang | TensorRT-LLM | Winner |
|--------|------|--------|--------------|--------|
| TTFT P95 | [TBD]ms | [TBD]ms | [TBD]ms | [TBD] |
| Cache Speedup | [TBD]% | [TBD]% | [TBD]% | [TBD] |
| Throughput | [TBD] tok/s | [TBD] tok/s | [TBD] tok/s | [TBD] |

**Best for RAG:** [TBD]
**Use Case:** Document Q&A, knowledge bases, customer support with context

### 7.3 Very Long Context (8K+ tokens)

**Test:** `xl_rag` (8192 tokens) at c=10

| Metric | vLLM | SGLang | TensorRT-LLM | Winner |
|--------|------|--------|--------------|--------|
| TTFT P95 | [TBD]ms | [TBD]ms | [TBD]ms | [TBD] |
| Memory per Request | [TBD]GB | [TBD]GB | [TBD]GB | [TBD] |
| Throughput | [TBD] tok/s | [TBD] tok/s | [TBD] tok/s | [TBD] |

**Best for Long Context:** [TBD]
**Use Case:** Full document analysis, legal documents, research papers

### 7.4 Code Generation

**Test:** `code_medium` (1024 tokens) at c=10

| Metric | vLLM | SGLang | TensorRT-LLM | Winner |
|--------|------|--------|--------------|--------|
| TPOT Mean | [TBD]ms | [TBD]ms | [TBD]ms | [TBD] |
| TPOT Stability | [TBD]σ | [TBD]σ | [TBD]σ | [TBD] |
| Throughput | [TBD] tok/s | [TBD] tok/s | [TBD] tok/s | [TBD] |

**Best for Code:** [TBD]
**Use Case:** Code completion, code generation, technical documentation

### 7.5 High Concurrency Production

**Test:** `medium_chat` at c=100

| Metric | vLLM | SGLang | TensorRT-LLM | Winner |
|--------|------|--------|--------------|--------|
| TTFT P95 | [TBD]ms | [TBD]ms | [TBD]ms | [TBD] |
| Throughput | [TBD] tok/s | [TBD] tok/s | [TBD] tok/s | [TBD] |
| Success Rate | [TBD]% | [TBD]% | [TBD]% | [TBD] |
| Stability | [TBD] | [TBD] | [TBD] | [TBD] |

**Best for Production:** [TBD]
**Use Case:** Multi-user APIs, high-traffic services

### 7.6 Workload Summary Table

| Use Case | Best Framework | Runner-Up | Key Reason |
|----------|----------------|-----------|------------|
| Interactive Chat | [TBD] | [TBD] | [TBD] |
| RAG (Shared Context) | [TBD] | [TBD] | [TBD] |
| Long Documents | [TBD] | [TBD] | [TBD] |
| Code Generation | [TBD] | [TBD] | [TBD] |
| High Concurrency | [TBD] | [TBD] | [TBD] |
| Batch Processing | [TBD] | [TBD] | [TBD] |

---

## 8. Reliability & Stability

### 8.1 Resource Utilization

#### GPU Memory Usage

| Framework | Idle | Low Load (c=10) | High Load (c=100) | Peak |
|-----------|------|-----------------|-------------------|------|
| **vLLM** | [TBD]GB | [TBD]GB | [TBD]GB | [TBD]GB |
| **SGLang** | [TBD]GB | [TBD]GB | [TBD]GB | [TBD]GB |
| **TensorRT-LLM** | [TBD]GB | [TBD]GB | [TBD]GB | [TBD]GB |

#### GPU Compute Utilization

| Framework | Avg Utilization | Peak Utilization | Efficiency |
|-----------|----------------|------------------|------------|
| **vLLM** | [TBD]% | [TBD]% | [TBD] |
| **SGLang** | [TBD]% | [TBD]% | [TBD] |
| **TensorRT-LLM** | [TBD]% | [TBD]% | [TBD] |


---

## 9. Cost Analysis

### 9.1 Cost Per Million Tokens

**Assumptions:**
- H100 rental cost: $[TBD]/hour
- Measured throughput at optimal concurrency
- 24/7 operation

#### Cost Efficiency by Framework

| Framework | Optimal Throughput | Tokens/Hour | Cost per 1M Tokens | Relative |
|-----------|-------------------|-------------|-------------------|----------|
| **vLLM** | [TBD] tok/s | [TBD]M | $[TBD] | 1.0× |
| **SGLang** | [TBD] tok/s | [TBD]M | $[TBD] | [TBD]× |
| **TensorRT-LLM** | [TBD] tok/s | [TBD]M | $[TBD] | [TBD]× |

### 9.2 TCO by Use Case

#### Chat Application (1B tokens/month)

| Framework | Hardware Cost | Total Cost | Cost per Active User |
|-----------|--------------|------------|---------------------|
| **vLLM** | $[TBD] | $[TBD] | $[TBD] |
| **SGLang** | $[TBD] | $[TBD] | $[TBD] |
| **TensorRT-LLM** | $[TBD] | $[TBD] | $[TBD] |

#### RAG Application (500M tokens/month, 70% prefix reuse)

| Framework | Hardware Cost | Cache Benefit | Total Cost |
|-----------|--------------|---------------|------------|
| **vLLM** | $[TBD] | -$[TBD] | $[TBD] |
| **SGLang** | $[TBD] | -$[TBD] | $[TBD] |
| **TensorRT-LLM** | $[TBD] | -$[TBD] | $[TBD] |

_Note: Cache benefit = cost savings from faster processing_

#### Batch Processing (2B tokens/month, low concurrency)

| Framework | Hardware Cost | Total Cost | Cost Ranking |
|-----------|--------------|------------|--------------|
| **vLLM** | $[TBD] | $[TBD] | [TBD] |
| **SGLang** | $[TBD] | $[TBD] | [TBD] |
| **TensorRT-LLM** | $[TBD] | $[TBD] | [TBD] |

### 9.3 ROI Analysis

**When does SGLang's cache advantage pay off?**
- Break-even point: [TBD]% prefix reuse
- Monthly savings: $[TBD] at [X]% reuse

**When does vLLM's concurrency advantage matter?**
- Break-even point: [TBD] concurrent users
- Monthly savings: $[TBD] at [X] concurrent

---

## 10. Decision Framework

### 10.1 Recommendation Decision Tree

```
START: Choose LLM Serving Framework
    |
    ├─→ Q1: Do you have >50% prefix reuse (RAG, agents)?
    |   ├─→ YES: Go to Q2
    |   └─→ NO: Go to Q3
    |
    ├─→ Q2: Is cache efficiency critical?
    |   ├─→ YES: **Recommendation: [TBD - likely SGLang]**
    |   └─→ NO: Go to Q3
    |
    ├─→ Q3: Do you need >100 concurrent requests?
    |   ├─→ YES: **Recommendation: [TBD - likely vLLM]**
    |   └─→ NO: Go to Q4
    |
    ├─→ Q4: Is this single-user or low concurrency?
    |   ├─→ YES: **Recommendation: [TBD - likely TensorRT-LLM]**
    |   └─→ NO: **Recommendation: [TBD - likely vLLM]**
```

### 10.2 Final Recommendations by Use Case

#### Interactive Chat Applications

**Recommended:** [TBD]
**Runner-Up:** [TBD]

**Reasoning:**
- [TBD - latency, concurrency, stability factors]

**When to use runner-up:**
- [TBD - specific conditions]

#### RAG Applications with Shared Context

**Recommended:** [TBD]
**Runner-Up:** [TBD]

**Reasoning:**
- [TBD - cache efficiency, throughput factors]

**Quantified Benefit:**
- [TBD]× faster on repeated queries
- $[TBD] monthly savings

#### Agentic Workflows / Tool Use

**Recommended:** [TBD]
**Runner-Up:** [TBD]

**Reasoning:**
- [TBD - structured generation, cache, reliability]

#### Multi-User Production APIs

**Recommended:** [TBD]
**Runner-Up:** [TBD]

**Reasoning:**
- [TBD - concurrency, stability, throughput]

**At what scale:**
- [TBD] concurrent users
- [TBD] requests/second

#### Single-User / Low-Concurrency Applications

**Recommended:** [TBD]
**Runner-Up:** [TBD]

**Reasoning:**
- [TBD - single-request latency, efficiency]

#### Batch Document Processing

**Recommended:** [TBD]
**Runner-Up:** [TBD]

**Reasoning:**
- [TBD - throughput, cost efficiency]

### 10.3 Migration Considerations

#### From vLLM to SGLang

**Effort:** [TBD - Easy/Medium/Hard]
**API Compatibility:** [TBD]%
**When worth it:** [TBD - conditions]

#### From SGLang to vLLM

**Effort:** [TBD - Easy/Medium/Hard]
**API Compatibility:** [TBD]%
**When worth it:** [TBD - conditions]

#### From TensorRT-LLM to vLLM/SGLang

**Effort:** [TBD - Easy/Medium/Hard]
**When worth it:** [TBD - conditions]

---

## 11. Conclusions

### 11.1 Overall Winner by Category

| Category | Winner | Margin | Key Metric |
|----------|--------|--------|------------|
| Latency | [TBD] | [TBD]% faster | TTFT P95: [TBD]ms |
| Throughput | [TBD] | [TBD]× higher | [TBD] tok/s |
| Cache Efficiency | [TBD] | [TBD]× speedup | Warm cache: [TBD]% |
| Reliability | [TBD] | [TBD]% success | [TBD]% uptime |
| Cost Efficiency | [TBD] | $[TBD] cheaper | $[TBD]/1M tokens |
| Production Ready | [TBD] | [TBD]/25 score | Maturity + docs |

### 11.2 Best Overall Framework

**For most users:** [TBD]

**Reasoning:**
[TBD - balanced performance, maturity, use case coverage]

**Market share implications:**
[TBD - when this recommendation aligns with industry adoption]

### 11.3 Key Takeaways

1. **[TBD]** - Most important finding
2. **[TBD]** - Second most important
3. **[TBD]** - Third most important
4. **[TBD]** - Surprising discovery
5. **[TBD]** - Actionable insight

### 11.4 Future Testing Recommendations

- [ ] Test with [other model sizes]
- [ ] Test with [other hardware configurations]
- [ ] Test [additional frameworks]
- [ ] Deep dive into [specific workload]

---

## Appendix A: Raw Data

### A.1 Complete Test Results

[Link to or embed full CSV/JSON results]

### A.2 System Configuration Details

```bash
# vLLM Configuration
[TBD - full command line]

# SGLang Configuration
[TBD - full command line]

# TensorRT-LLM Configuration
[TBD - full command line]
```

### A.3 GPU Information

```
[Output of nvidia-smi]
```

---

## Appendix B: Reproducibility

### B.1 Test Commands

**To reproduce these results:**

```bash
# Setup
git clone [benchmark repo]
cd llm-benchmark
./deploy_to_vastai.sh

# Run vLLM tests
./run_full_vllm_suite.sh

# Run SGLang tests (after switching servers)
./run_full_sglang_suite.sh

# Generate report
python analyze.py --results-dir results --plot
python compare_frameworks.py
```

### B.2 Data Files

- Test data: `data/*.json`
- Results: `results/*_summary.json`
- Raw data: `results/*_raw.json`

### B.3 Analysis Scripts

- Cache warmup: `analyze_cache_warmup.py`
- Full comparison: `analyze.py`
- Framework comparison: `compare_frameworks.py`

---

## Appendix C: Version Information

| Component | Version | Date |
|-----------|---------|------|
| vLLM | [TBD] | [TBD] |
| SGLang | [TBD] | [TBD] |
| TensorRT-LLM | [TBD] | [TBD] |
| CUDA | [TBD] | - |
| PyTorch | [TBD] | - |
| Model | DeepSeek-R1-Distill-Llama-8B | [TBD] |

---

**Report Generated:** [DATE]
**Test Duration:** [X] hours
**Total Requests:** [X]
**Total Tokens Generated:** [X]M
