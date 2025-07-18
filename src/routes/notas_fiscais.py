from flask import Blueprint, request, jsonify
from src.models.financeiro import db, NotaFiscal, ItemNotaFiscal, Fornecedor, ContaPagar, TipoDespesa
from werkzeug.utils import secure_filename
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import re
from decimal import Decimal

notas_fiscais_bp = Blueprint('notas_fiscais', __name__)

def processar_xml_nfe(xml_content):
    """Processa XML da NFe e extrai dados relevantes"""
    try:
        # Parse do XML
        root = ET.fromstring(xml_content)
        
        # Namespace da NFe
        ns = {'nfe': 'http://www.portalfiscal.inf.br/nfe'}
        
        # Busca o elemento infNFe
        inf_nfe = root.find('.//nfe:infNFe', ns)
        if inf_nfe is None:
            raise ValueError("XML inválido: elemento infNFe não encontrado")
        
        # Dados da identificação
        ide = inf_nfe.find('nfe:ide', ns)
        numero = ide.find('nfe:nNF', ns).text if ide.find('nfe:nNF', ns) is not None else ''
        serie = ide.find('nfe:serie', ns).text if ide.find('nfe:serie', ns) is not None else ''
        data_emissao_str = ide.find('nfe:dhEmi', ns).text if ide.find('nfe:dhEmi', ns) is not None else ''
        natureza_operacao = ide.find('nfe:natOp', ns).text if ide.find('nfe:natOp', ns) is not None else ''
        
        # Converte data de emissão
        data_emissao = None
        if data_emissao_str:
            try:
                # Remove timezone se presente
                data_emissao_str = data_emissao_str.split('-03:00')[0].split('+')[0]
                data_emissao = datetime.fromisoformat(data_emissao_str.replace('T', ' '))
            except:
                pass
        
        # Chave de acesso
        chave_acesso = inf_nfe.get('Id', '').replace('NFe', '')
        
        # Dados do emitente (fornecedor)
        emit = inf_nfe.find('nfe:emit', ns)
        cnpj_emit = emit.find('nfe:CNPJ', ns).text if emit.find('nfe:CNPJ', ns) is not None else ''
        razao_social_emit = emit.find('nfe:xNome', ns).text if emit.find('nfe:xNome', ns) is not None else ''
        nome_fantasia_emit = emit.find('nfe:xFant', ns).text if emit.find('nfe:xFant', ns) is not None else ''
        ie_emit = emit.find('nfe:IE', ns).text if emit.find('nfe:IE', ns) is not None else ''
        
        # Endereço do emitente
        endereco_emit = emit.find('nfe:enderEmit', ns)
        endereco_completo = ''
        cidade = ''
        uf = ''
        cep = ''
        telefone = ''
        
        if endereco_emit is not None:
            logradouro = endereco_emit.find('nfe:xLgr', ns).text if endereco_emit.find('nfe:xLgr', ns) is not None else ''
            numero_end = endereco_emit.find('nfe:nro', ns).text if endereco_emit.find('nfe:nro', ns) is not None else ''
            complemento = endereco_emit.find('nfe:xCpl', ns).text if endereco_emit.find('nfe:xCpl', ns) is not None else ''
            bairro = endereco_emit.find('nfe:xBairro', ns).text if endereco_emit.find('nfe:xBairro', ns) is not None else ''
            cidade = endereco_emit.find('nfe:xMun', ns).text if endereco_emit.find('nfe:xMun', ns) is not None else ''
            uf = endereco_emit.find('nfe:UF', ns).text if endereco_emit.find('nfe:UF', ns) is not None else ''
            cep = endereco_emit.find('nfe:CEP', ns).text if endereco_emit.find('nfe:CEP', ns) is not None else ''
            telefone = endereco_emit.find('nfe:fone', ns).text if endereco_emit.find('nfe:fone', ns) is not None else ''
            
            endereco_completo = f"{logradouro}, {numero_end}"
            if complemento:
                endereco_completo += f", {complemento}"
            if bairro:
                endereco_completo += f", {bairro}"
        
        # Formatar CNPJ
        cnpj_formatado = ''
        if cnpj_emit:
            cnpj_limpo = re.sub(r'[^0-9]', '', cnpj_emit)
            if len(cnpj_limpo) == 14:
                cnpj_formatado = f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:14]}"
        
        # Totais da nota
        total = inf_nfe.find('nfe:total/nfe:ICMSTot', ns)
        valor_total = Decimal('0')
        valor_desconto = Decimal('0')
        valor_liquido = Decimal('0')
        
        if total is not None:
            valor_total_elem = total.find('nfe:vNF', ns)
            valor_desconto_elem = total.find('nfe:vDesc', ns)
            
            if valor_total_elem is not None:
                valor_total = Decimal(valor_total_elem.text)
                valor_liquido = valor_total
            
            if valor_desconto_elem is not None:
                valor_desconto = Decimal(valor_desconto_elem.text)
        
        # Itens da nota
        itens = []
        detalhes = inf_nfe.findall('nfe:det', ns)
        
        for det in detalhes:
            numero_item = int(det.get('nItem', 0))
            prod = det.find('nfe:prod', ns)
            
            if prod is not None:
                codigo_produto = prod.find('nfe:cProd', ns).text if prod.find('nfe:cProd', ns) is not None else ''
                descricao = prod.find('nfe:xProd', ns).text if prod.find('nfe:xProd', ns) is not None else ''
                ncm = prod.find('nfe:NCM', ns).text if prod.find('nfe:NCM', ns) is not None else ''
                cfop = prod.find('nfe:CFOP', ns).text if prod.find('nfe:CFOP', ns) is not None else ''
                unidade = prod.find('nfe:uCom', ns).text if prod.find('nfe:uCom', ns) is not None else ''
                quantidade = Decimal(prod.find('nfe:qCom', ns).text) if prod.find('nfe:qCom', ns) is not None else Decimal('0')
                valor_unitario = Decimal(prod.find('nfe:vUnCom', ns).text) if prod.find('nfe:vUnCom', ns) is not None else Decimal('0')
                valor_total_item = Decimal(prod.find('nfe:vProd', ns).text) if prod.find('nfe:vProd', ns) is not None else Decimal('0')
                valor_desconto_item = Decimal(prod.find('nfe:vDesc', ns).text) if prod.find('nfe:vDesc', ns) is not None else Decimal('0')
                
                itens.append({
                    'numero_item': numero_item,
                    'codigo_produto': codigo_produto,
                    'descricao': descricao,
                    'ncm': ncm,
                    'cfop': cfop,
                    'unidade': unidade,
                    'quantidade': quantidade,
                    'valor_unitario': valor_unitario,
                    'valor_total': valor_total_item,
                    'valor_desconto': valor_desconto_item
                })
        
        # Dados de cobrança (duplicatas)
        duplicatas = []
        cobr = inf_nfe.find('nfe:cobr', ns)
        if cobr is not None:
            dups = cobr.findall('nfe:dup', ns)
            for dup in dups:
                numero_dup = dup.find('nfe:nDup', ns).text if dup.find('nfe:nDup', ns) is not None else ''
                data_venc_str = dup.find('nfe:dVenc', ns).text if dup.find('nfe:dVenc', ns) is not None else ''
                valor_dup = Decimal(dup.find('nfe:vDup', ns).text) if dup.find('nfe:vDup', ns) is not None else Decimal('0')
                
                data_vencimento = None
                if data_venc_str:
                    try:
                        data_vencimento = datetime.strptime(data_venc_str, '%Y-%m-%d').date()
                    except:
                        pass
                
                duplicatas.append({
                    'numero': numero_dup,
                    'data_vencimento': data_vencimento,
                    'valor': valor_dup
                })
        
        return {
            'numero': numero,
            'serie': serie,
            'chave_acesso': chave_acesso,
            'data_emissao': data_emissao,
            'natureza_operacao': natureza_operacao,
            'valor_total': valor_total,
            'valor_desconto': valor_desconto,
            'valor_liquido': valor_liquido,
            'fornecedor': {
                'cnpj': cnpj_formatado,
                'razao_social': razao_social_emit,
                'nome_fantasia': nome_fantasia_emit,
                'endereco': endereco_completo,
                'cidade': cidade,
                'uf': uf,
                'cep': cep,
                'telefone': telefone,
                'inscricao_estadual': ie_emit
            },
            'itens': itens,
            'duplicatas': duplicatas
        }
        
    except Exception as e:
        raise ValueError(f"Erro ao processar XML: {str(e)}")

