import streamlit as st
import pandas as pd
import os
from main import main as run_pipeline
from src.data_analysis import (
    load_weekly_data, 
    generate_hourly_chart,
    generate_top_chart,
    generate_biome_chart,
    calculate_risk_df
)
import glob

# Configuração da página
st.set_page_config(page_title="Monitor de Queimadas", layout="wide")

# Título da Aplicação
st.title("🔥 Monitor de Queimadas no Brasil")
st.markdown("Dashboard interativo para análise de focos de queimadas da última semana.")

# Botão para executar o pipeline
if st.button("Atualizar e Analisar Novos Dados"):
    with st.spinner("Executando o pipeline completo... Por favor, aguarde."):
        try:
            run_pipeline()
            st.success("Pipeline executado com sucesso! Os dados foram atualizados.")
        except Exception as e:
            st.error(f"Ocorreu um erro durante a execução do pipeline: {e}")

# --- Carregamento dos Dados e Definição de Caminhos ---
REPORTS_DIR = "reports"
PROCESSED_DATA_DIR = os.path.join("data", "processed")
df_semana = load_weekly_data(PROCESSED_DATA_DIR)

# --- Layout Principal ---
if not df_semana.empty:
    st.sidebar.header("Filtros de Análise")
    
    # --- Filtro Principal de Estado (na barra lateral) ---
    estados = ['Brasil (Todos)'] + sorted(df_semana['estado'].unique().tolist())
    estado_selecionado = st.sidebar.selectbox("Selecione uma Localidade", estados)

    # Filtra dados com base no estado e define o nível de análise
    if estado_selecionado != 'Brasil (Todos)':
        df_analise = df_semana[df_semana['estado'] == estado_selecionado]
        level_top_chart = 'municipio'
        level_risk_table = 'municipio'
        titulo_localidade = estado_selecionado
    else:
        df_analise = df_semana
        level_top_chart = 'estado'
        level_risk_table = 'estado'
        titulo_localidade = 'Brasil'

    # --- Filtro de Dia (na barra lateral) ---
    dias = ['Todos os Dias'] + sorted(df_analise['data_hora_gmt'].dt.date.unique().tolist())
    dia_selecionado = st.sidebar.selectbox("Selecione o Dia (para análise horária)", dias)

    st.header(f"Análise Detalhada para: {titulo_localidade}")

    # --- Gera e Exibe Análises Dinâmicas ---
    
    # 1. Tabela de Risco
    st.subheader(f"Localidades em Situação Crítica em {titulo_localidade}")
    df_risco = calculate_risk_df(df_analise, level=level_risk_table)
    if not df_risco.empty:
        st.dataframe(df_risco.style.format({
            'media_dias_sem_chuva': '{:.1f}',
            'media_frp': '{:.1f}',
            'indice_risco': '{:.2f}'
        }))
    else:
        st.info("Nenhum foco de queimada registrado para esta localidade na última semana.")

    # Gera os gráficos dinâmicos
    generate_top_chart(df_analise, REPORTS_DIR, level=level_top_chart)
    generate_biome_chart(df_analise, REPORTS_DIR)

    # 2. Gráficos de Topo e Bioma
    col1, col2 = st.columns(2)
    path_grafico_localidade = os.path.join(REPORTS_DIR, 'focos_por_localidade.png')
    path_grafico_bioma = os.path.join(REPORTS_DIR, 'focos_por_bioma.png')

    with col1:
        if os.path.exists(path_grafico_localidade):
            st.image(path_grafico_localidade, use_column_width=True)
        else:
            st.info("Sem dados para o gráfico de localidades.")
    with col2:
        if os.path.exists(path_grafico_bioma):
            st.image(path_grafico_bioma, use_column_width=True)
        else:
            st.info("Sem dados para o gráfico de biomas.")
            
    # 3. Análise Horária (simplificada)
    st.subheader("Análise Horária Detalhada")
    
    # Aplica o filtro de dia para a análise horária
    df_horaria = df_analise.copy()
    location_name = titulo_localidade
    
    if dia_selecionado != 'Todos os Dias':
        df_horaria = df_horaria[df_horaria['data_hora_gmt'].dt.date == dia_selecionado]
        location_name += f" - {dia_selecionado.strftime('%d/%m/%Y')}"
        
    generate_hourly_chart(df_horaria, REPORTS_DIR, location_name)
    path_grafico_hora = os.path.join(REPORTS_DIR, 'focos_por_hora.png')
    if os.path.exists(path_grafico_hora):
        st.image(path_grafico_hora, use_column_width=True)
    else:
        st.warning("Não há dados de focos para a seleção horária atual.")

else:
    st.info("Clique no botão 'Atualizar e Analisar Novos Dados' para carregar os dados.") 