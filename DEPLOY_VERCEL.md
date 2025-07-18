# 🚀 Deploy no Vercel - Sistema de Gestão Financeira

Este guia mostra como fazer o deploy do sistema no Vercel para acesso online.

## 📋 Pré-requisitos

1. **Conta no Vercel:** https://vercel.com
2. **Conta no GitHub:** (já configurada)
3. **Repositório:** https://github.com/evozago/financeiro

## 🚀 Passos para Deploy

### 1. Acessar o Vercel
1. Vá para: https://vercel.com
2. Clique em **"Sign up"** ou **"Login"**
3. Escolha **"Continue with GitHub"**
4. Autorize o Vercel a acessar seus repositórios

### 2. Importar Projeto
1. No dashboard do Vercel, clique em **"New Project"**
2. Encontre o repositório **"financeiro"**
3. Clique em **"Import"**

### 3. Configurar Deploy
1. **Project Name:** `sistema-financeiro` (ou o nome que preferir)
2. **Framework Preset:** Deixe como **"Other"**
3. **Root Directory:** Deixe vazio (usar raiz do projeto)
4. **Build Command:** Deixe vazio
5. **Output Directory:** Deixe vazio
6. **Install Command:** `pip install -r requirements.txt`

### 4. Variáveis de Ambiente (Opcional)
Se necessário, adicione:
- `FLASK_ENV=production`
- `PYTHONPATH=/var/task`

### 5. Deploy
1. Clique em **"Deploy"**
2. Aguarde o processo (2-5 minutos)
3. ✅ **Pronto!** Seu sistema estará online

## 🌐 Resultado

Após o deploy, você terá:
- **URL pública:** `https://sistema-financeiro-xxx.vercel.app`
- **HTTPS automático**
- **Deploy automático** a cada push no GitHub
- **Acesso global** de qualquer lugar

## 🔧 Configurações do Vercel

O projeto já está configurado com:
- ✅ **vercel.json** - Configuração de deploy
- ✅ **api/index.py** - Ponto de entrada serverless
- ✅ **requirements.txt** - Dependências Python
- ✅ **Estrutura otimizada** para Vercel

## 📱 Funcionalidades Online

Todas as funcionalidades funcionarão online:
- ✅ **Dashboard financeiro**
- ✅ **Gestão de fornecedores**
- ✅ **Processamento de XMLs**
- ✅ **OCR de comprovantes**
- ✅ **Conciliação bancária**
- ✅ **Interface responsiva**

## 🚨 Limitações do Vercel (Plano Gratuito)

- **Tempo de execução:** 10 segundos por função
- **Tamanho de arquivo:** 50MB por deploy
- **Bandwidth:** 100GB/mês
- **Execuções:** 100GB-hours/mês

Para uso empresarial intenso, considere o plano Pro.

## 🔄 Atualizações Automáticas

Sempre que você fizer push no GitHub:
1. Vercel detecta automaticamente
2. Faz novo deploy
3. Atualiza a URL pública
4. Mantém versões anteriores

## 🆘 Solução de Problemas

### Deploy Falhou?
1. Verifique os logs no dashboard do Vercel
2. Confirme que `requirements.txt` está correto
3. Verifique se não há erros de sintaxe

### Função não responde?
1. Verifique timeout (máximo 10s no plano gratuito)
2. Otimize operações pesadas
3. Use cache quando possível

### Banco de dados?
- SQLite funciona no Vercel
- Para produção, considere PostgreSQL externo
- Dados são temporários (resetam a cada deploy)

## 🎯 Próximos Passos

Após o deploy:
1. **Teste todas as funcionalidades**
2. **Configure domínio personalizado** (opcional)
3. **Configure analytics** (opcional)
4. **Monitore performance**

## 📞 Suporte

- **Documentação Vercel:** https://vercel.com/docs
- **Suporte Vercel:** https://vercel.com/support
- **GitHub Issues:** Para problemas do código

---

**🚀 Seu sistema estará online em poucos minutos!**

