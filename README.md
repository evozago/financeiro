# Sistema de Gestão Financeira

Um sistema completo de gestão financeira desenvolvido em Flask com funcionalidades avançadas de processamento de documentos fiscais, OCR e conciliação bancária.

## 🚀 Funcionalidades

### 📋 Gestão de Contas a Pagar
- Lançamento manual de contas a pagar
- Suporte a parcelamentos com vencimentos personalizados
- Controle de status (Pendente, Pago, Vencido, Cancelado)
- Dashboard com resumo financeiro

### 📄 Processamento de Notas Fiscais (XML)
- Importação automática de arquivos XML de notas fiscais
- Extração de dados do fornecedor (CNPJ, razão social, etc.)
- Processamento de valores (total, descontos, impostos)
- Identificação automática de parcelas e vencimentos
- Armazenamento completo dos produtos e detalhes

### 🏢 Gestão de Fornecedores
- Cadastro completo de fornecedores
- Dados fiscais (CNPJ, Inscrição Estadual)
- Informações de contato e endereço
- Histórico de transações

### 🏷️ Tipos de Despesa
- Categorização de despesas
- Tipos pré-configurados (Aluguel, Energia, Folha de Pagamento, etc.)
- CRUD completo (Criar, Editar, Excluir)
- Status ativo/inativo

### 📸 Reconhecimento de Comprovantes (OCR)
- Upload de comprovantes de pagamento (PNG, JPG, PDF)
- Reconhecimento automático via OCR (Tesseract)
- Extração de dados: valor, data, fornecedor, banco
- Associação automática com contas a pagar
- Confirmação manual de baixas

### 🏦 Conciliação Bancária
- Importação de extratos bancários (formato OFX)
- Conciliação automática baseada em valor e data (±10 dias)
- Conciliação manual para casos especiais
- Dashboard de conciliação com estatísticas
- Controle de transações conciliadas/não conciliadas

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask** - Framework web Python
- **SQLAlchemy** - ORM para banco de dados
- **SQLite** - Banco de dados
- **Tesseract OCR** - Reconhecimento de texto em imagens
- **OFXParse** - Processamento de arquivos OFX
- **Pillow** - Processamento de imagens

### Frontend
- **HTML5/CSS3** - Interface moderna e responsiva
- **JavaScript** - Interatividade e AJAX
- **Design Responsivo** - Compatível com desktop e mobile

### Processamento
- **XML Parser** - Processamento de notas fiscais
- **OCR Engine** - Reconhecimento de comprovantes
- **OFX Parser** - Processamento de extratos bancários

## 📦 Instalação

### Pré-requisitos
- Python 3.8+
- Tesseract OCR
- Git

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/financeiro.git
cd financeiro
```

### 2. Instale o Tesseract OCR
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-por

# macOS
brew install tesseract tesseract-lang

# Windows
# Baixe e instale do: https://github.com/UB-Mannheim/tesseract/wiki
```

### 3. Configure o ambiente Python
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 4. Configure o banco de dados
```bash
# O banco será criado automaticamente na primeira execução
python src/main.py
```

### 5. Execute o sistema
```bash
python src/main.py
```

O sistema estará disponível em: `http://localhost:5001`

## 📁 Estrutura do Projeto

```
sistema_financeiro/
├── src/
│   ├── models/
│   │   ├── user.py              # Configuração do banco
│   │   └── financeiro.py        # Modelos de dados
│   ├── routes/
│   │   ├── fornecedores.py      # API de fornecedores
│   │   ├── tipos_despesa.py     # API de tipos de despesa
│   │   ├── notas_fiscais.py     # API de notas fiscais
│   │   ├── contas_pagar.py      # API de contas a pagar
│   │   ├── comprovantes.py      # API de comprovantes (OCR)
│   │   └── conciliacao.py       # API de conciliação bancária
│   ├── static/
│   │   ├── index.html           # Interface principal
│   │   ├── styles.css           # Estilos CSS
│   │   └── script.js            # JavaScript
│   └── main.py                  # Aplicação principal
├── uploads/                     # Arquivos enviados
│   ├── comprovantes/           # Comprovantes de pagamento
│   └── extratos/               # Extratos bancários
├── requirements.txt             # Dependências Python
└── README.md                   # Documentação
```

## 🔧 Configuração

