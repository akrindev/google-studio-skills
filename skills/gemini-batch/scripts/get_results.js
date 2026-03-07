#!/usr/bin/env node
"use strict";

import { writeFile } from "node:fs/promises";
import process from "node:process";
import { parseArgs } from "node:util";

import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";

dotenv.config();

function printUsage() {
  console.log(`Retrieve batch job results.

Usage:
  node scripts/get_results.js <job_name>
  node scripts/get_results.js batches/abc123 --output results.jsonl

Options:
  --output, -o    Output file path for result JSONL
  --help, -h      Show this help message

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

function getState(value) {
  if (!value) return "UNKNOWN";
  if (typeof value === "string") return value;
  if (typeof value.name === "string") return value.name;
  return String(value);
}

async function getResults({ jobName, outputPath }) {
  const ai = new GoogleGenAI({ apiKey: getApiKey() });

  const batchJob = await ai.batches.get({ name: jobName });
  const state = getState(batchJob.state);
  if (state !== "JOB_STATE_SUCCEEDED") {
    console.log(`Warning: Job is not completed. State: ${state}`);
    return null;
  }

  if (batchJob.dest?.fileName) {
    const resultFileName = batchJob.dest.fileName;
    console.log(`Downloading results from: ${resultFileName}`);

    const fileContent = await ai.files.download({ file: resultFileName });
    const content = Buffer.from(fileContent).toString("utf-8");

    if (outputPath) {
      await writeFile(outputPath, content, "utf-8");
      console.log(`Results saved to ${outputPath}`);
    } else {
      console.log("Results:");
      for (const line of content.trim().split("\n")) {
        try {
          const result = JSON.parse(line);
          console.log(`  Key: ${result.key ?? "N/A"}`);
          if (result.response) {
            const text = result.response.text ?? JSON.stringify(result.response);
            console.log(`  Response: ${String(text).slice(0, 200)}...`);
          }
        } catch {
          console.log(`  ${line.slice(0, 200)}...`);
        }
      }
    }
    return content;
  }

  if (batchJob.dest?.inlinedResponses) {
    console.log("Inline Results:");
    batchJob.dest.inlinedResponses.forEach((resp, index) => {
      console.log(`\nResponse ${index + 1}:`);
      if (resp.response) {
        const text = resp.response.text ?? JSON.stringify(resp.response);
        console.log(text);
      } else if (resp.error) {
        console.log(`Error: ${typeof resp.error === "string" ? resp.error : JSON.stringify(resp.error)}`);
      }
    });
    return "inline_results";
  }

  console.log("No results found.");
  return null;
}

function parseCli() {
  const { values, positionals } = parseArgs({
    options: {
      output: { type: "string", short: "o" },
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
    jobName: positionals[0],
    outputPath: values.output,
  };
}

async function main() {
  try {
    const options = parseCli();
    await getResults(options);
  } catch (error) {
    console.error(`Error: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

await main();
