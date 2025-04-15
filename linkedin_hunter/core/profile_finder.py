"""
Módulo para localizar perfis do LinkedIn a partir de dados básicos
"""

import asyncio
import re
import urllib.parse
from typing import Dict, Optional, Any, List, Tuple

from crawl4ai import AsyncWebCrawler
from crawl4ai.config import BrowserConfig, CrawlerConfig

class ProfileFinder:
    """
    Componente para localizar perfis do LinkedIn a partir de dados básicos
    """
    
    def __init__(
        self,
        search_strategy: str = "google",
        headless: bool = True,
        timeout: int = 30000,
    ):
        """
        Inicializa o localizador de perfis
        
        Args:
            search_strategy: Estratégia de busca a ser utilizada ("google", "bing", "direct")
            headless: Se True, executa o navegador em modo headless
            timeout: Tempo limite para carregamento de páginas em milissegundos
        """
        self.search_strategy = search_strategy
        self.headless = headless
        self.timeout = timeout
        
        # Configuração do navegador
        self.browser_config = BrowserConfig(
            headless=self.headless,
            timeout=self.timeout,
        )
        
        # Configuração do crawler
        self.crawler_config = CrawlerConfig(
            browser=self.browser_config,
        )
        
        # Crawler assíncrono
        self.crawler = None
    
    async def _initialize_crawler(self):
        """
        Inicializa o crawler assíncrono
        """
        if self.crawler is None:
            self.crawler = AsyncWebCrawler(config=self.crawler_config)
            await self.crawler.start()
    
    async def find_profile(self, name: str, email: str, company: str) -> Dict[str, Any]:
        """
        Localiza o perfil do LinkedIn com base nos dados fornecidos
        
        Args:
            name: Nome da pessoa
            email: E-mail da pessoa
            company: Empresa onde a pessoa trabalha
            
        Returns:
            Dict: Contendo URL do perfil e score de confiança inicial
        """
        # Inicializa o crawler
        await self._initialize_crawler()
        
        # Escolhe a estratégia de busca
        if self.search_strategy == "google":
            profile_url, initial_confidence = await self._search_with_google(name, email, company)
        elif self.search_strategy == "bing":
            profile_url, initial_confidence = await self._search_with_bing(name, email, company)
        elif self.search_strategy == "direct":
            profile_url, initial_confidence = await self._search_direct(name, email, company)
        else:
            raise ValueError(f"Estratégia de busca inválida: {self.search_strategy}")
        
        # Fecha o crawler
        await self._close_crawler()
        
        return {
            "url": profile_url,
            "initial_confidence": initial_confidence
        }
    
    async def _search_with_google(self, name: str, email: str, company: str) -> Tuple[str, float]:
        """
        Busca o perfil usando o Google
        
        Args:
            name: Nome da pessoa
            email: E-mail da pessoa
            company: Empresa onde a pessoa trabalha
            
        Returns:
            Tuple[str, float]: URL do perfil e confiança inicial
        """
        # Constrói a query de busca
        query = f"{name} {company} site:linkedin.com/in"
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        # Executa a busca
        result = await self.crawler.arun(url=search_url)
        
        # Extrai os resultados
        linkedin_urls = self._extract_linkedin_profile_urls(result.html)
        
        if linkedin_urls:
            # Retorna o primeiro resultado com confiança alta
            return linkedin_urls[0], 0.8
        
        # Se não encontrou, tenta uma busca mais específica com o email
        username = email.split('@')[0]
        query = f"{name} {username} {company} site:linkedin.com/in"
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        
        # Executa a busca
        result = await self.crawler.arun(url=search_url)
        
        # Extrai os resultados
        linkedin_urls = self._extract_linkedin_profile_urls(result.html)
        
        if linkedin_urls:
            # Retorna o primeiro resultado com confiança média
            return linkedin_urls[0], 0.6
        
        # Se ainda não encontrou, retorna vazio
        return "", 0.0
    
    async def _search_with_bing(self, name: str, email: str, company: str) -> Tuple[str, float]:
        """
        Busca o perfil usando o Bing
        
        Args:
            name: Nome da pessoa
            email: E-mail da pessoa
            company: Empresa onde a pessoa trabalha
            
        Returns:
            Tuple[str, float]: URL do perfil e confiança inicial
        """
        # Constrói a query de busca
        query = f"{name} {company} site:linkedin.com/in"
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.bing.com/search?q={encoded_query}"
        
        # Executa a busca
        result = await self.crawler.arun(url=search_url)
        
        # Extrai os resultados
        linkedin_urls = self._extract_linkedin_profile_urls(result.html)
        
        if linkedin_urls:
            # Retorna o primeiro resultado com confiança alta
            return linkedin_urls[0], 0.8
        
        # Se não encontrou, tenta uma busca mais específica com o email
        username = email.split('@')[0]
        query = f"{name} {username} {company} site:linkedin.com/in"
        encoded_query = urllib.parse.quote(query)
        search_url = f"https://www.bing.com/search?q={encoded_query}"
        
        # Executa a busca
        result = await self.crawler.arun(url=search_url)
        
        # Extrai os resultados
        linkedin_urls = self._extract_linkedin_profile_urls(result.html)
        
        if linkedin_urls:
            # Retorna o primeiro resultado com confiança média
            return linkedin_urls[0], 0.6
        
        # Se ainda não encontrou, retorna vazio
        return "", 0.0
    
    async def _search_direct(self, name: str, email: str, company: str) -> Tuple[str, float]:
        """
        Tenta construir a URL do perfil diretamente
        
        Args:
            name: Nome da pessoa
            email: E-mail da pessoa
            company: Empresa onde a pessoa trabalha
            
        Returns:
            Tuple[str, float]: URL do perfil e confiança inicial
        """
        # Extrai o nome de usuário do email
        username = email.split('@')[0]
        
        # Tenta algumas variações comuns de URLs do LinkedIn
        possible_urls = []
        
        # Formato: nome-sobrenome
        name_parts = name.lower().split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = name_parts[-1]
            possible_urls.append(f"https://www.linkedin.com/in/{first_name}-{last_name}")
        
        # Formato: username do email
        possible_urls.append(f"https://www.linkedin.com/in/{username}")
        
        # Formato: nome.sobrenome
        if len(name_parts) >= 2:
            possible_urls.append(f"https://www.linkedin.com/in/{first_name}.{last_name}")
        
        # Tenta cada URL possível
        for url in possible_urls:
            try:
                result = await self.crawler.arun(url=url)
                
                # Verifica se a página existe e contém o nome da pessoa
                if name.lower() in result.title.lower() and "linkedin.com/in/" in result.url:
                    # Encontrou o perfil
                    return result.url, 0.5
            except Exception:
                # Ignora erros e continua tentando
                continue
        
        # Se não encontrou nenhum perfil, retorna vazio
        return "", 0.0
    
    def _extract_linkedin_profile_urls(self, html: str) -> List[str]:
        """
        Extrai URLs de perfis do LinkedIn do HTML
        
        Args:
            html: Conteúdo HTML da página
            
        Returns:
            List[str]: Lista de URLs de perfis do LinkedIn
        """
        # Padrão para URLs de perfil do LinkedIn nos resultados de busca
        pattern = r'https?://(?:www\.)?linkedin\.com/in/[\w\-]+/?[^"\'\s]*'
        matches = re.findall(pattern, html)
        
        # Remove duplicatas e retorna
        return list(dict.fromkeys(matches))
    
    async def _close_crawler(self):
        """
        Fecha o crawler e libera recursos
        """
        if self.crawler:
            await self.crawler.close()
            self.crawler = None
