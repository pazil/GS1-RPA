import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

def find_latest_processed_file(processed_data_dir: str) -> str:
    """
    Encontra o arquivo processado mais recente no diretório.

    Args:
        processed_data_dir (str): O caminho para o diretório de dados processados.

    Returns:
        str: O caminho para o arquivo mais recente, ou None se o diretório estiver vazio.
    """
    list_of_files = glob.glob(os.path.join(processed_data_dir, '*.parquet'))
    if not list_of_files:
        return None
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file

def load_weekly_data(processed_data_dir: str) -> pd.DataFrame:
    """
    Carrega todos os arquivos de dados processados da última semana e os combina.

    Args:
        processed_data_dir (str): O caminho para o diretório de dados processados.

    Returns:
        pd.DataFrame: Um DataFrame contendo todos os dados da semana, ou um DataFrame vazio.
    """
    today = datetime.now()
    seven_days_ago = today - timedelta(days=7)
    all_files = glob.glob(os.path.join(processed_data_dir, '*.parquet'))
    
    weekly_dfs = []
    for f in all_files:
        try:
            # Extrai a data do nome do arquivo
            date_str = os.path.basename(f).split('_')[-1].split('.')[0]
            file_date = datetime.strptime(date_str, '%Y%m%d')
            if seven_days_ago <= file_date <= today:
                df = pd.read_parquet(f)
                weekly_dfs.append(df)
        except (ValueError, IndexError):
            continue
    
    if not weekly_dfs:
        return pd.DataFrame()
        
    return pd.concat(weekly_dfs, ignore_index=True)

def generate_hourly_chart(df: pd.DataFrame, reports_dir: str, location_name: str = "Brasil"):
    """Gera e salva um gráfico da distribuição de focos por hora."""
    
    # Garante que a coluna 'hora' exista
    if 'data_hora_gmt' in df.columns and pd.api.types.is_datetime64_any_dtype(df['data_hora_gmt']):
        df['hora'] = df['data_hora_gmt'].dt.hour
    
    if df.empty or 'hora' not in df.columns:
        print(f"Não há dados para gerar o gráfico horário para {location_name}.")
        # Se o gráfico antigo existir, remove para não mostrar dados desatualizados
        path_grafico_hora = os.path.join(reports_dir, 'focos_por_hora.png')
        if os.path.exists(path_grafico_hora):
            os.remove(path_grafico_hora)
        return

    focos_por_hora = df['hora'].value_counts().sort_index().reset_index()
    focos_por_hora.columns = ['Hora', 'Total de Focos']

    plt.figure(figsize=(12, 7))
    sns.lineplot(data=focos_por_hora, x='Hora', y='Total de Focos', marker='o', color='red')
    title = f'Distribuição de Focos por Hora - {location_name}'
    plt.title(title)
    plt.xlabel('Hora do Dia')
    plt.ylabel('Total de Focos')
    plt.xticks(range(0, 24))
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    path_grafico_hora = os.path.join(reports_dir, 'focos_por_hora.png')
    plt.savefig(path_grafico_hora)
    plt.close()
    print(f"Gráfico de focos por hora ({location_name}) salvo em: {path_grafico_hora}")

def generate_top_chart(df: pd.DataFrame, reports_dir: str, level: str = 'estado'):
    """Gera o gráfico de Top 10 para estados ou municípios."""
    col_name = level
    title_name = 'Estados' if level == 'estado' else 'Municípios'
    path_grafico = os.path.join(reports_dir, 'focos_por_localidade.png')

    if df.empty or col_name not in df.columns:
        if os.path.exists(path_grafico): os.remove(path_grafico)
        return

    focos_counts = df[col_name].value_counts().nlargest(10).reset_index()
    focos_counts.columns = [title_name, 'Total de Focos']

    plt.figure(figsize=(12, 8))
    sns.barplot(data=focos_counts, x='Total de Focos', y=title_name, hue=title_name, palette='viridis', legend=False)
    plt.title(f'Top 10 {title_name} com Mais Focos de Queimada')
    plt.xlabel('Total de Focos')
    plt.ylabel(title_name)
    plt.tight_layout()
    plt.savefig(path_grafico)
    plt.close()
    print(f"Gráfico de Top 10 {title_name} salvo em: {path_grafico}")

