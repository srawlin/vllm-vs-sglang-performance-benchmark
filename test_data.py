#!/usr/bin/env python3
"""
Test data generator for LLM benchmarking.
Creates realistic prompts of various lengths for testing.
"""

import json
import random
from pathlib import Path
from typing import List, Dict


class TestDataGenerator:
    """Generate test data for LLM benchmarking"""

    # Sample text for generating prompts
    LOREM_IPSUM = """
    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor
    incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
    nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
    Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
    eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt
    in culpa qui officia deserunt mollit anim id est laborum.
    """

    CODING_PROMPTS = [
        "Write a Python function to",
        "Explain how to implement",
        "Debug this code:",
        "Optimize the following algorithm:",
        "Create a class that",
    ]

    RAG_PREFIXES = [
        "Based on the following document, answer the question.",
        "Given the context below, provide a detailed explanation.",
        "Using the information provided, summarize the key points.",
        "According to the text, explain how",
        "Analyze the following passage and",
    ]

    QUESTIONS = [
        "What is the main idea?",
        "How does this work?",
        "Can you explain this in detail?",
        "What are the key differences?",
        "Why is this important?",
        "What are the best practices?",
        "How can this be improved?",
        "What are the trade-offs?",
    ]

    def generate_prompt(self, target_tokens: int, prompt_type: str = "chat") -> str:
        """
        Generate a prompt of approximately target_tokens length.

        Args:
            target_tokens: Approximate number of tokens (1 token ≈ 4 chars)
            prompt_type: Type of prompt (chat, rag, code)
        """
        target_chars = target_tokens * 4

        if prompt_type == "chat":
            return self._generate_chat_prompt(target_chars)
        elif prompt_type == "rag":
            return self._generate_rag_prompt(target_chars)
        elif prompt_type == "code":
            return self._generate_code_prompt(target_chars)
        else:
            raise ValueError(f"Unknown prompt type: {prompt_type}")

    def _generate_chat_prompt(self, target_chars: int) -> str:
        """Generate a chat-style prompt"""
        if target_chars < 100:
            return random.choice(self.QUESTIONS)

        question = random.choice(self.QUESTIONS)
        context = (self.LOREM_IPSUM * (target_chars // len(self.LOREM_IPSUM) + 1))[:target_chars - len(question)]
        return f"{context.strip()}\n\n{question}"

    def _generate_rag_prompt(self, target_chars: int) -> str:
        """Generate a RAG-style prompt with context"""
        prefix = random.choice(self.RAG_PREFIXES)
        question = random.choice(self.QUESTIONS)

        remaining = target_chars - len(prefix) - len(question) - 20
        context = (self.LOREM_IPSUM * (remaining // len(self.LOREM_IPSUM) + 1))[:remaining]

        return f"{prefix}\n\nContext:\n{context.strip()}\n\nQuestion: {question}"

    def _generate_code_prompt(self, target_chars: int) -> str:
        """Generate a code-related prompt"""
        prefix = random.choice(self.CODING_PROMPTS)

        if target_chars < 200:
            return f"{prefix} sort a list efficiently."

        code_sample = """
def example_function(data):
    result = []
    for item in data:
        if item > 0:
            result.append(item * 2)
    return result
"""
        remaining = target_chars - len(prefix) - 50
        context = (code_sample * (remaining // len(code_sample) + 1))[:remaining]

        return f"{prefix}\n\n{context.strip()}\n\nRequirements: Handle edge cases and optimize performance."

    def generate_test_suite(self, output_dir: str = "data") -> Dict[str, str]:
        """
        Generate a complete test suite with various prompt sizes and types.

        Returns:
            Dictionary mapping test name to file path
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        test_files = {}

        # Define test scenarios
        scenarios = [
            # (name, token_count, prompt_type, num_samples)
            ("short_chat", 32, "chat", 100),
            ("medium_chat", 512, "chat", 100),
            ("long_rag", 2048, "rag", 50),
            ("xl_rag", 8192, "rag", 20),
            ("code_short", 128, "code", 50),
            ("code_medium", 1024, "code", 30),
        ]

        for name, tokens, ptype, count in scenarios:
            prompts = [
                {
                    "id": f"{name}_{i}",
                    "prompt": self.generate_prompt(tokens, ptype),
                    "type": ptype,
                    "target_tokens": tokens,
                    "max_tokens": 128,  # Output length
                }
                for i in range(count)
            ]

            file_path = output_path / f"{name}.json"
            with open(file_path, 'w') as f:
                json.dump(prompts, f, indent=2)

            test_files[name] = str(file_path)
            print(f"✓ Generated {count} prompts for {name} ({tokens} tokens)")

        # Generate cache reuse test (same prefix, different suffixes)
        self._generate_cache_test(output_path)
        test_files["cache_reuse"] = str(output_path / "cache_reuse.json")

        return test_files

    def _generate_cache_test(self, output_path: Path):
        """Generate test for cache reuse (prefix caching)"""
        # Create a long shared prefix
        shared_prefix = f"{self.RAG_PREFIXES[0]}\n\nContext:\n"
        shared_prefix += (self.LOREM_IPSUM * 100)[:8000]  # ~2000 tokens

        # Generate different questions with same prefix
        prompts = [
            {
                "id": f"cache_test_{i}",
                "prompt": f"{shared_prefix}\n\nQuestion: {q}",
                "type": "rag",
                "target_tokens": 2048,
                "max_tokens": 128,
                "shared_prefix": shared_prefix,  # For analysis
            }
            for i, q in enumerate(self.QUESTIONS * 10)  # 80 questions
        ]

        file_path = output_path / "cache_reuse.json"
        with open(file_path, 'w') as f:
            json.dump(prompts, f, indent=2)

        print(f"✓ Generated {len(prompts)} cache reuse test prompts")


def main():
    """Generate test data"""
    generator = TestDataGenerator()

    print("Generating LLM benchmark test data...")
    print("=" * 60)

    test_files = generator.generate_test_suite()

    print("=" * 60)
    print(f"✓ Test data generated in ./data/")
    print(f"✓ Total test suites: {len(test_files)}")


if __name__ == "__main__":
    main()
