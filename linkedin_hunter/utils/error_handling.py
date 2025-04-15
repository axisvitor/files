"""
Utilitários para tratamento de erros e limitação de taxa
"""

import asyncio
import random
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, cast

# Tipo genérico para funções
F = TypeVar('F', bound=Callable[..., Any])

class RateLimiter:
    """
    Implementa limitação de taxa para evitar bloqueios do LinkedIn
    """
    
    def __init__(
        self,
        requests_per_minute: int = 10,
        jitter_min_ms: int = 500,
        jitter_max_ms: int = 2000
    ):
        """
        Inicializa o limitador de taxa
        
        Args:
            requests_per_minute: Número máximo de requisições por minuto
            jitter_min_ms: Tempo mínimo de jitter em milissegundos
            jitter_max_ms: Tempo máximo de jitter em milissegundos
        """
        self.requests_per_minute = requests_per_minute
        self.jitter_min_ms = jitter_min_ms
        self.jitter_max_ms = jitter_max_ms
        self.interval = 60.0 / requests_per_minute
        self.last_request_time = 0.0
    
    async def wait(self):
        """
        Espera o tempo necessário para respeitar o limite de taxa
        """
        # Calcula o tempo desde a última requisição
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        
        # Se não passou tempo suficiente, espera
        if elapsed < self.interval:
            wait_time = self.interval - elapsed
            await asyncio.sleep(wait_time)
        
        # Adiciona jitter para parecer mais humano
        jitter = random.randint(self.jitter_min_ms, self.jitter_max_ms) / 1000.0
        await asyncio.sleep(jitter)
        
        # Atualiza o tempo da última requisição
        self.last_request_time = time.time()

def rate_limited(limiter: Optional[RateLimiter] = None):
    """
    Decorador para limitar a taxa de chamadas de funções
    
    Args:
        limiter: Instância de RateLimiter a ser usada
        
    Returns:
        Função decorada com limitação de taxa
    """
    # Usa um limitador padrão se nenhum for fornecido
    _limiter = limiter or RateLimiter()
    
    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Espera conforme a limitação de taxa
            await _limiter.wait()
            
            # Executa a função original
            return await func(*args, **kwargs)
        
        return cast(F, wrapper)
    
    return decorator

class LinkedInScraperError(Exception):
    """Classe base para erros do raspador de LinkedIn"""
    pass

class AuthenticationError(LinkedInScraperError):
    """Erro de autenticação no LinkedIn"""
    pass

class RateLimitError(LinkedInScraperError):
    """Erro de limite de taxa excedido"""
    pass

class ProfileNotFoundError(LinkedInScraperError):
    """Erro de perfil não encontrado"""
    pass

class CompanyNotFoundError(LinkedInScraperError):
    """Erro de empresa não encontrada"""
    pass

class ScrapingError(LinkedInScraperError):
    """Erro genérico de raspagem"""
    pass

async def retry_async(
    func: Callable,
    max_retries: int = 3,
    retry_delay: float = 2.0,
    exceptions: tuple = (Exception,),
    backoff_factor: float = 2.0
) -> Any:
    """
    Tenta executar uma função assíncrona várias vezes antes de desistir
    
    Args:
        func: Função assíncrona a ser executada
        max_retries: Número máximo de tentativas
        retry_delay: Tempo de espera inicial entre tentativas (em segundos)
        exceptions: Exceções que devem ser capturadas para retry
        backoff_factor: Fator de multiplicação do tempo de espera a cada tentativa
        
    Returns:
        Resultado da função
        
    Raises:
        Exception: A última exceção capturada após todas as tentativas
    """
    last_exception = None
    delay = retry_delay
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            
            if attempt < max_retries:
                # Adiciona jitter para evitar sincronização
                jitter = random.uniform(0.8, 1.2)
                wait_time = delay * jitter
                
                print(f"Tentativa {attempt + 1} falhou. Tentando novamente em {wait_time:.2f}s...")
                await asyncio.sleep(wait_time)
                
                # Aumenta o tempo de espera para a próxima tentativa
                delay *= backoff_factor
            else:
                # Última tentativa falhou
                print(f"Todas as {max_retries + 1} tentativas falharam.")
                raise last_exception

def detect_linkedin_blocks(html: str) -> Dict[str, bool]:
    """
    Detecta diferentes tipos de bloqueios do LinkedIn no HTML
    
    Args:
        html: Conteúdo HTML da página
        
    Returns:
        Dict[str, bool]: Dicionário indicando os tipos de bloqueio detectados
    """
    blocks = {
        "rate_limit": False,
        "captcha": False,
        "login_required": False,
        "account_restricted": False,
        "not_found": False
    }
    
    # Detecta limite de taxa
    rate_limit_patterns = [
        "você atingiu o limite de visualizações",
        "you've reached the limit of profile views",
        "please try again later",
        "tente novamente mais tarde"
    ]
    
    # Detecta CAPTCHA
    captcha_patterns = [
        "captcha",
        "verificação de segurança",
        "security verification",
        "prove you're a human"
    ]
    
    # Detecta necessidade de login
    login_patterns = [
        "entrar para ver",
        "sign in to view",
        "join now to view",
        "cadastre-se para ver"
    ]
    
    # Detecta conta restrita
    restricted_patterns = [
        "sua conta foi restrita",
        "your account has been restricted",
        "unusual activity",
        "atividade incomum"
    ]
    
    # Detecta página não encontrada
    not_found_patterns = [
        "página não encontrada",
        "page not found",
        "this page doesn't exist",
        "esta página não existe"
    ]
    
    html_lower = html.lower()
    
    # Verifica cada tipo de bloqueio
    for pattern in rate_limit_patterns:
        if pattern.lower() in html_lower:
            blocks["rate_limit"] = True
            break
    
    for pattern in captcha_patterns:
        if pattern.lower() in html_lower:
            blocks["captcha"] = True
            break
    
    for pattern in login_patterns:
        if pattern.lower() in html_lower:
            blocks["login_required"] = True
            break
    
    for pattern in restricted_patterns:
        if pattern.lower() in html_lower:
            blocks["account_restricted"] = True
            break
    
    for pattern in not_found_patterns:
        if pattern.lower() in html_lower:
            blocks["not_found"] = True
            break
    
    return blocks
