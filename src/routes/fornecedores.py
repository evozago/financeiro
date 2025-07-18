from flask import Blueprint, request, jsonify
from src.models.financeiro import db, Fornecedor
from sqlalchemy.exc import IntegrityError
import re

fornecedores_bp = Blueprint('fornecedores', __name__)

def validar_cnpj(cnpj):
    """Valida formato do CNPJ"""
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    return len(cnpj) == 14

def formatar_cnpj(cnpj):
    """Formata CNPJ para padrão XX.XXX.XXX/XXXX-XX"""
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"
    return cnpj

@fornecedores_bp.route('/fornecedores', methods=['GET'])
def listar_fornecedores():
    """Lista todos os fornecedores"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = Fornecedor.query
        
        if search:
            query = query.filter(
                db.or_(
                    Fornecedor.razao_social.ilike(f'%{search}%'),
                    Fornecedor.nome_fantasia.ilike(f'%{search}%'),
                    Fornecedor.cnpj.ilike(f'%{search}%')
                )
            )
        
        fornecedores = query.order_by(Fornecedor.razao_social).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [fornecedor.to_dict() for fornecedor in fornecedores.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': fornecedores.total,
                'pages': fornecedores.pages,
                'has_next': fornecedores.has_next,
                'has_prev': fornecedores.has_prev
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fornecedores_bp.route('/fornecedores/<int:fornecedor_id>', methods=['GET'])
def obter_fornecedor(fornecedor_id):
    """Obtém um fornecedor específico"""
    try:
        fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
        return jsonify({
            'success': True,
            'data': fornecedor.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fornecedores_bp.route('/fornecedores', methods=['POST'])
def criar_fornecedor():
    """Cria um novo fornecedor"""
    try:
        data = request.get_json()
        
        # Validações
        if not data.get('cnpj'):
            return jsonify({'success': False, 'error': 'CNPJ é obrigatório'}), 400
        
        if not data.get('razao_social'):
            return jsonify({'success': False, 'error': 'Razão social é obrigatória'}), 400
        
        cnpj = re.sub(r'[^0-9]', '', data['cnpj'])
        if not validar_cnpj(cnpj):
            return jsonify({'success': False, 'error': 'CNPJ inválido'}), 400
        
        # Verifica se já existe
        fornecedor_existente = Fornecedor.query.filter_by(cnpj=formatar_cnpj(cnpj)).first()
        if fornecedor_existente:
            return jsonify({'success': False, 'error': 'CNPJ já cadastrado'}), 400
        
        fornecedor = Fornecedor(
            cnpj=formatar_cnpj(cnpj),
            razao_social=data['razao_social'],
            nome_fantasia=data.get('nome_fantasia'),
            endereco=data.get('endereco'),
            cidade=data.get('cidade'),
            uf=data.get('uf'),
            cep=data.get('cep'),
            telefone=data.get('telefone'),
            email=data.get('email'),
            inscricao_estadual=data.get('inscricao_estadual')
        )
        
        db.session.add(fornecedor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': fornecedor.to_dict(),
            'message': 'Fornecedor criado com sucesso'
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'CNPJ já cadastrado'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@fornecedores_bp.route('/fornecedores/<int:fornecedor_id>', methods=['PUT'])
def atualizar_fornecedor(fornecedor_id):
    """Atualiza um fornecedor"""
    try:
        fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
        data = request.get_json()
        
        # Validações
        if 'cnpj' in data:
            cnpj = re.sub(r'[^0-9]', '', data['cnpj'])
            if not validar_cnpj(cnpj):
                return jsonify({'success': False, 'error': 'CNPJ inválido'}), 400
            
            cnpj_formatado = formatar_cnpj(cnpj)
            if cnpj_formatado != fornecedor.cnpj:
                fornecedor_existente = Fornecedor.query.filter_by(cnpj=cnpj_formatado).first()
                if fornecedor_existente:
                    return jsonify({'success': False, 'error': 'CNPJ já cadastrado'}), 400
                fornecedor.cnpj = cnpj_formatado
        
        if 'razao_social' in data:
            if not data['razao_social']:
                return jsonify({'success': False, 'error': 'Razão social é obrigatória'}), 400
            fornecedor.razao_social = data['razao_social']
        
        # Atualiza outros campos
        campos_opcionais = ['nome_fantasia', 'endereco', 'cidade', 'uf', 'cep', 
                           'telefone', 'email', 'inscricao_estadual']
        for campo in campos_opcionais:
            if campo in data:
                setattr(fornecedor, campo, data[campo])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': fornecedor.to_dict(),
            'message': 'Fornecedor atualizado com sucesso'
        })
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'CNPJ já cadastrado'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@fornecedores_bp.route('/fornecedores/<int:fornecedor_id>', methods=['DELETE'])
def deletar_fornecedor(fornecedor_id):
    """Deleta um fornecedor"""
    try:
        fornecedor = Fornecedor.query.get_or_404(fornecedor_id)
        
        # Verifica se tem notas fiscais ou contas a pagar associadas
        if fornecedor.notas_fiscais or fornecedor.contas_pagar:
            return jsonify({
                'success': False, 
                'error': 'Não é possível excluir fornecedor com notas fiscais ou contas a pagar associadas'
            }), 400
        
        db.session.delete(fornecedor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Fornecedor excluído com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@fornecedores_bp.route('/fornecedores/buscar-cnpj/<cnpj>', methods=['GET'])
def buscar_por_cnpj(cnpj):
    """Busca fornecedor por CNPJ"""
    try:
        cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
        if not validar_cnpj(cnpj_limpo):
            return jsonify({'success': False, 'error': 'CNPJ inválido'}), 400
        
        cnpj_formatado = formatar_cnpj(cnpj_limpo)
        fornecedor = Fornecedor.query.filter_by(cnpj=cnpj_formatado).first()
        
        if fornecedor:
            return jsonify({
                'success': True,
                'data': fornecedor.to_dict()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Fornecedor não encontrado'
            }), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

