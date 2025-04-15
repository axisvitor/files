"""
Testes para o módulo ProfileAnalyzer
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from linkedin_hunter.modules.profile_analyzer import ProfileAnalyzer

@pytest.mark.asyncio
async def test_build_prompt():
    """Testa a construção do prompt para o modelo Gemini"""
    
    # Mock para o modelo Gemini
    with patch('google.generativeai.GenerativeModel') as mock_model:
        # Configura o mock
        mock_instance = MagicMock()
        mock_model.return_value = mock_instance
        
        # Cria o analisador com uma chave de API fictícia
        analyzer = ProfileAnalyzer(api_key="fake-api-key")
        
        # Dados de perfil de exemplo
        profile_data = {
            "full_name": "John Smith",
            "headline": "Software Engineer at Example Corp",
            "location": "San Francisco, CA",
            "about": "Experienced software engineer with a passion for AI.",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Example Corp",
                    "duration": "2020 - Present",
                    "location": "San Francisco, CA"
                }
            ],
            "education": [
                {
                    "institution": "Stanford University",
                    "degree": "BS in Computer Science",
                    "duration": "2016 - 2020"
                }
            ],
            "skills": ["Python", "Machine Learning", "JavaScript"]
        }
        
        # Constrói o prompt
        prompt = analyzer._build_prompt(profile_data)
        
        # Verifica se o prompt contém as informações esperadas
        assert "John Smith" in prompt
        assert "Software Engineer at Example Corp" in prompt
        assert "San Francisco, CA" in prompt
        assert "Experienced software engineer with a passion for AI" in prompt
        assert "Software Engineer em Example Corp" in prompt
        assert "Stanford University" in prompt
        assert "BS in Computer Science" in prompt
        assert "Python, Machine Learning, JavaScript" in prompt

@pytest.mark.asyncio
async def test_analyze_profile():
    """Testa a análise de perfil com o modelo Gemini"""
    
    # Mock para o modelo Gemini
    with patch('google.generativeai.GenerativeModel') as mock_model:
        # Configura o mock
        mock_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "John Smith é um engenheiro de software experiente com foco em IA."
        mock_instance.generate_content_async.return_value = mock_response
        mock_model.return_value = mock_instance
        
        # Cria o analisador com uma chave de API fictícia
        analyzer = ProfileAnalyzer(api_key="fake-api-key")
        
        # Dados de perfil de exemplo
        profile_data = {
            "full_name": "John Smith",
            "headline": "Software Engineer at Example Corp",
            "location": "San Francisco, CA",
            "about": "Experienced software engineer with a passion for AI.",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Example Corp",
                    "duration": "2020 - Present",
                    "location": "San Francisco, CA"
                }
            ],
            "education": [
                {
                    "institution": "Stanford University",
                    "degree": "BS in Computer Science",
                    "duration": "2016 - 2020"
                }
            ],
            "skills": ["Python", "Machine Learning", "JavaScript"]
        }
        
        # Analisa o perfil
        analysis = await analyzer.analyze_profile(profile_data)
        
        # Verifica se a análise corresponde à resposta do mock
        assert analysis == "John Smith é um engenheiro de software experiente com foco em IA."
        
        # Verifica se o método generate_content_async foi chamado
        mock_instance.generate_content_async.assert_called_once()

@pytest.mark.asyncio
async def test_analyze_profile_error_handling():
    """Testa o tratamento de erros na análise de perfil"""
    
    # Mock para o modelo Gemini que lança uma exceção
    with patch('google.generativeai.GenerativeModel') as mock_model:
        # Configura o mock para lançar uma exceção
        mock_instance = MagicMock()
        mock_instance.generate_content_async.side_effect = Exception("API Error")
        mock_model.return_value = mock_instance
        
        # Cria o analisador com uma chave de API fictícia
        analyzer = ProfileAnalyzer(api_key="fake-api-key")
        
        # Dados de perfil de exemplo
        profile_data = {
            "full_name": "John Smith",
            "headline": "Software Engineer"
        }
        
        # Analisa o perfil
        analysis = await analyzer.analyze_profile(profile_data)
        
        # Verifica se a mensagem de erro genérica é retornada
        assert "Não foi possível gerar uma análise detalhada do perfil" in analysis
