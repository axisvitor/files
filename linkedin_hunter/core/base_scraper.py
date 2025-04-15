"""
Base Scraper para LinkedIn usando Crawl4AI
"""

import asyncio
import os
import json
import random
import logging
from typing import Dict, Optional, Any, List, Tuple

from crawl4ai import AsyncWebCrawler
from crawl4ai.config import BrowserConfig, CrawlerConfig
from dotenv import load_dotenv

from ..utils.human_interaction import HumanInteraction
from ..utils.block_detection import BlockDetector
from ..utils.proxy_manager import ProxyManager

load_dotenv()

class LinkedInBaseScraper:
    """
    Classe base para raspagem de dados do LinkedIn usando Crawl4AI
    """

    def __init__(
        self,
        headless: bool = True,
        use_stealth: bool = True,
        timeout: int = 30000,
        wait_for_selector: str = "body",
        linkedin_email: Optional[str] = None,
        linkedin_password: Optional[str] = None,
        cookies_path: Optional[str] = None,
        proxies_file: Optional[str] = None,
        rotate_user_agent: bool = True,
        test_proxies: bool = True,
    ):
        """
        Inicializa o raspador base do LinkedIn

        Args:
            headless: Se True, executa o navegador em modo headless (sem interface gráfica)
            use_stealth: Se True, usa técnicas de stealth para evitar detecção
            timeout: Tempo limite para carregamento de páginas em milissegundos
            wait_for_selector: Seletor CSS para aguardar antes de considerar a página carregada
            linkedin_email: Email para login no LinkedIn (opcional)
            linkedin_password: Senha para login no LinkedIn (opcional)
            cookies_path: Caminho para arquivo de cookies (opcional)
            proxies_file: Caminho para arquivo JSON com lista de proxies (opcional)
            rotate_user_agent: Se True, rotaciona os user-agents
            test_proxies: Se True, testa os proxies antes de usá-los
        """
        # Configura o logger se não estiver configurado
        if not logging.getLogger().handlers:
            logging.basicConfig(level=logging.INFO,
                              format='%(asctime)s - %(levelname)s - %(message)s')

        self.headless = headless
        self.use_stealth = use_stealth
        self.timeout = timeout
        self.wait_for_selector = wait_for_selector

        # Credenciais do LinkedIn
        self.linkedin_email = linkedin_email or os.getenv("LINKEDIN_EMAIL")
        self.linkedin_password = linkedin_password or os.getenv("LINKEDIN_PASSWORD")

        # Define o caminho para cookies
        if cookies_path is None:
            # Obtém o diretório do arquivo atual
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # Sobe dois níveis para chegar à raiz do projeto
            project_root = os.path.dirname(os.path.dirname(current_dir))
            # Define o caminho para o arquivo de cookies
            self.cookies_path = os.path.join(project_root, ".cookies")
        else:
            self.cookies_path = cookies_path

        # Inicializa o gerenciador de proxies
        self.proxy_manager = ProxyManager(
            proxies_file=proxies_file,
            test_proxies=test_proxies,
            rotate_user_agent=rotate_user_agent
        )

        # Obtém a configuração inicial do navegador
        proxy_config = self.proxy_manager.get_browser_config()

        # Configuração do navegador
        self.browser_config = BrowserConfig(
            headless=self.headless,
            use_stealth=self.use_stealth,
            timeout=self.timeout,
            wait_for_selector=self.wait_for_selector,
            user_agent=proxy_config.get('user_agent'),
            proxy=proxy_config.get('proxy')
        )

        # Configuração do crawler
        self.crawler_config = CrawlerConfig(
            browser=self.browser_config,
            wait_for_selector=self.wait_for_selector,
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

    async def _login(self, force_login: bool = False) -> bool:
        """
        Realiza login no LinkedIn

        Args:
            force_login: Se True, força novo login mesmo se já houver cookies

        Returns:
            bool: True se login bem-sucedido, False caso contrário
        """
        await self._initialize_crawler()

        # Verifica se já existe sessão válida
        if not force_login and await self._check_session():
            return True

        # Verifica se as credenciais estão disponíveis
        if not self.linkedin_email or not self.linkedin_password:
            raise ValueError("Credenciais do LinkedIn não fornecidas. Configure LINKEDIN_EMAIL e LINKEDIN_PASSWORD.")

        # Acessa página de login
        login_page = "https://www.linkedin.com/login"
        result = await self.crawler.arun(url=login_page)

        # Preenche formulário de login
        page = self.crawler.browser.page

        try:
            # Simula digitação humana para o email
            await HumanInteraction.human_like_typing(page, 'input#username', self.linkedin_email)

            # Pequena pausa antes de digitar a senha (como um humano faria)
            await asyncio.sleep(random.uniform(0.5, 1.5))

            # Simula digitação humana para a senha
            await HumanInteraction.human_like_typing(page, 'input#password', self.linkedin_password)

            # Pequena pausa antes de clicar no botão (como um humano faria)
            await asyncio.sleep(random.uniform(0.3, 0.8))

            # Clica no botão de login
            await page.click('button[type="submit"]')

            # Aguarda redirecionamento para a página inicial
            await page.wait_for_url("https://www.linkedin.com/feed/", timeout=self.timeout)

            # Salva cookies
            os.makedirs(os.path.dirname(self.cookies_path), exist_ok=True)
            await self._save_cookies()

            return True
        except Exception as e:
            print(f"Erro ao fazer login: {e}")
            return False

    async def _check_session(self) -> bool:
        """
        Verifica se a sessão atual é válida

        Returns:
            bool: True se a sessão for válida, False caso contrário
        """
        try:
            # Tenta carregar cookies se existirem
            if os.path.exists(self.cookies_path):
                await self._load_cookies()

            # Acessa feed do LinkedIn para verificar se está logado
            result = await self.crawler.arun(url="https://www.linkedin.com/feed/")
            page = self.crawler.browser.page

            # Verifica se está na página de feed (logado) ou na página de login/boas-vindas
            current_url = page.url
            if "linkedin.com/feed" in current_url:
                return True
            return False
        except Exception as e:
            print(f"Erro ao verificar sessão: {e}")
            return False

    async def _save_cookies(self):
        """
        Salva cookies da sessão atual
        """
        if self.crawler and self.crawler.browser and self.crawler.browser.context:
            cookies = await self.crawler.browser.context.cookies()
            os.makedirs(os.path.dirname(self.cookies_path), exist_ok=True)
            with open(self.cookies_path, 'w') as f:
                json.dump(cookies, f)

    async def _load_cookies(self):
        """
        Carrega cookies salvos
        """
        if os.path.exists(self.cookies_path) and self.crawler and self.crawler.browser and self.crawler.browser.context:
            with open(self.cookies_path, 'r') as f:
                cookies = json.load(f)
                await self.crawler.browser.context.add_cookies(cookies)

    async def _add_jitter(self, min_ms: int = 500, max_ms: int = 2000):
        """
        Adiciona um atraso aleatório para evitar detecção de automação

        Args:
            min_ms: Tempo mínimo de espera em milissegundos
            max_ms: Tempo máximo de espera em milissegundos
        """
        import random
        delay = random.randint(min_ms, max_ms) / 1000.0
        await asyncio.sleep(delay)

    async def _check_for_blocks(self, html: str, url: str) -> Dict[str, Any]:
        """
        Verifica se há bloqueios do LinkedIn na página

        Args:
            html: Conteúdo HTML da página
            url: URL da página

        Returns:
            Dict[str, Any]: Resultado da detecção de bloqueios

        Raises:
            Exception: Se um bloqueio crítico for detectado
        """
        # Detecta bloqueios
        detection_result = BlockDetector.detect_blocks(html, url)

        # Se não há bloqueios, retorna
        if not detection_result["is_blocked"]:
            return detection_result

        # Obtém ação recomendada
        action = BlockDetector.get_recommended_action(detection_result)

        # Registra o bloqueio
        logging.warning(f"Bloqueio detectado: {detection_result['block_types']}")
        logging.warning(f"Ação recomendada: {action['action']} - {action['message']}")

        # Trata o bloqueio de acordo com a ação recomendada
        if action["action"] == "stop":
            raise Exception(f"Bloqueio crítico: {action['message']}")

        elif action["action"] == "wait":
            wait_time = action["wait_time"]
            logging.info(f"Aguardando {wait_time} segundos antes de continuar...")
            await asyncio.sleep(wait_time)

        elif action["action"] == "login":
            logging.info("Tentando fazer login novamente...")
            await self._login(force_login=True)

        elif action["action"] == "change_proxy":
            # Rotaciona para o próximo proxy
            logging.info("Rotacionando para o próximo proxy...")
            await self._rotate_proxy()

            # Aguarda um tempo antes de continuar
            wait_time = min(action["wait_time"], 30)  # Máximo 30 segundos
            logging.info(f"Aguardando {wait_time} segundos antes de continuar...")
            await asyncio.sleep(wait_time)

        elif action["action"] == "manual_intervention":
            # Aqui você poderia implementar um sistema de notificação
            logging.error(f"Intervenção manual necessária: {action['message']}")
            raise Exception(f"Intervenção manual necessária: {action['message']}")

        return detection_result

    async def scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Método base para raspagem de dados

        Args:
            url: URL do LinkedIn para raspar
            **kwargs: Argumentos adicionais para o crawler

        Returns:
            Dict[str, Any]: Dados raspados
        """
        # Configura o logger se não estiver configurado
        if not logging.getLogger().handlers:
            logging.basicConfig(level=logging.INFO,
                              format='%(asctime)s - %(levelname)s - %(message)s')

        # Garante que o crawler está inicializado e logado
        await self._initialize_crawler()
        await self._login()

        # Adiciona jitter para evitar detecção
        await self._add_jitter()

        # Executa a raspagem
        result = await self.crawler.arun(url=url, **kwargs)

        # Verifica se há bloqueios
        await self._check_for_blocks(result.html, result.url)

        # Obtém a referência para a página
        page = self.crawler.browser.page

        # Verifica se é uma página de perfil
        is_profile_page = '/in/' in url

        # Simula comportamento humano na página
        await HumanInteraction.simulate_human_behavior(page, is_profile_page=is_profile_page)

        # Processa o resultado (implementado nas subclasses)
        return self._process_result(result)

    def _process_result(self, result):
        """
        Processa o resultado da raspagem (deve ser implementado nas subclasses)

        Args:
            result: Resultado da raspagem

        Returns:
            Dict[str, Any]: Dados processados
        """
        # Implementação básica, deve ser sobrescrita nas subclasses
        return {
            "url": result.url,
            "title": result.title,
            "markdown": result.markdown,
            "html": result.html,
        }

    async def _rotate_proxy(self):
        """
        Rotaciona para o próximo proxy e reinicia o crawler
        """
        # Obtém a nova configuração do proxy
        proxy_config = await self.proxy_manager.rotate_proxy()

        # Fecha o crawler atual se existir
        if self.crawler:
            await self.crawler.close()
            self.crawler = None

        # Atualiza a configuração do navegador
        self.browser_config = BrowserConfig(
            headless=self.headless,
            use_stealth=self.use_stealth,
            timeout=self.timeout,
            wait_for_selector=self.wait_for_selector,
            user_agent=proxy_config.get('user_agent'),
            proxy=proxy_config.get('proxy')
        )

        # Atualiza a configuração do crawler
        self.crawler_config = CrawlerConfig(
            browser=self.browser_config,
            wait_for_selector=self.wait_for_selector,
        )

        # Reinicializa o crawler
        await self._initialize_crawler()

        # Tenta fazer login novamente
        await self._login(force_login=True)

        logging.info(f"Proxy rotacionado. Novo User-Agent: {proxy_config.get('user_agent')[:30]}...")

    async def close(self):
        """
        Fecha o crawler e libera recursos
        """
        if self.crawler:
            await self.crawler.close()
            self.crawler = None

        # Salva o status dos proxies
        if hasattr(self, 'proxy_manager'):
            self.proxy_manager.save_proxies_status()
