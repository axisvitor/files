# Arquitetura do LinkedIn Profile Hunter

Este documento descreve a arquitetura do LinkedIn Profile Hunter, incluindo seus componentes principais, fluxo de dados e interações entre módulos.

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      LinkedIn Profile Hunter                             │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐         │
│  │ ProfileFinder │     │ ProfileScraper │     │ProfileAnalyzer│         │
│  │               │────▶│               │────▶│               │         │
│  │ Localiza perfil│     │ Extrai dados  │     │ Analisa perfil│         │
│  └───────────────┘     └───────────────┘     └───────────────┘         │
│          │                     │                     │                  │
│          │                     │                     │                  │
│          ▼                     ▼                     ▼                  │
│  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐         │
│  │ ProxyManager  │     │ BlockDetector │     │ConfidenceCalc │         │
│  │               │     │               │     │               │         │
│  │ Gerencia proxies│     │ Detecta bloqueios│     │ Calcula confiança│         │
│  └───────────────┘     └───────────────┘     └───────────────┘         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Diagrama de Fluxo de Dados

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Entrada │     │  Busca   │     │ Extração │     │ Análise  │     │  Saída   │
│          │────▶│          │────▶│          │────▶│          │────▶│          │
│Nome,Email│     │Localizar │     │Extrair   │     │Analisar  │     │Resultado │
│Empresa   │     │Perfil    │     │Dados     │     │com IA    │     │Estruturado│
└──────────┘     └──────────┘     └──────────┘     └──────────┘     └──────────┘
                       │                │                │
                       ▼                ▼                ▼
                 ┌──────────┐     ┌──────────┐     ┌──────────┐
                 │Rotação de│     │Detecção de│     │Cálculo de│
                 │Proxies   │     │Bloqueios  │     │Confiança │
                 └──────────┘     └──────────┘     └──────────┘
```

## Descrição dos Componentes

### Componentes Principais

1. **LinkedInProfileHunter**
   - Classe principal que orquestra todo o processo
   - Gerencia o fluxo de trabalho completo
   - Integra todos os componentes

2. **ProfileFinder**
   - Localiza perfis do LinkedIn a partir de dados básicos (nome, email, empresa)
   - Implementa diferentes estratégias de busca (Google, Bing, direta)
   - Retorna URL do perfil e confiança inicial

3. **ProfileScraper**
   - Extrai dados detalhados de perfis do LinkedIn
   - Gerencia autenticação e sessão
   - Implementa técnicas para evitar detecção

4. **ProfileAnalyzer**
   - Analisa os dados do perfil usando o modelo Gemini 2.0
   - Gera insights sobre a trajetória profissional
   - Formata os dados para análise

### Componentes de Suporte

5. **ConfidenceCalculator**
   - Calcula a confiabilidade da correspondência entre dados de entrada e perfil
   - Implementa algoritmos de comparação de nomes, empresas, etc.
   - Retorna um score de confiança (0-100%)

6. **BlockDetector**
   - Detecta diferentes tipos de bloqueios do LinkedIn
   - Identifica padrões de texto, elementos HTML e URLs
   - Recomenda ações com base no tipo de bloqueio

7. **ProxyManager**
   - Gerencia uma lista de proxies
   - Implementa rotação de proxies e user-agents
   - Testa e monitora a saúde dos proxies

8. **HumanInteraction**
   - Simula comportamento humano durante a navegação
   - Implementa rolagem, movimentos do mouse, cliques aleatórios
   - Torna a navegação mais natural para evitar detecção

## Fluxo de Execução

1. **Entrada de Dados**
   - O usuário fornece nome, email e empresa da pessoa

2. **Localização do Perfil**
   - O `ProfileFinder` busca o perfil do LinkedIn usando diferentes estratégias
   - Retorna a URL do perfil encontrado

3. **Extração de Dados**
   - O `ProfileScraper` acessa o perfil e extrai informações detalhadas
   - Durante a extração, o `BlockDetector` verifica se há bloqueios
   - Se um bloqueio for detectado, o `ProxyManager` rotaciona para outro proxy

4. **Análise e Processamento**
   - O `ConfidenceCalculator` calcula a confiabilidade da correspondência
   - O `ProfileAnalyzer` gera uma análise concisa usando o modelo Gemini 2.0

5. **Saída de Resultados**
   - Os resultados são estruturados no formato solicitado
   - Inclui dados do perfil, confiabilidade e análise

## Interações entre Componentes

- **LinkedInProfileHunter → ProfileFinder**: Solicita a localização do perfil
- **LinkedInProfileHunter → ProfileScraper**: Solicita a extração de dados
- **LinkedInProfileHunter → ProfileAnalyzer**: Solicita a análise do perfil
- **LinkedInProfileHunter → ConfidenceCalculator**: Solicita o cálculo de confiança

- **ProfileScraper → BlockDetector**: Verifica se há bloqueios durante a raspagem
- **ProfileScraper → ProxyManager**: Solicita rotação de proxies quando necessário
- **ProfileScraper → HumanInteraction**: Solicita simulação de comportamento humano

## Considerações de Design

1. **Modularidade**
   - Componentes independentes e substituíveis
   - Interfaces bem definidas entre módulos
   - Facilidade de manutenção e extensão

2. **Robustez**
   - Tratamento abrangente de erros e exceções
   - Mecanismos de retry com backoff exponencial
   - Detecção avançada de bloqueios

3. **Escalabilidade**
   - Arquitetura assíncrona para melhor desempenho
   - Suporte para rotação de proxies
   - Limitação de taxa inteligente

4. **Adaptabilidade**
   - Configuração centralizada
   - Parâmetros ajustáveis
   - Estratégias de busca configuráveis
