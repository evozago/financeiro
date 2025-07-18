# 🎯 Guia de Demonstração - Sistema de Gestão Financeira

Este guia mostra como testar todas as funcionalidades do sistema com dados de exemplo.

## 🚀 Início Rápido

### 1. Instalação
```bash
# Clone o repositório
git clone https://github.com/seu-usuario/financeiro.git
cd financeiro

# Execute o script de instalação
./install.sh

# Ou instale manualmente:
python -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
```

### 2. Executar o Sistema
```bash
source venv/bin/activate
python src/main.py
```

Acesse: `http://localhost:5001`

## 📋 Roteiro de Testes

### 1. Dashboard Inicial
- ✅ Visualize o dashboard com estatísticas zeradas
- ✅ Observe os cards de Contas Pendentes, Vencidas e Pagas
- ✅ Verifique a seção de Próximos Vencimentos

### 2. Gestão de Fornecedores
1. Clique em **"Fornecedores"**
2. Clique em **"Novo Fornecedor"**
3. Preencha os dados de exemplo:
   ```
   CNPJ: 79.525.242/0001-59
   Razão Social: TEX COTTON IND. DE CONFECCOES LTDA
   Nome Fantasia: Tex Cotton
   Endereço: Rua das Indústrias, 123
   Cidade: São Paulo
   UF: SP
   CEP: 01234-567
   Telefone: (11) 1234-5678
   Email: contato@texcotton.com.br
   ```
4. ✅ Salve e verifique se aparece na lista

### 3. Tipos de Despesa
1. Clique em **"Tipos de Despesa"**
2. ✅ Verifique os tipos pré-cadastrados:
   - Aluguel
   - Energia Elétrica
   - Folha de Pagamento
   - Fornecedores
   - Impostos
   - Manutenção
   - Material de Escritório
3. Teste editar um tipo existente
4. Teste criar um novo tipo: "Marketing"

### 4. Processamento de Nota Fiscal (XML)
1. Clique em **"Notas Fiscais"**
2. Clique em **"Importar XML"**
3. Use o arquivo XML de exemplo fornecido
4. ✅ Verifique se os dados foram extraídos:
   - Fornecedor: TEX COTTON
   - Valor: R$ 10.850,94
   - Desconto: R$ 221,45
   - 5 parcelas de R$ 2.168,69

### 5. Contas a Pagar
1. Clique em **"Contas a Pagar"**
2. ✅ Verifique as contas criadas automaticamente da nota fiscal
3. Teste criar uma conta manual:
   ```
   Fornecedor: [Selecione o cadastrado]
   Tipo: Aluguel
   Descrição: Aluguel Janeiro 2025
   Valor: R$ 3.500,00
   Vencimento: [Data futura]
   ```
4. ✅ Teste marcar uma conta como paga

### 6. Comprovantes de Pagamento (OCR)
1. Clique em **"Comprovantes"**
2. Clique em **"Enviar Comprovante"**
3. Faça upload de uma imagem de comprovante
4. ✅ Verifique o processamento OCR:
   - Valor reconhecido
   - Data reconhecida
   - Fornecedor identificado
5. ✅ Teste associar à uma conta a pagar

### 7. Conciliação Bancária
1. Clique em **"Conciliação"**
2. Clique em **"Importar OFX"**
3. Faça upload de um arquivo OFX do seu banco
4. ✅ Verifique a conciliação automática
5. ✅ Teste conciliação manual para itens não associados

## 🧪 Dados de Teste

### Fornecedor de Exemplo
```json
{
  "cnpj": "79.525.242/0001-59",
  "razao_social": "TEX COTTON IND. DE CONFECCOES LTDA",
  "nome_fantasia": "Tex Cotton",
  "endereco": "Rua das Indústrias, 123",
  "cidade": "São Paulo",
  "uf": "SP",
  "cep": "01234-567"
}
```

### Conta a Pagar Manual
```json
{
  "descricao": "Aluguel Janeiro 2025",
  "valor": 3500.00,
  "vencimento": "2025-01-31",
  "tipo": "Aluguel"
}
```

## 🔍 Funcionalidades para Testar

### ✅ Processamento de XML
- [ ] Upload de arquivo XML
- [ ] Extração de dados do fornecedor
- [ ] Cálculo de valores e impostos
- [ ] Criação automática de parcelas
- [ ] Visualização de itens da nota

### ✅ OCR de Comprovantes
- [ ] Upload de imagem (PNG/JPG)
- [ ] Upload de PDF
- [ ] Reconhecimento de valor
- [ ] Reconhecimento de data
- [ ] Identificação de banco/fornecedor
- [ ] Associação automática
- [ ] Confirmação manual

### ✅ Conciliação Bancária
- [ ] Import de arquivo OFX
- [ ] Conciliação automática por valor/data
- [ ] Conciliação manual
- [ ] Reversão de conciliação
- [ ] Dashboard de estatísticas

### ✅ Interface Web
- [ ] Responsividade (mobile/desktop)
- [ ] Navegação entre seções
- [ ] Modais funcionais
- [ ] Validação de formulários
- [ ] Feedback visual (loading, success, error)

## 🐛 Testes de Erro

### Teste Arquivos Inválidos
1. Tente fazer upload de arquivo não suportado
2. ✅ Verifique mensagem de erro apropriada

### Teste Dados Inválidos
1. Tente criar fornecedor com CNPJ inválido
2. Tente criar conta com valor negativo
3. ✅ Verifique validações

### Teste Limites
1. Teste upload de arquivo muito grande
2. Teste texto muito longo em campos
3. ✅ Verifique comportamento do sistema

## 📊 Verificações de Qualidade

### Performance
- [ ] Tempo de upload < 5 segundos
- [ ] Processamento OCR < 10 segundos
- [ ] Carregamento de páginas < 2 segundos

### Usabilidade
- [ ] Interface intuitiva
- [ ] Mensagens claras
- [ ] Navegação fluida
- [ ] Responsividade mobile

### Funcionalidade
- [ ] Todas as APIs funcionando
- [ ] Dados persistindo corretamente
- [ ] Cálculos precisos
- [ ] Associações corretas

## 🎉 Cenário Completo de Teste

1. **Setup**: Instale e execute o sistema
2. **Cadastro**: Crie fornecedores e tipos de despesa
3. **Import**: Importe uma nota fiscal XML
4. **Manual**: Adicione contas manuais
5. **OCR**: Processe comprovantes de pagamento
6. **Conciliação**: Importe e concilie extrato bancário
7. **Dashboard**: Verifique estatísticas atualizadas
8. **Relatórios**: Teste filtros e buscas

## 📞 Suporte

Se encontrar problemas durante os testes:

1. Verifique os logs no terminal
2. Consulte o README.md
3. Verifique se todas as dependências estão instaladas
4. Teste em navegador diferente
5. Abra uma issue no GitHub

---

**Happy Testing! 🚀**

