from src.models.user import db
from datetime import datetime
from decimal import Decimal

class Fornecedor(db.Model):
    __tablename__ = 'fornecedores'
    
    id = db.Column(db.Integer, primary_key=True)
    cnpj = db.Column(db.String(18), unique=True, nullable=False)
    inscricao_estadual = db.Column(db.String(20))
    razao_social = db.Column(db.String(200), nullable=False)
    nome_fantasia = db.Column(db.String(200))
    endereco = db.Column(db.String(300))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(9))
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    notas_fiscais = db.relationship('NotaFiscal', backref='fornecedor', lazy=True)
    contas_pagar = db.relationship('ContaPagar', backref='fornecedor', lazy=True)
    
    def __repr__(self):
        return f'<Fornecedor {self.razao_social}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'cnpj': self.cnpj,
            'inscricao_estadual': self.inscricao_estadual,
            'razao_social': self.razao_social,
            'nome_fantasia': self.nome_fantasia,
            'endereco': self.endereco,
            'cidade': self.cidade,
            'uf': self.uf,
            'cep': self.cep,
            'telefone': self.telefone,
            'email': self.email,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class TipoDespesa(db.Model):
    __tablename__ = 'tipos_despesa'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text)
    ativo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    contas_pagar = db.relationship('ContaPagar', backref='tipo_despesa', lazy=True)
    
    def __repr__(self):
        return f'<TipoDespesa {self.nome}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class NotaFiscal(db.Model):
    __tablename__ = 'notas_fiscais'
    
    id = db.Column(db.Integer, primary_key=True)
    chave_acesso = db.Column(db.String(44), unique=True, nullable=False)
    numero = db.Column(db.String(20), nullable=False)
    serie = db.Column(db.String(10), nullable=False)
    data_emissao = db.Column(db.Date, nullable=False)
    data_entrada = db.Column(db.Date)
    
    # Dados do fornecedor
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'), nullable=False)
    
    # Valores
    valor_produtos = db.Column(db.Numeric(15, 2), default=0)
    valor_desconto = db.Column(db.Numeric(15, 2), default=0)
    valor_frete = db.Column(db.Numeric(15, 2), default=0)
    valor_seguro = db.Column(db.Numeric(15, 2), default=0)
    valor_outras_despesas = db.Column(db.Numeric(15, 2), default=0)
    valor_total = db.Column(db.Numeric(15, 2), nullable=False)
    
    # Impostos
    valor_icms = db.Column(db.Numeric(15, 2), default=0)
    valor_ipi = db.Column(db.Numeric(15, 2), default=0)
    valor_pis = db.Column(db.Numeric(15, 2), default=0)
    valor_cofins = db.Column(db.Numeric(15, 2), default=0)
    
    # Dados de pagamento
    forma_pagamento = db.Column(db.String(50))
    condicao_pagamento = db.Column(db.String(100))
    
    # Controle
    arquivo_xml = db.Column(db.String(300))
    status = db.Column(db.String(20), default='IMPORTADA')  # IMPORTADA, PROCESSADA, ERRO
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    itens = db.relationship('ItemNotaFiscal', backref='nota_fiscal', lazy=True, cascade='all, delete-orphan')
    contas_pagar = db.relationship('ContaPagar', backref='nota_fiscal', lazy=True)
    
    def __repr__(self):
        return f'<NotaFiscal {self.numero}/{self.serie}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'chave_acesso': self.chave_acesso,
            'numero': self.numero,
            'serie': self.serie,
            'data_emissao': self.data_emissao.isoformat() if self.data_emissao else None,
            'data_entrada': self.data_entrada.isoformat() if self.data_entrada else None,
            'fornecedor_id': self.fornecedor_id,
            'fornecedor': self.fornecedor.to_dict() if self.fornecedor else None,
            'valor_produtos': float(self.valor_produtos) if self.valor_produtos else 0,
            'valor_desconto': float(self.valor_desconto) if self.valor_desconto else 0,
            'valor_frete': float(self.valor_frete) if self.valor_frete else 0,
            'valor_seguro': float(self.valor_seguro) if self.valor_seguro else 0,
            'valor_outras_despesas': float(self.valor_outras_despesas) if self.valor_outras_despesas else 0,
            'valor_total': float(self.valor_total) if self.valor_total else 0,
            'valor_icms': float(self.valor_icms) if self.valor_icms else 0,
            'valor_ipi': float(self.valor_ipi) if self.valor_ipi else 0,
            'valor_pis': float(self.valor_pis) if self.valor_pis else 0,
            'valor_cofins': float(self.valor_cofins) if self.valor_cofins else 0,
            'forma_pagamento': self.forma_pagamento,
            'condicao_pagamento': self.condicao_pagamento,
            'status': self.status,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'itens': [item.to_dict() for item in self.itens] if self.itens else []
        }

