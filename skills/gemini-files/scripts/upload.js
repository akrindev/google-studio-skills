#!/usr/bin/env node
"use strict";

import { access } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { parseArgs } from "node:util";

import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";

dotenv.config();

const MIME_TYPES = {
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".png": "image/png",
  ".gif": "image/gif",
  ".webp": "image/webp",
  ".pdf": "application/pdf",
  ".txt": "text/plain",
  ".mp3": "audio/mpeg",
  ".wav": "audio/wav",
  ".mp4": "video/mp4",
  ".mov": "video/quicktime",
  ".avi": "video/x-msvideo",
  ".webm": "video/webm",
  ".jsonl": "application/jsonl",
};

function printUsage() {
  console.log(`Upload files to Gemini File API.

Usage:
  node scripts/upload.js image.jpg
  node scripts/upload.js document.pdf --name "my-document"
  node scripts/upload.js video.mp4 --wait

Options:
  --name, -n      Display name for uploaded file
  --wait, -w      Wait until file becomes ACTIVE
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

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function getState(value) {
  if (!value) return "UNKNOWN";
  if (typeof value === "string") return value;
  if (typeof value.name === "string") return value.name;
  return String(value);
}

async function uploadFile({ filePath, displayName, wait }) {
  await access(filePath);
  const mimeType = MIME_TYPES[path.extname(filePath).toLowerCase()] || "application/octet-stream";

  const ai = new GoogleGenAI({ apiKey: getApiKey() });
  console.log(`Uploading ${filePath}...`);

  const uploadedFile = await ai.files.upload({
    file: filePath,
    config: {
      mimeType,
      displayName: displayName || path.basename(filePath),
    },
  });

  let state = getState(uploadedFile.state);
  console.log(`Uploaded: ${uploadedFile.name}`);
  console.log(`URI: ${uploadedFile.uri}`);
  console.log(`State: ${state}`);

  if (wait && state !== "ACTIVE") {
    console.log("Waiting for processing...");
    while (true) {
      const fileInfo = await ai.files.get({ name: uploadedFile.name });
      state = getState(fileInfo.state);
      if (state === "ACTIVE") {
        console.log("File ready!");
        break;
      }
      if (state === "FAILED") {
        throw new Error("Processing failed");
      }
      console.log("  Still processing...");
      await sleep(2000);
    }
  }

  return {
    name: uploadedFile.name,
    uri: uploadedFile.uri,
    displayName: uploadedFile.displayName,
    mimeType,
    state,
  };
}

function parseCli() {
  const { values, positionals } = parseArgs({
    options: {
      name: { type: "string", short: "n" },
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
    filePath: positionals[0],
    displayName: values.name,
    wait: values.wait,
  };
}

async function main() {
  try {
    const options = parseCli();
    const result = await uploadFile(options);
    console.log(`\nFile name: ${result.name}`);
    console.log("Use this name to reference the file in API calls");
  } catch (error) {
    console.error(`Error: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

await main();
