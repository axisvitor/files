"""
Módulo para detecção avançada de bloqueios do LinkedIn
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from bs4 import BeautifulSoup

class BlockDetector:
    """
    Detector avançado de bloqueios e limitações do LinkedIn
    """
    
    # Padrões de texto para diferentes tipos de bloqueios
    PATTERNS = {
        # Bloqueio de limite de visualizações
        "rate_limit": [
            r"you've\s+reached\s+the\s+(?:weekly|monthly)?\s*(?:limit|maximum)",
            r"você\s+atingiu\s+o\s+(?:limite|máximo)\s+(?:semanal|mensal)?",
            r"you've\s+viewed\s+the\s+maximum\s+number\s+of\s+profiles",
            r"try\s+again\s+later",
            r"tente\s+novamente\s+mais\s+tarde",
            r"come\s+back\s+later\s+to\s+view\s+more\s+profiles",
        ],
        
        # CAPTCHA e verificações de segurança
        "security_check": [
            r"security\s+verification",
            r"verificação\s+de\s+segurança",
            r"prove\s+you're\s+a\s+person",
            r"prove\s+que\s+você\s+é\s+humano",
            r"captcha",
            r"are\s+you\s+a\s+robot",
            r"você\s+é\s+um\s+robô",
            r"unusual\s+activity",
            r"atividade\s+incomum",
        ],
        
        # Bloqueio de login
        "login_required": [
            r"please\s+log\s+in\s+to\s+continue",
            r"faça\s+login\s+para\s+continuar",
            r"join\s+now\s+to\s+view",
            r"cadastre-se\s+para\s+ver",
            r"sign\s+in\s+to\s+view",
            r"entrar\s+para\s+ver",
        ],
        
        # Conta restrita ou suspensa
        "account_restricted": [
            r"your\s+account\s+has\s+been\s+restricted",
            r"sua\s+conta\s+foi\s+restrita",
            r"account\s+temporarily\s+restricted",
            r"conta\s+temporariamente\s+restrita",
            r"suspicious\s+activity",
            r"atividade\s+suspeita",
            r"we've\s+noticed\s+some\s+unusual\s+activity",
            r"notamos\s+alguma\s+atividade\s+incomum",
        ],
        
        # Página não encontrada
        "not_found": [
            r"page\s+not\s+found",
            r"página\s+não\s+encontrada",
            r"this\s+page\s+doesn't\s+exist",
            r"esta\s+página\s+não\s+existe",
            r"hmm,\s+we\s+can't\s+reach\s+this\s+page",
            r"hmm,\s+não\s+conseguimos\s+acessar\s+esta\s+página",
        ],
        
        # Perfil privado ou fora da rede
        "private_profile": [
            r"this\s+profile\s+is\s+not\s+available",
            r"este\s+perfil\s+não\s+está\s+disponível",
            r"out\s+of\s+your\s+network",
            r"fora\s+da\s+sua\s+rede",
            r"to\s+see\s+this\s+profile,\s+upgrade\s+to\s+premium",
            r"para\s+ver\s+este\s+perfil,\s+atualize\s+para\s+o\s+premium",
        ],
        
        # Bloqueio temporário de IP
        "ip_block": [
            r"we've\s+detected\s+unusual\s+activity\s+from\s+your\s+network",
            r"detectamos\s+atividade\s+incomum\s+da\s+sua\s+rede",
            r"your\s+IP\s+address\s+has\s+been\s+temporarily\s+blocked",
            r"seu\s+endereço\s+IP\s+foi\s+temporariamente\s+bloqueado",
            r"too\s+many\s+requests",
            r"muitas\s+solicitações",
        ],
    }
    
    # Elementos HTML que indicam bloqueios
    HTML_INDICATORS = {
        "rate_limit": [
            ".limit-reached",
            ".search-limit",
            ".limit-hit",
            "[data-test-limit-reached]",
        ],
        
        "security_check": [
            ".challenge",
            ".captcha-container",
            "#captcha",
            ".security-verification",
            "[data-test-security-check]",
        ],
        
        "login_required": [
            ".login-form",
            ".join-form",
            ".sign-in-card",
            "[data-test-login-required]",
        ],
        
        "account_restricted": [
            ".restricted-account",
            ".account-suspended",
            "[data-test-account-restricted]",
        ],
        
        "not_found": [
            ".not-found",
            ".error-404",
            "[data-test-404]",
            ".page-not-found",
        ],
        
        "private_profile": [
            ".private-profile",
            ".out-of-network",
            "[data-test-private-profile]",
        ],
        
        "ip_block": [
            ".ip-restricted",
            ".too-many-requests",
            "[data-test-ip-block]",
        ],
    }
    
    # URLs que indicam bloqueios
    URL_INDICATORS = {
        "security_check": [
            r"checkpoint/challenge",
            r"security/check",
            r"captcha",
        ],
        
        "login_required": [
            r"linkedin.com/login",
            r"linkedin.com/checkpoint",
        ],
        
        "account_restricted": [
            r"linkedin.com/checkpoint/restricted",
            r"linkedin.com/suspended",
        ],
        
        "not_found": [
            r"linkedin.com/404",
            r"linkedin.com/pub/error",
        ],
    }
    
    @classmethod
    def detect_blocks(cls, html: str, url: str) -> Dict[str, bool]:
        """
        Detecta diferentes tipos de bloqueios do LinkedIn
        
        Args:
            html: Conteúdo HTML da página
            url: URL da página
            
        Returns:
            Dict[str, bool]: Dicionário indicando os tipos de bloqueio detectados
        """
        blocks = {block_type: False for block_type in cls.PATTERNS.keys()}
        
        # Verifica bloqueios baseados no texto
        cls._check_text_patterns(html, blocks)
        
        # Verifica bloqueios baseados em elementos HTML
        cls._check_html_elements(html, blocks)
        
        # Verifica bloqueios baseados na URL
        cls._check_url_patterns(url, blocks)
        
        # Verifica bloqueios baseados em redirecionamentos
        cls._check_redirects(url, blocks)
        
        # Adiciona detalhes sobre o bloqueio
        block_details = cls._get_block_details(html, blocks)
        
        # Resultado final
        result = {
            "is_blocked": any(blocks.values()),
            "block_types": [k for k, v in blocks.items() if v],
            "details": block_details
        }
        
        return result
    
    @classmethod
    def _check_text_patterns(cls, html: str, blocks: Dict[str, bool]) -> None:
        """
        Verifica padrões de texto que indicam bloqueios
        
        Args:
            html: Conteúdo HTML da página
            blocks: Dicionário de bloqueios a ser atualizado
        """
        html_lower = html.lower()
        
        for block_type, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, html_lower, re.IGNORECASE):
                    blocks[block_type] = True
                    break
    
    @classmethod
    def _check_html_elements(cls, html: str, blocks: Dict[str, bool]) -> None:
        """
        Verifica elementos HTML que indicam bloqueios
        
        Args:
            html: Conteúdo HTML da página
            blocks: Dicionário de bloqueios a ser atualizado
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            for block_type, selectors in cls.HTML_INDICATORS.items():
                for selector in selectors:
                    if soup.select(selector):
                        blocks[block_type] = True
                        break
        except Exception:
            # Ignora erros de parsing
            pass
    
    @classmethod
    def _check_url_patterns(cls, url: str, blocks: Dict[str, bool]) -> None:
        """
        Verifica padrões de URL que indicam bloqueios
        
        Args:
            url: URL da página
            blocks: Dicionário de bloqueios a ser atualizado
        """
        url_lower = url.lower()
        
        for block_type, patterns in cls.URL_INDICATORS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower, re.IGNORECASE):
                    blocks[block_type] = True
                    break
    
    @classmethod
    def _check_redirects(cls, url: str, blocks: Dict[str, bool]) -> None:
        """
        Verifica redirecionamentos que indicam bloqueios
        
        Args:
            url: URL da página
            blocks: Dicionário de bloqueios a ser atualizado
        """
        # Verifica se foi redirecionado para a página de login
        if "linkedin.com/login" in url and not blocks["login_required"]:
            blocks["login_required"] = True
        
        # Verifica se foi redirecionado para a página de checkpoint
        if "linkedin.com/checkpoint" in url and not blocks["security_check"]:
            blocks["security_check"] = True
    
    @classmethod
    def _get_block_details(cls, html: str, blocks: Dict[str, bool]) -> Dict[str, Any]:
        """
        Obtém detalhes adicionais sobre o bloqueio
        
        Args:
            html: Conteúdo HTML da página
            blocks: Dicionário de bloqueios detectados
            
        Returns:
            Dict[str, Any]: Detalhes sobre o bloqueio
        """
        details = {}
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Tenta extrair mensagens de erro
            error_messages = []
            error_selectors = [
                ".error-message",
                ".alert-error",
                ".alert-warning",
                ".notification-text",
                ".message-body",
            ]
            
            for selector in error_selectors:
                elements = soup.select(selector)
                for element in elements:
                    if element.text.strip():
                        error_messages.append(element.text.strip())
            
            if error_messages:
                details["error_messages"] = error_messages
            
            # Tenta extrair tempo de espera para rate limits
            if blocks["rate_limit"]:
                wait_time_patterns = [
                    r"try\s+again\s+in\s+(\d+)\s+(minutes|hours|days)",
                    r"tente\s+novamente\s+em\s+(\d+)\s+(minutos|horas|dias)",
                ]
                
                for pattern in wait_time_patterns:
                    for text in error_messages:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            time_value = int(match.group(1))
                            time_unit = match.group(2)
                            details["wait_time"] = {
                                "value": time_value,
                                "unit": time_unit
                            }
                            break
        
        except Exception:
            # Ignora erros de parsing
            pass
        
        return details
    
    @classmethod
    def get_recommended_action(cls, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtém ações recomendadas com base no resultado da detecção
        
        Args:
            detection_result: Resultado da detecção de bloqueios
            
        Returns:
            Dict[str, Any]: Ações recomendadas
        """
        if not detection_result["is_blocked"]:
            return {"action": "continue", "wait_time": 0}
        
        block_types = detection_result["block_types"]
        
        # Prioriza os bloqueios mais graves
        if "account_restricted" in block_types:
            return {
                "action": "stop",
                "reason": "account_restricted",
                "message": "Conta restrita. Verifique manualmente sua conta do LinkedIn.",
                "wait_time": 86400  # 24 horas
            }
        
        if "ip_block" in block_types:
            return {
                "action": "change_proxy",
                "reason": "ip_block",
                "message": "IP bloqueado. Troque de proxy antes de continuar.",
                "wait_time": 3600  # 1 hora
            }
        
        if "security_check" in block_types:
            return {
                "action": "manual_intervention",
                "reason": "security_check",
                "message": "Verificação de segurança detectada. Intervenção manual necessária.",
                "wait_time": 1800  # 30 minutos
            }
        
        if "rate_limit" in block_types:
            wait_time = 3600  # 1 hora padrão
            
            # Verifica se há tempo de espera específico
            if "details" in detection_result and "wait_time" in detection_result["details"]:
                wait_info = detection_result["details"]["wait_time"]
                value = wait_info["value"]
                unit = wait_info["unit"]
                
                if "minute" in unit:
                    wait_time = value * 60
                elif "hour" in unit:
                    wait_time = value * 3600
                elif "day" in unit:
                    wait_time = value * 86400
            
            return {
                "action": "wait",
                "reason": "rate_limit",
                "message": "Limite de taxa atingido. Aguarde antes de continuar.",
                "wait_time": wait_time
            }
        
        if "login_required" in block_types:
            return {
                "action": "login",
                "reason": "login_required",
                "message": "Login necessário. Tente fazer login novamente.",
                "wait_time": 0
            }
        
        if "not_found" in block_types:
            return {
                "action": "skip",
                "reason": "not_found",
                "message": "Página não encontrada. Pule este perfil.",
                "wait_time": 0
            }
        
        if "private_profile" in block_types:
            return {
                "action": "skip",
                "reason": "private_profile",
                "message": "Perfil privado ou fora da rede. Pule este perfil.",
                "wait_time": 0
            }
        
        # Bloqueio genérico
        return {
            "action": "wait",
            "reason": "unknown_block",
            "message": "Bloqueio desconhecido detectado. Aguarde antes de continuar.",
            "wait_time": 1800  # 30 minutos
        }
