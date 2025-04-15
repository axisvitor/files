# Exemplo de Saída do LinkedIn Profile Hunter

Este documento apresenta um exemplo completo da saída gerada pelo LinkedIn Profile Hunter, mostrando o formato e conteúdo esperados.

## Exemplo 1: Saída Completa

```json
{
  "Nome": "Vagner Campos",
  "E-mail": "vagner.campos@arduus.tech",
  "Empresa": "Arduus Ventures",
  "Confiabilidade": "92.7%",
  "LinkedIn": "https://www.linkedin.com/in/vagner-campos/",
  "Cargo Atual": "CEO at Arduus Ventures",
  "Experiência Anterior": [
    {
      "title": "CEO",
      "company": "Arduus Ventures",
      "duration": "Jan 2020 - Present",
      "location": "São Paulo, Brazil"
    },
    {
      "title": "CTO",
      "company": "Tech Solutions Inc.",
      "duration": "Mar 2015 - Dec 2019",
      "location": "São Paulo, Brazil"
    },
    {
      "title": "Senior Software Engineer",
      "company": "Global Systems",
      "duration": "Jun 2010 - Feb 2015",
      "location": "São Paulo, Brazil"
    }
  ],
  "Formação": [
    {
      "institution": "Universidade de São Paulo",
      "degree": "Master of Computer Science",
      "duration": "2008 - 2010"
    },
    {
      "institution": "Universidade Estadual de Campinas",
      "degree": "Bachelor of Computer Engineering",
      "duration": "2004 - 2008"
    }
  ],
  "Habilidades principais": [
    "Leadership",
    "Strategic Planning",
    "Business Development",
    "Software Architecture",
    "Artificial Intelligence",
    "Machine Learning",
    "Cloud Computing",
    "Entrepreneurship",
    "Product Management",
    "Team Building"
  ],
  "Análise do Perfil": "Vagner Campos é um executivo de tecnologia com uma sólida trajetória que combina expertise técnica e liderança empresarial. Como CEO da Arduus Ventures, ele aplica sua formação em Ciência da Computação e experiência anterior como CTO para liderar iniciativas estratégicas em tecnologia e inovação. Sua progressão de carreira demonstra uma evolução consistente de posições técnicas para funções de liderança executiva.\n\nSua formação acadêmica em instituições de prestígio como USP e Unicamp, aliada à experiência prática em engenharia de software e arquitetura, fornece uma base sólida para sua atuação atual. O conjunto de habilidades que combina competências técnicas (IA, Machine Learning, Computação em Nuvem) com habilidades de gestão (Liderança, Planejamento Estratégico, Desenvolvimento de Negócios) indica um perfil versátil e equilibrado.\n\nSeu foco em empreendedorismo e gestão de produtos sugere que Vagner está envolvido não apenas com aspectos tecnológicos, mas também com a visão estratégica e o crescimento de negócios. A experiência consistente em empresas de tecnologia, culminando na posição atual de CEO, demonstra sua capacidade de liderar equipes e iniciativas de transformação digital."
}
```

## Exemplo 2: Perfil Não Encontrado

```json
{
  "Nome": "João Silva",
  "E-mail": "joao.silva@exemplo.com",
  "Empresa": "Empresa Desconhecida",
  "Confiabilidade": "0%",
  "LinkedIn": "Perfil não encontrado",
  "Cargo Atual": "N/A",
  "Experiência Anterior": [],
  "Formação": [],
  "Habilidades principais": [],
  "Análise do Perfil": "Não foi possível encontrar um perfil do LinkedIn correspondente aos dados fornecidos. Verifique se as informações estão corretas ou tente fornecer dados adicionais para melhorar a busca."
}
```

## Exemplo 3: Perfil com Baixa Confiabilidade

