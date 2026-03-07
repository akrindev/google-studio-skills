#!/usr/bin/env node
"use strict";

import process from "node:process";
import { parseArgs } from "node:util";

import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";

dotenv.config();

const DEFAULT_MODEL = "gemini-embedding-001";
const DEFAULT_TASK = "SEMANTIC_SIMILARITY";
const TASK_CHOICES = [
  "SEMANTIC_SIMILARITY",
  "RETRIEVAL_DOCUMENT",
  "RETRIEVAL_QUERY",
  "CLASSIFICATION",
  "CLUSTERING",
];
const DIM_CHOICES = [768, 1536, 3072];

function printUsage() {
  console.log(`Generate text embeddings using Gemini API.

Usage:
  node scripts/embed.js "Your text here"
  node scripts/embed.js "Search query" --task RETRIEVAL_QUERY
  node scripts/embed.js "Document text" --task RETRIEVAL_DOCUMENT --dim 768
  node scripts/embed.js "Text 1" "Text 2" "Text 3" --similarity

Options:
  --model, -m         Model ID (default: ${DEFAULT_MODEL})
  --task, -t          Task type (default: ${DEFAULT_TASK})
  --dim, -d           Output dimensionality: 768 | 1536 | 3072
  --similarity, -s    Calculate pairwise similarity
  --json, -j          Output embeddings as JSON
  --help, -h          Show this help message

Requirements:
  npm install @google/genai@latest dotenv@latest
`);
}

function getApiKey() {
  const apiKey = process.env.GOOGLE_API_KEY || process.env.GEMINI_API_KEY;
  if (!apiKey) {
    throw new Error("Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable");
  }
  return apiKey;
}

function cosineSimilarity(a, b) {
  let dot = 0;
  let normA = 0;
  let normB = 0;

  for (let i = 0; i < a.length; i += 1) {
    dot += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }

  if (normA === 0 || normB === 0) {
    return 0;
  }

  return dot / (Math.sqrt(normA) * Math.sqrt(normB));
}

function calculateSimilarity(embeddings) {
  const pairs = [];
  for (let i = 0; i < embeddings.length; i += 1) {
    for (let j = i + 1; j < embeddings.length; j += 1) {
      pairs.push([i, j, cosineSimilarity(embeddings[i], embeddings[j])]);
    }
  }
  return pairs;
}

async function generateEmbeddings({ texts, model, taskType, outputDim }) {
  const ai = new GoogleGenAI({ apiKey: getApiKey() });

  const config = { taskType };
  if (outputDim) {
    config.outputDimensionality = outputDim;
  }

  const response = await ai.models.embedContent({
    model,
    contents: texts.length > 1 ? texts : texts[0],
    config,
  });

  return (response.embeddings || []).map((e) => e.values || []);
}

function parseCli() {
  const { values, positionals } = parseArgs({
    options: {
      model: { type: "string", short: "m", default: DEFAULT_MODEL },
      task: { type: "string", short: "t", default: DEFAULT_TASK },
      dim: { type: "string", short: "d" },
      similarity: { type: "boolean", short: "s", default: false },
      json: { type: "boolean", short: "j", default: false },
      help: { type: "boolean", short: "h", default: false },
    },
    allowPositionals: true,
  });

  if (values.help) {
    printUsage();
    process.exit(0);
  }

  if (positionals.length === 0) {
    printUsage();
    process.exit(1);
  }

  if (!TASK_CHOICES.includes(values.task)) {
    throw new Error(`--task must be one of: ${TASK_CHOICES.join(", ")}`);
  }

  let dim;
  if (values.dim !== undefined) {
    dim = Number(values.dim);
    if (!DIM_CHOICES.includes(dim)) {
      throw new Error(`--dim must be one of: ${DIM_CHOICES.join(", ")}`);
    }
  }

  return {
    texts: positionals,
    model: values.model,
    taskType: values.task,
    outputDim: dim,
    similarity: values.similarity,
    json: values.json,
  };
}

async function main() {
  try {
    const options = parseCli();
    const embeddings = await generateEmbeddings(options);

    if (options.json) {
      console.log(JSON.stringify(embeddings));
      return;
    }

    if (options.similarity && options.texts.length > 1) {
      const pairs = calculateSimilarity(embeddings);
      console.log("Pairwise Similarity:");
      for (const [i, j, sim] of pairs) {
        const left = `${options.texts[i].slice(0, 30)}...`;
        const right = `${options.texts[j].slice(0, 30)}...`;
        console.log(`  '${left}' <-> '${right}': ${sim.toFixed(4)}`);
      }
      return;
    }

    embeddings.forEach((embedding, index) => {
      console.log(`Text ${index + 1}: '${options.texts[index].slice(0, 50)}...'`);
      console.log(`  Dimension: ${embedding.length}`);
      console.log(`  First 5 values: ${JSON.stringify(embedding.slice(0, 5))}`);
      console.log("");
    });
  } catch (error) {
    console.error(`Error: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

await main();
