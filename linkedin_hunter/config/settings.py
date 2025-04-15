"""
Configurações para o LinkedIn Profile Hunter
"""

import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Credenciais do LinkedIn
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

# Chave de API do Google para o Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Configurações do navegador
BROWSER_HEADLESS = os.getenv("BROWSER_HEADLESS", "True").lower() in ("true", "1", "t")
BROWSER_TIMEOUT = int(os.getenv("BROWSER_TIMEOUT", "30000"))

# Configurações de limitação de taxa
REQUESTS_PER_MINUTE = int(os.getenv("REQUESTS_PER_MINUTE", "5"))
JITTER_MIN_MS = int(os.getenv("JITTER_MIN_MS", "500"))
JITTER_MAX_MS = int(os.getenv("JITTER_MAX_MS", "2000"))

# Configurações de retry
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "5.0"))
BACKOFF_FACTOR = float(os.getenv("BACKOFF_FACTOR", "2.0"))

# Estratégia de busca para o ProfileFinder
SEARCH_STRATEGY = os.getenv("SEARCH_STRATEGY", "google")  # Opções: "google", "bing", "direct"