### Variáveis de Ambiente
O sistema usa configurações padrão, mas você pode personalizar:

```python
# src/main.py
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///caminho/para/banco.db'
```

### Configuração do OCR
O sistema está configurado para português brasileiro. Para outros idiomas:

```python
# src/routes/comprovantes.py
custom_config = r'--oem 3 --psm 6 -l por'  # Altere 'por' para seu idioma
```

## 📖 Como Usar

### 1. Configuração Inicial
1. Acesse o sistema em `http://localhost:5001`
2. Os tipos de despesa padrão são criados automaticamente
3. Cadastre seus fornecedores na aba "Fornecedores"

### 2. Importar Notas Fiscais
1. Vá para "Notas Fiscais"
2. Clique em "Importar XML"
3. Selecione o arquivo XML da nota fiscal
4. O sistema extrairá automaticamente todos os dados

### 3. Gerenciar Contas a Pagar
1. Acesse "Contas a Pagar"
2. As contas das notas fiscais são criadas automaticamente
3. Você pode adicionar contas manuais clicando em "Nova Conta"

### 4. Processar Comprovantes
1. Vá para "Comprovantes"
2. Clique em "Enviar Comprovante"
3. Faça upload da imagem/PDF do comprovante
4. O sistema reconhecerá automaticamente os dados
5. Confirme a associação com a conta a pagar

### 5. Conciliação Bancária
1. Acesse "Conciliação"
2. Clique em "Importar OFX"
3. Faça upload do arquivo OFX do seu banco
4. O sistema fará a conciliação automática
5. Revise e ajuste manualmente se necessário

## 🔍 Funcionalidades Detalhadas

### Processamento de XML (Notas Fiscais)
- Suporte completo ao padrão NFe
- Extração de dados do emitente e destinatário
- Processamento de itens e impostos
- Identificação de condições de pagamento
- Criação automática de contas a pagar parceladas

### OCR de Comprovantes
- Suporte a PNG, JPG e PDF
- Reconhecimento de valores em Real (R$)
- Extração de datas em vários formatos
- Identificação de bancos e instituições
- Tolerância de 5% para associação automática

### Conciliação Bancária
- Suporte ao formato OFX padrão
- Janela de conciliação de ±10 dias
- Conciliação por valor e data
- Reversão de conciliações
- Relatórios de conciliação

## 🚨 Solução de Problemas

### Erro de OCR
```bash
# Verifique se o Tesseract está instalado
tesseract --version

# Instale o idioma português se necessário
sudo apt install tesseract-ocr-por
```

### Erro de Banco de Dados
```bash
# Remova o banco e deixe recriar
rm src/database/app.db
python src/main.py
```

### Erro de Dependências
```bash
# Reinstale as dependências
pip install --upgrade -r requirements.txt
```

## 📊 API Endpoints

### Fornecedores
- `GET /api/fornecedores` - Listar fornecedores
- `POST /api/fornecedores` - Criar fornecedor
- `PUT /api/fornecedores/<id>` - Atualizar fornecedor
- `DELETE /api/fornecedores/<id>` - Excluir fornecedor

### Contas a Pagar
- `GET /api/contas-pagar` - Listar contas
- `POST /api/contas-pagar` - Criar conta
- `PUT /api/contas-pagar/<id>` - Atualizar conta
- `POST /api/contas-pagar/<id>/pagar` - Marcar como paga

### Comprovantes
- `POST /api/comprovantes/upload` - Upload e OCR
- `POST /api/comprovantes/<id>/associar` - Associar à conta
- `GET /api/comprovantes/<id>/sugestoes` - Sugerir contas

### Conciliação
- `POST /api/extratos/upload` - Upload de OFX
- `POST /api/conciliacoes/manual` - Conciliação manual
- `GET /api/dashboard/conciliacao` - Dashboard

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para suporte e dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação completa
- Verifique os logs do sistema em caso de erro

## 🔄 Atualizações

### Versão 1.0.0
- ✅ Sistema completo de gestão financeira
- ✅ Processamento de XMLs de notas fiscais
- ✅ OCR para comprovantes de pagamento
- ✅ Conciliação bancária com OFX
- ✅ Interface web responsiva
- ✅ APIs RESTful completas

---

**Desenvolvido com ❤️ para gestão financeira eficiente**

