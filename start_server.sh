#!/bin/bash

echo "=== QualiCam Server ==="
echo "Iniciando servidor Python com rotas específicas para o app..."

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Erro: Python3 não está instalado"
    exit 1
fi

# Verifica se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "Erro: pip3 não está instalado"
    exit 1
fi

# Instala dependências se necessário
echo "Verificando dependências..."
pip3 install -r requirements.txt

# Inicia o servidor
echo "Iniciando servidor na porta 5000..."
echo "Rotas disponíveis:"
echo "  - Cliente existente: /chapas, /retalhos, /health, etc."
echo "  - App QualiCam: /app/chapas, /app/retalhos, /app/health, etc."
echo ""
echo "Para acessar, use o IP desta máquina na rede local"
echo "Exemplo: http://192.168.15.7:5000"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo ""

python3 Server.py
