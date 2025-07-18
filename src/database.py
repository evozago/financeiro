import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL do banco de dados
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/financeiro')

# Se estiver no Vercel, usar a URL do Supabase
if os.getenv('VERCEL'):
    # URL do Supabase (será configurada nas variáveis de ambiente)
    DATABASE_URL = os.getenv('SUPABASE_DATABASE_URL', DATABASE_URL)

logger.info(f"Conectando ao banco: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'local'}")

# Criar engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Mudar para True para debug SQL
)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

def get_db():
    """Obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializar banco de dados"""
    try:
        logger.info("Criando tabelas do banco de dados...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tabelas criadas com sucesso!")
        
        # Criar dados iniciais
        create_initial_data()
        
    except Exception as e:
        logger.error(f"Erro ao inicializar banco: {e}")
        raise

def create_initial_data():
    """Criar dados iniciais"""
    from .models.financeiro import TipoDespesa
    
    db = SessionLocal()
    try:
        # Verificar se já existem tipos de despesa
        existing_types = db.query(TipoDespesa).count()
        
        if existing_types == 0:
            logger.info("Criando tipos de despesa iniciais...")
            
            tipos_iniciais = [
                {'nome': 'Fornecedores', 'descricao': 'Pagamentos a fornecedores de produtos e serviços'},
                {'nome': 'Água', 'descricao': 'Conta de água'},
                {'nome': 'Energia Elétrica', 'descricao': 'Conta de energia elétrica'},
                {'nome': 'Telefone/Internet', 'descricao': 'Contas de telefone e internet'},
                {'nome': 'Aluguel', 'descricao': 'Pagamento de aluguel'},
                {'nome': 'Folha de Pagamento', 'descricao': 'Salários e encargos trabalhistas'},
                {'nome': 'Material de Escritório', 'descricao': 'Compras de material de escritório'},
                {'nome': 'Combustível', 'descricao': 'Gastos com combustível'},
                {'nome': 'Manutenção', 'descricao': 'Serviços de manutenção'},
                {'nome': 'Impostos e Taxas', 'descricao': 'Pagamento de impostos e taxas governamentais'}
            ]
            
            for tipo_data in tipos_iniciais:
                tipo = TipoDespesa(**tipo_data, ativo=True)
                db.add(tipo)
            
            db.commit()
            logger.info(f"Criados {len(tipos_iniciais)} tipos de despesa iniciais")
        else:
            logger.info(f"Banco já possui {existing_types} tipos de despesa")
            
    except Exception as e:
        logger.error(f"Erro ao criar dados iniciais: {e}")
        db.rollback()
    finally:
        db.close()

def test_connection():
    """Testar conexão com o banco"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("Conexão com banco de dados OK!")
        return True
    except Exception as e:
        logger.error(f"Erro na conexão com banco: {e}")
        return False

