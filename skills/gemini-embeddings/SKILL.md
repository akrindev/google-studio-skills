---
name: gemini-embeddings
description: Generate text embeddings using Gemini Embedding API for semantic search, similarity matching, clustering, and RAG applications. Use for creating vector representations of text, document retrieval, and semantic analysis. Triggers on "embeddings", "semantic search", "vector search", "text similarity", "RAG", "retrieval".
---

# Gemini Embeddings

Generate high-quality text embeddings for semantic search, similarity analysis, clustering, and RAG (Retrieval Augmented Generation) applications.

## Prerequisites

- Set `GOOGLE_API_KEY` or `GEMINI_API_KEY` environment variable
- Install: `pip install google-genai`

## Quick Start

```python
from google import genai
from google.genai import types

client = genai.Client()

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents="What is the meaning of life?",
    config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
)

embedding = response.embeddings[0].values
print(f"Embedding dimension: {len(embedding)}")
```

## Available Scripts

- **scripts/embed.py** - Generate embeddings with configurable options

## Models

### Gemini Embedding (Current)
- **Model ID**: `gemini-embedding-001`
- **Output dimensions**: 768, 1536, or 3072 (configurable)
- **Default dimension**: 3072

### Text Embedding (DEPRECATED)
- **Model ID**: `text-embedding-004`
- **Status**: SHUT DOWN January 14, 2026
- **Use `gemini-embedding-001` instead**

## Task Types

| Task Type | Best For |
|-----------|----------|
| `SEMANTIC_SIMILARITY` | Comparing text similarity |
| `RETRIEVAL_DOCUMENT` | Embedding documents for retrieval |
| `RETRIEVAL_QUERY` | Embedding search queries |
| `CLASSIFICATION` | Text classification tasks |
| `CLUSTERING` | Grouping similar texts |

## Configurable Dimensions

```python
# Smaller dimension for efficiency
response = client.models.embed_content(
    model="gemini-embedding-001",
    contents="Your text here",
    config=types.EmbedContentConfig(
        output_dimensionality=768  # 768, 1536, or 3072
    )
)
```

## Batch Embedding

```python
texts = [
    "What is the meaning of life?",
    "What is the purpose of existence?",
    "How do I bake a cake?"
]

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents=texts,
    config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
)

embeddings = [e.values for e in response.embeddings]
```

## Similarity Calculation

```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Generate embeddings
result = [
    np.array(e.values) for e in client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY")
    ).embeddings
]

# Calculate similarity
similarity_matrix = cosine_similarity(np.array(result))
```

## Use Cases

- **Semantic Search**: Find documents similar to a query
- **RAG**: Retrieve relevant context for LLM prompts
- **Clustering**: Group similar documents
- **Classification**: Categorize text based on embeddings
- **Duplicate Detection**: Find near-duplicate content
