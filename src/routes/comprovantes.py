from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from src.models.financeiro import db, Comprovante, ContaPagar, Fornecedor
from datetime import datetime, date
from decimal import Decimal
import os
import pytesseract
from PIL import Image
import re
import tempfile

comprovantes_bp = Blueprint('comprovantes', __name__)

# Configurações de upload
UPLOAD_FOLDER = 'uploads/comprovantes'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_image(image_path):
    """Extrai texto de uma imagem usando OCR"""
    try:
        # Configurar Tesseract para português
        custom_config = r'--oem 3 --psm 6 -l por'
        
        # Abrir e processar imagem
        image = Image.open(image_path)
        
        # Converter para RGB se necessário
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Extrair texto
        text = pytesseract.image_to_string(image, config=custom_config)
        
        return text.strip()
    except Exception as e:
        print(f"Erro no OCR: {str(e)}")
        return ""

def parse_payment_info(text):
    """Extrai informações de pagamento do texto OCR"""
    info = {
        'valor': None,
        'data': None,
        'fornecedor': None,
        'banco': None,
        'agencia': None,
        'conta': None
    }
    
    # Padrões regex para extrair informações
    patterns = {
        'valor': [
            r'R\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            r'VALOR\s*:?\s*R?\$?\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            r'(\d{1,3}(?:\.\d{3})*(?:,\d{2}))\s*R\$?'
        ],
        'data': [
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'DATA\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})'
        ],
        'banco': [
            r'BANCO\s*:?\s*([A-Z\s]+)',
            r'(ITAU|BRADESCO|SANTANDER|CAIXA|BANCO DO BRASIL|NUBANK|INTER)',
            r'(\d{3})\s*-?\s*([A-Z\s]+BANCO[A-Z\s]*)'
        ],
        'agencia': [
            r'AG[EÊ]NCIA\s*:?\s*(\d{4,5})',
            r'AG\s*:?\s*(\d{4,5})'
        ],
        'conta': [
            r'CONTA\s*:?\s*(\d+[\-\d]*)',
            r'C\/C\s*:?\s*(\d+[\-\d]*)'
        ]
    }
    
    # Extrair valor
    for pattern in patterns['valor']:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            valor_str = match.group(1).replace('.', '').replace(',', '.')
            try:
                info['valor'] = float(valor_str)
                break
            except ValueError:
                continue
    
    # Extrair data
    for pattern in patterns['data']:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data_str = match.group(1)
            try:
                # Tentar diferentes formatos de data
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y']:
                    try:
                        info['data'] = datetime.strptime(data_str, fmt).date()
                        break
                    except ValueError:
                        continue
                if info['data']:
                    break
            except:
                continue
    
    # Extrair banco
    for pattern in patterns['banco']:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['banco'] = match.group(1).strip()
            break
    
    # Extrair agência
    for pattern in patterns['agencia']:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['agencia'] = match.group(1)
            break
    
    # Extrair conta
    for pattern in patterns['conta']:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info['conta'] = match.group(1)
            break
    
    # Tentar identificar fornecedor por palavras-chave
    fornecedores_conhecidos = [
        'ITAU', 'BRADESCO', 'SANTANDER', 'CAIXA', 'BANCO DO BRASIL',
        'NUBANK', 'INTER', 'SICREDI', 'BANRISUL', 'SAFRA'
    ]
    
    for fornecedor in fornecedores_conhecidos:
        if fornecedor.lower() in text.lower():
            info['fornecedor'] = fornecedor
            break
    
    return info

def find_matching_conta_pagar(valor, data_pagamento, fornecedor_nome=None):
    """Encontra conta a pagar que corresponde ao comprovante"""
    if not valor:
        return None
    
    # Buscar contas pendentes com valor similar
    tolerance = valor * 0.05  # 5% de tolerância
    valor_min = valor - tolerance
    valor_max = valor + tolerance
    
    query = ContaPagar.query.filter(
        ContaPagar.status == 'PENDENTE',
        ContaPagar.valor_original.between(valor_min, valor_max)
    )
    
    # Se temos data, buscar em janela de ±10 dias
    if data_pagamento:
        from datetime import timedelta
        data_inicio = data_pagamento - timedelta(days=10)
        data_fim = data_pagamento + timedelta(days=10)
        query = query.filter(ContaPagar.data_vencimento.between(data_inicio, data_fim))
    
    # Se temos fornecedor, tentar filtrar
    if fornecedor_nome:
        query = query.join(Fornecedor).filter(
            Fornecedor.razao_social.ilike(f'%{fornecedor_nome}%')
        )
    
    # Retornar a primeira correspondência
    return query.first()

