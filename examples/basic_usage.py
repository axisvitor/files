"""
Exemplo básico de uso do LinkedIn Profile Hunter
"""

import asyncio
import json
import os
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path para importação dos módulos
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_hunter.linkedin_profile_hunter import LinkedInProfileHunter

# Carrega variáveis de ambiente
load_dotenv()

async def main():
    # Inicializa o LinkedIn Profile Hunter
    hunter = LinkedInProfileHunter(
        # Você pode fornecer as credenciais diretamente ou via variáveis de ambiente
        # linkedin_email="seu-email@exemplo.com",
        # linkedin_password="sua-senha",
        # google_api_key="sua-chave-api-google",
        headless=False  # False para visualizar o navegador durante a execução
    )
    
    try:
        # Dados da pessoa para busca
        name = "Vagner Campos"
        email = "vagner.campos@arduus.tech"
        company = "Arduus Ventures"
        
        print(f"Iniciando busca para: {name} ({email}) na empresa {company}")
        
        # Executa a busca, extração e análise
        result = await hunter.hunt_profile(name, email, company)
        
        # Exibe o resultado
        print("\n=== RESULTADO ===\n")
        print(f"Nome: {result['Nome']}")
        print(f"E-mail: {result['E-mail']}")
        print(f"Empresa: {result['Empresa']}")
        print(f"Confiabilidade: {result['Confiabilidade']}")
        print(f"LinkedIn: {result['LinkedIn']}")
        print(f"Cargo Atual: {result['Cargo Atual']}")
        
        print("\nExperiência Anterior:")
        for exp in result['Experiência Anterior']:
            print(f"- {exp.get('title', 'N/A')} em {exp.get('company', 'N/A')}, {exp.get('duration', 'N/A')}")
        
        print("\nFormação:")
        for edu in result['Formação']:
            print(f"- {edu.get('degree', 'N/A')} em {edu.get('institution', 'N/A')}, {edu.get('duration', 'N/A')}")
        
        print("\nHabilidades principais:")
        print(", ".join(result['Habilidades principais']))
        
        print("\nAnálise do Perfil:")
        print(result['Análise do Perfil'])
        
        # Salva o resultado em um arquivo JSON
        with open("profile_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("\nResultado salvo em profile_result.json")
        
    except Exception as e:
        print(f"Erro durante a execução: {e}")
    
    finally:
        # Fecha o hunter e libera recursos
        await hunter.close()
        print("Recursos liberados")

if __name__ == "__main__":
    # Executa o exemplo
    asyncio.run(main())
