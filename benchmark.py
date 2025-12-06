#!/usr/bin/env python3
"""
LLM Inference Benchmark Suite
Supports vLLM, SGLang, TensorRT-LLM, and any OpenAI-compatible API
"""

import asyncio
import aiohttp
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics
from tqdm.asyncio import tqdm


@dataclass
class RequestResult:
    """Result from a single inference request"""
    request_id: str
    prompt_tokens: int
    completion_tokens: int
    ttft: float  # Time to first token (seconds)
    total_time: float  # Total request time (seconds)
    success: bool
    error: Optional[str] = None
    tokens_per_second: Optional[float] = None
    time_per_token: Optional[float] = None  # TPOT


@dataclass
class BenchmarkResult:
    """Aggregated benchmark results"""
    framework: str
    test_name: str
    timestamp: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_duration: float

    # Latency metrics (seconds)
    ttft_mean: float
    ttft_median: float
    ttft_p95: float
    ttft_p99: float
    ttft_std: float

    total_time_mean: float
    total_time_median: float
    total_time_p95: float
    total_time_p99: float

    # Throughput metrics
    throughput_tokens_per_sec: float
    requests_per_sec: float

    # Token metrics
    tpot_mean: float  # Time per output token
    tpot_median: float
    tpot_p95: float

    total_input_tokens: int
    total_output_tokens: int

    # Concurrency info
    concurrency_level: int


