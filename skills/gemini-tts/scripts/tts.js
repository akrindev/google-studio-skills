#!/usr/bin/env node
"use strict";

import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import process from "node:process";
import { parseArgs } from "node:util";

import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";

dotenv.config();

const DEFAULT_VOICE = "Kore";
const DEFAULT_OUTPUT_DIR = "audio/";
const DEFAULT_OUTPUT_NAME = "tts_output";
const DEFAULT_MODEL = "gemini-2.5-flash-preview-tts";

function printUsage() {
  console.log(`Generate speech from text using Gemini TTS API.

Usage:
  node scripts/tts.js "Hello, world!"
  node scripts/tts.js "Welcome!" --voice Puck --output welcome
  node scripts/tts.js "Conversation text" --speakers "Joe:Kore,Jane:Puck"
  node scripts/tts.js "Long text" --stream
  node scripts/tts.js "Custom folder" --output-dir ./my-audio/

Options:
  --voice, -v        Voice name (default: ${DEFAULT_VOICE})
  --output-dir       Output directory (default: ${DEFAULT_OUTPUT_DIR})
  --output, -o       Base output name (default: ${DEFAULT_OUTPUT_NAME})
  --no-timestamp     Disable timestamp in filename
  --model, -m        TTS model ID (default: ${DEFAULT_MODEL})
  --stream, -s       Use streaming mode
  --speakers         Multi-speaker map: "Joe:Kore,Jane:Puck"
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

function parseSpeakers(input) {
  const entries = [];
  for (const pair of input.split(",")) {
    if (!pair.includes(":")) continue;
    const [speaker, voice] = pair.split(":", 2).map((v) => v.trim());
    if (speaker && voice) {
      entries.push({ speaker, voice });
    }
  }
  return entries;
}

function decodeAudioData(data) {
  if (!data) return null;
  if (typeof data === "string") return Buffer.from(data, "base64");
  if (data instanceof Uint8Array) return Buffer.from(data);
  if (Array.isArray(data)) return Buffer.from(data);
  return null;
}

function buildWavBuffer(pcmData, sampleRate = 24000) {
  const channels = 1;
  const bitsPerSample = 16;
  const byteRate = sampleRate * channels * (bitsPerSample / 8);
  const blockAlign = channels * (bitsPerSample / 8);
  const dataSize = pcmData.length;
  const buffer = Buffer.alloc(44 + dataSize);

  buffer.write("RIFF", 0);
  buffer.writeUInt32LE(36 + dataSize, 4);
  buffer.write("WAVE", 8);
  buffer.write("fmt ", 12);
  buffer.writeUInt32LE(16, 16);
  buffer.writeUInt16LE(1, 20);
  buffer.writeUInt16LE(channels, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(byteRate, 28);
  buffer.writeUInt16LE(blockAlign, 32);
  buffer.writeUInt16LE(bitsPerSample, 34);
  buffer.write("data", 36);
  buffer.writeUInt32LE(dataSize, 40);
  pcmData.copy(buffer, 44);
  return buffer;
}

function buildFilename(baseName, useTimestamp) {
  if (!useTimestamp) {
    return baseName.endsWith(".wav") ? baseName : `${baseName}.wav`;
  }
  const now = new Date();
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, "0");
  const dd = String(now.getDate()).padStart(2, "0");
  const hh = String(now.getHours()).padStart(2, "0");
  const mi = String(now.getMinutes()).padStart(2, "0");
  const ss = String(now.getSeconds()).padStart(2, "0");
  return `${baseName}_${yyyy}${mm}${dd}_${hh}${mi}${ss}.wav`;
}

async function generateTts({ text, voice, outputDir, outputName, model, stream, speakers, useTimestamp }) {
  const ai = new GoogleGenAI({ apiKey: getApiKey() });

  let speechConfig;
  if (speakers.length > 0) {
    speechConfig = {
      multiSpeakerVoiceConfig: {
        speakerVoiceConfigs: speakers.map((entry) => ({
          speaker: entry.speaker,
          voiceConfig: {
            prebuiltVoiceConfig: { voiceName: entry.voice },
          },
        })),
      },
    };
  } else {
    speechConfig = {
      voiceConfig: {
        prebuiltVoiceConfig: { voiceName: voice },
      },
    };
  }

  const request = {
    model,
    contents: [{ role: "user", parts: [{ text }] }],
    config: {
      responseModalities: ["AUDIO"],
      speechConfig,
    },
  };

  const chunks = [];
  if (stream) {
    console.log("Streaming audio...");
    const responseStream = await ai.models.generateContentStream(request);
    for await (const chunk of responseStream) {
      const part = chunk.candidates?.[0]?.content?.parts?.[0];
      const audioChunk = decodeAudioData(part?.inlineData?.data);
      if (audioChunk) {
        chunks.push(audioChunk);
      }
    }
  } else {
    const response = await ai.models.generateContent(request);
    const part = response.candidates?.[0]?.content?.parts?.[0];
    const audioData = decodeAudioData(part?.inlineData?.data);
    if (audioData) {
      chunks.push(audioData);
    }
  }

  if (chunks.length === 0) {
    throw new Error("No audio generated");
  }

  await mkdir(outputDir, { recursive: true });
  const filename = buildFilename(outputName, useTimestamp);
  const fullPath = path.join(outputDir, filename);
  const pcmData = Buffer.concat(chunks);
  const wavData = buildWavBuffer(pcmData, 24000);
  await writeFile(fullPath, wavData);
  console.log(`Saved: ${fullPath}`);
  return fullPath;
}

function parseCli() {
  const { values, positionals } = parseArgs({
    options: {
      voice: { type: "string", short: "v", default: DEFAULT_VOICE },
      "output-dir": { type: "string", default: DEFAULT_OUTPUT_DIR },
      output: { type: "string", short: "o", default: DEFAULT_OUTPUT_NAME },
      "no-timestamp": { type: "boolean", default: false },
      model: { type: "string", short: "m", default: DEFAULT_MODEL },
      stream: { type: "boolean", short: "s", default: false },
      speakers: { type: "string" },
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
    text: positionals.join(" "),
    voice: values.voice,
    outputDir: values["output-dir"],
    outputName: values.output,
    model: values.model,
    stream: values.stream,
    speakers: values.speakers ? parseSpeakers(values.speakers) : [],
    useTimestamp: !values["no-timestamp"],
  };
}

async function main() {
  try {
    const options = parseCli();
    await generateTts(options);
  } catch (error) {
    console.error(`Error: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

await main();