@comprovantes_bp.route('/comprovantes', methods=['GET'])
def listar_comprovantes():
    """Lista comprovantes de pagamento"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        comprovantes = Comprovante.query.order_by(
            Comprovante.data_upload.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [comprovante.to_dict() for comprovante in comprovantes.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': comprovantes.total,
                'pages': comprovantes.pages,
                'has_next': comprovantes.has_next,
                'has_prev': comprovantes.has_prev
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@comprovantes_bp.route('/comprovantes/upload', methods=['POST'])
def upload_comprovante():
    """Upload e processamento de comprovante de pagamento"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False, 
                'error': 'Tipo de arquivo não permitido. Use PNG, JPG, JPEG ou PDF'
            }), 400
        
        # Criar diretório se não existir
        upload_dir = os.path.join(os.path.dirname(__file__), '..', '..', UPLOAD_FOLDER)
        os.makedirs(upload_dir, exist_ok=True)
        
        # Salvar arquivo
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        # Processar OCR
        texto_ocr = extract_text_from_image(filepath)
        info_pagamento = parse_payment_info(texto_ocr)
        
        # Criar registro do comprovante
        comprovante = Comprovante(
            nome_arquivo=filename,
            caminho_arquivo=filepath,
            texto_ocr=texto_ocr,
            valor_reconhecido=Decimal(str(info_pagamento['valor'])) if info_pagamento['valor'] else None,
            data_reconhecida=info_pagamento['data'],
            fornecedor_reconhecido=info_pagamento['fornecedor'],
            banco_reconhecido=info_pagamento['banco'],
            status_ocr='PROCESSADO' if info_pagamento['valor'] else 'ERRO'
        )
        
        # Tentar encontrar conta a pagar correspondente
        if info_pagamento['valor'] and info_pagamento['data']:
            conta_correspondente = find_matching_conta_pagar(
                info_pagamento['valor'],
                info_pagamento['data'],
                info_pagamento['fornecedor']
            )
            
            if conta_correspondente:
                comprovante.conta_pagar_id = conta_correspondente.id
                comprovante.status_ocr = 'ASSOCIADO'
        
        db.session.add(comprovante)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': comprovante.to_dict(),
            'message': 'Comprovante processado com sucesso',
            'info_extraida': info_pagamento
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@comprovantes_bp.route('/comprovantes/<int:comprovante_id>/associar', methods=['POST'])
def associar_comprovante(comprovante_id):
    """Associa comprovante a uma conta a pagar"""
    try:
        comprovante = Comprovante.query.get_or_404(comprovante_id)
        data = request.get_json()
        
        conta_pagar_id = data.get('conta_pagar_id')
        if not conta_pagar_id:
            return jsonify({'success': False, 'error': 'ID da conta a pagar é obrigatório'}), 400
        
        conta_pagar = ContaPagar.query.get(conta_pagar_id)
        if not conta_pagar:
            return jsonify({'success': False, 'error': 'Conta a pagar não encontrada'}), 400
        
        if conta_pagar.status == 'PAGO':
            return jsonify({'success': False, 'error': 'Conta já está paga'}), 400
        
        # Associar comprovante
        comprovante.conta_pagar_id = conta_pagar_id
        comprovante.status_ocr = 'ASSOCIADO'
        
        # Opcionalmente marcar conta como paga
        if data.get('marcar_como_pago', False):
            conta_pagar.status = 'PAGO'
            conta_pagar.data_pagamento = comprovante.data_reconhecida or date.today()
            conta_pagar.valor_pago = comprovante.valor_reconhecido or conta_pagar.valor_original
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': comprovante.to_dict(),
            'message': 'Comprovante associado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@comprovantes_bp.route('/comprovantes/<int:comprovante_id>/desassociar', methods=['POST'])
def desassociar_comprovante(comprovante_id):
    """Desassocia comprovante de uma conta a pagar"""
    try:
        comprovante = Comprovante.query.get_or_404(comprovante_id)
        
        if comprovante.conta_pagar_id:
            # Se a conta foi marcada como paga por este comprovante, reverter
            conta_pagar = ContaPagar.query.get(comprovante.conta_pagar_id)
            if conta_pagar and conta_pagar.status == 'PAGO':
                conta_pagar.status = 'PENDENTE'
                conta_pagar.data_pagamento = None
                conta_pagar.valor_pago = None
        
        comprovante.conta_pagar_id = None
        comprovante.status_ocr = 'PROCESSADO'
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': comprovante.to_dict(),
            'message': 'Comprovante desassociado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@comprovantes_bp.route('/comprovantes/<int:comprovante_id>', methods=['DELETE'])
def deletar_comprovante(comprovante_id):
    """Deleta um comprovante"""
    try:
        comprovante = Comprovante.query.get_or_404(comprovante_id)
        
        # Remover arquivo físico
        if os.path.exists(comprovante.caminho_arquivo):
            os.remove(comprovante.caminho_arquivo)
        
        # Se estava associado a uma conta paga, reverter status
        if comprovante.conta_pagar_id:
            conta_pagar = ContaPagar.query.get(comprovante.conta_pagar_id)
            if conta_pagar and conta_pagar.status == 'PAGO':
                conta_pagar.status = 'PENDENTE'
                conta_pagar.data_pagamento = None
                conta_pagar.valor_pago = None
        
        db.session.delete(comprovante)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Comprovante excluído com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@comprovantes_bp.route('/comprovantes/sugestoes/<int:comprovante_id>', methods=['GET'])
def sugerir_contas_pagar(comprovante_id):
    """Sugere contas a pagar para associar ao comprovante"""
    try:
        comprovante = Comprovante.query.get_or_404(comprovante_id)
        
        if not comprovante.valor_reconhecido:
            return jsonify({
                'success': True,
                'data': [],
                'message': 'Valor não reconhecido no comprovante'
            })
        
        # Buscar contas similares
        valor = float(comprovante.valor_reconhecido)
        tolerance = valor * 0.1  # 10% de tolerância
        valor_min = valor - tolerance
        valor_max = valor + tolerance
        
        query = ContaPagar.query.filter(
            ContaPagar.status == 'PENDENTE',
            ContaPagar.valor_original.between(valor_min, valor_max)
        )
        
        # Se temos data, priorizar por proximidade
        if comprovante.data_reconhecida:
            from datetime import timedelta
            data_inicio = comprovante.data_reconhecida - timedelta(days=30)
            data_fim = comprovante.data_reconhecida + timedelta(days=30)
            query = query.filter(ContaPagar.data_vencimento.between(data_inicio, data_fim))
        
        contas = query.order_by(ContaPagar.data_vencimento.asc()).limit(10).all()
        
        return jsonify({
            'success': True,
            'data': [conta.to_dict() for conta in contas]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

