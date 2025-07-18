import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.fornecedores import fornecedores_bp
from src.routes.tipos_despesa import tipos_despesa_bp
from src.routes.notas_fiscais import notas_fiscais_bp
from src.routes.contas_pagar import contas_pagar_bp
from src.routes.comprovantes import comprovantes_bp
from src.routes.conciliacao import conciliacao_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'sistema_financeiro_2025_key_secure'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Enable CORS for all routes
CORS(app)

# Register blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(fornecedores_bp, url_prefix='/api')
app.register_blueprint(tipos_despesa_bp, url_prefix='/api')
app.register_blueprint(notas_fiscais_bp, url_prefix='/api')
app.register_blueprint(contas_pagar_bp, url_prefix='/api')
app.register_blueprint(comprovantes_bp, url_prefix='/api')
app.register_blueprint(conciliacao_bp, url_prefix='/api')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

with app.app_context():
    db.create_all()
    
    # Create default expense types if they don't exist
    from src.models.financeiro import TipoDespesa
    tipos_default = [
        {'nome': 'Fornecedores', 'descricao': 'Contas a pagar de fornecedores'},
        {'nome': 'Aluguel', 'descricao': 'Despesas com aluguel'},
        {'nome': 'Água', 'descricao': 'Despesas com água'},
        {'nome': 'Energia Elétrica', 'descricao': 'Despesas com energia elétrica'},
        {'nome': 'Telefone/Internet', 'descricao': 'Despesas com telefone e internet'},
        {'nome': 'Folha de Pagamento', 'descricao': 'Despesas com folha de pagamento'},
        {'nome': 'Impostos', 'descricao': 'Despesas com impostos'},
        {'nome': 'Manutenção', 'descricao': 'Despesas com manutenção'},
        {'nome': 'Material de Escritório', 'descricao': 'Despesas com material de escritório'},
        {'nome': 'Outras Despesas', 'descricao': 'Outras despesas diversas'}
    ]
    
    for tipo_data in tipos_default:
        tipo_existente = TipoDespesa.query.filter_by(nome=tipo_data['nome']).first()
        if not tipo_existente:
            tipo = TipoDespesa(nome=tipo_data['nome'], descricao=tipo_data['descricao'])
            db.session.add(tipo)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
