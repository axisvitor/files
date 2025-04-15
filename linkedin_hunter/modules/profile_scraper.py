"""
Módulo para raspagem de perfis do LinkedIn
"""

import asyncio
import re
from typing import Dict, Optional, Any, List

from ..core.base_scraper import LinkedInBaseScraper

class ProfileScraper(LinkedInBaseScraper):
    """
    Raspador especializado para perfis do LinkedIn
    """
    
    async def scrape_profile(self, profile_url: str) -> Dict[str, Any]:
        """
        Raspa dados de um perfil do LinkedIn
        
        Args:
            profile_url: URL do perfil do LinkedIn
            
        Returns:
            Dict[str, Any]: Dados do perfil
        """
        # Verifica se a URL é de um perfil do LinkedIn
        if not self._validate_profile_url(profile_url):
            raise ValueError(f"URL inválida para perfil do LinkedIn: {profile_url}")
        
        # Executa a raspagem usando o método base
        result = await self.scrape(profile_url)
        
        # Processa os dados específicos do perfil
        profile_data = self._extract_profile_data(result)
        
        return profile_data
    
    def _validate_profile_url(self, url: str) -> bool:
        """
        Valida se a URL é de um perfil do LinkedIn
        
        Args:
            url: URL para validar
            
        Returns:
            bool: True se for uma URL válida de perfil do LinkedIn
        """
        # Padrão para URLs de perfil do LinkedIn
        pattern = r"^https?://(www\.)?linkedin\.com/in/[\w\-]+/?.*$"
        return bool(re.match(pattern, url))
    
    def _extract_profile_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai dados estruturados do perfil a partir do resultado da raspagem
        
        Args:
            result: Resultado da raspagem
            
        Returns:
            Dict[str, Any]: Dados estruturados do perfil
        """
        # Extrai dados básicos
        profile_data = {
            "url": result["url"],
            "full_name": self._extract_full_name(result),
            "headline": self._extract_headline(result),
            "location": self._extract_location(result),
            "about": self._extract_about(result),
            "experience": self._extract_experience(result),
            "education": self._extract_education(result),
            "skills": self._extract_skills(result),
            "recommendations": self._extract_recommendations(result),
            "connections": self._extract_connections(result),
        }
        
        return profile_data
    
    def _extract_full_name(self, result: Dict[str, Any]) -> str:
        """Extrai o nome completo do perfil"""
        # Implementação usando o título da página que geralmente contém o nome
        if result.get("title"):
            # O título geralmente é "Nome Sobrenome | LinkedIn"
            title_parts = result["title"].split("|")
            if len(title_parts) > 0:
                return title_parts[0].strip()
        
        # Tenta extrair do markdown usando heurísticas
        if result.get("markdown"):
            # O nome geralmente é o primeiro cabeçalho H1 ou H2
            h1_match = re.search(r"# ([^\n]+)", result["markdown"])
            if h1_match:
                return h1_match.group(1).strip()
            
            h2_match = re.search(r"## ([^\n]+)", result["markdown"])
            if h2_match:
                return h2_match.group(1).strip()
        
        return "Nome não encontrado"
    
    def _extract_headline(self, result: Dict[str, Any]) -> str:
        """Extrai o título profissional/headline do perfil"""
        if result.get("markdown"):
            # O headline geralmente aparece logo após o nome
            headline_match = re.search(r"# [^\n]+\n+([^\n#]+)", result["markdown"])
            if headline_match:
                return headline_match.group(1).strip()
        
        return ""
    
    def _extract_location(self, result: Dict[str, Any]) -> str:
        """Extrai a localização do perfil"""
        if result.get("markdown"):
            # A localização geralmente aparece próxima ao headline
            location_pattern = r"(?:Location|Localização|Local):\s*([^\n]+)"
            location_match = re.search(location_pattern, result["markdown"], re.IGNORECASE)
            if location_match:
                return location_match.group(1).strip()
        
        return ""
    
    def _extract_about(self, result: Dict[str, Any]) -> str:
        """Extrai a seção 'sobre' do perfil"""
        if result.get("markdown"):
            # A seção sobre geralmente tem um cabeçalho específico
            about_pattern = r"(?:## |### )(?:About|Sobre)[^\n]*\n+(.*?)(?:\n## |\n### |$)"
            about_match = re.search(about_pattern, result["markdown"], re.IGNORECASE | re.DOTALL)
            if about_match:
                return about_match.group(1).strip()
        
        return ""
    
    def _extract_experience(self, result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extrai as experiências profissionais do perfil"""
        experiences = []
        
        if result.get("markdown"):
            # A seção de experiência geralmente tem um cabeçalho específico
            exp_section_pattern = r"(?:## |### )(?:Experience|Experiência)[^\n]*\n+(.*?)(?:\n## |\n### |$)"
            exp_section_match = re.search(exp_section_pattern, result["markdown"], re.IGNORECASE | re.DOTALL)
            
            if exp_section_match:
                exp_section = exp_section_match.group(1).strip()
                
                # Padrão para cada experiência individual
                exp_pattern = r"(?:\*\*|\* )([^\n]+)(?:\*\*|\*)\n+(?:\*\*|\* )?([^\n]*)(?:\*\*|\*)?\n+(?:([^\n]*)\n+)?(?:([^\n]*)\n+)?"
                exp_matches = re.finditer(exp_pattern, exp_section)
                
                for match in exp_matches:
                    exp = {}
                    if match.group(1):
                        exp["title"] = match.group(1).strip()
                    if match.group(2):
                        exp["company"] = match.group(2).strip()
                    if match.group(3):
                        exp["duration"] = match.group(3).strip()
                    if match.group(4):
                        exp["location"] = match.group(4).strip()
                    
                    if exp:
                        experiences.append(exp)
        
        return experiences
    
    def _extract_education(self, result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extrai as informações educacionais do perfil"""
        education = []
        
        if result.get("markdown"):
            # A seção de educação geralmente tem um cabeçalho específico
            edu_section_pattern = r"(?:## |### )(?:Education|Educação|Formação)[^\n]*\n+(.*?)(?:\n## |\n### |$)"
            edu_section_match = re.search(edu_section_pattern, result["markdown"], re.IGNORECASE | re.DOTALL)
            
            if edu_section_match:
                edu_section = edu_section_match.group(1).strip()
                
                # Padrão para cada educação individual
                edu_pattern = r"(?:\*\*|\* )([^\n]+)(?:\*\*|\*)\n+(?:\*\*|\* )?([^\n]*)(?:\*\*|\*)?\n+(?:([^\n]*)\n+)?"
                edu_matches = re.finditer(edu_pattern, edu_section)
                
                for match in edu_matches:
                    edu = {}
                    if match.group(1):
                        edu["institution"] = match.group(1).strip()
                    if match.group(2):
                        edu["degree"] = match.group(2).strip()
                    if match.group(3):
                        edu["duration"] = match.group(3).strip()
                    
                    if edu:
                        education.append(edu)
        
        return education
    
    def _extract_skills(self, result: Dict[str, Any]) -> List[str]:
        """Extrai as habilidades do perfil"""
        skills = []
        
        if result.get("markdown"):
            # A seção de habilidades geralmente tem um cabeçalho específico
            skills_section_pattern = r"(?:## |### )(?:Skills|Habilidades|Competências)[^\n]*\n+(.*?)(?:\n## |\n### |$)"
            skills_section_match = re.search(skills_section_pattern, result["markdown"], re.IGNORECASE | re.DOTALL)
            
            if skills_section_match:
                skills_section = skills_section_match.group(1).strip()
                
                # Extrai habilidades de listas
                skills_list_pattern = r"(?:\* |\- )([^\n]+)"
                skills_matches = re.finditer(skills_list_pattern, skills_section)
                
                for match in skills_matches:
                    if match.group(1):
                        skills.append(match.group(1).strip())
        
        return skills
    
    def _extract_recommendations(self, result: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extrai as recomendações do perfil"""
        recommendations = []
        
        if result.get("markdown"):
            # A seção de recomendações geralmente tem um cabeçalho específico
            rec_section_pattern = r"(?:## |### )(?:Recommendations|Recomendações)[^\n]*\n+(.*?)(?:\n## |\n### |$)"
            rec_section_match = re.search(rec_section_pattern, result["markdown"], re.IGNORECASE | re.DOTALL)
            
            if rec_section_match:
                rec_section = rec_section_match.group(1).strip()
                
                # Padrão para cada recomendação individual
                rec_pattern = r"(?:\*\*|\* )([^\n]+)(?:\*\*|\*)\n+(?:\*\*|\* )?([^\n]*)(?:\*\*|\*)?\n+(?:([^\n]*)\n+)?"
                rec_matches = re.finditer(rec_pattern, rec_section)
                
                for match in rec_matches:
                    rec = {}
                    if match.group(1):
                        rec["author"] = match.group(1).strip()
                    if match.group(2):
                        rec["relationship"] = match.group(2).strip()
                    if match.group(3):
                        rec["text"] = match.group(3).strip()
                    
                    if rec:
                        recommendations.append(rec)
        
        return recommendations
    
    def _extract_connections(self, result: Dict[str, Any]) -> str:
        """Extrai o número de conexões do perfil"""
        if result.get("markdown"):
            # O número de conexões geralmente aparece próximo ao nome
            connections_pattern = r"(\d+(?:,\d+)*)\s+(?:connections|conexões)"
            connections_match = re.search(connections_pattern, result["markdown"], re.IGNORECASE)
            if connections_match:
                return connections_match.group(1).strip()
        
        return ""
