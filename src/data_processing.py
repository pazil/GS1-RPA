import pandas as pd
import os
import glob

def process_data(raw_file_path: str, processed_file_path: str):
    """
    Lê os dados brutos, limpa e os salva em formato Parquet.

    Args:
        raw_file_path (str): Caminho do arquivo de dados brutos.
        processed_file_path (str): Caminho para salvar o arquivo processado.
    """
    try:
        # Carrega o arquivo CSV
        df = pd.read_csv(raw_file_path)

        # Limpeza e Transformação
        # Converte a coluna de data para datetime
        df['data_hora_gmt'] = pd.to_datetime(df['data_hora_gmt'], format='%Y-%m-%d %H:%M:%S')

        # Verifica valores ausentes (exemplo: preenchendo com 0 para dias sem chuva)
        df['numero_dias_sem_chuva'].fillna(0, inplace=True)
        # Converte para inteiro, pois não precisamos da parte decimal
        df['numero_dias_sem_chuva'] = df['numero_dias_sem_chuva'].astype(int)

        # Padroniza os nomes de colunas (opcional, mas boa prática)
        df.columns = [col.strip().lower() for col in df.columns]

        # Garante que o diretório de destino exista
        os.makedirs(os.path.dirname(processed_file_path), exist_ok=True)
        
        # Salva o dataframe processado em formato Parquet
        df.to_parquet(processed_file_path, index=False)
        
        print(f"Dados processados e salvos com sucesso em: {processed_file_path}")
        print("\nAmostra dos dados processados:")
        print(df.head())
        print("\nInformações do DataFrame:")
        df.info()

    except FileNotFoundError:
        print(f"Erro: O arquivo {raw_file_path} não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro durante o processamento dos dados: {e}")

if __name__ == '__main__':
    # Esta parte é para execução de teste do módulo individualmente
    RAW_DATA_DIR = os.path.join("data", "raw")
    PROCESSED_DATA_DIR = os.path.join("data", "processed")
    
    # Encontra o arquivo mais recente para o teste
    list_of_files = glob.glob(os.path.join(RAW_DATA_DIR, '*.csv'))
    if not list_of_files:
        print("Nenhum arquivo de dados brutos encontrado para processar.")
    else:
        latest_raw_file = max(list_of_files, key=os.path.getctime)
        
        # Define o nome do arquivo processado com base no original
        file_name = os.path.basename(latest_raw_file)
        processed_file_name = os.path.splitext(file_name)[0] + '.parquet'
        processed_file_path = os.path.join(PROCESSED_DATA_DIR, processed_file_name)
        
        process_data(latest_raw_file, processed_file_path) 