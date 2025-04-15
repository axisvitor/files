"""
Exemplo avançado de uso do LinkedIn Profile Hunter com múltiplas buscas
"""

import asyncio
import json
import os
import time
from dotenv import load_dotenv

# Adiciona o diretório raiz ao path para importação dos módulos
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linkedin_hunter.linkedin_profile_hunter import LinkedInProfileHunter
from linkedin_hunter.utils.error_handling import RateLimiter

# Carrega variáveis de ambiente
load_dotenv()

async def process_person(hunter, name, email, company, output_dir):
    """
    Processa uma pessoa e salva o resultado
    
    Args:
        hunter: Instância do LinkedInProfileHunter
        name: Nome da pessoa
        email: E-mail da pessoa
        company: Empresa da pessoa
        output_dir: Diretório para salvar os resultados
    """
    try:
        print(f"\nProcessando: {name} ({email}) na empresa {company}")
        
        # Executa a busca, extração e análise
        start_time = time.time()
        result = await hunter.hunt_profile(name, email, company)
        elapsed_time = time.time() - start_time
        
        print(f"Processamento concluído em {elapsed_time:.2f} segundos")
        print(f"Confiabilidade: {result['Confiabilidade']}")
        print(f"LinkedIn: {result['LinkedIn']}")
        
        # Cria nome de arquivo baseado no nome da pessoa
        safe_name = name.replace(" ", "_").lower()
        filename = f"{safe_name}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Salva o resultado em um arquivo JSON
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"Resultado salvo em {filepath}")
        
        return result
        
    except Exception as e:
        print(f"Erro ao processar {name}: {e}")
        return None

async def main():
    # Cria diretório para resultados
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    
    # Inicializa o LinkedIn Profile Hunter
    hunter = LinkedInProfileHunter(
        headless=True  # True para execução sem interface gráfica
    )
    
    try:
        # Lista de pessoas para buscar
        people = [
            {
                "name": "Vagner Campos",
                "email": "vagner.campos@arduus.tech",
                "company": "Arduus Ventures"
            },
            {
                "name": "Satya Nadella",
                "email": "satya.nadella@microsoft.com",
                "company": "Microsoft"
            },
            {
                "name": "Sundar Pichai",
                "email": "sundar.pichai@google.com",
                "company": "Google"
            }
        ]
        
        print(f"Iniciando processamento de {len(people)} pessoas...")
        
        # Processa cada pessoa sequencialmente
        results = []
        for person in people:
            result = await process_person(
                hunter,
                person["name"],
                person["email"],
                person["company"],
                output_dir
            )
            if result:
                results.append(result)
        
        # Salva um resumo de todos os resultados
        summary = [{
            "Nome": r["Nome"],
            "E-mail": r["E-mail"],
            "Empresa": r["Empresa"],
            "Confiabilidade": r["Confiabilidade"],
            "LinkedIn": r["LinkedIn"],
            "Cargo Atual": r["Cargo Atual"]
        } for r in results]
        
        with open(os.path.join(output_dir, "summary.json"), "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\nProcessamento concluído. {len(results)} perfis encontrados.")
        print(f"Resumo salvo em {os.path.join(output_dir, 'summary.json')}")
        
    except Exception as e:
        print(f"Erro durante a execução: {e}")
    
    finally:
        # Fecha o hunter e libera recursos
        await hunter.close()
        print("Recursos liberados")

if __name__ == "__main__":
    # Executa o exemplo
    asyncio.run(main())
