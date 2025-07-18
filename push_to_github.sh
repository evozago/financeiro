#!/bin/bash

echo "🚀 Script de Push para GitHub - Sistema Financeiro"
echo "=================================================="
echo ""

# Verificar se estamos no diretório correto
if [ ! -f "src/main.py" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto"
    echo "   Certifique-se de estar na pasta 'sistema_financeiro'"
    exit 1
fi

# Verificar se git está inicializado
if [ ! -d ".git" ]; then
    echo "📦 Inicializando repositório Git..."
    git init
    git branch -M main
fi

# Configurar remote
echo "🔗 Configurando repositório remoto..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/evozago/financeiro.git

# Verificar status
echo "📋 Status do repositório:"
git status

echo ""
echo "🔑 IMPORTANTE: Você precisará das suas credenciais do GitHub"
echo "   - Username: evozago"
echo "   - Password: Seu token de acesso pessoal (não a senha da conta)"
echo ""
echo "💡 Para criar um token de acesso:"
echo "   1. Vá para: https://github.com/settings/tokens"
echo "   2. Clique em 'Generate new token (classic)'"
echo "   3. Selecione 'repo' permissions"
echo "   4. Use o token como senha"
echo ""

read -p "Pressione ENTER para continuar com o push..."

# Fazer push
echo "📤 Fazendo push para o GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! Sistema enviado para o GitHub com sucesso!"
    echo "🌐 Repositório: https://github.com/evozago/financeiro"
    echo ""
    echo "📋 Próximos passos:"
    echo "   1. Acesse: https://github.com/evozago/financeiro"
    echo "   2. Verifique se todos os arquivos foram enviados"
    echo "   3. Leia o README.md para instruções de instalação"
    echo "   4. Use o DEMO.md para testar o sistema"
else
    echo ""
    echo "❌ Erro no push. Verifique suas credenciais e tente novamente."
    echo "💡 Dicas:"
    echo "   - Use seu username: evozago"
    echo "   - Use um token de acesso como senha (não a senha da conta)"
    echo "   - Certifique-se de ter permissões no repositório"
fi

