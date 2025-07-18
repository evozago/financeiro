from flask import Blueprint, request, jsonify
from src.models.financeiro import db, ContaPagar, Fornecedor, TipoDespesa, NotaFiscal
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import and_, or_

contas_pagar_bp = Blueprint('contas_pagar', __name__)

@contas_pagar_bp.route('/contas-pagar', methods=['GET'])
def listar_contas_pagar():
    """Lista contas a pagar com filtros"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        fornecedor_id = request.args.get('fornecedor_id', type=int)
        tipo_despesa_id = request.args.get('tipo_despesa_id', type=int)
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        vencidas = request.args.get('vencidas', '').lower() == 'true'
        
        query = ContaPagar.query
        
        # Filtro por texto
        if search:
            query = query.join(Fornecedor).filter(
                or_(
                    ContaPagar.descricao.ilike(f'%{search}%'),
                    ContaPagar.numero_documento.ilike(f'%{search}%'),
                    Fornecedor.razao_social.ilike(f'%{search}%')
                )
            )
        
        # Filtro por status
        if status:
            query = query.filter(ContaPagar.status == status)
        
        # Filtro por fornecedor
        if fornecedor_id:
            query = query.filter(ContaPagar.fornecedor_id == fornecedor_id)
        
        # Filtro por tipo de despesa
        if tipo_despesa_id:
            query = query.filter(ContaPagar.tipo_despesa_id == tipo_despesa_id)
        
        # Filtro por período
        if data_inicio:
            try:
                data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
                query = query.filter(ContaPagar.data_vencimento >= data_inicio_obj)
            except ValueError:
                pass
        
        if data_fim:
            try:
                data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
                query = query.filter(ContaPagar.data_vencimento <= data_fim_obj)
            except ValueError:
                pass
        
        # Filtro por contas vencidas
        if vencidas:
            hoje = date.today()
            query = query.filter(
                and_(
                    ContaPagar.data_vencimento < hoje,
                    ContaPagar.status == 'PENDENTE'
                )
            )
        
        contas = query.order_by(ContaPagar.data_vencimento.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [conta.to_dict() for conta in contas.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': contas.total,
                'pages': contas.pages,
                'has_next': contas.has_next,
                'has_prev': contas.has_prev
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@contas_pagar_bp.route('/contas-pagar/<int:conta_id>', methods=['GET'])
def obter_conta_pagar(conta_id):
    """Obtém uma conta a pagar específica"""
    try:
        conta = ContaPagar.query.get_or_404(conta_id)
        return jsonify({
            'success': True,
            'data': conta.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@contas_pagar_bp.route('/contas-pagar', methods=['POST'])
def criar_conta_pagar():
    """Cria uma nova conta a pagar"""
    try:
        data = request.get_json()
        
        # Validações obrigatórias
        if not data.get('fornecedor_id'):
            return jsonify({'success': False, 'error': 'Fornecedor é obrigatório'}), 400
        
        if not data.get('tipo_despesa_id'):
            return jsonify({'success': False, 'error': 'Tipo de despesa é obrigatório'}), 400
        
        if not data.get('descricao'):
            return jsonify({'success': False, 'error': 'Descrição é obrigatória'}), 400
        
        if not data.get('valor_original'):
            return jsonify({'success': False, 'error': 'Valor é obrigatório'}), 400
        
        if not data.get('data_vencimento'):
            return jsonify({'success': False, 'error': 'Data de vencimento é obrigatória'}), 400
        
        # Verifica se fornecedor existe
        fornecedor = Fornecedor.query.get(data['fornecedor_id'])
        if not fornecedor:
            return jsonify({'success': False, 'error': 'Fornecedor não encontrado'}), 400
        
        # Verifica se tipo de despesa existe
        tipo_despesa = TipoDespesa.query.get(data['tipo_despesa_id'])
        if not tipo_despesa:
            return jsonify({'success': False, 'error': 'Tipo de despesa não encontrado'}), 400
        
        # Converte data de vencimento
        try:
            data_vencimento = datetime.strptime(data['data_vencimento'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'error': 'Data de vencimento inválida'}), 400
        
        # Verifica se é parcelado
        parcelas = data.get('parcelas', [])
        if parcelas and len(parcelas) > 1:
            # Cria múltiplas contas para parcelamento
            contas_criadas = []
            
            for i, parcela in enumerate(parcelas, 1):
                try:
                    data_venc_parcela = datetime.strptime(parcela['data_vencimento'], '%Y-%m-%d').date()
                except ValueError:
                    return jsonify({'success': False, 'error': f'Data de vencimento da parcela {i} inválida'}), 400
                
                conta_pagar = ContaPagar(
                    fornecedor_id=data['fornecedor_id'],
                    tipo_despesa_id=data['tipo_despesa_id'],
                    descricao=f"{data['descricao']} - Parcela {i}/{len(parcelas)}",
                    valor_original=Decimal(str(parcela['valor'])),
                    data_vencimento=data_venc_parcela,
                    numero_parcela=i,
                    total_parcelas=len(parcelas),
                    numero_documento=data.get('numero_documento', ''),
                    observacoes=data.get('observacoes', ''),
                    status='PENDENTE'
                )
                
                db.session.add(conta_pagar)
                contas_criadas.append(conta_pagar)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': [conta.to_dict() for conta in contas_criadas],
                'message': f'{len(parcelas)} parcelas criadas com sucesso'
            }), 201
        
        else:
            # Cria conta única
            conta_pagar = ContaPagar(
                fornecedor_id=data['fornecedor_id'],
                tipo_despesa_id=data['tipo_despesa_id'],
                descricao=data['descricao'],
                valor_original=Decimal(str(data['valor_original'])),
                data_vencimento=data_vencimento,
                numero_documento=data.get('numero_documento', ''),
                observacoes=data.get('observacoes', ''),
                status='PENDENTE'
            )
            
            db.session.add(conta_pagar)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': conta_pagar.to_dict(),
                'message': 'Conta a pagar criada com sucesso'
            }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@contas_pagar_bp.route('/contas-pagar/<int:conta_id>', methods=['PUT'])
def atualizar_conta_pagar(conta_id):
    """Atualiza uma conta a pagar"""
    try:
        conta = ContaPagar.query.get_or_404(conta_id)
        data = request.get_json()
        
        # Não permite alterar contas já pagas
        if conta.status == 'PAGO':
            return jsonify({'success': False, 'error': 'Não é possível alterar conta já paga'}), 400
        
        # Atualiza campos permitidos
        if 'fornecedor_id' in data:
            fornecedor = Fornecedor.query.get(data['fornecedor_id'])
            if not fornecedor:
                return jsonify({'success': False, 'error': 'Fornecedor não encontrado'}), 400
            conta.fornecedor_id = data['fornecedor_id']
        
        if 'tipo_despesa_id' in data:
            tipo_despesa = TipoDespesa.query.get(data['tipo_despesa_id'])
            if not tipo_despesa:
                return jsonify({'success': False, 'error': 'Tipo de despesa não encontrado'}), 400
            conta.tipo_despesa_id = data['tipo_despesa_id']
        
        if 'descricao' in data:
            if not data['descricao']:
                return jsonify({'success': False, 'error': 'Descrição é obrigatória'}), 400
            conta.descricao = data['descricao']
        
        if 'valor_original' in data:
            if not data['valor_original']:
                return jsonify({'success': False, 'error': 'Valor é obrigatório'}), 400
            conta.valor_original = Decimal(str(data['valor_original']))
        
        if 'data_vencimento' in data:
            try:
                conta.data_vencimento = datetime.strptime(data['data_vencimento'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Data de vencimento inválida'}), 400
        
        if 'numero_documento' in data:
            conta.numero_documento = data['numero_documento']
        
        if 'observacoes' in data:
            conta.observacoes = data['observacoes']
        
        if 'status' in data and data['status'] in ['PENDENTE', 'PAGO', 'VENCIDO', 'CANCELADO']:
            conta.status = data['status']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': conta.to_dict(),
            'message': 'Conta a pagar atualizada com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@contas_pagar_bp.route('/contas-pagar/<int:conta_id>/pagar', methods=['POST'])
def pagar_conta(conta_id):
    """Marca uma conta como paga"""
    try:
        conta = ContaPagar.query.get_or_404(conta_id)
        data = request.get_json()
        
        if conta.status == 'PAGO':
            return jsonify({'success': False, 'error': 'Conta já está paga'}), 400
        
        # Dados do pagamento
        data_pagamento = data.get('data_pagamento')
        valor_pago = data.get('valor_pago', conta.valor_original)
        
        if data_pagamento:
            try:
                conta.data_pagamento = datetime.strptime(data_pagamento, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'success': False, 'error': 'Data de pagamento inválida'}), 400
        else:
            conta.data_pagamento = date.today()
        
        conta.valor_pago = Decimal(str(valor_pago))
        conta.status = 'PAGO'
        
        if 'observacoes' in data:
            conta.observacoes = data['observacoes']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': conta.to_dict(),
            'message': 'Conta marcada como paga'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@contas_pagar_bp.route('/contas-pagar/<int:conta_id>', methods=['DELETE'])
def deletar_conta_pagar(conta_id):
    """Deleta uma conta a pagar"""
    try:
        conta = ContaPagar.query.get_or_404(conta_id)
        
        # Não permite excluir contas já pagas
        if conta.status == 'PAGO':
            return jsonify({'success': False, 'error': 'Não é possível excluir conta já paga'}), 400
        
        # Verifica se tem comprovantes ou conciliações associadas
        if conta.comprovantes or conta.conciliacoes:
            return jsonify({
                'success': False,
                'error': 'Não é possível excluir conta com comprovantes ou conciliações associadas'
            }), 400
        
        db.session.delete(conta)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Conta a pagar excluída com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@contas_pagar_bp.route('/contas-pagar/dashboard', methods=['GET'])
def dashboard_contas_pagar():
    """Retorna dados para dashboard de contas a pagar"""
    try:
        hoje = date.today()
        
        # Totais por status
        total_pendente = db.session.query(db.func.sum(ContaPagar.valor_original)).filter(
            ContaPagar.status == 'PENDENTE'
        ).scalar() or 0
        
        total_pago = db.session.query(db.func.sum(ContaPagar.valor_pago)).filter(
            ContaPagar.status == 'PAGO'
        ).scalar() or 0
        
        total_vencido = db.session.query(db.func.sum(ContaPagar.valor_original)).filter(
            and_(
                ContaPagar.status == 'PENDENTE',
                ContaPagar.data_vencimento < hoje
            )
        ).scalar() or 0
        
        # Contadores
        count_pendente = ContaPagar.query.filter(ContaPagar.status == 'PENDENTE').count()
        count_pago = ContaPagar.query.filter(ContaPagar.status == 'PAGO').count()
        count_vencido = ContaPagar.query.filter(
            and_(
                ContaPagar.status == 'PENDENTE',
                ContaPagar.data_vencimento < hoje
            )
        ).count()
        
        # Próximos vencimentos (próximos 30 dias)
        from datetime import timedelta
        data_limite = hoje + timedelta(days=30)
        
        proximos_vencimentos = ContaPagar.query.filter(
            and_(
                ContaPagar.status == 'PENDENTE',
                ContaPagar.data_vencimento.between(hoje, data_limite)
            )
        ).order_by(ContaPagar.data_vencimento.asc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': {
                'totais': {
                    'pendente': float(total_pendente),
                    'pago': float(total_pago),
                    'vencido': float(total_vencido)
                },
                'contadores': {
                    'pendente': count_pendente,
                    'pago': count_pago,
                    'vencido': count_vencido
                },
                'proximos_vencimentos': [conta.to_dict() for conta in proximos_vencimentos]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@contas_pagar_bp.route('/contas-pagar/atualizar-status', methods=['POST'])
def atualizar_status_automatico():
    """Atualiza status das contas automaticamente (vencidas)"""
    try:
        hoje = date.today()
        
        # Marca contas vencidas
        contas_vencidas = ContaPagar.query.filter(
            and_(
                ContaPagar.status == 'PENDENTE',
                ContaPagar.data_vencimento < hoje
            )
        ).all()
        
        count_atualizadas = 0
        for conta in contas_vencidas:
            conta.status = 'VENCIDO'
            count_atualizadas += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{count_atualizadas} contas marcadas como vencidas'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

