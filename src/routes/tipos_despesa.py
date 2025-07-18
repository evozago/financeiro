from flask import Blueprint, request, jsonify
from src.models.financeiro import db, TipoDespesa
from sqlalchemy.exc import IntegrityError

tipos_despesa_bp = Blueprint("tipos_despesa", __name__)

@tipos_despesa_bp.route("/tipos-despesa", methods=["GET"])
def listar_tipos_despesa():
    """Lista todos os tipos de despesa"""
    try:
        tipos_despesa = TipoDespesa.query.order_by(TipoDespesa.nome).all()
        return jsonify({
            "success": True,
            "data": [tipo.to_dict() for tipo in tipos_despesa]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@tipos_despesa_bp.route("/tipos-despesa/<int:tipo_despesa_id>", methods=["GET"])
def obter_tipo_despesa(tipo_despesa_id):
    """Obtém um tipo de despesa específico"""
    try:
        tipo_despesa = TipoDespesa.query.get_or_404(tipo_despesa_id)
        return jsonify({
            "success": True,
            "data": tipo_despesa.to_dict()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@tipos_despesa_bp.route("/tipos-despesa", methods=["POST"])
def criar_tipo_despesa():
    """Cria um novo tipo de despesa"""
    try:
        data = request.get_json()
        if not data.get("nome"):
            return jsonify({"success": False, "error": "Nome é obrigatório"}), 400
        
        tipo_despesa = TipoDespesa(
            nome=data["nome"],
            descricao=data.get("descricao"),
            ativo=data.get("ativo", True)
        )
        
        db.session.add(tipo_despesa)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": tipo_despesa.to_dict(),
            "message": "Tipo de despesa criado com sucesso"
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Tipo de despesa já cadastrado"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@tipos_despesa_bp.route("/tipos-despesa/<int:tipo_despesa_id>", methods=["PUT"])
def atualizar_tipo_despesa(tipo_despesa_id):
    """Atualiza um tipo de despesa"""
    try:
        tipo_despesa = TipoDespesa.query.get_or_404(tipo_despesa_id)
        data = request.get_json()
        
        if "nome" in data:
            if not data["nome"]:
                return jsonify({"success": False, "error": "Nome é obrigatório"}), 400
            tipo_despesa.nome = data["nome"]
        
        if "descricao" in data:
            tipo_despesa.descricao = data["descricao"]
            
        if "ativo" in data:
            tipo_despesa.ativo = data["ativo"]
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "data": tipo_despesa.to_dict(),
            "message": "Tipo de despesa atualizado com sucesso"
        })
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({"success": False, "error": "Tipo de despesa já cadastrado"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@tipos_despesa_bp.route("/tipos-despesa/<int:tipo_despesa_id>", methods=["DELETE"])
def deletar_tipo_despesa(tipo_despesa_id):
    """Deleta um tipo de despesa"""
    try:
        tipo_despesa = TipoDespesa.query.get_or_404(tipo_despesa_id)
        
        if tipo_despesa.contas_pagar:
            return jsonify({
                "success": False, 
                "error": "Não é possível excluir tipo de despesa com contas a pagar associadas"
            }), 400
        
        db.session.delete(tipo_despesa)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Tipo de despesa excluído com sucesso"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500


