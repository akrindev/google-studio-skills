#!/usr/bin/env node
"use strict";

import { readFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { parseArgs } from "node:util";

import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";

dotenv.config();

const DEFAULT_MODEL = "gemini-3-flash-preview";

function printUsage() {
  console.log(`Generate text content using Gemini API.

Usage:
  node scripts/generate.js "Your prompt here"
  node scripts/generate.js "Describe this" --image photo.png
  node scripts/generate.js "Complex task" --thinking
  node scripts/generate.js "Return JSON" --json
  node scripts/generate.js "Current events" --grounding
  node scripts/generate.js "Be helpful" --system "You are a coding assistant"

Options:
  --model, -m        Model ID (default: ${DEFAULT_MODEL})
  --image, -i        Path to image for multimodal prompt
  --system, -s       System instruction
  --thinking, -t     Enable thinking mode
  --json, -j         Force JSON response format
  --grounding, -g    Enable Google Search grounding
  --temperature      Sampling temperature (0.0-2.0)
  --max-tokens       Maximum output tokens
  --help, -h         Show this help message

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

function getMimeType(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === ".png") return "image/png";
  if (ext === ".jpg" || ext === ".jpeg") return "image/jpeg";
  if (ext === ".webp") return "image/webp";
  return "application/octet-stream";
}

async function generateContent({
  prompt,
  model = DEFAULT_MODEL,
  imagePath,
  systemInstruction,
  thinking,
  jsonOutput,
  grounding,
  temperature,
  maxTokens,
}) {
  const ai = new GoogleGenAI({ apiKey: getApiKey() });

  let contents = prompt;
  if (imagePath) {
    const imageData = await readFile(imagePath);
    contents = [
      { role: "user", parts: [{ text: prompt }, { inlineData: { mimeType: getMimeType(imagePath), data: imageData.toString("base64") } }] },
    ];
  }

  const config = {};
  if (systemInstruction) {
    config.systemInstruction = systemInstruction;
  }
  if (thinking) {
    config.thinkingConfig = { thinkingBudget: 1024 };
  }
  if (jsonOutput) {
    config.responseMimeType = "application/json";
  }
  if (grounding) {
    config.tools = [{ googleSearch: {} }];
  }
  if (temperature !== undefined) {
    config.temperature = temperature;
  }
  if (maxTokens !== undefined) {
    config.maxOutputTokens = maxTokens;
  }

  const response = await ai.models.generateContent({
    model,
    contents,
    config,
  });

  return response.text || "";
}

function parseCli() {
  const { values, positionals } = parseArgs({
    options: {
      model: { type: "string", short: "m", default: DEFAULT_MODEL },
      image: { type: "string", short: "i" },
      system: { type: "string", short: "s" },
      thinking: { type: "boolean", short: "t", default: false },
      json: { type: "boolean", short: "j", default: false },
      grounding: { type: "boolean", short: "g", default: false },
      temperature: { type: "string" },
      "max-tokens": { type: "string" },
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

  const temperature = values.temperature !== undefined ? Number(values.temperature) : undefined;
  const maxTokens = values["max-tokens"] !== undefined ? Number(values["max-tokens"]) : undefined;

  if (temperature !== undefined && Number.isNaN(temperature)) {
    throw new Error("--temperature must be a number");
  }
  if (maxTokens !== undefined && (!Number.isInteger(maxTokens) || maxTokens <= 0)) {
    throw new Error("--max-tokens must be a positive integer");
  }

  return {
    prompt: positionals.join(" "),
    model: values.model,
    imagePath: values.image,
    systemInstruction: values.system,
    thinking: values.thinking,
    jsonOutput: values.json,
    grounding: values.grounding,
    temperature,
    maxTokens,
  };
}

async function main() {
  try {
    const options = parseCli();
    const output = await generateContent(options);
    console.log(output);
  } catch (error) {
    console.error(`Error: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

await main();
