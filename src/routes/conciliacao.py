from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from src.models.financeiro import db, ExtratoBancario, ConciliacaoBancaria, ContaPagar, Fornecedor
from datetime import datetime, date, timedelta
from decimal import Decimal
import os
import tempfile
from ofxparse import OfxParser

conciliacao_bp = Blueprint('conciliacao', __name__)

# Configurações de upload
UPLOAD_FOLDER = 'uploads/extratos'
ALLOWED_EXTENSIONS = {'ofx', 'qfx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_ofx_file(filepath):
    """Processa arquivo OFX e extrai transações"""
    try:
        with open(filepath, 'rb') as ofx_file:
            ofx = OfxParser.parse(ofx_file)
        
        transacoes = []
        
        # Processar conta bancária
        if hasattr(ofx, 'account') and ofx.account:
            account = ofx.account
            
            # Informações da conta
            conta_info = {
                'banco': getattr(account.institution, 'organization', ''),
                'agencia': getattr(account, 'branch_id', ''),
                'conta': getattr(account, 'account_id', ''),
                'tipo': getattr(account, 'account_type', '')
            }
            
            # Processar transações
            if hasattr(account, 'statement') and account.statement:
                for transaction in account.statement.transactions:
                    transacao = {
                        'data': transaction.date.date() if hasattr(transaction.date, 'date') else transaction.date,
                        'valor': float(transaction.amount),
                        'tipo': transaction.type,
                        'descricao': transaction.memo or transaction.payee or '',
                        'id_transacao': getattr(transaction, 'id', ''),
                        'conta_info': conta_info
                    }
                    transacoes.append(transacao)
        
        return transacoes, conta_info
        
    except Exception as e:
        print(f"Erro ao processar OFX: {str(e)}")
        return [], {}

def find_matching_conta_pagar_for_transaction(valor, data_transacao, descricao=''):
    """Encontra conta a pagar que corresponde à transação bancária"""
    if valor >= 0:  # Só processar débitos (valores negativos)
        return None
    
    valor_absoluto = abs(valor)
    tolerance = valor_absoluto * 0.05  # 5% de tolerância
    valor_min = valor_absoluto - tolerance
    valor_max = valor_absoluto + tolerance
    
    # Buscar contas pendentes ou pagas em janela de ±10 dias
    data_inicio = data_transacao - timedelta(days=10)
    data_fim = data_transacao + timedelta(days=10)
    
    query = ContaPagar.query.filter(
        ContaPagar.valor_original.between(valor_min, valor_max),
        ContaPagar.data_vencimento.between(data_inicio, data_fim)
    ).filter(
        ContaPagar.status.in_(['PENDENTE', 'PAGO'])
    )
    
    # Se temos descrição, tentar filtrar por fornecedor
    if descricao:
        # Extrair palavras-chave da descrição
        palavras_chave = descricao.upper().split()
        for palavra in palavras_chave:
            if len(palavra) > 3:  # Só palavras com mais de 3 caracteres
                query_com_fornecedor = query.join(Fornecedor).filter(
                    Fornecedor.razao_social.ilike(f'%{palavra}%')
                )
                resultado = query_com_fornecedor.first()
                if resultado:
                    return resultado
    
    # Retornar primeira correspondência por valor e data
    return query.order_by(ContaPagar.data_vencimento.asc()).first()

@conciliacao_bp.route('/extratos', methods=['GET'])
def listar_extratos():
    """Lista extratos bancários importados"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', '')
        
        query = ExtratoBancario.query
        
        if status:
            query = query.filter(ExtratoBancario.status == status)
        
        extratos = query.order_by(
            ExtratoBancario.data_transacao.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [extrato.to_dict() for extrato in extratos.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': extratos.total,
                'pages': extratos.pages,
                'has_next': extratos.has_next,
                'has_prev': extratos.has_prev
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@conciliacao_bp.route('/extratos/upload', methods=['POST'])
def upload_extrato_ofx():
    """Upload e processamento de arquivo OFX"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False, 
                'error': 'Tipo de arquivo não permitido. Use OFX ou QFX'
            }), 400
        
        # Criar diretório se não existir
        upload_dir = os.path.join(os.path.dirname(__file__), '..', '..', UPLOAD_FOLDER)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Salvar arquivo temporariamente
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Processar arquivo OFX
        transacoes, conta_info = parse_ofx_file(filepath)
        
        if not transacoes:
            return jsonify({
                'success': False, 
                'error': 'Nenhuma transação encontrada no arquivo OFX'
            }), 400
        
        # Salvar transações no banco
        extratos_criados = []
        conciliacoes_automaticas = 0
        
        for transacao in transacoes:
            # Verificar se transação já existe
            extrato_existente = ExtratoBancario.query.filter_by(
                id_transacao=transacao['id_transacao'],
                data_transacao=transacao['data'],
                valor=Decimal(str(transacao['valor']))
            ).first()
            
            if extrato_existente:
                continue  # Pular transações duplicadas
            
            # Criar registro do extrato
            extrato = ExtratoBancario(
                data_transacao=transacao['data'],
                valor=Decimal(str(transacao['valor'])),
                tipo_transacao=transacao['tipo'],
                descricao=transacao['descricao'],
                id_transacao=transacao['id_transacao'],
                banco=conta_info.get('banco', ''),
                agencia=conta_info.get('agencia', ''),
                conta=conta_info.get('conta', ''),
                nome_arquivo=filename,
                status='NAO_CONCILIADO'
            )
            
            # Tentar conciliação automática para débitos
            if transacao['valor'] < 0:
                conta_correspondente = find_matching_conta_pagar_for_transaction(
                    transacao['valor'],
                    transacao['data'],
                    transacao['descricao']
                )
                
                if conta_correspondente:
                    # Criar conciliação automática
                    conciliacao = ConciliacaoBancaria(
                        extrato_bancario=extrato,
                        conta_pagar=conta_correspondente,
                        tipo_conciliacao='AUTOMATICA',
                        data_conciliacao=datetime.now(),
                        observacoes='Conciliação automática baseada em valor e data'
                    )
                    
                    extrato.status = 'CONCILIADO'
                    
                    # Marcar conta como paga se ainda não estiver
                    if conta_correspondente.status == 'PENDENTE':
                        conta_correspondente.status = 'PAGO'
                        conta_correspondente.data_pagamento = transacao['data']
                        conta_correspondente.valor_pago = Decimal(str(abs(transacao['valor'])))
                    
                    db.session.add(conciliacao)
                    conciliacoes_automaticas += 1
            
            db.session.add(extrato)
            extratos_criados.append(extrato)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Extrato processado com sucesso. {len(extratos_criados)} transações importadas, {conciliacoes_automaticas} conciliações automáticas',
            'data': {
                'transacoes_importadas': len(extratos_criados),
                'conciliacoes_automaticas': conciliacoes_automaticas,
                'conta_info': conta_info
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@conciliacao_bp.route('/conciliacoes', methods=['GET'])
def listar_conciliacoes():
    """Lista conciliações bancárias"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        tipo = request.args.get('tipo', '')
        
        query = ConciliacaoBancaria.query
        
        if tipo:
            query = query.filter(ConciliacaoBancaria.tipo_conciliacao == tipo)
        
        conciliacoes = query.order_by(
            ConciliacaoBancaria.data_conciliacao.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [conciliacao.to_dict() for conciliacao in conciliacoes.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': conciliacoes.total,
                'pages': conciliacoes.pages,
                'has_next': conciliacoes.has_next,
                'has_prev': conciliacoes.has_prev
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@conciliacao_bp.route('/conciliacoes/manual', methods=['POST'])
def conciliar_manual():
    """Conciliação manual entre extrato e conta a pagar"""
    try:
        data = request.get_json()
        
        extrato_id = data.get('extrato_id')
        conta_pagar_id = data.get('conta_pagar_id')
        observacoes = data.get('observacoes', '')
        
        if not extrato_id or not conta_pagar_id:
            return jsonify({
                'success': False, 
                'error': 'ID do extrato e da conta a pagar são obrigatórios'
            }), 400
        
        extrato = ExtratoBancario.query.get(extrato_id)
        conta_pagar = ContaPagar.query.get(conta_pagar_id)
        
        if not extrato:
            return jsonify({'success': False, 'error': 'Extrato não encontrado'}), 400
        
        if not conta_pagar:
            return jsonify({'success': False, 'error': 'Conta a pagar não encontrada'}), 400
        
        if extrato.status == 'CONCILIADO':
            return jsonify({'success': False, 'error': 'Extrato já está conciliado'}), 400
        
        # Criar conciliação manual
        conciliacao = ConciliacaoBancaria(
            extrato_bancario_id=extrato_id,
            conta_pagar_id=conta_pagar_id,
            tipo_conciliacao='MANUAL',
            data_conciliacao=datetime.now(),
            observacoes=observacoes
        )
        
        # Atualizar status do extrato
        extrato.status = 'CONCILIADO'
        
        # Marcar conta como paga se ainda não estiver
        if conta_pagar.status == 'PENDENTE':
            conta_pagar.status = 'PAGO'
            conta_pagar.data_pagamento = extrato.data_transacao
            conta_pagar.valor_pago = abs(extrato.valor)
        
        db.session.add(conciliacao)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': conciliacao.to_dict(),
            'message': 'Conciliação manual realizada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@conciliacao_bp.route('/conciliacoes/<int:conciliacao_id>/desfazer', methods=['POST'])
def desfazer_conciliacao(conciliacao_id):
    """Desfaz uma conciliação bancária"""
    try:
        conciliacao = ConciliacaoBancaria.query.get_or_404(conciliacao_id)
        
        # Reverter status do extrato
        if conciliacao.extrato_bancario:
            conciliacao.extrato_bancario.status = 'NAO_CONCILIADO'
        
        # Reverter status da conta a pagar
        if conciliacao.conta_pagar and conciliacao.conta_pagar.status == 'PAGO':
            conciliacao.conta_pagar.status = 'PENDENTE'
            conciliacao.conta_pagar.data_pagamento = None
            conciliacao.conta_pagar.valor_pago = None
        
        # Remover conciliação
        db.session.delete(conciliacao)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Conciliação desfeita com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@conciliacao_bp.route('/extratos/sugestoes/<int:extrato_id>', methods=['GET'])
def sugerir_contas_para_extrato(extrato_id):
    """Sugere contas a pagar para conciliar com extrato"""
    try:
        extrato = ExtratoBancario.query.get_or_404(extrato_id)
        
        if extrato.valor >= 0:  # Só sugerir para débitos
            return jsonify({
                'success': True,
                'data': [],
                'message': 'Sugestões disponíveis apenas para débitos'
            })
        
        valor_absoluto = abs(float(extrato.valor))
        tolerance = valor_absoluto * 0.1  # 10% de tolerância
        valor_min = valor_absoluto - tolerance
        valor_max = valor_absoluto + tolerance
        
        # Buscar em janela de ±15 dias
        data_inicio = extrato.data_transacao - timedelta(days=15)
        data_fim = extrato.data_transacao + timedelta(days=15)
        
        query = ContaPagar.query.filter(
            ContaPagar.valor_original.between(valor_min, valor_max),
            ContaPagar.data_vencimento.between(data_inicio, data_fim),
            ContaPagar.status.in_(['PENDENTE', 'PAGO'])
        )
        
        # Priorizar por proximidade de data
        contas = query.order_by(
            db.func.abs(
                db.func.julianday(ContaPagar.data_vencimento) - 
                db.func.julianday(extrato.data_transacao)
            )
        ).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': [conta.to_dict() for conta in contas]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@conciliacao_bp.route('/dashboard/conciliacao', methods=['GET'])
def dashboard_conciliacao():
    """Dashboard de conciliação bancária"""
    try:
        # Estatísticas de extratos
        total_extratos = ExtratoBancario.query.count()
        extratos_conciliados = ExtratoBancario.query.filter_by(status='CONCILIADO').count()
        extratos_nao_conciliados = ExtratoBancario.query.filter_by(status='NAO_CONCILIADO').count()
        
        # Estatísticas de conciliações
        total_conciliacoes = ConciliacaoBancaria.query.count()
        conciliacoes_automaticas = ConciliacaoBancaria.query.filter_by(tipo_conciliacao='AUTOMATICA').count()
        conciliacoes_manuais = ConciliacaoBancaria.query.filter_by(tipo_conciliacao='MANUAL').count()
        
        # Valores
        valor_total_extratos = db.session.query(
            db.func.sum(ExtratoBancario.valor)
        ).filter(ExtratoBancario.valor < 0).scalar() or 0
        
        valor_conciliado = db.session.query(
            db.func.sum(ExtratoBancario.valor)
        ).filter(
            ExtratoBancario.valor < 0,
            ExtratoBancario.status == 'CONCILIADO'
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'extratos': {
                    'total': total_extratos,
                    'conciliados': extratos_conciliados,
                    'nao_conciliados': extratos_nao_conciliados,
                    'percentual_conciliado': round((extratos_conciliados / total_extratos * 100) if total_extratos > 0 else 0, 2)
                },
                'conciliacoes': {
                    'total': total_conciliacoes,
                    'automaticas': conciliacoes_automaticas,
                    'manuais': conciliacoes_manuais
                },
                'valores': {
                    'total_debitos': float(abs(valor_total_extratos)),
                    'valor_conciliado': float(abs(valor_conciliado)),
                    'valor_pendente': float(abs(valor_total_extratos - valor_conciliado))
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

