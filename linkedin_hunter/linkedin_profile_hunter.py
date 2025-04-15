"""
Classe principal do LinkedIn Profile Hunter
"""

import os
import asyncio
from typing import Dict, Any, Optional

from dotenv import load_dotenv

from .core.profile_finder import ProfileFinder
from .modules.profile_scraper import ProfileScraper
from .modules.profile_analyzer import ProfileAnalyzer
from .utils.confidence_calculator import ConfidenceCalculator
from .utils.error_handling import retry_async, RateLimiter
from .config.settings import (
    LINKEDIN_EMAIL,
    LINKEDIN_PASSWORD,
    GOOGLE_API_KEY,
    BROWSER_HEADLESS,
    SEARCH_STRATEGY,
    REQUESTS_PER_MINUTE,
    MAX_RETRIES,
    RETRY_DELAY,
    BACKOFF_FACTOR
)

# Carrega variáveis de ambiente
load_dotenv()

class LinkedInProfileHunter:
    """
    Interface principal para o LinkedIn Profile Hunter
    """
    
    def __init__(
        self,
        google_api_key: Optional[str] = None,
        linkedin_email: Optional[str] = None,
        linkedin_password: Optional[str] = None,
        headless: Optional[bool] = None,
        search_strategy: Optional[str] = None
    ):
        """
        Inicializa o LinkedIn Profile Hunter
        
        Args:
            google_api_key: Chave de API do Google para o Gemini
            linkedin_email: Email para login no LinkedIn
            linkedin_password: Senha para login no LinkedIn
            headless: Se True, executa o navegador em modo headless
            search_strategy: Estratégia de busca para o ProfileFinder
        """
        # Carrega configurações
        self.google_api_key = google_api_key or GOOGLE_API_KEY
        self.linkedin_email = linkedin_email or LINKEDIN_EMAIL
        self.linkedin_password = linkedin_password or LINKEDIN_PASSWORD
        self.headless = headless if headless is not None else BROWSER_HEADLESS
        self.search_strategy = search_strategy or SEARCH_STRATEGY
        
        # Cria limitador de taxa compartilhado
        self.rate_limiter = RateLimiter(requests_per_minute=REQUESTS_PER_MINUTE)
        
        # Inicializa componentes
        self.profile_finder = ProfileFinder(
            search_strategy=self.search_strategy,
            headless=self.headless
        )
        
        self.profile_scraper = ProfileScraper(
            headless=self.headless,
            linkedin_email=self.linkedin_email,
            linkedin_password=self.linkedin_password
        )
        
        self.profile_analyzer = ProfileAnalyzer(
            api_key=self.google_api_key
        )
        
        self.confidence_calculator = ConfidenceCalculator()
    
    async def hunt_profile(self, name: str, email: str, company: str) -> Dict[str, Any]:
        """
        Busca, extrai e analisa o perfil do LinkedIn
        
        Args:
            name: Nome da pessoa
            email: E-mail da pessoa
            company: Empresa onde a pessoa trabalha
            
        Returns:
            Dict: Resultados estruturados conforme o formato solicitado
        """
        # Encontrar perfil
        print(f"Buscando perfil para: {name} ({email}) na empresa {company}...")
        
        # Aguarda limitação de taxa
        await self.rate_limiter.wait()
        
        # Função para busca com retry
        async def find_profile_with_retry():
            return await self.profile_finder.find_profile(name, email, company)
        
        # Executa a busca com retry
        profile_result = await retry_async(
            find_profile_with_retry,
            max_retries=MAX_RETRIES,
            retry_delay=RETRY_DELAY,
            backoff_factor=BACKOFF_FACTOR
        )
        
        profile_url = profile_result['url']
        
        if not profile_url:
            return {
                'Nome': name,
                'E-mail': email,
                'Empresa': company,
                'Confiabilidade': "0%",
                'LinkedIn': "Perfil não encontrado",
                'Cargo Atual': "N/A",
                'Experiência Anterior': [],
                'Formação': [],
                'Habilidades principais': [],
                'Análise do Perfil': "Não foi possível encontrar um perfil do LinkedIn correspondente aos dados fornecidos."
            }
        
        print(f"Perfil encontrado: {profile_url}")
        
        # Extrair dados do perfil
        print("Extraindo dados do perfil...")
        
        # Aguarda limitação de taxa
        await self.rate_limiter.wait()
        
        # Função para raspagem com retry
        async def scrape_profile_with_retry():
            return await self.profile_scraper.scrape_profile(profile_url)
        
        # Executa a raspagem com retry
        profile_data = await retry_async(
            scrape_profile_with_retry,
            max_retries=MAX_RETRIES,
            retry_delay=RETRY_DELAY,
            backoff_factor=BACKOFF_FACTOR
        )
        
        # Calcular confiabilidade
        print("Calculando confiabilidade...")
        input_data = {'name': name, 'email': email, 'company': company}
        confidence = self.confidence_calculator.calculate_confidence(input_data, profile_data)
        
        # Analisar perfil com IA
        print("Analisando perfil com IA...")
        
        # Aguarda limitação de taxa
        await self.rate_limiter.wait()
        
        # Função para análise com retry
        async def analyze_profile_with_retry():
            return await self.profile_analyzer.analyze_profile(profile_data)
        
        # Executa a análise com retry
        analysis = await retry_async(
            analyze_profile_with_retry,
            max_retries=MAX_RETRIES,
            retry_delay=RETRY_DELAY,
            backoff_factor=BACKOFF_FACTOR
        )
        
        # Formatar resultado final
        result = {
            'Nome': name,
            'E-mail': email,
            'Empresa': company,
            'Confiabilidade': f"{confidence}%",
            'LinkedIn': profile_url,
            'Cargo Atual': profile_data.get('headline', 'N/A'),
            'Experiência Anterior': profile_data.get('experience', []),
            'Formação': profile_data.get('education', []),
            'Habilidades principais': profile_data.get('skills', []),
            'Análise do Perfil': analysis
        }
        
        return result
    
    async def close(self):
        """
        Fecha os componentes e libera recursos
        """
        if hasattr(self, 'profile_scraper'):
            await self.profile_scraper.close()
        
        if hasattr(self, 'profile_finder') and hasattr(self.profile_finder, '_close_crawler'):
            await self.profile_finder._close_crawler()
