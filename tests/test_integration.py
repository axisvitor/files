"""
Testes de integração para o LinkedIn Profile Hunter
"""

import os
import pytest
import asyncio
from unittest.mock import patch, MagicMock

from linkedin_hunter.linkedin_profile_hunter import LinkedInProfileHunter
from linkedin_hunter.core.profile_finder import ProfileFinder
from linkedin_hunter.modules.profile_scraper import ProfileScraper
from linkedin_hunter.modules.profile_analyzer import ProfileAnalyzer
from linkedin_hunter.utils.confidence_calculator import ConfidenceCalculator
from linkedin_hunter.utils.block_detection import BlockDetector

# Fixture para criar um mock do crawler
@pytest.fixture
def mock_crawler():
    crawler = MagicMock()
    crawler.arun = MagicMock()
    crawler.browser = MagicMock()
    crawler.browser.page = MagicMock()
    return crawler

# Fixture para criar um mock do resultado da raspagem
@pytest.fixture
def mock_scrape_result():
    result = MagicMock()
    result.url = "https://www.linkedin.com/in/test-profile/"
    result.title = "Test Profile | LinkedIn"
    result.html = "<html><body><h1>Test Profile</h1><p>Software Engineer at Test Company</p></body></html>"
    result.markdown = "# Test Profile\n\nSoftware Engineer at Test Company"
    return result

# Fixture para criar um mock do ProfileFinder
@pytest.fixture
def mock_profile_finder():
    with patch('linkedin_hunter.core.profile_finder.ProfileFinder') as mock:
        finder = mock.return_value
        finder.find_profile.return_value = {
            "url": "https://www.linkedin.com/in/test-profile/",
            "initial_confidence": 0.8
        }
        yield finder

# Fixture para criar um mock do ProfileScraper
@pytest.fixture
def mock_profile_scraper(mock_scrape_result):
    with patch('linkedin_hunter.modules.profile_scraper.ProfileScraper') as mock:
        scraper = mock.return_value
        scraper.scrape_profile.return_value = {
            "url": "https://www.linkedin.com/in/test-profile/",
            "full_name": "Test Profile",
            "headline": "Software Engineer at Test Company",
            "location": "San Francisco, CA",
            "about": "Experienced software engineer",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Test Company",
                    "duration": "2020 - Present",
                    "location": "San Francisco, CA"
                }
            ],
            "education": [
                {
                    "institution": "Test University",
                    "degree": "BS in Computer Science",
                    "duration": "2016 - 2020"
                }
            ],
            "skills": ["Python", "JavaScript", "Machine Learning"],
            "recommendations": [],
            "connections": "500+"
        }
        yield scraper

# Fixture para criar um mock do ProfileAnalyzer
@pytest.fixture
def mock_profile_analyzer():
    with patch('linkedin_hunter.modules.profile_analyzer.ProfileAnalyzer') as mock:
        analyzer = mock.return_value
        analyzer.analyze_profile.return_value = "Test Profile is a software engineer with experience in Python and JavaScript."
        yield analyzer

# Fixture para criar um mock do ConfidenceCalculator
@pytest.fixture
def mock_confidence_calculator():
    with patch('linkedin_hunter.utils.confidence_calculator.ConfidenceCalculator') as mock:
        calculator = mock.return_value
        calculator.calculate_confidence.return_value = 85.5
        yield calculator

# Fixture para criar um mock do BlockDetector
@pytest.fixture
def mock_block_detector():
    with patch('linkedin_hunter.utils.block_detection.BlockDetector') as mock:
        mock.detect_blocks.return_value = {
            "is_blocked": False,
            "block_types": [],
            "details": {}
        }
        mock.get_recommended_action.return_value = {
            "action": "continue",
            "wait_time": 0
        }
        yield mock

@pytest.mark.asyncio
async def test_full_integration_flow(
    mock_profile_finder,
    mock_profile_scraper,
    mock_profile_analyzer,
    mock_confidence_calculator,
    mock_block_detector
):
    """Testa o fluxo completo de integração com mocks"""
    
    # Cria o hunter com os mocks
    hunter = LinkedInProfileHunter(
        linkedin_email="test@example.com",
        linkedin_password="password123",
        google_api_key="fake-api-key",
        headless=True
    )
    
    # Substitui os componentes pelos mocks
    hunter.profile_finder = mock_profile_finder
    hunter.profile_scraper = mock_profile_scraper
    hunter.profile_analyzer = mock_profile_analyzer
    hunter.confidence_calculator = mock_confidence_calculator
    
    # Executa o método principal
    result = await hunter.hunt_profile(
        name="Test User",
        email="test.user@example.com",
        company="Test Company"
    )
    
    # Verifica se o método find_profile foi chamado com os argumentos corretos
    mock_profile_finder.find_profile.assert_called_once_with(
        "Test User", "test.user@example.com", "Test Company"
    )
    
    # Verifica se o método scrape_profile foi chamado com a URL correta
    mock_profile_scraper.scrape_profile.assert_called_once_with(
        "https://www.linkedin.com/in/test-profile/"
    )
    
    # Verifica se o método analyze_profile foi chamado com os dados corretos
    mock_profile_analyzer.analyze_profile.assert_called_once()
    
    # Verifica se o método calculate_confidence foi chamado com os dados corretos
    mock_confidence_calculator.calculate_confidence.assert_called_once()
    
    # Verifica o resultado final
    assert result["Nome"] == "Test User"
    assert result["E-mail"] == "test.user@example.com"
    assert result["Empresa"] == "Test Company"
    assert result["Confiabilidade"] == "85.5%"
    assert result["LinkedIn"] == "https://www.linkedin.com/in/test-profile/"
    assert result["Cargo Atual"] == "Software Engineer at Test Company"
    assert len(result["Experiência Anterior"]) == 1
    assert len(result["Formação"]) == 1
    assert len(result["Habilidades principais"]) == 3
    assert result["Análise do Perfil"] == "Test Profile is a software engineer with experience in Python and JavaScript."

