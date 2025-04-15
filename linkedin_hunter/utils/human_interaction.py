"""
Utilitários para simular interações humanas durante a navegação
"""

import asyncio
import random
from typing import Optional, Tuple, List

class HumanInteraction:
    """
    Classe para simular interações humanas durante a navegação
    """
    
    @staticmethod
    async def random_scroll(page, min_scrolls: int = 2, max_scrolls: int = 5, 
                           min_distance: int = 100, max_distance: int = 800,
                           min_delay: float = 0.5, max_delay: float = 3.0):
        """
        Realiza rolagens aleatórias na página para simular comportamento humano
        
        Args:
            page: Objeto page do Playwright
            min_scrolls: Número mínimo de rolagens
            max_scrolls: Número máximo de rolagens
            min_distance: Distância mínima de rolagem em pixels
            max_distance: Distância máxima de rolagem em pixels
            min_delay: Atraso mínimo entre rolagens em segundos
            max_delay: Atraso máximo entre rolagens em segundos
        """
        num_scrolls = random.randint(min_scrolls, max_scrolls)
        
        for _ in range(num_scrolls):
            # Determina a distância de rolagem (positiva para baixo, negativa para cima)
            distance = random.randint(min_distance, max_distance)
            
            # Ocasionalmente rola para cima (20% das vezes)
            if random.random() < 0.2 and _ > 0:
                distance = -distance // 2  # Rola para cima com menor distância
            
            # Executa a rolagem
            await page.evaluate(f"window.scrollBy(0, {distance})")
            
            # Aguarda um tempo aleatório entre rolagens
            await asyncio.sleep(random.uniform(min_delay, max_delay))
    
    @staticmethod
    async def random_mouse_movement(page, num_movements: int = 3):
        """
        Realiza movimentos aleatórios do mouse na página
        
        Args:
            page: Objeto page do Playwright
            num_movements: Número de movimentos aleatórios
        """
        # Obtém as dimensões da viewport
        viewport_size = await page.evaluate("""
            () => {
                return {
                    width: window.innerWidth,
                    height: window.innerHeight
                }
            }
        """)
        
        width = viewport_size['width']
        height = viewport_size['height']
        
        for _ in range(num_movements):
            # Gera coordenadas aleatórias dentro da viewport
            x = random.randint(0, width)
            y = random.randint(0, height)
            
            # Move o mouse para a posição aleatória
            await page.mouse.move(x, y)
            
            # Pequena pausa entre movimentos
            await asyncio.sleep(random.uniform(0.1, 0.5))
    
    @staticmethod
    async def human_like_typing(page, selector: str, text: str, 
                               min_delay: float = 0.05, max_delay: float = 0.2):
        """
        Simula digitação humana com velocidade variável
        
        Args:
            page: Objeto page do Playwright
            selector: Seletor CSS do elemento onde digitar
            text: Texto a ser digitado
            min_delay: Atraso mínimo entre teclas em segundos
            max_delay: Atraso máximo entre teclas em segundos
        """
        # Clica no elemento
        await page.click(selector)
        
        # Limpa o campo (se necessário)
        await page.fill(selector, "")
        
        # Digita caractere por caractere com atrasos variáveis
        for char in text:
            # Digita um caractere
            await page.type(selector, char, delay=0)
            
            # Pausa aleatória entre caracteres
            typing_delay = random.uniform(min_delay, max_delay)
            
            # Pausa ocasionalmente mais longa (como um humano pensando)
            if random.random() < 0.1:
                typing_delay *= 3
                
            await asyncio.sleep(typing_delay)
    
    @staticmethod
    async def random_non_critical_clicks(page, selectors: List[str], 
                                        click_probability: float = 0.3):
        """
        Realiza cliques aleatórios em elementos não críticos da página
        
        Args:
            page: Objeto page do Playwright
            selectors: Lista de seletores CSS de elementos não críticos
            click_probability: Probabilidade de clicar em cada elemento
        """
        for selector in selectors:
            # Verifica se o elemento existe
            element_exists = await page.evaluate(f"""
                () => {{
                    return document.querySelector('{selector}') !== null;
                }}
            """)
            
            if element_exists and random.random() < click_probability:
                try:
                    # Rola até o elemento
                    await page.evaluate(f"""
                        () => {{
                            const element = document.querySelector('{selector}');
                            if (element) {{
                                element.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                            }}
                        }}
                    """)
                    
                    # Pequena pausa antes de clicar
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    
                    # Clica no elemento
                    await page.click(selector)
                    
                    # Pausa após o clique
                    await asyncio.sleep(random.uniform(1.0, 3.0))
                    
                    # Se abriu uma nova página ou modal, fecha
                    if random.random() < 0.5:
                        await page.keyboard.press("Escape")
                        await asyncio.sleep(random.uniform(0.5, 1.0))
                        
                except Exception:
                    # Ignora erros ao clicar em elementos não críticos
                    pass
    
    @staticmethod
    async def view_profile_sections(page):
        """
        Simula um usuário visualizando diferentes seções de um perfil do LinkedIn
        
        Args:
            page: Objeto page do Playwright
        """
        # Lista de seletores de seções comuns em perfis do LinkedIn
        section_selectors = [
            "section#experience",
            "section#education",
            "section#skills",
            "section#recommendations",
            "section#interests",
            "section#about",
            "section#volunteering",
            "section#accomplishments"
        ]
        
        # Seleciona algumas seções aleatoriamente para visualizar
        num_sections = random.randint(2, min(5, len(section_selectors)))
        selected_sections = random.sample(section_selectors, num_sections)
        
        for selector in selected_sections:
            try:
                # Verifica se a seção existe
                section_exists = await page.evaluate(f"""
                    () => {{
                        return document.querySelector('{selector}') !== null;
                    }}
                """)
                
                if section_exists:
                    # Rola até a seção
                    await page.evaluate(f"""
                        () => {{
                            const section = document.querySelector('{selector}');
                            if (section) {{
                                section.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                            }}
                        }}
                    """)
                    
                    # Pausa para "ler" a seção
                    await asyncio.sleep(random.uniform(2.0, 5.0))
                    
                    # Ocasionalmente expande seções colapsadas
                    expand_buttons = await page.query_selector_all(f"{selector} button.expand")
                    if expand_buttons and random.random() < 0.7:
                        await random.choice(expand_buttons).click()
                        await asyncio.sleep(random.uniform(1.0, 3.0))
            
            except Exception:
                # Ignora erros ao interagir com seções
                continue
    
    @staticmethod
    async def simulate_human_behavior(page, is_profile_page: bool = False):
        """
        Simula um conjunto de comportamentos humanos em uma página
        
        Args:
            page: Objeto page do Playwright
            is_profile_page: Se True, aplica comportamentos específicos para páginas de perfil
        """
        # Movimento inicial do mouse
        await HumanInteraction.random_mouse_movement(page, num_movements=2)
        
        # Rolagem inicial
        await HumanInteraction.random_scroll(page, min_scrolls=1, max_scrolls=3)
        
        # Se for uma página de perfil, visualiza seções específicas
        if is_profile_page:
            await HumanInteraction.view_profile_sections(page)
        else:
            # Para páginas genéricas, faz mais rolagens
            await HumanInteraction.random_scroll(page, min_scrolls=2, max_scrolls=4)
        
        # Elementos não críticos que podem ser clicados em qualquer página do LinkedIn
        non_critical_selectors = [
            "button.artdeco-pill",  # Filtros
            "button.artdeco-tab",   # Abas
            ".artdeco-dropdown",    # Dropdowns
            ".share-box-feed-entry__trigger", # Caixa "Começar publicação"
            ".feed-shared-social-actions", # Botões de reação
            ".artdeco-pagination__button:not([disabled])" # Botões de paginação
        ]
        
        # Cliques aleatórios em elementos não críticos
        await HumanInteraction.random_non_critical_clicks(
            page, 
            non_critical_selectors,
            click_probability=0.2
        )
        
        # Rolagem final
        await HumanInteraction.random_scroll(page, min_scrolls=1, max_scrolls=2)
        
        # Movimento final do mouse
        await HumanInteraction.random_mouse_movement(page, num_movements=1)
