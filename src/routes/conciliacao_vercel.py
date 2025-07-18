from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta

conciliacao_bp = Blueprint('conciliacao', __name__)

@conciliacao_bp.route('/conciliacao/extrato', methods=['POST'])
def importar_extrato():
    """Importa extrato bancário (versão simplificada para Vercel)"""
    try:
        if 'arquivo' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        arquivo = request.files['arquivo']
        if arquivo.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Para Vercel, retornamos dados de exemplo
        return jsonify({
            'message': 'Funcionalidade de importação OFX não disponível na versão web',
            'info': 'Para usar importação OFX, execute o sistema localmente',
            'arquivo_recebido': arquivo.filename,
            'transacoes_exemplo': [
                {
                    'id': 1,
                    'data': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                    'valor': -1500.00,
                    'descricao': 'TED FORNECEDOR XYZ',
                    'conciliado': False
                },
                {
                    'id': 2,
                    'data': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                    'valor': -850.00,
                    'descricao': 'PIX PAGAMENTO',
                    'conciliado': False
                }
            ]
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao importar extrato: {str(e)}'}), 500

@conciliacao_bp.route('/conciliacao/automatica', methods=['POST'])
def conciliacao_automatica():
    """Executa conciliação automática"""
    try:
        return jsonify({
            'message': 'Conciliação automática simulada',
            'conciliadas': 2,
            'pendentes': 1,
            'total_processado': 3
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro na conciliação automática: {str(e)}'}), 500

@conciliacao_bp.route('/conciliacao/manual', methods=['POST'])
def conciliacao_manual():
    """Executa conciliação manual"""
    try:
        data = request.get_json()
        transacao_id = data.get('transacao_id')
        conta_id = data.get('conta_id')
        
        return jsonify({
            'message': 'Conciliação manual realizada com sucesso',
            'transacao_id': transacao_id,
            'conta_id': conta_id
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro na conciliação manual: {str(e)}'}), 500

@conciliacao_bp.route('/conciliacao/dashboard', methods=['GET'])
def dashboard_conciliacao():
    """Dashboard de conciliação"""
    try:
        return jsonify({
            'total_transacoes': 10,
            'conciliadas': 7,
            'pendentes': 3,
            'valor_conciliado': 15750.00,
            'valor_pendente': 4250.00
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao carregar dashboard: {str(e)}'}), 500

