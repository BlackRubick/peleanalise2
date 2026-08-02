#!/usr/bin/env node
/**
 * ia-train.js — Entrenar modelo de IA (DermaMNIST → EfficientNetB0)
 * Run via: npm run ia:train
 */

'use strict';

const { spawnSync } = require('child_process');
const path = require('path');
const fs   = require('fs');

const IS_WIN   = process.platform === 'win32';
const FRONTEND = __dirname;
const AI_DIR   = path.resolve(FRONTEND, '..', 'python-ai');
const VENV_PY  = IS_WIN
  ? path.join(AI_DIR, 'venv', 'Scripts', 'python.exe')
  : path.join(AI_DIR, 'venv', 'bin', 'python3');
const MODEL    = path.join(AI_DIR, 'models', 'melanoma_classifier.keras');
const SCRIPT   = path.join(AI_DIR, 'scripts', 'train_model.py');

const C = {
  reset: '\x1b[0m', bold: '\x1b[1m',
  cyan: '\x1b[36m', green: '\x1b[32m', yellow: '\x1b[33m', red: '\x1b[31m',
};

console.log('');
console.log(`${C.cyan}${C.bold}╔══════════════════════════════════════╗${C.reset}`);
console.log(`${C.cyan}${C.bold}║    PeleAnálise — Entrenamiento IA    ║${C.reset}`);
console.log(`${C.cyan}${C.bold}╚══════════════════════════════════════╝${C.reset}`);
console.log('');

// Verify venv exists
if (!fs.existsSync(VENV_PY)) {
  console.log(`${C.yellow}⚠  Entorno virtual no encontrado.${C.reset}`);
  console.log(`${C.yellow}   Ejecuta primero: npm run dev${C.reset}`);
  console.log(`${C.yellow}   Esto creará el venv e instalará las dependencias Python.${C.reset}`);
  process.exit(1);
}

// Warn if model already exists
if (fs.existsSync(MODEL)) {
  const sizeMB = (fs.statSync(MODEL).size / 1024 / 1024).toFixed(1);
  console.log(`${C.yellow}⚠  Ya existe un modelo entrenado (${sizeMB} MB).${C.reset}`);
  console.log(`${C.yellow}   El entrenamiento lo sobreescribirá.${C.reset}`);
  console.log('');
}

console.log(`${C.cyan}   Dataset:  DermaMNIST (HAM10000 real, descarga automática)${C.reset}`);
console.log(`${C.cyan}   Modelo:   EfficientNetB0 fine-tuned${C.reset}`);
console.log(`${C.cyan}   Tiempo:   ~30-60 min (CPU) / ~15 min (GPU)${C.reset}`);
console.log(`${C.cyan}   Destino:  python-ai/models/melanoma_classifier.keras${C.reset}`);
console.log('');
console.log(`${C.yellow}   Descargando dataset si es necesario...${C.reset}`);
console.log('');

const result = spawnSync(VENV_PY, [SCRIPT], {
  cwd: AI_DIR,
  stdio: 'inherit',
  shell: false,
  env: { ...process.env, PYTHONUNBUFFERED: '1' },
});

if (result.status === 0) {
  console.log('');
  console.log(`${C.green}${C.bold}✓  Modelo guardado en python-ai/models/melanoma_classifier.keras${C.reset}`);
  console.log(`${C.green}   Reinicia el servidor para activar las predicciones reales.${C.reset}`);
} else {
  console.log('');
  console.log(`${C.red}✗  El entrenamiento falló (código ${result.status}).${C.reset}`);
  process.exit(result.status ?? 1);
}
