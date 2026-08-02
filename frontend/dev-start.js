#!/usr/bin/env node
/**
 * dev-start.js — Cross-platform dev launcher for PeleAnálise
 * Works on macOS and Windows (no bash / PowerShell required).
 * Run via: npm run dev
 */

'use strict';

const { execSync, spawnSync, spawn } = require('child_process');
const path   = require('path');
const fs     = require('fs');
const rl     = require('readline');

// ── constants ──────────────────────────────────────────────────────────────────
const IS_WIN     = process.platform === 'win32';
const FRONTEND   = __dirname;                                        // frontend/
const AI_DIR     = path.resolve(FRONTEND, '..', 'python-ai');       // python-ai/
const VENV       = path.join(AI_DIR, 'venv');
const MODEL_FILE = path.join(AI_DIR, 'models', 'melanoma_classifier.keras');

const VENV_PY  = IS_WIN
  ? path.join(VENV, 'Scripts', 'python.exe')
  : path.join(VENV, 'bin', 'python3');
const VENV_PIP = IS_WIN
  ? path.join(VENV, 'Scripts', 'pip.exe')
  : path.join(VENV, 'bin', 'pip');

// ── colors ─────────────────────────────────────────────────────────────────────
const C = {
  reset: '\x1b[0m', bold: '\x1b[1m',
  cyan: '\x1b[36m', magenta: '\x1b[35m',
  green: '\x1b[32m', yellow: '\x1b[33m', red: '\x1b[31m',
};
const ok   = m => console.log(`${C.green}✓  ${m}${C.reset}`);
const warn = m => console.log(`${C.yellow}⚠  ${m}${C.reset}`);
const step = m => console.log(`${C.yellow}⟳  ${m}${C.reset}`);
const info = m => console.log(`${C.cyan}   ${m}${C.reset}`);
const err  = m => console.log(`${C.red}✗  ${m}${C.reset}`);

// ── shell helpers ──────────────────────────────────────────────────────────────
function run(cmd, opts = {}) {
  try {
    execSync(cmd, {
      stdio: opts.silent ? 'pipe' : 'inherit',
      shell: true,
      cwd: opts.cwd || FRONTEND,
      env: { ...process.env, FORCE_COLOR: '1' },
    });
    return true;
  } catch (e) {
    if (opts.ignoreError) return false;
    if (!opts.silent) err(`Falló: ${cmd}`);
    throw e;
  }
}

function out(cmd, opts = {}) {
  try {
    return execSync(cmd, {
      shell: true, encoding: 'utf8', stdio: 'pipe',
      cwd: opts.cwd || FRONTEND,
    }).trim();
  } catch { return ''; }
}

function ask(question) {
  return new Promise(resolve => {
    const iface = rl.createInterface({ input: process.stdin, output: process.stdout });
    iface.question(question, answer => { iface.close(); resolve(answer); });
  });
}

