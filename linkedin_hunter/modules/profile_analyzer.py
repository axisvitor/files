"""
Módulo para análise de perfis do LinkedIn usando Gemini 2.0
"""

import os
import json
from typing import Dict, Any, List, Optional

import google.generativeai as genai

class ProfileAnalyzer:
    """
    Componente para análise de perfis do LinkedIn usando Gemini 2.0
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o analisador de perfis
        
        Args:
            api_key: Chave de API do Google AI (opcional, pode ser fornecida via variável de ambiente)
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("Chave de API do Google AI não fornecida. Configure GOOGLE_API_KEY.")
        
        # Configura o cliente Gemini
        genai.configure(api_key=self.api_key)
        
        # Inicializa o modelo Gemini
        self.model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp-01-21')
    
    async def analyze_profile(self, profile_data: Dict[str, Any]) -> str:
        """
        Analisa os dados do perfil e gera insights
        
        Args:
            profile_data: Dados extraídos do perfil do LinkedIn
            
        Returns:
            str: Análise gerada pelo modelo Gemini
        """
        # Constrói o prompt para o Gemini
        prompt = self._build_prompt(profile_data)
        
        try:
            # Obter resposta do modelo
            response = await self.model.generate_content_async(prompt)
            
            # Retorna o texto da resposta
            return response.text
        except Exception as e:
            # Em caso de erro, retorna uma mensagem genérica
            print(f"Erro ao analisar perfil com Gemini: {e}")
            return "Não foi possível gerar uma análise detalhada do perfil neste momento."
    
    def _build_prompt(self, profile_data: Dict[str, Any]) -> str:
        """
        Constrói o prompt para o modelo Gemini
        
        Args:
            profile_data: Dados do perfil
            
        Returns:
            str: Prompt formatado
        """
        # Formata as experiências para o prompt
        experiences_text = self._format_experiences(profile_data.get('experience', []))
        
        # Formata a educação para o prompt
        education_text = self._format_education(profile_data.get('education', []))
        
        # Formata as habilidades para o prompt
        skills_text = self._format_skills(profile_data.get('skills', []))
        
        # Constrói o prompt completo
        prompt = f"""
        Você é um analista profissional especializado em perfis de carreira. Analise o seguinte perfil do LinkedIn e forneça uma análise concisa (máximo 3 parágrafos) sobre a trajetória profissional desta pessoa.

        PERFIL:
        Nome: {profile_data.get('full_name', 'N/A')}
        Cargo Atual: {profile_data.get('headline', 'N/A')}
        Localização: {profile_data.get('location', 'N/A')}
        Sobre: {profile_data.get('about', 'N/A')}
        
        Experiências Anteriores:
        {experiences_text}
        
        Formação Acadêmica:
        {education_text}
        
        Habilidades:
        {skills_text}

        Sua análise deve:
        1. Identificar a especialização principal e área de atuação
        2. Destacar a progressão de carreira e conquistas notáveis
        3. Mencionar formação relevante e como ela se relaciona com a trajetória
        4. Identificar possíveis interesses profissionais com base nas habilidades

        Mantenha um tom profissional e objetivo, baseando-se apenas nos dados fornecidos.
        """
        
        return prompt
    
    def _format_experiences(self, experiences: List[Dict[str, str]]) -> str:
        """
        Formata as experiências para o prompt
        
        Args:
            experiences: Lista de experiências
            
        Returns:
            str: Texto formatado
        """
        if not experiences:
            return "Nenhuma experiência disponível"
        
        formatted_text = ""
        for exp in experiences:
            title = exp.get('title', 'N/A')
            company = exp.get('company', 'N/A')
            duration = exp.get('duration', 'N/A')
            location = exp.get('location', 'N/A')
            
            formatted_text += f"- {title} em {company}, {duration}, {location}\n"
        
        return formatted_text
    
    def _format_education(self, education: List[Dict[str, str]]) -> str:
        """
        Formata a educação para o prompt
        
        Args:
            education: Lista de formações acadêmicas
            
        Returns:
            str: Texto formatado
        """
        if not education:
            return "Nenhuma formação disponível"
        
        formatted_text = ""
        for edu in education:
            institution = edu.get('institution', 'N/A')
            degree = edu.get('degree', 'N/A')
            duration = edu.get('duration', 'N/A')
            
            formatted_text += f"- {degree} em {institution}, {duration}\n"
        
        return formatted_text
    
    def _format_skills(self, skills: List[str]) -> str:
        """
        Formata as habilidades para o prompt
        
        Args:
            skills: Lista de habilidades
            
        Returns:
            str: Texto formatado
        """
        if not skills:
            return "Nenhuma habilidade disponível"
        
        return ", ".join(skills)
