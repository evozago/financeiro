from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import logging
from database import init_db, test_connection

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Criar aplicação Flask
app = Flask(__name__, static_folder='static')
CORS(app)

# Configurações
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Registrar blueprints
from routes.fornecedores import fornecedores_bp
from routes.tipos_despesa import tipos_despesa_bp
from routes.notas_fiscais import notas_fiscais_bp
from routes.contas_pagar import contas_pagar_bp
from routes.comprovantes_vercel import comprovantes_bp
from routes.conciliacao_vercel import conciliacao_bp

app.register_blueprint(fornecedores_bp, url_prefix='/api')
app.register_blueprint(tipos_despesa_bp, url_prefix='/api')
app.register_blueprint(notas_fiscais_bp, url_prefix='/api')
app.register_blueprint(contas_pagar_bp, url_prefix='/api')
app.register_blueprint(comprovantes_bp, url_prefix='/api')
app.register_blueprint(conciliacao_bp, url_prefix='/api')

@app.route('/')
def index():
    """Página principal"""
    return send_from_directory('static', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    """Servir arquivos estáticos"""
    return send_from_directory('static', filename)

@app.route('/health')
def health():
    """Endpoint de saúde"""
    db_status = test_connection()
    return jsonify({
        'status': 'healthy' if db_status else 'unhealthy',
        'database': 'connected' if db_status else 'disconnected',
        'version': '2.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Erro interno: {error}")
    return jsonify({'error': 'Erro interno do servidor'}), 500

# Inicializar banco de dados
try:
    logger.info("Inicializando aplicação...")
    init_db()
    logger.info("Aplicação inicializada com sucesso!")
except Exception as e:
    logger.error(f"Erro ao inicializar aplicação: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Iniciando servidor na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)

