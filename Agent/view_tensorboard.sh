#!/bin/bash
# Script para visualizar los logs de TensorBoard

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Obtener el directorio de logs (por defecto results/car_racing_ppo)
TENSORBOARD_DIR="${1:-results/car_racing_ppo}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Iniciando TensorBoard${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "Directorio de logs: ${YELLOW}$TENSORBOARD_DIR${NC}"
echo ""
echo -e "${GREEN}TensorBoard estará disponible en:${NC} http://localhost:6006"
echo -e "${YELLOW}Presiona Ctrl+C para detener TensorBoard${NC}"
echo ""

# Directorio del script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Verificar que uv está instalado
if ! command -v uv &> /dev/null; then
    echo -e "${RED}✗ uv no encontrado${NC}"
    echo -e "${YELLOW}Instala uv con: curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
    exit 1
fi

# Verificar que el venv existe, si no, sincronizar dependencias
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠ Entorno virtual no encontrado${NC}"
    echo -e "${GREEN}Creando entorno virtual y sincronizando dependencias...${NC}"
    uv sync --python 3.10
    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Error sincronizando dependencias${NC}"
        exit 1
    fi
fi

# Ejecutar TensorBoard (tensorboard ya está en las dependencias)
uv run tensorboard --logdir "$TENSORBOARD_DIR" --port 6006