class LLMBenchmark:
    """LLM Inference Benchmark Runner"""

    def __init__(
        self,
        server_url: str,
        api_key: str,
        model_name: str,
        framework: str = "vllm",
        timeout: int = 300
    ):
        self.server_url = server_url.rstrip('/')
        self.api_key = api_key
        self.model_name = model_name
        self.framework = framework
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def send_request(
        self,
        session: aiohttp.ClientSession,
        prompt: str,
        max_tokens: int,
        temperature: float,
        request_id: str
    ) -> RequestResult:
        """Send a single inference request and measure performance"""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }

        try:
            start_time = time.perf_counter()

            async with session.post(
                f"{self.server_url}/v1/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout,
                ssl=False  # For self-signed certs
            ) as response:

                if response.status != 200:
                    error_text = await response.text()
                    return RequestResult(
                        request_id=request_id,
                        prompt_tokens=0,
                        completion_tokens=0,
                        ttft=0,
                        total_time=0,
                        success=False,
                        error=f"HTTP {response.status}: {error_text}"
                    )

                result = await response.json()
                end_time = time.perf_counter()

                total_time = end_time - start_time

                # Extract token counts
                usage = result.get('usage', {})
                prompt_tokens = usage.get('prompt_tokens', 0)
                completion_tokens = usage.get('completion_tokens', 0)

                # For non-streaming, TTFT ≈ total_time (we don't have first token timing)
                # This is a limitation - ideally we'd use streaming
                ttft = total_time  # Approximation

                # Calculate metrics
                tokens_per_second = completion_tokens / total_time if total_time > 0 else 0
                time_per_token = total_time / completion_tokens if completion_tokens > 0 else 0

                return RequestResult(
                    request_id=request_id,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    ttft=ttft,
                    total_time=total_time,
                    success=True,
                    tokens_per_second=tokens_per_second,
                    time_per_token=time_per_token
                )

        except asyncio.TimeoutError:
            return RequestResult(
                request_id=request_id,
                prompt_tokens=0,
                completion_tokens=0,
                ttft=0,
                total_time=0,
                success=False,
                error="Request timeout"
            )
        except Exception as e:
            return RequestResult(
                request_id=request_id,
                prompt_tokens=0,
                completion_tokens=0,
                ttft=0,
                total_time=0,
                success=False,
                error=str(e)
            )

    async def run_concurrent_benchmark(
        self,
        prompts: List[Dict],
        concurrency: int,
        temperature: float = 0.6
    ) -> List[RequestResult]:
        """Run benchmark with controlled concurrency"""

        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_request(session, prompt_data):
            async with semaphore:
                return await self.send_request(
                    session=session,
                    prompt=prompt_data['prompt'],
                    max_tokens=prompt_data.get('max_tokens', 128),
                    temperature=temperature,
                    request_id=prompt_data['id']
                )

        connector = aiohttp.TCPConnector(limit=concurrency * 2, ssl=False)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [bounded_request(session, p) for p in prompts]
            results = await tqdm.gather(*tasks, desc=f"Concurrency={concurrency}")

        return results

    def analyze_results(
        self,
        results: List[RequestResult],
        test_name: str,
        concurrency: int,
        total_duration: float
    ) -> BenchmarkResult:
        """Analyze results and compute statistics"""

        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]

        if not successful:
            raise ValueError("No successful requests to analyze")

        # Extract metrics
        ttfts = [r.ttft for r in successful]
        total_times = [r.total_time for r in successful]
        tpots = [r.time_per_token for r in successful if r.time_per_token]

        total_input_tokens = sum(r.prompt_tokens for r in successful)
        total_output_tokens = sum(r.completion_tokens for r in successful)
        total_tokens = total_output_tokens

        return BenchmarkResult(
            framework=self.framework,
            test_name=test_name,
            timestamp=datetime.now().isoformat(),
            total_requests=len(results),
            successful_requests=len(successful),
            failed_requests=len(failed),
            total_duration=total_duration,

            # TTFT statistics
            ttft_mean=statistics.mean(ttfts),
            ttft_median=statistics.median(ttfts),
            ttft_p95=self._percentile(ttfts, 95),
            ttft_p99=self._percentile(ttfts, 99),
            ttft_std=statistics.stdev(ttfts) if len(ttfts) > 1 else 0,

            # Total time statistics
            total_time_mean=statistics.mean(total_times),
            total_time_median=statistics.median(total_times),
            total_time_p95=self._percentile(total_times, 95),
            total_time_p99=self._percentile(total_times, 99),

            # Throughput
            throughput_tokens_per_sec=total_tokens / total_duration,
            requests_per_sec=len(successful) / total_duration,

            # TPOT statistics
            tpot_mean=statistics.mean(tpots) if tpots else 0,
            tpot_median=statistics.median(tpots) if tpots else 0,
            tpot_p95=self._percentile(tpots, 95) if tpots else 0,

            # Token counts
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,

            concurrency_level=concurrency
        )

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def save_results(
        self,
        benchmark_result: BenchmarkResult,
        raw_results: List[RequestResult],
        output_dir: str
    ):
        """Save results to JSON files"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save summary
        summary_file = output_path / f"{self.framework}_{benchmark_result.test_name}_{timestamp}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(asdict(benchmark_result), f, indent=2)

        # Save raw results
        raw_file = output_path / f"{self.framework}_{benchmark_result.test_name}_{timestamp}_raw.json"
        with open(raw_file, 'w') as f:
            json.dump([asdict(r) for r in raw_results], f, indent=2)

        print(f"\n✓ Results saved:")
        print(f"  Summary: {summary_file}")
        print(f"  Raw:     {raw_file}")

    async def run_test_suite(
        self,
        test_file: str,
        concurrency_levels: List[int],
        output_dir: str
    ):
        """Run complete test suite with multiple concurrency levels"""

        # Load test data
        with open(test_file, 'r') as f:
            test_data = json.load(f)

        test_name = Path(test_file).stem

        print(f"\n{'='*70}")
        print(f"Running benchmark: {test_name}")
        print(f"Framework: {self.framework}")
        print(f"Server: {self.server_url}")
        print(f"Model: {self.model_name}")
        print(f"Test prompts: {len(test_data)}")
        print(f"{'='*70}\n")

        all_results = []

        for concurrency in concurrency_levels:
            print(f"\n--- Concurrency Level: {concurrency} ---")

            start_time = time.perf_counter()
            raw_results = await self.run_concurrent_benchmark(
                prompts=test_data,
                concurrency=concurrency
            )
            total_duration = time.perf_counter() - start_time

            benchmark_result = self.analyze_results(
                results=raw_results,
                test_name=f"{test_name}_c{concurrency}",
                concurrency=concurrency,
                total_duration=total_duration
            )

            # Print summary
            self.print_summary(benchmark_result)

            # Save results
            self.save_results(benchmark_result, raw_results, output_dir)

            all_results.append(benchmark_result)

            # Brief pause between tests
            await asyncio.sleep(2)

        return all_results

    def print_summary(self, result: BenchmarkResult):
        """Print benchmark summary"""
        print(f"\n📊 Benchmark Results Summary")
        print(f"{'─'*70}")
        print(f"Framework:        {result.framework}")
        print(f"Test:             {result.test_name}")
        print(f"Concurrency:      {result.concurrency_level}")
        print(f"Duration:         {result.total_duration:.2f}s")
        print(f"\n🎯 Request Stats:")
        print(f"  Total:          {result.total_requests}")
        print(f"  Successful:     {result.successful_requests}")
        print(f"  Failed:         {result.failed_requests}")
        print(f"  Success Rate:   {result.successful_requests/result.total_requests*100:.1f}%")
        print(f"\n⚡ Latency (seconds):")
        print(f"  TTFT Mean:      {result.ttft_mean:.3f}s")
        print(f"  TTFT Median:    {result.ttft_median:.3f}s")
        print(f"  TTFT P95:       {result.ttft_p95:.3f}s")
        print(f"  TTFT P99:       {result.ttft_p99:.3f}s")
        print(f"  TTFT StdDev:    {result.ttft_std:.3f}s")
        print(f"\n  TPOT Mean:      {result.tpot_mean*1000:.2f}ms")
        print(f"  TPOT Median:    {result.tpot_median*1000:.2f}ms")
        print(f"  TPOT P95:       {result.tpot_p95*1000:.2f}ms")
        print(f"\n🚀 Throughput:")
        print(f"  Tokens/sec:     {result.throughput_tokens_per_sec:.2f}")
        print(f"  Requests/sec:   {result.requests_per_sec:.2f}")
        print(f"\n📈 Token Stats:")
        print(f"  Input tokens:   {result.total_input_tokens:,}")
        print(f"  Output tokens:  {result.total_output_tokens:,}")
        print(f"{'─'*70}")


def main():
    parser = argparse.ArgumentParser(description="LLM Inference Benchmark Suite")
    parser.add_argument("--server-url", required=True, help="Server URL (e.g., https://...trycloudflare.com)")
    parser.add_argument("--api-key", required=True, help="API key (Bearer token)")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--framework", required=True, choices=["vllm", "sglang", "tensorrt", "other"],
                        help="Framework being tested")
    parser.add_argument("--test-file", required=True, help="Path to test data JSON file")
    parser.add_argument("--concurrency", type=int, nargs="+", default=[1, 10, 50],
                        help="Concurrency levels to test (default: 1 10 50)")
    parser.add_argument("--output-dir", default="results", help="Output directory for results")
    parser.add_argument("--timeout", type=int, default=300, help="Request timeout in seconds")

    args = parser.parse_args()

    benchmark = LLMBenchmark(
        server_url=args.server_url,
        api_key=args.api_key,
        model_name=args.model,
        framework=args.framework,
        timeout=args.timeout
    )

    asyncio.run(benchmark.run_test_suite(
        test_file=args.test_file,
        concurrency_levels=args.concurrency,
        output_dir=args.output_dir
    ))


if __name__ == "__main__":
    main()