def generate_biome_chart(df: pd.DataFrame, reports_dir: str):
    """Gera o gráfico de distribuição por bioma para o DataFrame fornecido."""
    path_grafico = os.path.join(reports_dir, 'focos_por_bioma.png')
    if df.empty or 'bioma' not in df.columns or df['bioma'].nunique() == 0:
        if os.path.exists(path_grafico): os.remove(path_grafico)
        return

    focos_por_bioma = df['bioma'].value_counts().reset_index()
    focos_por_bioma.columns = ['Bioma', 'Total de Focos']

    plt.figure(figsize=(10, 7))
    sns.barplot(data=focos_por_bioma, x='Total de Focos', y='Bioma', hue='Bioma', palette='plasma', legend=False)
    plt.title('Total de Focos de Queimada por Bioma')
    plt.xlabel('Total de Focos')
    plt.ylabel('Bioma')
    plt.tight_layout()
    plt.savefig(path_grafico)
    plt.close()
    print(f"Gráfico de focos por bioma salvo em: {path_grafico}")

def calculate_risk_df(df: pd.DataFrame, level: str = 'municipio') -> pd.DataFrame:
    """Calcula e retorna um DataFrame com as localidades em risco (estado ou município)."""
    if df.empty or level not in df.columns:
        return pd.DataFrame()

    risk_df = df.groupby(level).agg(
        total_focos=('id', 'count'),
        media_dias_sem_chuva=('numero_dias_sem_chuva', 'mean'),
        media_frp=('frp', 'mean')
    ).reset_index()

    risk_df['media_frp'].fillna(0, inplace=True)
    
    # Normaliza os dados para o cálculo do índice
    for col in ['total_focos', 'media_dias_sem_chuva', 'media_frp']:
        range_val = risk_df[col].max() - risk_df[col].min()
        if range_val > 0:
            risk_df[col + '_norm'] = (risk_df[col] - risk_df[col].min()) / range_val
        else:
            risk_df[col + '_norm'] = 0

    risk_df['indice_risco'] = (
        risk_df['total_focos_norm'] * 0.5 + 
        risk_df['media_dias_sem_chuva_norm'] * 0.3 + 
        risk_df['media_frp_norm'] * 0.2
    )

    top_critical = risk_df.sort_values(by='indice_risco', ascending=False).head(15)
    
    # Renomeia a coluna de localidade para um nome genérico para o app
    top_critical.rename(columns={level: 'Localidade'}, inplace=True)
    
    return top_critical[['Localidade', 'total_focos', 'media_dias_sem_chuva', 'media_frp', 'indice_risco']]

def analyze_and_generate_report(processed_data_dir: str, reports_dir: str):
    """
    Carrega os dados da semana e gera um relatório completo para o Brasil.
    """
    try:
        df = load_weekly_data(processed_data_dir)
        if df.empty:
            print("Nenhum dado da última semana encontrado para análise.")
            return

        print(f"Dados da semana carregados com sucesso! Total de {len(df)} registros.")
        os.makedirs(reports_dir, exist_ok=True)
        
        # --- Gráfico Comparativo Semanal (sempre para o Brasil todo) ---
        df['data'] = df['data_hora_gmt'].dt.date
        focos_por_dia = df.groupby('data')['id'].count().reset_index()
        focos_por_dia.columns = ['Data', 'Total de Focos']
        plt.figure(figsize=(12, 7))
        sns.barplot(data=focos_por_dia, x='Data', y='Total de Focos', color='royalblue')
        plt.title('Focos de Queimada nos Últimos 7 Dias (Brasil)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        path_grafico_semanal = os.path.join(reports_dir, 'focos_semanal.png')
        plt.savefig(path_grafico_semanal)
        plt.close()
        print(f"Gráfico do comparativo semanal salvo em: {path_grafico_semanal}")

        # --- Gera as análises para o Brasil todo para o pipeline não-interativo ---
        generate_top_chart(df, reports_dir, level='estado')
        generate_biome_chart(df, reports_dir)
        
        # Salva a tabela de risco por MUNICÍPIO por padrão para o pipeline não-interativo
        df_risco = calculate_risk_df(df, level='municipio')
        path_tabela_risco = os.path.join(reports_dir, 'tabela_risco_municipios.csv')
        df_risco.to_csv(path_tabela_risco, index=False)
        print(f"Tabela de municípios em risco salva em: {path_tabela_risco}")

    except FileNotFoundError:
        print(f"Erro: O diretório {processed_data_dir} não foi encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro durante a análise e geração de relatório: {e}")

if __name__ == '__main__':
    # Esta parte é para execução de teste do módulo individualmente
    PROCESSED_DATA_DIR = os.path.join("data", "processed")
    REPORTS_DIR = "reports"
    
    # Encontra o arquivo mais recente para o teste
    latest_processed_file = find_latest_processed_file(PROCESSED_DATA_DIR)
    
    if latest_processed_file:
        analyze_and_generate_report(PROCESSED_DATA_DIR, REPORTS_DIR)
    else:
        print("Nenhum arquivo de dados processados encontrado para analisar.") 