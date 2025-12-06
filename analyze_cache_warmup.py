#!/usr/bin/env python3
"""
Analyze cache warmup effect by examining per-request latency.
Shows how TTFT improves as cache warms up.
"""

import json
import glob
import argparse
from pathlib import Path
import statistics


def analyze_cache_warmup(raw_results_file: str):
    """Analyze per-request timing to show cache warmup effect"""

    with open(raw_results_file) as f:
        results = json.load(f)

    print("\n" + "=" * 70)
    print("CACHE WARMUP ANALYSIS")
    print("=" * 70)
    print(f"File: {Path(raw_results_file).name}")
    print(f"Total requests: {len(results)}")
    print("=" * 70)

    # Extract TTFT for each request
    ttfts = [(i+1, r['ttft'] * 1000) for i, r in enumerate(results) if r['success']]

    if not ttfts:
        print("No successful requests found!")
        return

    # Calculate statistics
    first_request_ttft = ttfts[0][1]
    subsequent_ttfts = [t for _, t in ttfts[1:]]

    if subsequent_ttfts:
        avg_warm_ttft = statistics.mean(subsequent_ttfts)
        speedup_pct = ((first_request_ttft - avg_warm_ttft) / first_request_ttft) * 100
    else:
        avg_warm_ttft = first_request_ttft
        speedup_pct = 0

    print(f"\n📊 Cache Performance Summary:")
    print(f"  First request (cold):     {first_request_ttft:7.1f}ms")
    print(f"  Avg subsequent (warm):    {avg_warm_ttft:7.1f}ms")
    print(f"  Cache speedup:            {speedup_pct:6.1f}%")

    # Show request-by-request breakdown
    print(f"\n🔥 Request-by-Request Cache Warmup:")
    print("=" * 70)
    print(f"{'Req#':>5} | {'TTFT (ms)':>10} | {'vs First':>10} | {'Status':>10}")
    print("-" * 70)

    for i, (req_num, ttft) in enumerate(ttfts[:20]):  # Show first 20
        speedup = ((first_request_ttft - ttft) / first_request_ttft) * 100

        if i == 0:
            status = "COLD ❄️"
        elif i < 3:
            status = "WARMING 🌡️"
        else:
            status = "HOT 🔥"

        print(f"{req_num:5d} | {ttft:10.1f} | {speedup:9.1f}% | {status:>10}")

    if len(ttfts) > 20:
        print(f"... ({len(ttfts) - 20} more requests)")

    # Identify cache stabilization point
    print(f"\n📈 Cache Stabilization:")
    print("=" * 70)

    # Group requests into buckets
    bucket_size = 10
    buckets = []
    for i in range(0, len(ttfts), bucket_size):
        bucket = ttfts[i:i+bucket_size]
        avg_ttft = statistics.mean([t for _, t in bucket])
        buckets.append((i+1, i+len(bucket), avg_ttft))

    print(f"{'Requests':>15} | {'Avg TTFT (ms)':>15} | {'Speedup':>10}")
    print("-" * 70)
    for start, end, avg_ttft in buckets[:10]:  # Show first 10 buckets
        speedup = ((first_request_ttft - avg_ttft) / first_request_ttft) * 100
        print(f"{start:5d}-{end:<5d} | {avg_ttft:15.1f} | {speedup:9.1f}%")

    # Determine if cache is effective
    print(f"\n🎯 Cache Effectiveness:")
    print("=" * 70)
    if speedup_pct > 10:
        print(f"✅ EXCELLENT: Cache provides {speedup_pct:.1f}% speedup")
        print("   Cache is working very well!")
    elif speedup_pct > 5:
        print(f"✅ GOOD: Cache provides {speedup_pct:.1f}% speedup")
        print("   Cache is helping moderately")
    elif speedup_pct > 1:
        print(f"⚠️  MINIMAL: Cache provides only {speedup_pct:.1f}% speedup")
        print("   Cache may not be configured optimally")
    else:
        print(f"❌ NO EFFECT: Cache provides {speedup_pct:.1f}% speedup")
        print("   Cache may not be enabled or requests don't share prefixes")

    print("=" * 70 + "\n")


def find_cache_tests(results_dir: str):
    """Find all cache-related test results"""
    pattern = str(Path(results_dir) / "*cache*_raw.json")
    files = glob.glob(pattern)
    return sorted(files, key=lambda x: Path(x).stat().st_mtime, reverse=True)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze cache warmup effect from benchmark results"
    )
    parser.add_argument(
        "--results-dir",
        default="results",
        help="Directory containing result files"
    )
    parser.add_argument(
        "--file",
        help="Specific raw results file to analyze"
    )

    args = parser.parse_args()

    if args.file:
        # Analyze specific file
        analyze_cache_warmup(args.file)
    else:
        # Find and analyze cache tests
        cache_files = find_cache_tests(args.results_dir)

        if not cache_files:
            print(f"No cache test results found in {args.results_dir}")
            print("Run: ./run_remote_benchmark.sh vllm cache_reuse \"1\"")
            return

        print(f"Found {len(cache_files)} cache test result(s)")
        print("Analyzing most recent test...\n")

        # Analyze most recent
        analyze_cache_warmup(cache_files[0])

        if len(cache_files) > 1:
            print("\nOther cache test files available:")
            for f in cache_files[1:]:
                print(f"  - {Path(f).name}")
            print("\nAnalyze specific file with: --file <filename>")


if __name__ == "__main__":
    main()
