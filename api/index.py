import os
import sys

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.main import app

# Esta é a função que o Vercel irá chamar
def handler(request):
    return app(request.environ, lambda status, headers: None)

# Para compatibilidade com Vercel
if __name__ == "__main__":
    app.run(debug=False)

