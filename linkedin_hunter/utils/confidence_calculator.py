"""
Módulo para calcular a confiabilidade da correspondência entre dados de entrada e perfil
"""

import re
from typing import Dict, Any, List, Optional
from difflib import SequenceMatcher

class ConfidenceCalculator:
    """
    Calcula a confiabilidade da correspondência entre os dados de entrada e o perfil encontrado
    """
    
    def calculate_confidence(self, input_data: Dict[str, str], profile_data: Dict[str, Any]) -> float:
        """
        Calcula o score de confiança
        
        Args:
            input_data: Dados de entrada (nome, email, empresa)
            profile_data: Dados extraídos do perfil
            
        Returns:
            float: Score de confiança (0-100%)
        """
        score = 0
        total_weight = 0
        
        # Verificar correspondência de nome (peso 40)
        name_score = self._compare_names(input_data.get('name', ''), profile_data.get('full_name', ''))
        score += name_score * 40
        total_weight += 40
        
        # Verificar correspondência de empresa (peso 30)
        company_score = self._compare_company(input_data.get('company', ''), profile_data.get('experience', []))
        score += company_score * 30
        total_weight += 30
        
        # Verificar correspondência de email (peso 30)
        # Isso é mais difícil, pois o email raramente está no perfil
        # Podemos verificar se o nome de usuário do email aparece no nome ou em outras partes do perfil
        email_score = self._compare_email(input_data.get('email', ''), profile_data)
        score += email_score * 30
        total_weight += 30
        
        # Calcular porcentagem final
        if total_weight > 0:
            final_score = (score / total_weight) * 100
        else:
            final_score = 0
        
        return round(final_score, 2)
    
    def _compare_names(self, input_name: str, profile_name: str) -> float:
        """
        Compara nomes e retorna score de 0 a 1
        
        Args:
            input_name: Nome fornecido como entrada
            profile_name: Nome extraído do perfil
            
        Returns:
            float: Score de similaridade (0-1)
        """
        if not input_name or not profile_name:
            return 0
        
        # Normaliza os nomes (remove acentos, converte para minúsculas)
        input_name = self._normalize_text(input_name)
        profile_name = self._normalize_text(profile_name)
        
        # Verifica correspondência exata
        if input_name == profile_name:
            return 1.0
        
        # Verifica se todos os tokens do input_name estão no profile_name
        input_tokens = set(input_name.split())
        profile_tokens = set(profile_name.split())
        
        if input_tokens.issubset(profile_tokens):
            return 0.9
        
        # Verifica se o primeiro e último nome correspondem
        input_parts = input_name.split()
        profile_parts = profile_name.split()
        
        if len(input_parts) >= 2 and len(profile_parts) >= 2:
            if input_parts[0] == profile_parts[0] and input_parts[-1] == profile_parts[-1]:
                return 0.8
        
        # Calcula similaridade usando SequenceMatcher
        similarity = SequenceMatcher(None, input_name, profile_name).ratio()
        
        # Ajusta a similaridade para dar mais peso a correspondências parciais
        if similarity > 0.7:
            return similarity
        
        # Verifica iniciais
        if self._check_initials(input_name, profile_name):
            return 0.6
        
        return similarity
    
    def _compare_company(self, input_company: str, experiences: List[Dict[str, str]]) -> float:
        """
        Compara empresa com experiências e retorna score de 0 a 1
        
        Args:
            input_company: Empresa fornecida como entrada
            experiences: Lista de experiências extraídas do perfil
            
        Returns:
            float: Score de similaridade (0-1)
        """
        if not input_company or not experiences:
            return 0
        
        # Normaliza o nome da empresa
        input_company = self._normalize_text(input_company)
        
        # Verifica se a empresa aparece como experiência atual
        current_experience = self._get_current_experience(experiences)
        if current_experience:
            company_name = self._normalize_text(current_experience.get('company', ''))
            
            # Correspondência exata
            if input_company == company_name:
                return 1.0
            
            # Correspondência parcial
            similarity = SequenceMatcher(None, input_company, company_name).ratio()
            if similarity > 0.7:
                return similarity
            
            # Verifica se uma é substring da outra
            if input_company in company_name or company_name in input_company:
                return 0.8
        
        # Verifica todas as experiências
        max_similarity = 0
        for exp in experiences:
            company_name = self._normalize_text(exp.get('company', ''))
            
            # Correspondência exata
            if input_company == company_name:
                return 0.9  # Um pouco menos que atual, mas ainda alta
            
            # Correspondência parcial
            similarity = SequenceMatcher(None, input_company, company_name).ratio()
            max_similarity = max(max_similarity, similarity)
            
            # Verifica se uma é substring da outra
            if input_company in company_name or company_name in input_company:
                max_similarity = max(max_similarity, 0.7)
        
        return max_similarity
    
    def _compare_email(self, input_email: str, profile_data: Dict[str, Any]) -> float:
        """
        Compara email com dados do perfil e retorna score de 0 a 1
        
        Args:
            input_email: Email fornecido como entrada
            profile_data: Dados extraídos do perfil
            
        Returns:
            float: Score de similaridade (0-1)
        """
        if not input_email:
            return 0
        
        # Extrai username do email
        username_match = re.match(r'^([^@]+)@', input_email)
        if not username_match:
            return 0
        
        username = username_match.group(1).lower()
        
        # Verifica se o username aparece no nome
        full_name = self._normalize_text(profile_data.get('full_name', ''))
        if username in full_name.replace(' ', '').lower():
            return 0.8
        
        # Verifica se o username é uma combinação de partes do nome
        name_parts = full_name.lower().split()
        if len(name_parts) >= 2:
            # Verifica padrões comuns: nome.sobrenome, nome_sobrenome, inicial+sobrenome
            first_name = name_parts[0]
            last_name = name_parts[-1]
            
            patterns = [
                f"{first_name}.{last_name}",
                f"{first_name}_{last_name}",
                f"{first_name}{last_name}",
                f"{first_name[0]}{last_name}",
            ]
            
            for pattern in patterns:
                if username == pattern:
                    return 0.9
                
                similarity = SequenceMatcher(None, username, pattern).ratio()
                if similarity > 0.8:
                    return 0.7
        
        # Verifica se o domínio do email corresponde à empresa atual
        email_domain = input_email.split('@')[-1].lower()
        current_experience = self._get_current_experience(profile_data.get('experience', []))
        
        if current_experience:
            company_name = self._normalize_text(current_experience.get('company', '')).lower()
            company_words = re.findall(r'\w+', company_name)
            
            # Verifica se alguma palavra da empresa aparece no domínio do email
            for word in company_words:
                if len(word) > 3 and word in email_domain:
                    return 0.6
        
        # Baixa confiança se nada corresponder
        return 0.2
    
    def _normalize_text(self, text: str) -> str:
        """
        Normaliza texto para comparação (remove acentos, converte para minúsculas)
        
        Args:
            text: Texto para normalizar
            
        Returns:
            str: Texto normalizado
        """
        import unicodedata
        
        # Remove acentos
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
        
        # Converte para minúsculas e remove espaços extras
        text = text.lower().strip()
        
        return text
    
    def _check_initials(self, input_name: str, profile_name: str) -> bool:
        """
        Verifica se as iniciais correspondem
        
        Args:
            input_name: Nome fornecido como entrada
            profile_name: Nome extraído do perfil
            
        Returns:
            bool: True se as iniciais corresponderem
        """
        # Obtém iniciais do input_name
        input_initials = ''.join(word[0] for word in input_name.split() if word)
        
        # Obtém iniciais do profile_name
        profile_initials = ''.join(word[0] for word in profile_name.split() if word)
        
        # Verifica se as iniciais correspondem
        return input_initials == profile_initials
    
    def _get_current_experience(self, experiences: List[Dict[str, str]]) -> Optional[Dict[str, str]]:
        """
        Obtém a experiência atual (mais recente) do perfil
        
        Args:
            experiences: Lista de experiências extraídas do perfil
            
        Returns:
            Optional[Dict[str, str]]: Experiência atual ou None
        """
        if not experiences:
            return None
        
        # Assume que a primeira experiência na lista é a mais recente
        return experiences[0]
