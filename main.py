from src.data_collection import get_last_week_file_urls, download_file
from src.data_processing import process_data
from src.data_analysis import analyze_and_generate_report
import os
import glob

def main():
    """
    Orquestra o pipeline completo: coleta, processamento e análise dos dados de queimadas.
    """
    print("--- INICIANDO PIPELINE DE MONITORAMENTO DE QUEIMADAS ---")

    # --- 1. Coleta de Dados ---
    print("\n[ETAPA 1/3] Coletando dados da última semana...")
    LISTING_URL = "https://dataserver-coids.inpe.br/queimadas/queimadas/focos/csv/diario/Brasil/"
    RAW_DATA_DIR = os.path.join("data", "raw")
    
    urls_to_download = get_last_week_file_urls(LISTING_URL)
    
    if not urls_to_download:
        print("Nenhum arquivo novo encontrado para baixar. Análise será feita com dados existentes.")
    else:
        for url in urls_to_download:
            file_name = os.path.basename(url)
            save_path = os.path.join(RAW_DATA_DIR, file_name)
            if not os.path.exists(save_path):
                print(f"Baixando {file_name}...")
                download_file(url, save_path)
            else:
                print(f"Arquivo {file_name} já existe. Pulando download.")

    # --- 2. Processamento de Dados ---
    print("\n[ETAPA 2/3] Processando novos dados...")
    PROCESSED_DATA_DIR = os.path.join("data", "processed")
    
    # Pega todos os arquivos CSV do diretório raw
    all_raw_files = glob.glob(os.path.join(RAW_DATA_DIR, '*.csv'))
    for raw_file_path in all_raw_files:
        file_name = os.path.basename(raw_file_path)
        processed_file_name = os.path.splitext(file_name)[0] + '.parquet'
        processed_file_path = os.path.join(PROCESSED_DATA_DIR, processed_file_name)
        
        # Processa apenas se o arquivo processado ainda não existir
        if not os.path.exists(processed_file_path):
            print(f"Processando {file_name}...")
            process_data(raw_file_path, processed_file_path)
        else:
            print(f"Arquivo {file_name} já foi processado. Pulando.")


    # --- 3. Análise e Geração de Relatório ---
    print("\n[ETAPA 3/3] Gerando relatório de análise...")
    REPORTS_DIR = "reports"
    analyze_and_generate_report(PROCESSED_DATA_DIR, REPORTS_DIR)

    print("\n--- PIPELINE CONCLUÍDO COM SUCESSO! ---")
    print(f"Relatórios gerados na pasta: {REPORTS_DIR}")

if __name__ == "__main__":
    main() 