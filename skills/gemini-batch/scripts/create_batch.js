#!/usr/bin/env node
"use strict";

import { access } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { parseArgs } from "node:util";

import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";

dotenv.config();

const DEFAULT_MODEL = "gemini-3-flash-preview";

function printUsage() {
  console.log(`Create a batch job from a JSONL file.

Usage:
  node scripts/create_batch.js requests.jsonl
  node scripts/create_batch.js requests.jsonl --model gemini-3-flash-preview
  node scripts/create_batch.js requests.jsonl --name "my-batch-job"

Options:
  --model, -m      Model ID (default: ${DEFAULT_MODEL})
  --name, -n       Display name for batch job
  --help, -h       Show this help message

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

async function createBatchJob({ inputFile, model, displayName }) {
  await access(inputFile);
  const ai = new GoogleGenAI({ apiKey: getApiKey() });

  console.log(`Uploading batch input file: ${inputFile}...`);
  const uploadedFile = await ai.files.upload({
    file: inputFile,
    config: {
      displayName: displayName || path.parse(inputFile).name,
      mimeType: "jsonl",
    },
  });

  console.log(`File uploaded: ${uploadedFile.name}`);

  const batchJob = await ai.batches.create({
    model,
    src: uploadedFile.name,
    config: {
      displayName: displayName || `batch-${path.parse(inputFile).name}`,
    },
  });

  console.log(`Batch job created: ${batchJob.name}`);
  return batchJob.name;
}

function parseCli() {
  const { values, positionals } = parseArgs({
    options: {
      model: { type: "string", short: "m", default: DEFAULT_MODEL },
      name: { type: "string", short: "n" },
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

  return {
    inputFile: positionals[0],
    model: values.model,
    displayName: values.name,
  };
}

async function main() {
  try {
    const options = parseCli();
    const jobName = await createBatchJob(options);
    console.log(`\nJob name: ${jobName}`);
    console.log("Use check_status.js to monitor progress");
  } catch (error) {
    console.error(`Error: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

await main();
