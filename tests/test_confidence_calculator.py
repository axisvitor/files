"""
Testes para o módulo ConfidenceCalculator
"""

import pytest
from linkedin_hunter.utils.confidence_calculator import ConfidenceCalculator

def test_calculate_confidence_exact_match():
    """Testa o cálculo de confiança com correspondência exata"""
    
    calculator = ConfidenceCalculator()
    
    # Dados de entrada
    input_data = {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "company": "Example Corp"
    }
    
    # Dados do perfil com correspondência exata
    profile_data = {
        "full_name": "John Smith",
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Example Corp",
                "duration": "2020 - Present"
            }
        ]
    }
    
    # Calcula a confiança
    confidence = calculator.calculate_confidence(input_data, profile_data)
    
    # Verifica se a confiança é alta (> 80%)
    assert confidence > 80

def test_calculate_confidence_partial_match():
    """Testa o cálculo de confiança com correspondência parcial"""
    
    calculator = ConfidenceCalculator()
    
    # Dados de entrada
    input_data = {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "company": "Example Corp"
    }
    
    # Dados do perfil com correspondência parcial
    profile_data = {
        "full_name": "John A. Smith",
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Example Corporation",
                "duration": "2020 - Present"
            }
        ]
    }
    
    # Calcula a confiança
    confidence = calculator.calculate_confidence(input_data, profile_data)
    
    # Verifica se a confiança é média (entre 50% e 80%)
    assert 50 < confidence < 80

def test_calculate_confidence_low_match():
    """Testa o cálculo de confiança com correspondência baixa"""
    
    calculator = ConfidenceCalculator()
    
    # Dados de entrada
    input_data = {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "company": "Example Corp"
    }
    
    # Dados do perfil com correspondência baixa
    profile_data = {
        "full_name": "Jonathan Smith",
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Different Company",
                "duration": "2020 - Present"
            }
        ]
    }
    
    # Calcula a confiança
    confidence = calculator.calculate_confidence(input_data, profile_data)
    
    # Verifica se a confiança é baixa (< 50%)
    assert confidence < 50

def test_compare_names():
    """Testa a comparação de nomes"""
    
    calculator = ConfidenceCalculator()
    
    # Testes de comparação de nomes
    assert calculator._compare_names("John Smith", "John Smith") == 1.0
    assert calculator._compare_names("John Smith", "John A. Smith") > 0.8
    assert calculator._compare_names("John Smith", "J. Smith") > 0.5
    assert calculator._compare_names("John Smith", "Jane Doe") < 0.3

def test_compare_company():
    """Testa a comparação de empresas"""
    
    calculator = ConfidenceCalculator()
    
    # Experiências de exemplo
    experiences = [
        {
            "title": "Software Engineer",
            "company": "Example Corp",
            "duration": "2020 - Present"
        },
        {
            "title": "Junior Developer",
            "company": "Previous Company",
            "duration": "2018 - 2020"
        }
    ]
    
    # Testes de comparação de empresas
    assert calculator._compare_company("Example Corp", experiences) > 0.9
    assert calculator._compare_company("Example Corporation", experiences) > 0.7
    assert calculator._compare_company("Previous Company", experiences) > 0.5
    assert calculator._compare_company("Unknown Company", experiences) < 0.3
