#!/bin/bash

CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RESET="\033[0m"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════╗${RESET}"
echo -e "${CYAN}║       PeleAnálise — Dev Server       ║${RESET}"
echo -e "${CYAN}╚══════════════════════════════════════╝${RESET}"
echo ""

# ── 1. .env ────────────────────────────────────────────────────────────────────
if [ ! -f .env ]; then
  echo -e "${YELLOW}⚙  .env no encontrado → creando desde .env.example...${RESET}"
  cp .env.example .env
  echo -e "${GREEN}✓  .env creado. Edítalo con tus credenciales antes de continuar.${RESET}"
  echo ""
  read -p "   Presiona Enter cuando hayas configurado el .env (Ctrl+C para salir): "
fi

set -a
source .env
set +a
echo -e "${GREEN}✓  .env cargado${RESET}"

# ── 2. Base de datos (via Node — compatible Mac y Windows) ─────────────────────
echo ""
DB_NAME=$(echo "$DATABASE_URL" | sed -E 's|.*/([^?]+).*|\1|')
echo -e "${YELLOW}🗄  Creando base de datos '${DB_NAME}' si no existe...${RESET}"
node -e "
const url = process.env.DATABASE_URL.replace(/\/[^/]+(\?.*)?$/, '/');
import('mysql2/promise').then(m => m.createConnection(url + 'information_schema')).then(async conn => {
  await conn.execute('CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci');
  await conn.end();
}).catch(() => process.exit(0));
" 2>/dev/null || true
echo -e "${GREEN}✓  Base de datos OK${RESET}"

# ── 3. Dependencias Node ───────────────────────────────────────────────────────
echo ""
if [ ! -d node_modules ]; then
  echo -e "${YELLOW}📦 Instalando dependencias Node...${RESET}"
  npm install
  echo -e "${GREEN}✓  Dependencias Node instaladas${RESET}"
else
  echo -e "${GREEN}✓  node_modules OK${RESET}"
fi

# ── 4. Prisma: generar cliente y sincronizar tablas ────────────────────────────
echo ""
if [ ! -d node_modules/.prisma/client ]; then
  echo -e "${YELLOW}🔧 Generando cliente Prisma...${RESET}"
  npx prisma generate
fi

echo -e "${YELLOW}🗄  Sincronizando tablas con Prisma (db push)...${RESET}"
npx prisma db push --accept-data-loss 2>&1 | grep -v "^$" | tail -5
echo -e "${GREEN}✓  Tablas sincronizadas${RESET}"

# ── 5. Seed: solo si users está vacía ─────────────────────────────────────────
echo ""
USER_COUNT=$(node -e "
import('mysql2/promise').then(m => m.createConnection(process.env.DATABASE_URL)).then(async conn => {
  const [rows] = await conn.execute('SELECT COUNT(*) as c FROM users');
  console.log(rows[0].c);
  await conn.end();
}).catch(() => console.log('0'));
" 2>/dev/null || echo "0")

if [ "$USER_COUNT" = "0" ]; then
  echo -e "${YELLOW}🌱 Ejecutando seed (usuarios iniciales)...${RESET}"
  npx tsx prisma/seed.ts
  echo -e "${GREEN}✓  Seed completado${RESET}"
else
  echo -e "${GREEN}✓  Seed omitido (ya hay datos)${RESET}"
fi

# ── 6. Python: entorno virtual ────────────────────────────────────────────────
echo ""
VENV_DIR="../python-ai/venv"

# Buscar Python disponible — incluye el launcher 'py' de Windows
PYTHON_BIN=""
for candidate in python3.12 python3.11 python3 "py -3.11" "py -3.12" "py -3" py python; do
  # Separar comando de argumentos
  CMD=$(echo "$candidate" | cut -d' ' -f1)
  ARGS=$(echo "$candidate" | cut -d' ' -f2- -s)
  if command -v "$CMD" &>/dev/null; then
    # Verificar que devuelva una versión real (no el alias de la tienda de Windows)
    VER=$($CMD $ARGS --version 2>&1) || VER=""
    if echo "$VER" | grep -qE '^Python 3\.(9|1[0-9])'; then
      PYTHON_BIN="$CMD $ARGS"
      break
    fi
  fi
done

if [ -z "$PYTHON_BIN" ]; then
  echo -e "${YELLOW}⚠  Python no encontrado.${RESET}"
  echo -e "${YELLOW}   Instala Python 3.11 desde https://www.python.org/downloads/${RESET}"
  echo -e "${YELLOW}   Asegúrate de marcar 'Add Python to PATH' durante la instalación.${RESET}"
  exit 1
fi

PYTHON_VER=$($PYTHON_BIN --version 2>&1)
echo -e "${GREEN}✓  Usando $PYTHON_VER${RESET}"

# Si el venv existe pero tiene rutas rotas (ej: fue creado en otra máquina), borrarlo
if [ -d "$VENV_DIR" ]; then
  VENV_OK=false
  if [ -f "$VENV_DIR/Scripts/python.exe" ] && "$VENV_DIR/Scripts/python.exe" --version &>/dev/null 2>&1; then
    VENV_OK=true
  elif [ -f "$VENV_DIR/bin/python" ] && "$VENV_DIR/bin/python" --version &>/dev/null 2>&1; then
    VENV_OK=true
  fi
  if [ "$VENV_OK" = "false" ]; then
    echo -e "${YELLOW}🐍 venv incompatible (creado en otra máquina) → recreando...${RESET}"
    rm -rf "$VENV_DIR"
  fi
fi

# Crear venv si no existe
if [ ! -d "$VENV_DIR" ]; then
  echo -e "${YELLOW}🐍 Creando entorno virtual Python...${RESET}"
  $PYTHON_BIN -m venv "$VENV_DIR"
  echo -e "${GREEN}✓  Entorno virtual creado${RESET}"
fi

# Detectar ruta del venv según OS (Windows usa Scripts/, Unix usa bin/)
if [ -f "$VENV_DIR/Scripts/python.exe" ] || [ -f "$VENV_DIR/Scripts/python" ]; then
  VENV_PYTHON="$VENV_DIR/Scripts/python"
  VENV_PIP="$VENV_DIR/Scripts/pip"
else
  VENV_PYTHON="$VENV_DIR/bin/python"
  VENV_PIP="$VENV_DIR/bin/pip"
fi

if ! "$VENV_PYTHON" -c "import uvicorn" 2>/dev/null; then
  echo -e "${YELLOW}🐍 Instalando dependencias Python...${RESET}"
  "$VENV_PIP" install --upgrade pip --quiet
  "$VENV_PIP" install -r ../python-ai/requirements.txt
  echo -e "${GREEN}✓  Dependencias Python instaladas${RESET}"
else
  echo -e "${GREEN}✓  Dependencias Python OK${RESET}"
fi

# ── 7. Arrancar servidores ─────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}🚀 Iniciando servidores...${RESET}"
echo -e "   ${CYAN}Nuxt   →${RESET} http://localhost:3000"
echo -e "   ${MAGENTA}Python →${RESET} http://localhost:8000"
echo ""

VENV_PYTHON_ABS=$(cd "$(dirname "$VENV_PYTHON")" && pwd)/$(basename "$VENV_PYTHON")

npx concurrently \
  -n "nuxt,python" \
  -c "cyan,magenta" \
  --kill-others-on-fail \
  "npx nuxt dev" \
  "cd ../python-ai && '$VENV_PYTHON_ABS' -m uvicorn app.main:app --reload --port 8000"
