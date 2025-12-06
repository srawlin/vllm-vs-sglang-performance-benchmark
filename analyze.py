#!/usr/bin/env python3
"""
Results analyzer and report generator for LLM benchmarks
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import List, Dict
import argparse
from tabulate import tabulate


class BenchmarkAnalyzer:
    """Analyze and compare benchmark results"""

    def __init__(self, results_dir: str):
        self.results_dir = Path(results_dir)
        self.results = []

    def load_results(self):
        """Load all summary JSON files from results directory"""
        summary_files = list(self.results_dir.glob("*_summary.json"))

        for file in summary_files:
            with open(file, 'r') as f:
                data = json.load(f)
                self.results.append(data)

        print(f"Loaded {len(self.results)} benchmark results")
        return self.results

    def create_dataframe(self) -> pd.DataFrame:
        """Convert results to pandas DataFrame"""
        return pd.DataFrame(self.results)

    def generate_comparison_table(self) -> str:
        """Generate markdown comparison table"""
        if not self.results:
            return "No results to analyze"

        df = self.create_dataframe()

        # Select key columns
        columns = [
            'framework',
            'test_name',
            'concurrency_level',
            'successful_requests',
            'ttft_mean',
            'ttft_p95',
            'tpot_mean',
            'throughput_tokens_per_sec',
            'requests_per_sec'
        ]

        display_df = df[columns].copy()

        # Format for readability
        display_df['ttft_mean'] = display_df['ttft_mean'].apply(lambda x: f"{x:.3f}s")
        display_df['ttft_p95'] = display_df['ttft_p95'].apply(lambda x: f"{x:.3f}s")
        display_df['tpot_mean'] = display_df['tpot_mean'].apply(lambda x: f"{x*1000:.2f}ms")
        display_df['throughput_tokens_per_sec'] = display_df['throughput_tokens_per_sec'].apply(lambda x: f"{x:.1f}")
        display_df['requests_per_sec'] = display_df['requests_per_sec'].apply(lambda x: f"{x:.2f}")

        # Rename columns
        display_df.columns = [
            'Framework',
            'Test',
            'Concurrency',
            'Requests',
            'TTFT Mean',
            'TTFT P95',
            'TPOT Mean',
            'Throughput (tok/s)',
            'Req/s'
        ]

        return tabulate(display_df, headers='keys', tablefmt='github', showindex=False)

    def generate_framework_comparison(self) -> Dict[str, pd.DataFrame]:
        """Compare frameworks across same test scenarios"""
        df = self.create_dataframe()

        # Group by test_name and concurrency
        comparisons = {}

        for test_name in df['test_name'].unique():
            test_df = df[df['test_name'] == test_name]

            comparison = test_df[[
                'framework',
                'concurrency_level',
                'ttft_mean',
                'ttft_p95',
                'tpot_mean',
                'throughput_tokens_per_sec'
            ]].copy()

            comparison = comparison.round(3)
            comparisons[test_name] = comparison

        return comparisons

    def plot_throughput_comparison(self, output_file: str = "throughput_comparison.png"):
        """Create throughput comparison plot"""
        df = self.create_dataframe()

        if df.empty:
            print("No data to plot")
            return

        plt.figure(figsize=(12, 6))

        # Group by framework and concurrency
        for framework in df['framework'].unique():
            framework_df = df[df['framework'] == framework]
            framework_df = framework_df.sort_values('concurrency_level')

            plt.plot(
                framework_df['concurrency_level'],
                framework_df['throughput_tokens_per_sec'],
                marker='o',
                label=framework,
                linewidth=2
            )

        plt.xlabel('Concurrency Level', fontsize=12)
        plt.ylabel('Throughput (tokens/sec)', fontsize=12)
        plt.title('Throughput vs Concurrency', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        output_path = self.results_dir / output_file
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved plot: {output_path}")
        plt.close()

    def plot_latency_comparison(self, output_file: str = "latency_comparison.png"):
        """Create latency comparison plot"""
        df = self.create_dataframe()

        if df.empty:
            print("No data to plot")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        # TTFT comparison
        for framework in df['framework'].unique():
            framework_df = df[df['framework'] == framework]
            framework_df = framework_df.sort_values('concurrency_level')

            ax1.plot(
                framework_df['concurrency_level'],
                framework_df['ttft_mean'] * 1000,  # Convert to ms
                marker='o',
                label=framework,
                linewidth=2
            )

        ax1.set_xlabel('Concurrency Level', fontsize=11)
        ax1.set_ylabel('TTFT Mean (ms)', fontsize=11)
        ax1.set_title('Time to First Token', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # TPOT comparison
        for framework in df['framework'].unique():
            framework_df = df[df['framework'] == framework]
            framework_df = framework_df.sort_values('concurrency_level')

            ax2.plot(
                framework_df['concurrency_level'],
                framework_df['tpot_mean'] * 1000,  # Convert to ms
                marker='o',
                label=framework,
                linewidth=2
            )

        ax2.set_xlabel('Concurrency Level', fontsize=11)
        ax2.set_ylabel('TPOT Mean (ms)', fontsize=11)
        ax2.set_title('Time Per Output Token', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        output_path = self.results_dir / output_file
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✓ Saved plot: {output_path}")
        plt.close()

    def generate_markdown_report(self, output_file: str = "benchmark_report.md"):
        """Generate comprehensive markdown report"""
        df = self.create_dataframe()

        report = []
        report.append("# LLM Inference Benchmark Report\n")
        report.append(f"Generated: {pd.Timestamp.now()}\n")
        report.append(f"Total benchmarks: {len(self.results)}\n")

        # Executive Summary
        report.append("\n## Executive Summary\n")
        frameworks = df['framework'].unique()
        report.append(f"**Frameworks tested:** {', '.join(frameworks)}\n")
        report.append(f"**Test scenarios:** {df['test_name'].nunique()}\n")
        report.append(f"**Total requests:** {df['successful_requests'].sum():,}\n")

        # Overall winner by throughput
        max_throughput = df.loc[df['throughput_tokens_per_sec'].idxmax()]
        report.append(f"\n**Highest throughput:** {max_throughput['framework']} ")
        report.append(f"({max_throughput['throughput_tokens_per_sec']:.1f} tok/s at concurrency {max_throughput['concurrency_level']})\n")

        # Best latency
        min_ttft = df.loc[df['ttft_mean'].idxmin()]
        report.append(f"**Lowest TTFT:** {min_ttft['framework']} ")
        report.append(f"({min_ttft['ttft_mean']*1000:.1f}ms at concurrency {min_ttft['concurrency_level']})\n")

        # Full comparison table
        report.append("\n## Full Results Comparison\n")
        report.append(self.generate_comparison_table())
        report.append("\n")

        # Per-test analysis
        report.append("\n## Detailed Analysis by Test\n")
        for test_name in df['test_name'].unique():
            report.append(f"\n### {test_name}\n")
            test_df = df[df['test_name'] == test_name]

            test_table = test_df[[
                'framework',
                'concurrency_level',
                'ttft_mean',
                'tpot_mean',
                'throughput_tokens_per_sec'
            ]].copy()

            test_table['ttft_mean'] = test_table['ttft_mean'].apply(lambda x: f"{x*1000:.1f}ms")
            test_table['tpot_mean'] = test_table['tpot_mean'].apply(lambda x: f"{x*1000:.2f}ms")
            test_table['throughput_tokens_per_sec'] = test_table['throughput_tokens_per_sec'].apply(lambda x: f"{x:.1f}")

            test_table.columns = ['Framework', 'Concurrency', 'TTFT', 'TPOT', 'Throughput (tok/s)']

            report.append(tabulate(test_table, headers='keys', tablefmt='github', showindex=False))
            report.append("\n")

        # Recommendations
        report.append("\n## Recommendations\n")
        report.append(self._generate_recommendations(df))

        # Save report
        output_path = self.results_dir / output_file
        with open(output_path, 'w') as f:
            f.write('\n'.join(report))

        print(f"✓ Saved report: {output_path}")
        return '\n'.join(report)

    def _generate_recommendations(self, df: pd.DataFrame) -> str:
        """Generate recommendations based on results"""
        recommendations = []

        # Find best framework for different scenarios
        best_low_latency = df.loc[df['ttft_mean'].idxmin()]
        best_throughput = df.loc[df['throughput_tokens_per_sec'].idxmax()]
        best_high_concurrency = df[df['concurrency_level'] >= 50].loc[
            df[df['concurrency_level'] >= 50]['throughput_tokens_per_sec'].idxmax()
        ] if len(df[df['concurrency_level'] >= 50]) > 0 else best_throughput

        recommendations.append(f"### For Low-Latency Applications\n")
        recommendations.append(f"**Recommended:** {best_low_latency['framework']}\n")
        recommendations.append(f"- TTFT: {best_low_latency['ttft_mean']*1000:.1f}ms\n")
        recommendations.append(f"- Best for: Interactive chat, real-time applications\n")

        recommendations.append(f"\n### For High-Throughput Batch Processing\n")
        recommendations.append(f"**Recommended:** {best_throughput['framework']}\n")
        recommendations.append(f"- Throughput: {best_throughput['throughput_tokens_per_sec']:.1f} tok/s\n")
        recommendations.append(f"- Best for: Batch document processing, offline analysis\n")

        recommendations.append(f"\n### For High-Concurrency Production\n")
        recommendations.append(f"**Recommended:** {best_high_concurrency['framework']}\n")
        recommendations.append(f"- Throughput at high load: {best_high_concurrency['throughput_tokens_per_sec']:.1f} tok/s\n")
        recommendations.append(f"- Best for: Multi-user APIs, production services\n")

        return ''.join(recommendations)

    def print_summary(self):
        """Print summary to console"""
        df = self.create_dataframe()

        print("\n" + "="*80)
        print("BENCHMARK RESULTS SUMMARY")
        print("="*80)

        print(f"\nTotal benchmarks: {len(self.results)}")
        print(f"Frameworks: {', '.join(df['framework'].unique())}")
        print(f"Total requests: {df['successful_requests'].sum():,}")

        print("\n" + "-"*80)
        print("TOP PERFORMERS")
        print("-"*80)

        max_throughput = df.loc[df['throughput_tokens_per_sec'].idxmax()]
        print(f"\n🏆 Highest Throughput: {max_throughput['framework']}")
        print(f"   {max_throughput['throughput_tokens_per_sec']:.1f} tok/s")
        print(f"   Test: {max_throughput['test_name']}, Concurrency: {max_throughput['concurrency_level']}")

        min_ttft = df.loc[df['ttft_mean'].idxmin()]
        print(f"\n⚡ Lowest Latency (TTFT): {min_ttft['framework']}")
        print(f"   {min_ttft['ttft_mean']*1000:.1f}ms")
        print(f"   Test: {min_ttft['test_name']}, Concurrency: {min_ttft['concurrency_level']}")

        print("\n" + "="*80 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Analyze LLM benchmark results")
    parser.add_argument("--results-dir", default="results", help="Directory containing result JSON files")
    parser.add_argument("--output-report", default="benchmark_report.md", help="Output markdown report filename")
    parser.add_argument("--plot", action="store_true", help="Generate comparison plots")

    args = parser.parse_args()

    analyzer = BenchmarkAnalyzer(args.results_dir)
    analyzer.load_results()

    if not analyzer.results:
        print("No results found. Run benchmarks first.")
        return

    # Print summary
    analyzer.print_summary()

    # Generate report
    print("\nGenerating report...")
    analyzer.generate_markdown_report(args.output_report)

    # Generate plots
    if args.plot:
        print("\nGenerating plots...")
        analyzer.plot_throughput_comparison()
        analyzer.plot_latency_comparison()

    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    main()
