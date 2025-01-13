import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import random
from typing import List, Dict
from urllib.parse import quote_plus

class AINewsCrawler:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
        ]
        self.news_data = []

    def get_random_headers(self):
        """Gera headers aleatórios para cada requisição"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        }

    def fetch_page(self, url: str) -> str:
        """Busca página com tratamento de erros e delays"""
        try:
            time.sleep(random.uniform(2, 4))
            response = requests.get(url, headers=self.get_random_headers(), timeout=15)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Erro ao acessar {url}: {str(e)}")
            return ""

    def crawl_google_news(self, query: str) -> List[Dict]:
        """Crawl Google News pela query especificada"""
        news_list = []
        encoded_query = quote_plus(query)
        base_url = f"https://news.google.com/search?q={encoded_query}&hl=pt-BR&gl=BR&ceid=BR:pt-419"

        try:
            html = self.fetch_page(base_url)
            if not html:
                return news_list

            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.find_all('article', class_='MQsxIb')

            for article in articles[:20]:  # Limita a 20 artigos por busca
                try:
                    title_elem = article.find('h3')
                    link_elem = article.find('a')
                    source_elem = article.find('div', 'QmrVtf')
                    time_elem = article.find('time')

                    if title_elem and link_elem:
                        news_list.append({
                            'title': title_elem.text.strip(),
                            'link': f"https://news.google.com{link_elem['href'][1:]}",
                            'source': source_elem.text.strip() if source_elem else "Google News",
                            'date': time_elem['datetime'] if time_elem else datetime.now().strftime('%Y-%m-%d'),
                            'origin': 'Google News'
                        })

                except Exception as e:
                    print(f"Erro ao processar artigo do Google News: {str(e)}")
                    continue

        except Exception as e:
            print(f"Erro ao crawlear Google News: {str(e)}")

        return news_list

    def crawl_bing_news(self, query: str) -> List[Dict]:
        """Crawl Bing News pela query especificada"""
        news_list = []
        encoded_query = quote_plus(query)
        base_url = f"https://www.bing.com/news/search?q={encoded_query}&setlang=pt-BR"

        try:
            html = self.fetch_page(base_url)
            if not html:
                return news_list

            soup = BeautifulSoup(html, 'html.parser')
            articles = soup.find_all('div', class_='news-card newsitem cardcommon')

            for article in articles[:20]:  # Limita a 20 artigos por busca
                try:
                    title_elem = article.find('a', class_='title')
                    source_elem = article.find('div', class_='source')
                    time_elem = article.find('span', class_='timestamp')

                    if title_elem:
                        news_list.append({
                            'title': title_elem.text.strip(),
                            'link': title_elem['href'],
                            'source': source_elem.text.strip() if source_elem else "Bing News",
                            'date': time_elem.text.strip() if time_elem else datetime.now().strftime('%Y-%m-%d'),
                            'origin': 'Bing News'
                        })

                except Exception as e:
                    print(f"Erro ao processar artigo do Bing News: {str(e)}")
                    continue

        except Exception as e:
            print(f"Erro ao crawlear Bing News: {str(e)}")

        return news_list

    def run(self, query: str):
        """Execute crawler em todas as fontes configuradas"""
        print('Iniciando coleta de notícias...')
        
        # Lista para armazenar todas as queries
        queries = [
            query,
            f"{query} inteligência artificial",
            f"{query} artificial intelligence",
            f"{query} AI",
            f"{query} machine learning"
        ]
        
        # Coleta notícias para cada query
        for q in queries:
            print(f'\nBuscando notícias para: "{q}"')
            
            # Coleta do Google News
            print('Coletando do Google News...')
            google_news = self.crawl_google_news(q)
            if google_news:
                self.news_data.extend(google_news)
                print(f'Encontradas {len(google_news)} notícias no Google News')
            
            # Coleta do Bing News
            print('Coletando do Bing News...')
            bing_news = self.crawl_bing_news(q)
            if bing_news:
                self.news_data.extend(bing_news)
                print(f'Encontradas {len(bing_news)} notícias no Bing News')
            
            time.sleep(random.uniform(2, 4))  # Delay entre queries
        
        # Remove duplicatas baseado no título
        self.news_data = list({article['title']: article for article in self.news_data}.values())
        
        if self.news_data:
            self.save_to_csv()
            print(f'\nColeta finalizada. Total de notícias únicas: {len(self.news_data)}')
        else:
            print('\nNenhuma notícia encontrada.')

    def save_to_csv(self, filename='ai_news.csv'):
        """Salva as notícias coletadas em um arquivo CSV"""
        if not self.news_data:
            return
            
        df = pd.DataFrame(self.news_data)
        df['data_coleta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Ordena por data de coleta (mais recentes primeiro)
        df = df.sort_values('data_coleta', ascending=False)
        
        # Salva com encoding UTF-8
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f'Dados salvos em {filename}')
        
        # Mostra um resumo das fontes
        print('\nResumo das fontes:')
        print(df['origin'].value_counts())

# Exemplo de uso
if __name__ == '__main__':
    crawler = AINewsCrawler()
    
    # Exemplo de busca por notícias sobre ChatGPT
    crawler.run("ChatGPT")

     