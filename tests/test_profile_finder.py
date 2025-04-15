"""
Testes para o módulo ProfileFinder
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from linkedin_hunter.core.profile_finder import ProfileFinder

@pytest.mark.asyncio
async def test_find_profile_with_google():
    """Testa a busca de perfil usando o Google"""
    
    # Mock para o crawler
    mock_crawler = MagicMock()
    mock_crawler.arun = MagicMock()
    mock_crawler.arun.return_value = MagicMock(
        html='<html><body><a href="https://www.linkedin.com/in/test-profile/">Test Profile</a></body></html>'
    )
    
    # Mock para o método _initialize_crawler
    with patch.object(ProfileFinder, '_initialize_crawler', return_value=None) as mock_init:
        with patch.object(ProfileFinder, '_close_crawler', return_value=None) as mock_close:
            # Configura o mock para o crawler
            finder = ProfileFinder(search_strategy="google")
            finder.crawler = mock_crawler
            
            # Executa o método
            result = await finder.find_profile("Test User", "test.user@example.com", "Test Company")
            
            # Verifica se o método _initialize_crawler foi chamado
            mock_init.assert_called_once()
            
            # Verifica se o método _close_crawler foi chamado
            mock_close.assert_called_once()
            
            # Verifica o resultado
            assert isinstance(result, dict)
            assert "url" in result
            assert "initial_confidence" in result
            assert result["url"] == "https://www.linkedin.com/in/test-profile/"
            assert result["initial_confidence"] > 0

@pytest.mark.asyncio
async def test_extract_linkedin_profile_urls():
    """Testa a extração de URLs de perfis do LinkedIn do HTML"""
    
    finder = ProfileFinder()
    
    # HTML de exemplo com URLs de perfis do LinkedIn
    html = """
    <html>
    <body>
        <a href="https://www.linkedin.com/in/profile1/">Profile 1</a>
        <a href="https://linkedin.com/in/profile2/">Profile 2</a>
        <a href="https://www.linkedin.com/in/profile3">Profile 3</a>
        <a href="https://www.linkedin.com/company/company1/">Company 1</a>
    </body>
    </html>
    """
    
    # Extrai as URLs
    urls = finder._extract_linkedin_profile_urls(html)
    
    # Verifica se as URLs de perfis foram extraídas corretamente
    assert len(urls) == 3
    assert "https://www.linkedin.com/in/profile1/" in urls
    assert "https://linkedin.com/in/profile2/" in urls
    assert "https://www.linkedin.com/in/profile3" in urls
    assert "https://www.linkedin.com/company/company1/" not in urls