class ItemNotaFiscal(db.Model):
    __tablename__ = 'itens_nota_fiscal'
    
    id = db.Column(db.Integer, primary_key=True)
    nota_fiscal_id = db.Column(db.Integer, db.ForeignKey('notas_fiscais.id'), nullable=False)
    
    # Dados do produto
    codigo_produto = db.Column(db.String(50))
    descricao = db.Column(db.String(300), nullable=False)
    ncm = db.Column(db.String(10))
    cfop = db.Column(db.String(10))
    unidade = db.Column(db.String(10))
    quantidade = db.Column(db.Numeric(15, 4), nullable=False)
    valor_unitario = db.Column(db.Numeric(15, 4), nullable=False)
    valor_total = db.Column(db.Numeric(15, 2), nullable=False)
    valor_desconto = db.Column(db.Numeric(15, 2), default=0)
    
    # Impostos do item
    valor_icms = db.Column(db.Numeric(15, 2), default=0)
    valor_ipi = db.Column(db.Numeric(15, 2), default=0)
    valor_pis = db.Column(db.Numeric(15, 2), default=0)
    valor_cofins = db.Column(db.Numeric(15, 2), default=0)
    
    def __repr__(self):
        return f'<ItemNotaFiscal {self.descricao}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nota_fiscal_id': self.nota_fiscal_id,
            'codigo_produto': self.codigo_produto,
            'descricao': self.descricao,
            'ncm': self.ncm,
            'cfop': self.cfop,
            'unidade': self.unidade,
            'quantidade': float(self.quantidade) if self.quantidade else 0,
            'valor_unitario': float(self.valor_unitario) if self.valor_unitario else 0,
            'valor_total': float(self.valor_total) if self.valor_total else 0,
            'valor_desconto': float(self.valor_desconto) if self.valor_desconto else 0,
            'valor_icms': float(self.valor_icms) if self.valor_icms else 0,
            'valor_ipi': float(self.valor_ipi) if self.valor_ipi else 0,
            'valor_pis': float(self.valor_pis) if self.valor_pis else 0,
            'valor_cofins': float(self.valor_cofins) if self.valor_cofins else 0
        }

class ContaPagar(db.Model):
    __tablename__ = 'contas_pagar'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relacionamentos
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedores.id'), nullable=False)
    tipo_despesa_id = db.Column(db.Integer, db.ForeignKey('tipos_despesa.id'), nullable=False)
    nota_fiscal_id = db.Column(db.Integer, db.ForeignKey('notas_fiscais.id'))
    
    # Dados da conta
    descricao = db.Column(db.String(300), nullable=False)
    numero_documento = db.Column(db.String(50))
    valor_original = db.Column(db.Numeric(15, 2), nullable=False)
    valor_pago = db.Column(db.Numeric(15, 2))
    data_vencimento = db.Column(db.Date, nullable=False)
    data_pagamento = db.Column(db.Date)
    
    # Parcelamento
    numero_parcela = db.Column(db.Integer, default=1)
    total_parcelas = db.Column(db.Integer, default=1)
    
    # Status e controle
    status = db.Column(db.String(20), default='PENDENTE')  # PENDENTE, PAGO, VENCIDO, CANCELADO
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ContaPagar {self.descricao}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'fornecedor_id': self.fornecedor_id,
            'fornecedor': self.fornecedor.to_dict() if self.fornecedor else None,
            'tipo_despesa_id': self.tipo_despesa_id,
            'tipo_despesa': self.tipo_despesa.to_dict() if self.tipo_despesa else None,
            'nota_fiscal_id': self.nota_fiscal_id,
            'nota_fiscal': self.nota_fiscal.to_dict() if self.nota_fiscal else None,
            'descricao': self.descricao,
            'numero_documento': self.numero_documento,
            'valor_original': float(self.valor_original) if self.valor_original else 0,
            'valor_pago': float(self.valor_pago) if self.valor_pago else None,
            'data_vencimento': self.data_vencimento.isoformat() if self.data_vencimento else None,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'numero_parcela': self.numero_parcela,
            'total_parcelas': self.total_parcelas,
            'status': self.status,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Comprovante(db.Model):
    __tablename__ = 'comprovantes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_arquivo = db.Column(db.String(255), nullable=False)
    caminho_arquivo = db.Column(db.String(500), nullable=False)
    data_upload = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Dados extraídos por OCR
    texto_ocr = db.Column(db.Text)
    valor_reconhecido = db.Column(db.Numeric(15, 2))
    data_reconhecida = db.Column(db.Date)
    fornecedor_reconhecido = db.Column(db.String(255))
    banco_reconhecido = db.Column(db.String(100))
    status_ocr = db.Column(db.String(20), default='PENDENTE')  # PENDENTE, PROCESSADO, ERRO, ASSOCIADO
    
    # Relacionamento com conta a pagar
    conta_pagar_id = db.Column(db.Integer, db.ForeignKey('contas_pagar.id'))
    conta_pagar = db.relationship('ContaPagar', backref='comprovantes')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_arquivo': self.nome_arquivo,
            'data_upload': self.data_upload.isoformat() if self.data_upload else None,
            'valor_reconhecido': float(self.valor_reconhecido) if self.valor_reconhecido else None,
            'data_reconhecida': self.data_reconhecida.isoformat() if self.data_reconhecida else None,
            'fornecedor_reconhecido': self.fornecedor_reconhecido,
            'banco_reconhecido': self.banco_reconhecido,
            'status_ocr': self.status_ocr,
            'conta_pagar_id': self.conta_pagar_id,
            'conta_pagar': self.conta_pagar.to_dict() if self.conta_pagar else None
        }

