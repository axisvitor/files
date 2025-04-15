# LinkedIn Profile Hunter

Uma aplicação em Python que busca, analisa e extrai informações profissionais de uma pessoa a partir de dados básicos como nome, e-mail e empresa.

## Visão Geral

O LinkedIn Profile Hunter é uma ferramenta que:

1. Localiza perfis do LinkedIn com base em dados básicos (nome, e-mail, empresa)
2. Extrai informações detalhadas do perfil encontrado
3. Calcula um score de confiabilidade para a correspondência
4. Gera uma análise concisa do perfil usando IA (Gemini 2.0)
5. Apresenta os resultados de forma estruturada

## Características

- **Busca Inteligente**: Utiliza múltiplas estratégias para localizar o perfil correto
- **Extração Robusta**: Obtém dados detalhados de perfis do LinkedIn
- **Análise com IA**: Utiliza o modelo Gemini 2.0 Flash Thinking para análise de perfis
- **Cálculo de Confiabilidade**: Avalia a probabilidade de o perfil encontrado ser da pessoa buscada
- **Arquitetura Modular**: Componentes independentes e substituíveis
- **Tratamento de Erros**: Mecanismos robustos para lidar com falhas e exceções
- **Limitação de Taxa**: Controle de requisições para evitar bloqueios
- **Interações Humanas**: Simulação de comportamento humano com rolagem, movimentos do mouse e cliques aleatórios

## Requisitos

- Python 3.8+
- Bibliotecas (ver `requirements.txt`):
  - crawl4ai
  - playwright
  - pandas
  - beautifulsoup4
  - python-dotenv
  - google-generativeai
  - fuzzywuzzy
  - pytest (para testes)

## Instalação

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/linkedin-profile-hunter.git
cd linkedin-profile-hunter
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Instale o navegador necessário para o Playwright:

```bash
python -m playwright install chromium
```

4. Configure as variáveis de ambiente:

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite o arquivo .env com suas credenciais
# LINKEDIN_EMAIL=seu-email@exemplo.com
# LINKEDIN_PASSWORD=sua-senha
# GOOGLE_API_KEY=sua-chave-api-google
```

## Arquitetura

O projeto segue uma arquitetura modular com os seguintes componentes:

### Core
- **ProfileFinder**: Localiza perfis do LinkedIn a partir de dados básicos
- **BaseScraper**: Classe base para raspagem de dados do LinkedIn

### Modules
- **ProfileScraper**: Extrai dados detalhados de perfis do LinkedIn
- **ProfileAnalyzer**: Analisa perfis usando o modelo Gemini 2.0

### Utils
- **ConfidenceCalculator**: Calcula a confiabilidade da correspondência
- **ErrorHandling**: Mecanismos para tratamento de erros e limitação de taxa

### Config
- **Settings**: Configurações centralizadas do aplicativo

## Estrutura do Projeto

```text
linkedin_hunter/
├── __init__.py
├── linkedin_profile_hunter.py
├── core/
│   ├── __init__.py
│   ├── base_scraper.py
│   └── profile_finder.py
├── modules/
│   ├── __init__.py
│   ├── profile_scraper.py
│   └── profile_analyzer.py
├── utils/
│   ├── __init__.py
│   ├── error_handling.py
│   └── confidence_calculator.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── tests/
│   ├── __init__.py
│   ├── test_profile_finder.py
│   ├── test_profile_scraper.py
│   └── test_profile_analyzer.py
├── examples/
│   ├── basic_usage.py
│   └── advanced_usage.py
├── .env.example
├── .env
├── requirements.txt
└── README.md
```

## Uso

### Raspagem de Perfis

```python
import asyncio
from linkedin_scraper.modules.profile_scraper import ProfileScraper

async def main():
    # Inicializa o raspador de perfis
    scraper = ProfileScraper(
        headless=True,  # True para executar sem interface gráfica
        linkedin_email="seu-email@exemplo.com",
        linkedin_password="sua-senha"
    )

    try:
        # URL do perfil do LinkedIn
        profile_url = "https://www.linkedin.com/in/nome-do-perfil/"

        # Raspa os dados do perfil
        profile_data = await scraper.scrape_profile(profile_url)

        # Processa os dados
        print(profile_data)

    finally:
        # Fecha o raspador e libera recursos
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Raspagem de Empresas

