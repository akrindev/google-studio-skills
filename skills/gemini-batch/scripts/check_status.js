#!/usr/bin/env node
"use strict";

import process from "node:process";
import { parseArgs } from "node:util";

import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";

dotenv.config();

const COMPLETED_STATES = new Set([
  "JOB_STATE_SUCCEEDED",
  "JOB_STATE_FAILED",
  "JOB_STATE_CANCELLED",
  "JOB_STATE_EXPIRED",
]);

function printUsage() {
  console.log(`Check batch job status.

Usage:
  node scripts/check_status.js <job_name>
  node scripts/check_status.js batches/abc123 --wait

Options:
  --wait, -w      Poll every 30s until complete
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

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function checkStatus({ jobName, wait }) {
  const ai = new GoogleGenAI({ apiKey: getApiKey() });

  let batchJob = await ai.batches.get({ name: jobName });
  let state = getState(batchJob.state);

  if (wait) {
    console.log(`Polling status for job: ${jobName}`);
    while (!COMPLETED_STATES.has(state)) {
      console.log(`Current state: ${state}`);
      await sleep(30000);
      batchJob = await ai.batches.get({ name: jobName });
      state = getState(batchJob.state);
    }
  }

  if (state === "JOB_STATE_SUCCEEDED") {
    console.log("Job succeeded!");
  } else if (state === "JOB_STATE_FAILED") {
    console.log("Job failed!");
    if (batchJob.error) {
      console.log(`Error: ${typeof batchJob.error === "string" ? batchJob.error : JSON.stringify(batchJob.error)}`);
    }
  } else {
    console.log(`Job state: ${state}`);
  }

  return state;
}

function parseCli() {
  const { values, positionals } = parseArgs({
    options: {
      wait: { type: "boolean", short: "w", default: false },
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
    wait: values.wait,
  };
}

async function main() {
  try {
    const options = parseCli();
    await checkStatus(options);
  } catch (error) {
    console.error(`Error: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

await main();