// ── step 1: .env ───────────────────────────────────────────────────────────────
async function checkEnv() {
  const envPath     = path.join(FRONTEND, '.env');
  const examplePath = path.join(FRONTEND, '.env.example');

  if (!fs.existsSync(envPath)) {
    if (!fs.existsSync(examplePath)) {
      warn('.env.example no encontrado. Continúa sin él.');
      return;
    }
    warn('.env no encontrado → copiando desde .env.example...');
    fs.copyFileSync(examplePath, envPath);
    console.log('');
    console.log(`${C.yellow}${C.bold}  Edita frontend/.env con tus credenciales de base de datos:${C.reset}`);
    console.log(`${C.cyan}  DATABASE_URL, JWT_SECRET, JWT_REFRESH_SECRET${C.reset}`);
    console.log('');
    await ask('  Presiona Enter cuando hayas guardado el .env... ');
  }

  // Load into process.env
  const lines = fs.readFileSync(envPath, 'utf8').split('\n');
  for (const line of lines) {
    const m = line.match(/^\s*([^#=\s]+)\s*=\s*"?([^"]*)"?\s*$/);
    if (m) process.env[m[1]] = m[2];
  }
  ok('.env cargado');
}

// ── step 2: node deps ──────────────────────────────────────────────────────────
function checkNodeDeps() {
  if (!fs.existsSync(path.join(FRONTEND, 'node_modules'))) {
    step('Instalando dependencias Node...');
    run('npm install');
    ok('Dependencias Node instaladas');
  } else {
    ok('node_modules OK');
  }
}

// ── step 3: prisma ─────────────────────────────────────────────────────────────
function setupPrisma() {
  const prismaClient = path.join(FRONTEND, 'node_modules', '.prisma', 'client');
  if (!fs.existsSync(prismaClient)) {
    step('Generando cliente Prisma...');
    run('npx prisma generate', { silent: true });
  }
  step('Sincronizando tablas (prisma db push)...');
  run('npx prisma db push --accept-data-loss', { silent: false });
  ok('Base de datos sincronizada');
}

// ── step 4: seed ───────────────────────────────────────────────────────────────
function runSeed() {
  step('Ejecutando seed (upsert — seguro si ya existe)...');
  run('npx tsx prisma/seed.ts', { silent: true, ignoreError: true });
  ok('Seed OK');
}

// ── step 5: find system python ─────────────────────────────────────────────────
function findPython() {
  const candidates = IS_WIN
    ? ['python', 'python3', 'py -3.12', 'py -3.11', 'py -3.10', 'py -3']
    : ['python3.12', 'python3.11', 'python3.10', 'python3', 'python'];

  for (const cmd of candidates) {
    const ver = out(`${cmd} --version`);
    if (/Python 3\.(9|1\d)/.test(ver)) return { cmd, ver };
  }
  return null;
}

// ── step 6: python venv ────────────────────────────────────────────────────────
function setupPython() {
  // Validate existing venv
  if (fs.existsSync(VENV)) {
    const venvOk = fs.existsSync(VENV_PY) &&
      out(`"${VENV_PY}" --version`).startsWith('Python');
    if (!venvOk) {
      warn('venv incompatible o corrompido → recreando...');
      fs.rmSync(VENV, { recursive: true, force: true });
    }
  }

  // Create venv if missing
  if (!fs.existsSync(VENV)) {
    const py = findPython();
    if (!py) {
      err('Python 3.9+ no encontrado en el sistema.');
      err('Instala Python desde https://www.python.org/downloads/');
      if (IS_WIN) err("Marca 'Add Python to PATH' durante la instalación.");
      process.exit(1);
    }
    step(`Creando venv con ${py.ver}...`);
    run(`${py.cmd} -m venv "${VENV}"`);
    ok('Entorno virtual creado');
  }

  // Install deps if uvicorn is missing
  const hasUvicorn = out(`"${VENV_PY}" -c "import uvicorn; print('ok')"`) === 'ok';
  if (!hasUvicorn) {
    step('Instalando dependencias Python...');
    run(`"${VENV_PIP}" install --upgrade pip --quiet`);
    run(`"${VENV_PIP}" install -r "${path.join(AI_DIR, 'requirements.txt')}"`);
    ok('Dependencias Python instaladas');
  } else {
    ok('Dependencias Python OK');
  }
}

// ── step 7: model check ────────────────────────────────────────────────────────
function checkModel() {
  if (fs.existsSync(MODEL_FILE)) {
    const size = (fs.statSync(MODEL_FILE).size / 1024 / 1024).toFixed(1);
    ok(`Modelo IA cargado (${size} MB) → predicciones reales`);
  } else {
    console.log('');
    console.log(`${C.yellow}${C.bold}  ⚠  Modelo de IA no entrenado${C.reset}`);
    console.log(`${C.yellow}     Las predicciones usarán el mock (resultados aleatorios).${C.reset}`);
    console.log(`${C.cyan}     Para entrenar el modelo real (30-60 min):${C.reset}`);
    console.log(`${C.cyan}       npm run ia:train${C.reset}`);
    console.log('');
  }
}

// ── step 8: start servers ──────────────────────────────────────────────────────
function startServers() {
  console.log(`${C.green}${C.bold}🚀 Iniciando servidores...${C.reset}`);
  info(`Nuxt   → http://localhost:3000`);
  info(`Python → http://localhost:8000`);
  console.log('');

  const nuxtArgs = IS_WIN ? ['nuxt', 'dev'] : ['nuxt', 'dev'];
  const nuxt = spawn('npx', nuxtArgs, {
    cwd: FRONTEND,
    stdio: 'inherit',
    shell: true,
    env: { ...process.env, FORCE_COLOR: '1' },
  });

  const pyArgs = ['-m', 'uvicorn', 'app.main:app', '--reload', '--port', '8000'];
  const python = spawn(VENV_PY, pyArgs, {
    cwd: AI_DIR,
    stdio: 'inherit',
    shell: false,
    env: { ...process.env, PYTHONUNBUFFERED: '1' },
  });

  const cleanup = () => {
    nuxt.kill('SIGTERM');
    python.kill('SIGTERM');
  };

  process.on('SIGINT',  cleanup);
  process.on('SIGTERM', cleanup);

  nuxt.on('exit',   code => { python.kill('SIGTERM'); process.exit(code ?? 0); });
  python.on('exit', code => { nuxt.kill('SIGTERM');   process.exit(code ?? 0); });
}

// ── main ───────────────────────────────────────────────────────────────────────
async function main() {
  console.log('');
  console.log(`${C.cyan}${C.bold}╔══════════════════════════════════════╗${C.reset}`);
  console.log(`${C.cyan}${C.bold}║       PeleAnálise — Dev Server       ║${C.reset}`);
  console.log(`${C.cyan}${C.bold}╚══════════════════════════════════════╝${C.reset}`);
  console.log('');

  try {
    await checkEnv();
    console.log('');
    checkNodeDeps();
    console.log('');
    setupPrisma();
    console.log('');
    runSeed();
    console.log('');
    setupPython();
    console.log('');
    checkModel();
    startServers();
  } catch (e) {
    err('Error inesperado:');
    console.error(e.message || e);
    process.exit(1);
  }
}

main();