class ExtratoBancario(db.Model):
    __tablename__ = 'extratos_bancarios'
    
    id = db.Column(db.Integer, primary_key=True)
    data_transacao = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Numeric(15, 2), nullable=False)
    tipo_transacao = db.Column(db.String(50))  # DEBIT, CREDIT, etc.
    descricao = db.Column(db.String(500))
    id_transacao = db.Column(db.String(100))  # ID único da transação no banco
    
    # Dados da conta
    banco = db.Column(db.String(100))
    agencia = db.Column(db.String(20))
    conta = db.Column(db.String(50))
    
    # Controle
    nome_arquivo = db.Column(db.String(255))
    data_importacao = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='NAO_CONCILIADO')  # NAO_CONCILIADO, CONCILIADO
    
    def to_dict(self):
        return {
            'id': self.id,
            'data_transacao': self.data_transacao.isoformat() if self.data_transacao else None,
            'valor': float(self.valor) if self.valor else None,
            'tipo_transacao': self.tipo_transacao,
            'descricao': self.descricao,
            'id_transacao': self.id_transacao,
            'banco': self.banco,
            'agencia': self.agencia,
            'conta': self.conta,
            'nome_arquivo': self.nome_arquivo,
            'data_importacao': self.data_importacao.isoformat() if self.data_importacao else None,
            'status': self.status
        }

class ConciliacaoBancaria(db.Model):
    __tablename__ = 'conciliacoes_bancarias'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relacionamentos
    extrato_bancario_id = db.Column(db.Integer, db.ForeignKey('extratos_bancarios.id'), nullable=False)
    extrato_bancario = db.relationship('ExtratoBancario', backref='conciliacoes')
    
    conta_pagar_id = db.Column(db.Integer, db.ForeignKey('contas_pagar.id'), nullable=False)
    conta_pagar = db.relationship('ContaPagar', backref='conciliacoes')
    
    # Dados da conciliação
    tipo_conciliacao = db.Column(db.String(20), nullable=False)  # AUTOMATICA, MANUAL
    data_conciliacao = db.Column(db.DateTime, default=datetime.utcnow)
    observacoes = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'extrato_bancario_id': self.extrato_bancario_id,
            'extrato_bancario': self.extrato_bancario.to_dict() if self.extrato_bancario else None,
            'conta_pagar_id': self.conta_pagar_id,
            'conta_pagar': self.conta_pagar.to_dict() if self.conta_pagar else None,
            'tipo_conciliacao': self.tipo_conciliacao,
            'data_conciliacao': self.data_conciliacao.isoformat() if self.data_conciliacao else None,
            'observacoes': self.observacoes
        }

