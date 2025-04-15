"""
Módulo para gerenciamento de proxies e user-agents
"""

import os
import json
import random
import logging
import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple, Any

class ProxyManager:
    """
    Gerenciador de proxies para evitar bloqueios do LinkedIn
    """
    
    # Lista de User-Agents comuns
    USER_AGENTS = [
        # Chrome em Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
        
        # Firefox em Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
        
        # Edge em Windows
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38",
        
        # Safari em macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
        
        # Chrome em macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        
        # Firefox em macOS
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:92.0) Gecko/20100101 Firefox/92.0",
        
        # Chrome em Linux
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        
        # Firefox em Linux
        "Mozilla/5.0 (X11; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
        "Mozilla/5.0 (X11; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
        
        # Mobile - Android
        "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; SM-G998U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.115 Mobile Safari/537.36",
        
        # Mobile - iOS
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    ]
    
    def __init__(
        self,
        proxies_file: Optional[str] = None,
        test_proxies: bool = True,
        rotate_user_agent: bool = True,
        max_failures: int = 3
    ):
        """
        Inicializa o gerenciador de proxies
        
        Args:
            proxies_file: Caminho para o arquivo JSON com lista de proxies
            test_proxies: Se True, testa os proxies antes de usá-los
            rotate_user_agent: Se True, rotaciona os user-agents
            max_failures: Número máximo de falhas antes de marcar um proxy como inválido
        """
        self.proxies_file = proxies_file
        self.test_proxies = test_proxies
        self.rotate_user_agent = rotate_user_agent
        self.max_failures = max_failures
        
        # Inicializa as listas de proxies
        self.proxies: List[Dict[str, Any]] = []
        self.working_proxies: List[Dict[str, Any]] = []
        self.failed_proxies: List[Dict[str, Any]] = []
        
        # Proxy atual
        self.current_proxy: Optional[Dict[str, Any]] = None
        
        # User-Agent atual
        self.current_user_agent: str = random.choice(self.USER_AGENTS)
        
        # Carrega os proxies do arquivo
        self._load_proxies()
    
    def _load_proxies(self) -> None:
        """
        Carrega a lista de proxies do arquivo
        """
        # Se não há arquivo de proxies, usa apenas rotação de user-agent
        if not self.proxies_file:
            logging.info("Nenhum arquivo de proxies fornecido. Usando apenas rotação de user-agent.")
            return
        
        # Verifica se o arquivo existe
        if not os.path.exists(self.proxies_file):
            logging.warning(f"Arquivo de proxies não encontrado: {self.proxies_file}")
            return
        
        try:
            # Carrega os proxies do arquivo
            with open(self.proxies_file, 'r') as f:
                proxies_data = json.load(f)
            
            # Verifica o formato dos dados
            if isinstance(proxies_data, list):
                self.proxies = proxies_data
            elif isinstance(proxies_data, dict) and 'proxies' in proxies_data:
                self.proxies = proxies_data['proxies']
            else:
                logging.error("Formato de arquivo de proxies inválido.")
                return
            
            # Inicializa os proxies
            for proxy in self.proxies:
                # Adiciona campos de controle se não existirem
                if 'failures' not in proxy:
                    proxy['failures'] = 0
                if 'last_used' not in proxy:
                    proxy['last_used'] = 0
                if 'success_count' not in proxy:
                    proxy['success_count'] = 0
            
            logging.info(f"Carregados {len(self.proxies)} proxies do arquivo.")
            
            # Testa os proxies se necessário
            if self.test_proxies and self.proxies:
                asyncio.create_task(self._test_proxies())
        
        except Exception as e:
            logging.error(f"Erro ao carregar proxies: {e}")
    
    async def _test_proxies(self) -> None:
        """
        Testa os proxies para verificar quais estão funcionando
        """
        logging.info("Testando proxies...")
        
        # Lista para armazenar as tarefas
        tasks = []
        
        # Cria uma tarefa para cada proxy
        for proxy in self.proxies:
            task = asyncio.create_task(self._test_proxy(proxy))
            tasks.append(task)
        
        # Aguarda todas as tarefas
        await asyncio.gather(*tasks)
        
        # Atualiza a lista de proxies funcionando
        self.working_proxies = [p for p in self.proxies if p['failures'] < self.max_failures]
        
        logging.info(f"{len(self.working_proxies)} proxies funcionando de {len(self.proxies)} testados.")
    
    async def _test_proxy(self, proxy: Dict[str, Any]) -> bool:
        """
        Testa um proxy específico
        
        Args:
            proxy: Dicionário com informações do proxy
            
        Returns:
            bool: True se o proxy está funcionando, False caso contrário
        """
        # URL de teste (LinkedIn)
        test_url = "https://www.linkedin.com/robots.txt"
        
        # Configura o proxy
        proxy_url = self._get_proxy_url(proxy)
        
        try:
            # Tenta acessar a URL de teste
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    test_url,
                    proxy=proxy_url,
                    timeout=10,
                    headers={"User-Agent": random.choice(self.USER_AGENTS)}
                ) as response:
                    # Verifica se a resposta foi bem-sucedida
                    if response.status == 200:
                        proxy['failures'] = 0
                        proxy['success_count'] += 1
                        return True
                    else:
                        proxy['failures'] += 1
                        return False
        
        except Exception:
            # Marca o proxy como falho
            proxy['failures'] += 1
            return False
    
    def _get_proxy_url(self, proxy: Dict[str, Any]) -> str:
        """
        Obtém a URL do proxy no formato adequado
        
        Args:
            proxy: Dicionário com informações do proxy
            
        Returns:
            str: URL do proxy
        """
        # Formato: protocol://username:password@host:port
        protocol = proxy.get('protocol', 'http')
        host = proxy.get('host', '')
        port = proxy.get('port', '')
        username = proxy.get('username', '')
        password = proxy.get('password', '')
        
        if username and password:
            return f"{protocol}://{username}:{password}@{host}:{port}"
        else:
            return f"{protocol}://{host}:{port}"
    
    def get_next_proxy(self) -> Optional[Dict[str, Any]]:
        """
        Obtém o próximo proxy da lista
        
        Returns:
            Optional[Dict[str, Any]]: Próximo proxy ou None se não houver proxies disponíveis
        """
        # Se não há proxies funcionando, retorna None
        if not self.working_proxies:
            return None
        
        # Seleciona o próximo proxy (o menos usado recentemente)
        self.working_proxies.sort(key=lambda p: (p['last_used'], p['failures']))
        self.current_proxy = self.working_proxies[0]
        
        # Atualiza o timestamp de uso
        self.current_proxy['last_used'] = asyncio.get_event_loop().time()
        
        return self.current_proxy
    
    def get_next_user_agent(self) -> str:
        """
        Obtém o próximo user-agent da lista
        
        Returns:
            str: Próximo user-agent
        """
        if self.rotate_user_agent:
            self.current_user_agent = random.choice(self.USER_AGENTS)
        
        return self.current_user_agent
    
    def mark_proxy_success(self, proxy: Dict[str, Any]) -> None:
        """
        Marca um proxy como bem-sucedido
        
        Args:
            proxy: Proxy a ser marcado
        """
        if not proxy:
            return
        
        proxy['failures'] = max(0, proxy['failures'] - 1)
        proxy['success_count'] += 1
    
    def mark_proxy_failure(self, proxy: Dict[str, Any]) -> None:
        """
        Marca um proxy como falho
        
        Args:
            proxy: Proxy a ser marcado
        """
        if not proxy:
            return
        
        proxy['failures'] += 1
        
        # Se excedeu o número máximo de falhas, move para a lista de falhos
        if proxy['failures'] >= self.max_failures:
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
                self.failed_proxies.append(proxy)
    
    def get_browser_config(self) -> Dict[str, Any]:
        """
        Obtém a configuração do navegador com proxy e user-agent
        
        Returns:
            Dict[str, Any]: Configuração do navegador
        """
        config = {}
        
        # Adiciona o user-agent
        config['user_agent'] = self.get_next_user_agent()
        
        # Adiciona o proxy se disponível
        proxy = self.get_next_proxy()
        if proxy:
            config['proxy'] = {
                'server': self._get_proxy_url(proxy)
            }
        
        return config
    
    def save_proxies_status(self) -> None:
        """
        Salva o status dos proxies no arquivo
        """
        if not self.proxies_file:
            return
        
        try:
            # Combina as listas de proxies
            all_proxies = self.working_proxies + self.failed_proxies
            
            # Salva no arquivo
            with open(self.proxies_file, 'w') as f:
                json.dump({'proxies': all_proxies}, f, indent=2)
            
            logging.info(f"Status dos proxies salvo em {self.proxies_file}")
        
        except Exception as e:
            logging.error(f"Erro ao salvar status dos proxies: {e}")
    
    async def rotate_proxy(self) -> Dict[str, Any]:
        """
        Rotaciona para o próximo proxy e user-agent
        
        Returns:
            Dict[str, Any]: Configuração do navegador com o novo proxy e user-agent
        """
        # Marca o proxy atual como falho
        if self.current_proxy:
            self.mark_proxy_failure(self.current_proxy)
        
        # Obtém o próximo proxy e user-agent
        return self.get_browser_config()
