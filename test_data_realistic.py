#!/usr/bin/env python3
"""
Realistic test data generator for LLM benchmarking.
Uses real-world text patterns instead of Lorem ipsum.
"""

import json
import random
from pathlib import Path
from typing import List, Dict


class RealisticTestDataGenerator:
    """Generate realistic test data for LLM benchmarking"""

    # Real conversational prompts
    CHAT_PROMPTS = [
        "What are the main differences between Python and JavaScript for web development?",
        "Can you explain how neural networks learn from data?",
        "I'm planning a trip to Japan. What should I know about transportation?",
        "How do I debug a memory leak in my Node.js application?",
        "What are the best practices for securing a REST API?",
        "Explain the concept of compound interest with a simple example.",
        "What causes inflation and how does it affect the economy?",
        "How can I improve my time management skills?",
        "What are the health benefits of intermittent fasting?",
        "Explain quantum computing in simple terms.",
        "What's the difference between machine learning and deep learning?",
        "How do I optimize SQL queries for better performance?",
        "What are some effective strategies for learning a new language?",
        "Explain the Byzantine Generals Problem in distributed systems.",
        "What causes climate change and what can we do about it?",
        "How does blockchain technology work?",
        "What are the key principles of user experience design?",
        "Explain the difference between abstract classes and interfaces.",
        "What are some common cognitive biases and how do they affect decision making?",
        "How does the immune system fight off infections?",
    ]

    # Technical documentation style text
    TECH_CONTEXT = """
    Kubernetes is an open-source container orchestration platform that automates the deployment,
    scaling, and management of containerized applications. It was originally developed by Google
    and is now maintained by the Cloud Native Computing Foundation.

    The core components of Kubernetes include:

    1. Master Node: Controls the cluster and makes scheduling decisions
       - API Server: Entry point for all REST commands
       - Scheduler: Assigns pods to nodes
       - Controller Manager: Maintains desired state
       - etcd: Distributed key-value store for cluster data

    2. Worker Nodes: Run containerized applications
       - Kubelet: Manages containers on the node
       - Kube-proxy: Handles networking
       - Container Runtime: Runs containers (Docker, containerd)

    Key concepts include Pods (smallest deployable units), Services (expose applications),
    Deployments (declarative updates), ConfigMaps and Secrets (configuration management),
    and Persistent Volumes (storage abstraction).

    Kubernetes uses a declarative approach where you specify the desired state, and the
    system works to maintain that state. This makes it resilient and self-healing.
    """

    PYTHON_DOCS = """
    Python is a high-level, interpreted programming language known for its simplicity and readability.
    It supports multiple programming paradigms including procedural, object-oriented, and functional
    programming.

    Key features include:
    - Dynamic typing and automatic memory management
    - Comprehensive standard library
    - Extensive third-party packages via PyPI
    - Cross-platform compatibility
    - Strong community support

    Common use cases:
    1. Web Development: Django, Flask, FastAPI
    2. Data Science: Pandas, NumPy, Scikit-learn
    3. Machine Learning: TensorFlow, PyTorch, Keras
    4. Automation: Scripting and task automation
    5. Scientific Computing: SciPy, Matplotlib

    Python follows the principle of "There should be one-- and preferably only one --obvious way
    to do it" from the Zen of Python. This philosophy emphasizes code readability and simplicity.
    """

    # Real code examples
    CODE_EXAMPLES = [
        """
def binary_search(arr, target):
    '''
    Perform binary search on a sorted array.
    Time complexity: O(log n)
    Space complexity: O(1)
    '''
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2

        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
""",
        """
class LRUCache:
    '''
    Least Recently Used (LRU) cache implementation.
    Uses OrderedDict for O(1) get and put operations.
    '''
    def __init__(self, capacity: int):
        self.cache = {}
        self.capacity = capacity
        self.order = []

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1

        self.order.remove(key)
        self.order.append(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.order.remove(key)
        elif len(self.cache) >= self.capacity:
            oldest = self.order.pop(0)
            del self.cache[oldest]

        self.cache[key] = value
        self.order.append(key)
""",
        """
async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Failed to fetch user data:', error);
        throw error;
    }
}
""",
    ]

    RAG_DOCUMENTS = [
        """
        The transformer architecture, introduced in "Attention is All You Need" (2017), revolutionized
        natural language processing. Unlike recurrent neural networks (RNNs), transformers process entire
        sequences in parallel using self-attention mechanisms.

        The core innovation is the attention mechanism, which allows the model to weigh the importance
        of different words in a sequence when processing each word. This is computed as:

        Attention(Q, K, V) = softmax(QK^T / √d_k)V

        Where Q (queries), K (keys), and V (values) are learned projections of the input. The architecture
        consists of an encoder and decoder, each with multiple layers of multi-head attention and
        feed-forward networks.

        Key advantages include:
        1. Parallelization: No sequential dependency enables faster training
        2. Long-range dependencies: Better capture of relationships between distant words
        3. Interpretability: Attention weights show what the model focuses on

        Transformers have become the foundation for modern language models like BERT, GPT, and T5,
        achieving state-of-the-art results across numerous NLP tasks including translation,
        summarization, and question answering.
        """,
        """
        Database indexing is a data structure technique used to optimize query performance. An index
        is similar to a book's index, allowing the database to quickly locate data without scanning
        every row.

        Types of indexes:

        1. B-Tree Index (most common):
           - Balanced tree structure
           - Efficient for range queries and exact matches
           - Default in most databases
           - Works well for equality and range predicates

        2. Hash Index:
           - Uses hash function for fast exact matches
           - O(1) lookup time
           - Not suitable for range queries

        3. Bitmap Index:
           - Efficient for columns with low cardinality
           - Uses bit arrays
           - Excellent for data warehousing

        4. Full-Text Index:
           - Specialized for text search
           - Supports natural language queries
           - Used in search engines

        Trade-offs:
        - Faster reads but slower writes (index must be updated)
        - Additional storage overhead
        - Memory consumption
        - Index maintenance cost

        Best practices:
        - Index foreign keys and frequently queried columns
        - Avoid over-indexing (diminishing returns)
        - Monitor index usage with EXPLAIN queries
        - Consider composite indexes for multi-column queries
        - Rebuild fragmented indexes periodically
        """,
    ]

    def __init__(self):
        self.chat_prompts = self.CHAT_PROMPTS.copy()
        random.shuffle(self.chat_prompts)

    def generate_chat_prompt(self, target_tokens: int) -> str:
        """Generate realistic chat prompt"""
        if target_tokens < 50:
            return random.choice(self.CHAT_PROMPTS)

        # For longer prompts, add context
        base_prompt = random.choice(self.CHAT_PROMPTS)

        if target_tokens < 200:
            context = "I've been reading about this topic and have some background knowledge. "
            return f"{context}{base_prompt}"

        # Add substantial context for longer prompts
        context_options = [self.TECH_CONTEXT, self.PYTHON_DOCS]
        context = random.choice(context_options)

        # Calculate how much context to include
        target_chars = target_tokens * 4
        context_needed = max(0, target_chars - len(base_prompt) - 50)

        if context_needed > len(context):
            # Repeat context if needed
            context = (context * (context_needed // len(context) + 1))[:context_needed]
        else:
            context = context[:context_needed]

        return f"{context.strip()}\n\nQuestion: {base_prompt}"

    def generate_rag_prompt(self, target_tokens: int) -> str:
        """Generate RAG-style prompt with document context"""
        question = random.choice(self.CHAT_PROMPTS)
        document = random.choice(self.RAG_DOCUMENTS)

        target_chars = target_tokens * 4
        context_needed = target_chars - len(question) - 100

        # Expand document if needed
        if context_needed > len(document):
            all_docs = " ".join(self.RAG_DOCUMENTS)
            document = (all_docs * (context_needed // len(all_docs) + 1))[:context_needed]
        else:
            document = document[:context_needed]

        return f"""Based on the following document, please answer the question.

Document:
{document.strip()}

Question: {question}

Please provide a detailed answer based only on the information in the document."""

    def generate_code_prompt(self, target_tokens: int) -> str:
        """Generate code-related prompt"""
        tasks = [
            "Review this code and suggest improvements:",
            "Debug this code and fix any issues:",
            "Optimize this code for better performance:",
            "Add error handling to this code:",
            "Refactor this code following best practices:",
            "Add unit tests for this code:",
            "Explain how this code works:",
            "Convert this code to use async/await:",
        ]

        task = random.choice(tasks)
        code = random.choice(self.CODE_EXAMPLES)

        target_chars = target_tokens * 4

        # Add multiple code examples if needed for length
        while len(task) + len(code) < target_chars * 0.8:
            code += "\n\n" + random.choice(self.CODE_EXAMPLES)

        prompt = f"{task}\n\n```python\n{code}\n```\n\nProvide detailed feedback and suggestions."

        return prompt[:target_chars]

    def generate_test_suite(self, output_dir: str = "data") -> Dict[str, str]:
        """Generate complete test suite with realistic data"""
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
            prompts = []

            for i in range(count):
                if ptype == "chat":
                    prompt_text = self.generate_chat_prompt(tokens)
                elif ptype == "rag":
                    prompt_text = self.generate_rag_prompt(tokens)
                elif ptype == "code":
                    prompt_text = self.generate_code_prompt(tokens)

                prompts.append({
                    "id": f"{name}_{i}",
                    "prompt": prompt_text,
                    "type": ptype,
                    "target_tokens": tokens,
                    "max_tokens": 128,
                })

            file_path = output_path / f"{name}.json"
            with open(file_path, 'w') as f:
                json.dump(prompts, f, indent=2)

            test_files[name] = str(file_path)
            print(f"✓ Generated {count} realistic prompts for {name} ({tokens} tokens)")

        # Generate cache reuse test
        self._generate_cache_test(output_path)
        test_files["cache_reuse"] = str(output_path / "cache_reuse.json")

        return test_files

    def _generate_cache_test(self, output_path: Path):
        """Generate test for cache reuse with realistic shared context"""
        # Use a real document as shared prefix
        shared_prefix = f"""Based on the following technical documentation, please answer the question.

Documentation:
{self.RAG_DOCUMENTS[0]}

{self.RAG_DOCUMENTS[1]}

"""

        # Generate different questions
        questions = self.CHAT_PROMPTS * 4  # 80 questions

        prompts = [
            {
                "id": f"cache_test_{i}",
                "prompt": f"{shared_prefix}Question: {q}\n\nProvide a detailed answer based on the documentation.",
                "type": "rag",
                "target_tokens": 2048,
                "max_tokens": 128,
                "shared_prefix": shared_prefix,
            }
            for i, q in enumerate(questions)
        ]

        file_path = output_path / "cache_reuse.json"
        with open(file_path, 'w') as f:
            json.dump(prompts, f, indent=2)

        print(f"✓ Generated {len(prompts)} cache reuse test prompts with realistic context")


def main():
    """Generate realistic test data"""
    generator = RealisticTestDataGenerator()

    print("Generating REALISTIC LLM benchmark test data...")
    print("=" * 60)
    print("Using real conversational patterns, code, and documentation")
    print("=" * 60)

    test_files = generator.generate_test_suite()

    print("=" * 60)
    print(f"✓ Realistic test data generated in ./data/")
    print(f"✓ Total test suites: {len(test_files)}")
    print("\nThis data is much more representative of actual LLM workloads!")


if __name__ == "__main__":
    main()
