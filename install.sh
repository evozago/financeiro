#!/bin/bash

echo "🚀 Instalando Sistema de Gestão Financeira..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8+"
    exit 1
fi

# Verificar se pip está instalado
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 não encontrado. Por favor, instale pip3"
    exit 1
fi

# Instalar Tesseract OCR
echo "📦 Instalando Tesseract OCR..."
if command -v apt &> /dev/null; then
    sudo apt update
    sudo apt install -y tesseract-ocr tesseract-ocr-por
elif command -v brew &> /dev/null; then
    brew install tesseract tesseract-lang
else
    echo "⚠️  Por favor, instale o Tesseract OCR manualmente"
    echo "   Ubuntu/Debian: sudo apt install tesseract-ocr tesseract-ocr-por"
    echo "   macOS: brew install tesseract tesseract-lang"
    echo "   Windows: https://github.com/UB-Mannheim/tesseract/wiki"
fi

# Criar ambiente virtual
echo "🐍 Criando ambiente virtual..."
python3 -m venv venv

# Ativar ambiente virtual
echo "🔧 Ativando ambiente virtual..."
source venv/bin/activate

# Instalar dependências
echo "📚 Instalando dependências Python..."
pip install -r requirements.txt

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p src/database
mkdir -p uploads/comprovantes
mkdir -p uploads/extratos

echo "✅ Instalação concluída!"
echo ""
echo "🎯 Para executar o sistema:"
echo "   1. source venv/bin/activate"
echo "   2. python src/main.py"
echo "   3. Acesse: http://localhost:5001"
echo ""
echo "📖 Consulte o README.md para mais informações"