@notas_fiscais_bp.route('/notas-fiscais', methods=['GET'])
def listar_notas_fiscais():
    """Lista todas as notas fiscais"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = NotaFiscal.query
        
        if search:
            query = query.join(Fornecedor).filter(
                db.or_(
                    NotaFiscal.numero.ilike(f'%{search}%'),
                    NotaFiscal.chave_acesso.ilike(f'%{search}%'),
                    Fornecedor.razao_social.ilike(f'%{search}%')
                )
            )
        
        notas = query.order_by(NotaFiscal.data_emissao.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [nota.to_dict() for nota in notas.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': notas.total,
                'pages': notas.pages,
                'has_next': notas.has_next,
                'has_prev': notas.has_prev
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@notas_fiscais_bp.route('/notas-fiscais/<int:nota_id>', methods=['GET'])
def obter_nota_fiscal(nota_id):
    """Obtém uma nota fiscal específica com seus itens"""
    try:
        nota = NotaFiscal.query.get_or_404(nota_id)
        nota_dict = nota.to_dict()
        nota_dict['itens'] = [item.to_dict() for item in nota.itens]
        
        return jsonify({
            'success': True,
            'data': nota_dict
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@notas_fiscais_bp.route('/notas-fiscais/upload', methods=['POST'])
def upload_nota_fiscal():
    """Faz upload e processa XML de nota fiscal"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nenhum arquivo selecionado'}), 400
        
        if not file.filename.lower().endswith('.xml'):
            return jsonify({'success': False, 'error': 'Apenas arquivos XML são aceitos'}), 400
        
        # Lê o conteúdo do arquivo
        xml_content = file.read().decode('utf-8')
        
        # Processa o XML
        dados_nfe = processar_xml_nfe(xml_content)
        
        # Verifica se a nota já existe
        nota_existente = NotaFiscal.query.filter_by(chave_acesso=dados_nfe['chave_acesso']).first()
        if nota_existente:
            return jsonify({
                'success': False, 
                'error': 'Nota fiscal já cadastrada',
                'data': nota_existente.to_dict()
            }), 400
        
        # Busca ou cria o fornecedor
        fornecedor = None
        if dados_nfe['fornecedor']['cnpj']:
            fornecedor = Fornecedor.query.filter_by(cnpj=dados_nfe['fornecedor']['cnpj']).first()
            
            if not fornecedor:
                fornecedor = Fornecedor(
                    cnpj=dados_nfe['fornecedor']['cnpj'],
                    razao_social=dados_nfe['fornecedor']['razao_social'],
                    nome_fantasia=dados_nfe['fornecedor']['nome_fantasia'],
                    endereco=dados_nfe['fornecedor']['endereco'],
                    cidade=dados_nfe['fornecedor']['cidade'],
                    uf=dados_nfe['fornecedor']['uf'],
                    cep=dados_nfe['fornecedor']['cep'],
                    telefone=dados_nfe['fornecedor']['telefone'],
                    inscricao_estadual=dados_nfe['fornecedor']['inscricao_estadual']
                )
                db.session.add(fornecedor)
                db.session.flush()  # Para obter o ID
        
        if not fornecedor:
            return jsonify({'success': False, 'error': 'Dados do fornecedor inválidos'}), 400
        
        # Cria a nota fiscal
        nota_fiscal = NotaFiscal(
            numero=dados_nfe['numero'],
            serie=dados_nfe['serie'],
            chave_acesso=dados_nfe['chave_acesso'],
            fornecedor_id=fornecedor.id,
            data_emissao=dados_nfe['data_emissao'],
            valor_total=dados_nfe['valor_total'],
            valor_desconto=dados_nfe['valor_desconto'],
            valor_liquido=dados_nfe['valor_liquido'],
            natureza_operacao=dados_nfe['natureza_operacao'],
            xml_content=xml_content,
            status='PROCESSADA'
        )
        
        db.session.add(nota_fiscal)
        db.session.flush()  # Para obter o ID
        
        # Cria os itens da nota fiscal
        for item_data in dados_nfe['itens']:
            item = ItemNotaFiscal(
                nota_fiscal_id=nota_fiscal.id,
                numero_item=item_data['numero_item'],
                codigo_produto=item_data['codigo_produto'],
                descricao=item_data['descricao'],
                ncm=item_data['ncm'],
                cfop=item_data['cfop'],
                unidade=item_data['unidade'],
                quantidade=item_data['quantidade'],
                valor_unitario=item_data['valor_unitario'],
                valor_total=item_data['valor_total'],
                valor_desconto=item_data['valor_desconto']
            )
            db.session.add(item)
        
        # Cria contas a pagar para as duplicatas
        if dados_nfe['duplicatas']:
            # Busca tipo de despesa padrão ou cria um
            tipo_despesa = TipoDespesa.query.filter_by(nome='Fornecedores').first()
            if not tipo_despesa:
                tipo_despesa = TipoDespesa(nome='Fornecedores', descricao='Contas a pagar de fornecedores')
                db.session.add(tipo_despesa)
                db.session.flush()
            
            for i, dup in enumerate(dados_nfe['duplicatas'], 1):
                conta_pagar = ContaPagar(
                    fornecedor_id=fornecedor.id,
                    tipo_despesa_id=tipo_despesa.id,
                    nota_fiscal_id=nota_fiscal.id,
                    descricao=f"NF {dados_nfe['numero']}/{dados_nfe['serie']} - Parcela {i}",
                    valor_original=dup['valor'],
                    data_vencimento=dup['data_vencimento'],
                    numero_parcela=i,
                    total_parcelas=len(dados_nfe['duplicatas']),
                    numero_documento=dup['numero'],
                    status='PENDENTE'
                )
                db.session.add(conta_pagar)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': nota_fiscal.to_dict(),
            'message': f'Nota fiscal {dados_nfe["numero"]}/{dados_nfe["serie"]} processada com sucesso'
        }), 201
        
    except ValueError as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Erro interno: {str(e)}'}), 500

@notas_fiscais_bp.route('/notas-fiscais/<int:nota_id>', methods=['DELETE'])
def deletar_nota_fiscal(nota_id):
    """Deleta uma nota fiscal"""
    try:
        nota = NotaFiscal.query.get_or_404(nota_id)
        
        # Verifica se tem contas a pagar pagas associadas
        contas_pagas = [cp for cp in nota.contas_pagar if cp.status == 'PAGO']
        if contas_pagas:
            return jsonify({
                'success': False,
                'error': 'Não é possível excluir nota fiscal com contas a pagar já quitadas'
            }), 400
        
        db.session.delete(nota)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Nota fiscal excluída com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

