#!/usr/bin/env python3
"""
Script para instalar as dependências necessárias para o LinkedIn Profile Hunter
"""

import subprocess
import sys
import os
import shutil

def main():
    print("Instalando LinkedIn Profile Hunter...")
    
    # Instala o pacote em modo de desenvolvimento
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
    
    # Instala o navegador para o Playwright
    print("\nInstalando navegador para o Playwright...")
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
    
    # Cria arquivo .env a partir do .env.example se não existir
    if not os.path.exists(".env") and os.path.exists(".env.example"):
        print("\nCriando arquivo .env a partir do .env.example...")
        shutil.copy(".env.example", ".env")
        print("Arquivo .env criado. Por favor, edite-o com suas credenciais.")
    
    print("\nInstalação concluída com sucesso!")
    print("Para começar, edite o arquivo .env com suas credenciais.")
    print("Em seguida, execute um dos exemplos em examples/:")
    print("  python examples/basic_usage.py")
    print("  python examples/advanced_usage.py")

if __name__ == "__main__":
    main()