```python
import asyncio
from linkedin_scraper.modules.company_scraper import CompanyScraper

async def main():
    # Inicializa o raspador de empresas
    scraper = CompanyScraper(
        headless=True,  # True para executar sem interface gráfica
        linkedin_email="seu-email@exemplo.com",
        linkedin_password="sua-senha"
    )

    try:
        # URL da empresa no LinkedIn
        company_url = "https://www.linkedin.com/company/nome-da-empresa/"

        # Raspa os dados da empresa
        company_data = await scraper.scrape_company(company_url)

        # Obtém lista de funcionários
        employees = await scraper.get_employees(company_url, max_employees=50)

        # Processa os dados
        print(company_data)
        print(f"Funcionários encontrados: {len(employees)}")

    finally:
        # Fecha o raspador e libera recursos
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Uso com Tratamento de Erros e Limitação de Taxa

```python
import asyncio
from linkedin_scraper.modules.profile_scraper import ProfileScraper
from linkedin_scraper.utils.error_handling import retry_async, RateLimiter

async def main():
    # Cria um limitador de taxa
    rate_limiter = RateLimiter(requests_per_minute=5)

    # Inicializa o raspador
    scraper = ProfileScraper(
        headless=True,
        linkedin_email="seu-email@exemplo.com",
        linkedin_password="sua-senha"
    )

    try:
        # URL do perfil
        profile_url = "https://www.linkedin.com/in/nome-do-perfil/"

        # Aguarda limitação de taxa
        await rate_limiter.wait()

        # Função para raspagem com retry
        async def scrape_with_retry():
            return await scraper.scrape_profile(profile_url)

        # Executa com retry e backoff exponencial
        profile_data = await retry_async(
            scrape_with_retry,
            max_retries=3,
            retry_delay=5.0,
            backoff_factor=2.0
        )

        # Processa os dados
        print(profile_data)

    finally:
        # Fecha o raspador
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## Exemplos Completos

O diretório `examples/` contém exemplos completos de uso:

- `profile_example.py`: Demonstra a raspagem de perfis
- `company_example.py`: Demonstra a raspagem de empresas e funcionários
- `complete_example.py`: Exemplo completo com tratamento de erros e limitação de taxa

Para executar os exemplos:

```bash
# Certifique-se de configurar o arquivo .env primeiro
python examples/profile_example.py
python examples/company_example.py
python examples/complete_example.py
```

## Boas Práticas

1. **Respeite os Limites**: O LinkedIn tem limites de taxa. Use o `RateLimiter` para evitar bloqueios.
2. **Autenticação**: Sempre forneça credenciais válidas do LinkedIn para melhores resultados.
3. **Modo Headless**: Use `headless=True` em produção para melhor desempenho.
4. **Tratamento de Erros**: Implemente retentativas com backoff exponencial para lidar com falhas temporárias.
5. **Cookies**: Reutilize cookies de sessão quando possível para reduzir logins.

## Interações Humanas

O sistema implementa várias técnicas para simular comportamento humano e evitar detecção:

1. **Digitação Humana**: Simula a digitação com velocidade variável e pausas aleatórias
2. **Rolagem de Página**: Realiza rolagens aleatórias para cima e para baixo na página
3. **Movimentos do Mouse**: Simula movimentos aleatórios do mouse pela página
4. **Cliques Não Críticos**: Ocasionalmente clica em elementos não críticos da página
5. **Visualização de Seções**: Em páginas de perfil, simula a visualização de diferentes seções
6. **Jitter Aleatório**: Adiciona atrasos aleatórios entre ações
7. **Limitação de Taxa**: Controla o número de requisições por minuto

Estas técnicas tornam a navegação mais natural e reduzem significativamente o risco de bloqueio pelo LinkedIn.

## Limitações

- O LinkedIn pode alterar sua estrutura HTML, o que pode afetar a extração de dados.
- O uso excessivo pode levar a bloqueios temporários da sua conta do LinkedIn.
- Alguns perfis e empresas podem ter configurações de privacidade que limitam os dados visíveis.

## Solução de Problemas

### Problemas de Login

- Verifique se as credenciais estão corretas no arquivo `.env`
- Certifique-se de que sua conta do LinkedIn não está exigindo verificação adicional
- Tente com `headless=False` para visualizar o processo de login

### Perfil Não Encontrado

- Verifique se os dados fornecidos são precisos
- Tente diferentes estratégias de busca (`SEARCH_STRATEGY` no arquivo `.env`)
- Considere fornecer mais informações específicas sobre a pessoa

### Erros de API do Gemini

- Verifique se sua chave de API é válida
- Confirme se você tem acesso ao modelo `gemini-2.0-flash-thinking-exp-01-21`
- Verifique os limites de uso da sua conta Google AI

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

Este projeto é licenciado sob a licença MIT.