```json
{
  "Nome": "Maria Santos",
  "E-mail": "maria.santos@exemplo.com",
  "Empresa": "Tech Solutions",
  "Confiabilidade": "45.3%",
  "LinkedIn": "https://www.linkedin.com/in/maria-c-santos/",
  "Cargo Atual": "Product Manager at Digital Innovations",
  "Experiência Anterior": [
    {
      "title": "Product Manager",
      "company": "Digital Innovations",
      "duration": "Mar 2021 - Present",
      "location": "São Paulo, Brazil"
    },
    {
      "title": "Product Analyst",
      "company": "Tech Solutions",
      "duration": "Jan 2018 - Feb 2021",
      "location": "São Paulo, Brazil"
    }
  ],
  "Formação": [
    {
      "institution": "Universidade Federal do Rio de Janeiro",
      "degree": "Bachelor of Business Administration",
      "duration": "2014 - 2018"
    }
  ],
  "Habilidades principais": [
    "Product Management",
    "Agile Methodologies",
    "User Experience",
    "Market Research",
    "Data Analysis"
  ],
  "Análise do Perfil": "Maria Santos é uma profissional de gerenciamento de produtos com experiência em empresas de tecnologia. Atualmente atua como Product Manager na Digital Innovations, tendo anteriormente trabalhado como Product Analyst na Tech Solutions, o que demonstra uma progressão natural em sua carreira na área de produtos.\n\nSua formação em Administração de Empresas pela UFRJ fornece uma base sólida para sua atuação em funções que exigem compreensão de negócios e estratégia. Suas habilidades principais estão alinhadas com as competências esperadas para um gerente de produtos, incluindo metodologias ágeis, experiência do usuário e análise de dados.\n\nNOTA: Este perfil foi identificado com baixa confiabilidade (45.3%) devido a discrepâncias entre os dados fornecidos e as informações encontradas no perfil. A empresa atual não corresponde à informada, e existem variações no nome completo. Recomenda-se verificar se este é realmente o perfil correto da pessoa buscada."
}
```

## Campos da Saída

### Dados Básicos
- **Nome**: Nome fornecido como entrada
- **E-mail**: E-mail fornecido como entrada
- **Empresa**: Empresa fornecida como entrada
- **Confiabilidade**: Porcentagem de confiança de que o perfil encontrado pertence à pessoa buscada
- **LinkedIn**: URL do perfil do LinkedIn encontrado ou mensagem de erro

### Informações Profissionais
- **Cargo Atual**: Cargo/título atual extraído do perfil
- **Experiência Anterior**: Lista de experiências profissionais com:
  - `title`: Cargo/título
  - `company`: Empresa
  - `duration`: Período
  - `location`: Localização

### Formação e Habilidades
- **Formação**: Lista de formações acadêmicas com:
  - `institution`: Instituição de ensino
  - `degree`: Grau/curso
  - `duration`: Período
- **Habilidades principais**: Lista de habilidades extraídas do perfil

### Análise
- **Análise do Perfil**: Análise gerada pelo modelo Gemini 2.0, incluindo insights sobre background, especialização, trajetória e interesses profissionais

## Notas sobre a Saída

1. **Confiabilidade**:
   - 90-100%: Alta confiabilidade, perfil correto com alta probabilidade
   - 70-89%: Boa confiabilidade, perfil provavelmente correto
   - 50-69%: Confiabilidade média, verificação recomendada
   - 0-49%: Baixa confiabilidade, verificação necessária

2. **Perfil Não Encontrado**:
   - Quando nenhum perfil é encontrado, a confiabilidade é 0%
   - Campos de informações profissionais, formação e habilidades ficam vazios
   - A análise contém uma mensagem explicativa

3. **Análise com IA**:
   - Gerada pelo modelo Gemini 2.0 Flash Thinking
   - Limitada a aproximadamente 3 parágrafos
   - Baseada apenas nos dados extraídos do perfil
   - Para perfis com baixa confiabilidade, inclui uma nota de advertência