@pytest.mark.asyncio
async def test_profile_not_found(mock_profile_finder):
    """Testa o comportamento quando o perfil não é encontrado"""
    
    # Configura o mock para retornar URL vazia
    mock_profile_finder.find_profile.return_value = {
        "url": "",
        "initial_confidence": 0.0
    }
    
    # Cria o hunter com o mock
    hunter = LinkedInProfileHunter(
        linkedin_email="test@example.com",
        linkedin_password="password123",
        google_api_key="fake-api-key",
        headless=True
    )
    
    # Substitui o ProfileFinder pelo mock
    hunter.profile_finder = mock_profile_finder
    
    # Executa o método principal
    result = await hunter.hunt_profile(
        name="Nonexistent User",
        email="nonexistent@example.com",
        company="Unknown Company"
    )
    
    # Verifica o resultado
    assert result["Nome"] == "Nonexistent User"
    assert result["E-mail"] == "nonexistent@example.com"
    assert result["Empresa"] == "Unknown Company"
    assert result["Confiabilidade"] == "0%"
    assert result["LinkedIn"] == "Perfil não encontrado"
    assert result["Cargo Atual"] == "N/A"
    assert len(result["Experiência Anterior"]) == 0
    assert len(result["Formação"]) == 0
    assert len(result["Habilidades principais"]) == 0
    assert "Não foi possível encontrar um perfil" in result["Análise do Perfil"]

@pytest.mark.asyncio
async def test_block_detection_and_handling(
    mock_profile_finder,
    mock_profile_scraper,
    mock_block_detector
):
    """Testa a detecção e tratamento de bloqueios"""
    
    # Configura o mock do BlockDetector para simular um bloqueio
    with patch('linkedin_hunter.utils.block_detection.BlockDetector.detect_blocks') as mock_detect:
        mock_detect.return_value = {
            "is_blocked": True,
            "block_types": ["rate_limit"],
            "details": {}
        }
        
        with patch('linkedin_hunter.utils.block_detection.BlockDetector.get_recommended_action') as mock_action:
            mock_action.return_value = {
                "action": "wait",
                "reason": "rate_limit",
                "message": "Limite de taxa atingido. Aguarde antes de continuar.",
                "wait_time": 5  # Tempo curto para o teste
            }
            
            # Cria o hunter com os mocks
            hunter = LinkedInProfileHunter(
                linkedin_email="test@example.com",
                linkedin_password="password123",
                google_api_key="fake-api-key",
                headless=True
            )
            
            # Substitui os componentes pelos mocks
            hunter.profile_finder = mock_profile_finder
            hunter.profile_scraper = mock_profile_scraper
            
            # Patch para o método _check_for_blocks para verificar se é chamado
            with patch.object(ProfileScraper, '_check_for_blocks') as mock_check:
                # Configura o mock para não fazer nada
                mock_check.return_value = {}
                
                # Executa o método principal
                await hunter.hunt_profile(
                    name="Test User",
                    email="test.user@example.com",
                    company="Test Company"
                )
                
                # Verifica se o método _check_for_blocks foi chamado
                assert mock_check.called

@pytest.mark.asyncio
async def test_proxy_rotation(
    mock_profile_finder,
    mock_profile_scraper
):
    """Testa a rotação de proxies"""
    
    # Patch para o método _rotate_proxy para verificar se é chamado
    with patch.object(ProfileScraper, '_rotate_proxy') as mock_rotate:
        # Configura o mock para não fazer nada
        mock_rotate.return_value = None
        
        # Cria o hunter com os mocks
        hunter = LinkedInProfileHunter(
            linkedin_email="test@example.com",
            linkedin_password="password123",
            google_api_key="fake-api-key",
            headless=True,
            proxies_file="proxies.json.example"
        )
        
        # Substitui os componentes pelos mocks
        hunter.profile_finder = mock_profile_finder
        hunter.profile_scraper = mock_profile_scraper
        
        # Configura o mock do BlockDetector para simular um bloqueio de IP
        with patch('linkedin_hunter.utils.block_detection.BlockDetector.detect_blocks') as mock_detect:
            mock_detect.return_value = {
                "is_blocked": True,
                "block_types": ["ip_block"],
                "details": {}
            }
            
            with patch('linkedin_hunter.utils.block_detection.BlockDetector.get_recommended_action') as mock_action:
                mock_action.return_value = {
                    "action": "change_proxy",
                    "reason": "ip_block",
                    "message": "IP bloqueado. Troque de proxy antes de continuar.",
                    "wait_time": 5  # Tempo curto para o teste
                }
                
                # Patch para o método _check_for_blocks para usar os mocks acima
                with patch.object(ProfileScraper, '_check_for_blocks') as mock_check:
                    # Configura o mock para chamar o método _rotate_proxy
                    async def side_effect(*args, **kwargs):
                        await hunter.profile_scraper._rotate_proxy()
                        return {}
                    
                    mock_check.side_effect = side_effect
                    
                    # Executa o método principal
                    await hunter.hunt_profile(
                        name="Test User",
                        email="test.user@example.com",
                        company="Test Company"
                    )
                    
                    # Verifica se o método _rotate_proxy foi chamado
                    assert mock_rotate.called
