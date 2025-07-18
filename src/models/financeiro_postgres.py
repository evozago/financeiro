from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Fornecedor(Base):
    __tablename__ = 'fornecedores'
    
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(18), unique=True, index=True, nullable=False)
    razao_social = Column(String(255), nullable=False)
    nome_fantasia = Column(String(255))
    endereco = Column(Text)
    cidade = Column(String(100))
    uf = Column(String(2))
    cep = Column(String(10))
    telefone = Column(String(20))
    email = Column(String(100))
    inscricao_estadual = Column(String(20))
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    notas_fiscais = relationship("NotaFiscal", back_populates="fornecedor")
    contas_pagar = relationship("ContaPagar", back_populates="fornecedor")

class TipoDespesa(Base):
    __tablename__ = 'tipos_despesa'
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    descricao = Column(Text)
    ativo = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    contas_pagar = relationship("ContaPagar", back_populates="tipo_despesa")

class NotaFiscal(Base):
    __tablename__ = 'notas_fiscais'
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), nullable=False)
    serie = Column(String(10))
    chave_acesso = Column(String(44), unique=True, index=True)
    data_emissao = Column(Date, nullable=False)
    data_entrada = Column(Date)
    valor_total = Column(Float, nullable=False)
    valor_desconto = Column(Float, default=0)
    valor_produtos = Column(Float, nullable=False)
    status = Column(String(20), default='PROCESSADA')
    forma_pagamento = Column(String(50))
    condicao_pagamento = Column(String(100))
    arquivo_xml = Column(Text)
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    fornecedor = relationship("Fornecedor", back_populates="notas_fiscais")
    itens = relationship("ItemNotaFiscal", back_populates="nota_fiscal", cascade="all, delete-orphan")
    duplicatas = relationship("DuplicataNF", back_populates="nota_fiscal", cascade="all, delete-orphan")

class ItemNotaFiscal(Base):
    __tablename__ = 'itens_nota_fiscal'
    
    id = Column(Integer, primary_key=True, index=True)
    nota_fiscal_id = Column(Integer, ForeignKey('notas_fiscais.id'), nullable=False)
    codigo_produto = Column(String(50))
    descricao = Column(Text, nullable=False)
    ncm = Column(String(10))
    cfop = Column(String(10))
    unidade = Column(String(10))
    quantidade = Column(Float, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    valor_total = Column(Float, nullable=False)
    valor_desconto = Column(Float, default=0)
    valor_icms = Column(Float, default=0)
    valor_ipi = Column(Float, default=0)
    valor_pis = Column(Float, default=0)
    valor_cofins = Column(Float, default=0)
    
    # Relacionamentos
    nota_fiscal = relationship("NotaFiscal", back_populates="itens")

class DuplicataNF(Base):
    __tablename__ = 'duplicatas_nf'
    
    id = Column(Integer, primary_key=True, index=True)
    nota_fiscal_id = Column(Integer, ForeignKey('notas_fiscais.id'), nullable=False)
    numero_duplicata = Column(String(20), nullable=False)
    data_vencimento = Column(Date, nullable=False)
    valor = Column(Float, nullable=False)
    
    # Relacionamentos
    nota_fiscal = relationship("NotaFiscal", back_populates="duplicatas")

class ContaPagar(Base):
    __tablename__ = 'contas_pagar'
    
    id = Column(Integer, primary_key=True, index=True)
    fornecedor_id = Column(Integer, ForeignKey('fornecedores.id'), nullable=False)
    tipo_despesa_id = Column(Integer, ForeignKey('tipos_despesa.id'), nullable=False)
    nota_fiscal_id = Column(Integer, ForeignKey('notas_fiscais.id'), nullable=True)
    descricao = Column(Text, nullable=False)
    valor_original = Column(Float, nullable=False)
    valor_pago = Column(Float)
    data_vencimento = Column(Date, nullable=False)
    data_pagamento = Column(Date)
    numero_documento = Column(String(50))
    observacoes = Column(Text)
    status = Column(String(20), default='PENDENTE')  # PENDENTE, PAGO, VENCIDO, CANCELADO
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    fornecedor = relationship("Fornecedor", back_populates="contas_pagar")
    tipo_despesa = relationship("TipoDespesa", back_populates="contas_pagar")
    nota_fiscal = relationship("NotaFiscal")

class ComprovanteOCR(Base):
    __tablename__ = 'comprovantes_ocr'
    
    id = Column(Integer, primary_key=True, index=True)
    nome_arquivo = Column(String(255), nullable=False)
    caminho_arquivo = Column(String(500), nullable=False)
    texto_extraido = Column(Text)
    valor_reconhecido = Column(Float)
    data_reconhecida = Column(Date)
    fornecedor_reconhecido = Column(String(255))
    status_ocr = Column(String(20), default='PROCESSANDO')  # PROCESSANDO, SUCESSO, ERRO
    conta_pagar_id = Column(Integer, ForeignKey('contas_pagar.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    conta_pagar = relationship("ContaPagar")

class ExtratoBancario(Base):
    __tablename__ = 'extratos_bancarios'
    
    id = Column(Integer, primary_key=True, index=True)
    nome_arquivo = Column(String(255), nullable=False)
    banco = Column(String(100))
    conta = Column(String(50))
    data_inicio = Column(Date)
    data_fim = Column(Date)
    saldo_inicial = Column(Float)
    saldo_final = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    movimentacoes = relationship("MovimentacaoBancaria", back_populates="extrato", cascade="all, delete-orphan")

class MovimentacaoBancaria(Base):
    __tablename__ = 'movimentacoes_bancarias'
    
    id = Column(Integer, primary_key=True, index=True)
    extrato_id = Column(Integer, ForeignKey('extratos_bancarios.id'), nullable=False)
    data_movimentacao = Column(Date, nullable=False)
    descricao = Column(Text, nullable=False)
    valor = Column(Float, nullable=False)
    tipo = Column(String(10), nullable=False)  # DEBITO, CREDITO
    saldo = Column(Float)
    conta_pagar_id = Column(Integer, ForeignKey('contas_pagar.id'), nullable=True)
    conciliado = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    extrato = relationship("ExtratoBancario", back_populates="movimentacoes")
    conta_pagar = relationship("ContaPagar")

class ConciliacaoBancaria(Base):
    __tablename__ = 'conciliacoes_bancarias'
    
    id = Column(Integer, primary_key=True, index=True)
    movimentacao_id = Column(Integer, ForeignKey('movimentacoes_bancarias.id'), nullable=False)
    conta_pagar_id = Column(Integer, ForeignKey('contas_pagar.id'), nullable=False)
    valor_diferenca = Column(Float, default=0)
    observacoes = Column(Text)
    tipo_conciliacao = Column(String(20), default='AUTOMATICA')  # AUTOMATICA, MANUAL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    movimentacao = relationship("MovimentacaoBancaria")
    conta_pagar = relationship("ContaPagar")

