#!/usr/bin/env python3
"""Generate text embeddings using Gemini API.

Usage:
    python embed.py "Your text here"
    python embed.py "Search query" --task RETRIEVAL_QUERY
    python embed.py "Document text" --task RETRIEVAL_DOCUMENT --dim 768
    python embed.py "Text 1" "Text 2" "Text 3" --similarity

Requirements:
    pip install google-genai numpy
"""

import argparse
import os
import sys

# Load .env file if present
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def get_client():
    """Get Gemini API client."""
    try:
        from google import genai
    except ImportError:
        print("Error: google-genai not installed. Run: pip install google-genai")
        sys.exit(1)

    api_key = os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        sys.exit(1)

    return genai.Client(api_key=api_key)


def generate_embeddings(
    texts: list[str],
    model: str = "gemini-embedding-001",
    task_type: str = "SEMANTIC_SIMILARITY",
    output_dim: int | None = None,
) -> list[list[float]]:
    """Generate embeddings for texts.

    Args:
        texts: List of texts to embed
        model: Embedding model ID
        task_type: Task type for optimization
        output_dim: Output dimensionality (768, 1536, or 3072)

    Returns:
        List of embedding vectors
    """
    from google.genai import types

    client = get_client()

    config = types.EmbedContentConfig(task_type=task_type)
    if output_dim:
        config.output_dimensionality = output_dim

    response = client.models.embed_content(
        model=model,
        contents=texts if len(texts) > 1 else texts[0],
        config=config,
    )

    return [e.values for e in response.embeddings]


def calculate_similarity(embeddings: list[list[float]]) -> list[tuple[int, int, float]]:
    """Calculate pairwise cosine similarity."""
    try:
        import numpy as np
    except ImportError:
        print("Error: numpy not installed. Run: pip install numpy")
        sys.exit(1)

    embeddings_array = np.array(embeddings)

    # Normalize
    norms = np.linalg.norm(embeddings_array, axis=1, keepdims=True)
    normalized = embeddings_array / norms

    # Calculate similarity matrix
    similarity_matrix = np.dot(normalized, normalized.T)

    # Extract pairs
    pairs = []
    n = len(embeddings)
    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((i, j, float(similarity_matrix[i, j])))

    return pairs


def main():
    parser = argparse.ArgumentParser(
        description="Generate text embeddings using Gemini API"
    )
    parser.add_argument("texts", nargs="+", help="Text(s) to embed")
    parser.add_argument(
        "--model",
        "-m",
        default="gemini-embedding-001",
        help="Model ID (default: gemini-embedding-001)",
    )
    parser.add_argument(
        "--task",
        "-t",
        default="SEMANTIC_SIMILARITY",
        choices=[
            "SEMANTIC_SIMILARITY",
            "RETRIEVAL_DOCUMENT",
            "RETRIEVAL_QUERY",
            "CLASSIFICATION",
            "CLUSTERING",
        ],
        help="Task type (default: SEMANTIC_SIMILARITY)",
    )
    parser.add_argument(
        "--dim",
        "-d",
        type=int,
        choices=[768, 1536, 3072],
        help="Output dimensionality (default: 3072)",
    )
    parser.add_argument(
        "--similarity",
        "-s",
        action="store_true",
        help="Calculate pairwise similarity (requires multiple texts)",
    )
    parser.add_argument(
        "--json", "-j", action="store_true", help="Output embeddings as JSON"
    )

    args = parser.parse_args()

    try:
        embeddings = generate_embeddings(
            texts=args.texts,
            model=args.model,
            task_type=args.task,
            output_dim=args.dim,
        )

        if args.json:
            import json

            print(json.dumps(embeddings))
        elif args.similarity and len(args.texts) > 1:
            pairs = calculate_similarity(embeddings)
            print("Pairwise Similarity:")
            for i, j, sim in pairs:
                print(
                    f"  '{args.texts[i][:30]}...' <-> '{args.texts[j][:30]}...': {sim:.4f}"
                )
        else:
            for i, (text, emb) in enumerate(zip(args.texts, embeddings)):
                print(f"Text {i + 1}: '{text[:50]}...'")
                print(f"  Dimension: {len(emb)}")
                print(f"  First 5 values: {emb[:5]}")
                print()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
