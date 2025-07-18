from flask import Blueprint, request, jsonify
import os
from datetime import datetime

comprovantes_bp = Blueprint('comprovantes', __name__)

@comprovantes_bp.route('/comprovantes', methods=['GET'])
def listar_comprovantes():
    """Lista todos os comprovantes"""
    return jsonify([])

@comprovantes_bp.route('/comprovantes', methods=['POST'])
def processar_comprovante():
    """Processa comprovante de pagamento (versão simplificada para Vercel)"""
    try:
        if 'arquivo' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        arquivo = request.files['arquivo']
        if arquivo.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        # Para Vercel, retornamos uma mensagem informativa
        return jsonify({
            'message': 'Funcionalidade de OCR não disponível na versão web',
            'info': 'Para usar OCR, execute o sistema localmente com: python src/main.py',
            'arquivo_recebido': arquivo.filename,
            'dados_exemplo': {
                'valor': 1500.00,
                'data': datetime.now().strftime('%Y-%m-%d'),
                'fornecedor': 'Exemplo Fornecedor',
                'banco': 'Banco Exemplo'
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao processar comprovante: {str(e)}'}), 500

@comprovantes_bp.route('/comprovantes/<int:comprovante_id>/associar', methods=['POST'])
def associar_comprovante(comprovante_id):
    """Associa comprovante a uma conta a pagar"""
    try:
        data = request.get_json()
        conta_id = data.get('conta_id')
        
        return jsonify({
            'message': 'Associação simulada com sucesso',
            'comprovante_id': comprovante_id,
            'conta_id': conta_id
        })
        
    except Exception as e:
        return jsonify({'error': f'Erro ao associar comprovante: {str(e)}'}), 500

