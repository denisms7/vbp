import streamlit as st
import pandas as pd
from Dashboard import obter_dados
from components.graficos import rodape

# Configuração da página
st.set_page_config(
    page_title="PMCS - VBP - SEAB",
    page_icon="📊",
    layout="wide",
)


df = obter_dados()

safra = (df["Safra"].dropna().astype(str).sort_values().unique())
cultura = (df["Cultura"].dropna().astype(str).sort_values().unique())
municipio = (df["Município"].dropna().astype(str).sort_values().unique())
csv = df.to_csv(index=False, sep=";", encoding="utf-8-sig")

num_linhas = len(df)
num_safras = len(safra)
num_cultura = len(cultura)
num_municipio = len(municipio)

st.subheader("Dados", divider=True)

# Link da fonte
st.markdown(
    'Fonte de Dados: <a href="https://www.agricultura.pr.gov.br/vbp" target="_blank">'
    'SEAB/PR - VBP</a>',
    unsafe_allow_html=True
)

# Criando colunas para métricas
col1, col2, col3 = st.columns(3)
col1.metric("Linhas", num_linhas)
col2.metric("Municípios", num_municipio)
col3.metric("Culturas", num_cultura)

col4, col5, col6 = st.columns(3)
col4.metric("Safras/Anos", num_safras)
col5.metric("Safra Inicial", safra.min())
col6.metric("Safra Final", safra.max())


st.download_button(
    label="📥 Exportar Dados",
    data=csv,
    file_name="Dados-VBP.csv",
    mime="text/csv",
)


st.subheader("Dados Alterados", divider=True)

codigo = """
    # Correcao Nomes
    df["Município"] = df["Município"].replace("RANCHO ALEGRE DO OESTE", "RANCHO ALEGRE D'OESTE")
    df["Município"] = df["Município"].replace("SANTA CRUZ DO MONTE CASTELO", "SANTA CRUZ DE MONTE CASTELO")
    df["Município"] = df["Município"].replace("SANTA IZABEL DO IVAI", "SANTA ISABEL DO IVAI")
    df["Município"] = df["Município"].replace("SANTA TEREZINHA DO ITAIPU", "SANTA TEREZINHA DE ITAIPU")
    df["Município"] = df["Município"].replace("SAO JORGE DO OESTE", "SAO JORGE D'OESTE")
    df["Município"] = df["Município"].replace("SAUDADES DO IGUACU", "SAUDADE DO IGUACU")

    df["Cultura"] = df["Cultura"].replace("ALHO PORO", "ALHO PORRO")
    df["Cultura"] = df["Cultura"].replace("CRISANTEMO VASO", "CRISANTEMO (VASO)")
    df["Cultura"] = df["Cultura"].replace("MANDIOCA CONSUMO HUMANO", "MANDIOCA CONSUMO (HUMANO)")
    df["Cultura"] = df["Cultura"].replace("CARANGUEIJO", "CARANGUEJO")
    df["Cultura"] = df["Cultura"].replace("MANDIOCA INDUSTRIA", "MANDIOCA INDUSTRIA/CONSUMO ANIMAL")
"""

st.code(codigo, language="python")


st.subheader("Municípios", divider=True)
df_municipio = pd.DataFrame(municipio, columns=["Município"])
st.dataframe(df_municipio)


st.subheader("Culturas", divider=True)
df_cultura = pd.DataFrame(cultura, columns=["Cultura"])
st.dataframe(df_cultura)


# ===========================================================
# RODAPE
# ===========================================================
rodape()
