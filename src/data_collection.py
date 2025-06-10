import requests
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_last_week_file_urls(listing_url: str) -> list:
    """
    Encontra as URLs de todos os arquivos CSV da última semana em uma página de listagem.

    Args:
        listing_url (str): A URL da página que lista os arquivos.

    Returns:
        list: Uma lista de URLs completas dos arquivos da última semana.
    """
    try:
        response = requests.get(listing_url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        
        csv_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.csv')]
        
        if not csv_links:
            print("Nenhum arquivo CSV encontrado na página.")
            return []

        today = datetime.now()
        seven_days_ago = today - timedelta(days=7)
        week_files = []

        for link in csv_links:
            try:
                # Extrai a data do nome do arquivo (ex: focos_diario_br_20240611.csv)
                date_str = link.split('_')[-1].split('.')[0]
                file_date = datetime.strptime(date_str, '%Y%m%d')
                
                if seven_days_ago <= file_date <= today:
                    week_files.append(urljoin(listing_url, link))
            except (ValueError, IndexError):
                # Ignora links que não seguem o padrão de data esperado
                continue
        
        print(f"Encontrados {len(week_files)} arquivos da última semana.")
        return week_files

    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página de listagem de arquivos: {e}")
        return []

def download_file(url: str, save_path: str):
    """
    Baixa um arquivo de uma URL e o salva.

    Args:
        url (str): A URL do arquivo a ser baixado.
        save_path (str): O caminho onde o arquivo será salvo.
    """
    try:
        response = requests.get(url, timeout=60) # Aumentado o timeout para arquivos maiores
        response.raise_for_status()

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Download concluído com sucesso! Arquivo salvo em: {save_path}")

    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer o download do arquivo: {e}")

if __name__ == '__main__':
    # URL da página com a listagem dos arquivos diários
    LISTING_URL = "https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/diario/Brasil/"
    RAW_DATA_DIR = os.path.join("data", "raw")

    urls_to_download = get_last_week_file_urls(LISTING_URL)
    
    if urls_to_download:
        for url in urls_to_download:
            file_name = os.path.basename(url)
            save_path = os.path.join(RAW_DATA_DIR, file_name)
            # Verifica se o arquivo já existe para não baixar novamente
            if not os.path.exists(save_path):
                print(f"Baixando {file_name}...")
                download_file(url, save_path)
            else:
                print(f"Arquivo {file_name} já existe. Pulando o download.") 