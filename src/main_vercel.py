import os
import sys

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.fornecedores import fornecedores_bp
from src.routes.tipos_despesa import tipos_despesa_bp
from src.routes.notas_fiscais import notas_fiscais_bp
from src.routes.contas_pagar import contas_pagar_bp
from src.routes.comprovantes_vercel import comprovantes_bp
from src.routes.conciliacao_vercel import conciliacao_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'sistema_financeiro_2025_key_secure'

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

# Database configuration - Vercel compatible
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # In-memory database for Vercel
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize database
db.init_app(app)

# Create tables and default data
with app.app_context():
    db.create_all()
    
    # Create default expense types if they don't exist
    from src.models.financeiro import TipoDespesa
    tipos_default = [
        {'nome': 'Aluguel', 'descricao': 'Despesas com aluguel'},
        {'nome': 'Energia Elétrica', 'descricao': 'Despesas com energia elétrica'},
        {'nome': 'Folha de Pagamento', 'descricao': 'Despesas com folha de pagamento'},
        {'nome': 'Fornecedores', 'descricao': 'Contas a pagar de fornecedores'},
        {'nome': 'Impostos', 'descricao': 'Despesas com impostos'},
        {'nome': 'Manutenção', 'descricao': 'Despesas com manutenção'},
        {'nome': 'Material de Escritório', 'descricao': 'Despesas com material de escritório'}
    ]
    
    for tipo_data in tipos_default:
        tipo_existente = TipoDespesa.query.filter_by(nome=tipo_data['nome']).first()
        if not tipo_existente:
            novo_tipo = TipoDespesa(nome=tipo_data['nome'], descricao=tipo_data['descricao'])
            db.session.add(novo_tipo)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar tipos de despesa padrão: {e}")

# Route for serving static files
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    try:
        return send_from_directory(app.static_folder, filename)
    except:
        return send_from_directory(app.static_folder, 'index.html')

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Sistema Financeiro está funcionando!', 'version': 'vercel'})

# Info endpoint
@app.route('/api/info')
def info():
    return jsonify({
        'sistema': 'Gestão Financeira',
        'versao': 'Vercel Compatible',
        'funcionalidades': {
            'fornecedores': 'Disponível',
            'tipos_despesa': 'Disponível', 
            'notas_fiscais': 'Disponível',
            'contas_pagar': 'Disponível',
            'ocr_comprovantes': 'Limitado (execute localmente para funcionalidade completa)',
            'conciliacao_bancaria': 'Limitado (execute localmente para funcionalidade completa)'
        },
        'observacao': 'Para funcionalidades completas de OCR e importação OFX, execute o sistema localmente'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

# Para Vercel
app = app

