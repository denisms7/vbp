import streamlit as st
from components.data import carregar_dados, encontrar_cidade_mais_proxima
from components.graficos import geral, estado, rodape, cultura, indicadores


# ===========================================================
# Configuração da página
# ===========================================================
st.set_page_config(
    page_title="PMCS - VBP - SEAB",
    page_icon="📊",
    layout="wide",
)


# ===========================================================
# Salvar Cache dos dados
# ===========================================================
@st.cache_data(show_spinner="Carregando dados...")
def obter_dados():
    return carregar_dados()


# Carregar dados
df = obter_dados()

cidade = (df["Município"].dropna().astype(str).sort_values().unique())
culturas = (df["Cultura"].dropna().astype(str).sort_values().unique())
safras = (df["Safra"].dropna().astype(str).sort_values().unique())

st.title("Valor Bruto da Produção")

st.markdown(
    """
    O **Valor Bruto da Produção (VBP)** é um índice de frequência anual, calculado com base na produção agrícola municipal e nos preços recebidos pelos produtores paranaenses. Engloba produtos da agricultura, da pecuária, da silvicultura, do extrativismo vegetal, da olericultura, da fruticultura, de plantas aromáticas, medicinais e ornamentais, da pesca etc.

    Além de fornecer dados sobre a produção agropecuária de todos os Municípios do estado do Paraná, tal índice compõe o **Fundo de Participação dos Municípios**. O Valor Bruto da Produção tem uma participação de 8% no cálculo usado para a determinação do índice final a ser aplicado sobre a arrecadação do ICMS, que resulta na cota-parte devida a cada Município.
    """
)


# ===========================================================
# GERAL
# ===========================================================
st.subheader("Produção por Município", divider=True)

safra_inicio, safra_fim = st.sidebar.select_slider(
    "Selecione as Safras:",
    options=safras,
    value=(safras[0], safras[-1]),
)

safra_inicio = int(str(safra_inicio).replace("/", "").replace("-", ""))
safra_fim = int(str(safra_fim).replace("/", "").replace("-", ""))

cidade_default = encontrar_cidade_mais_proxima(cidade, "CENTENARIO DO SUL")
cidades_selecionadas = st.sidebar.multiselect("Selecione o(s) Município(s):", options=sorted(cidade), default=cidade_default)

if cidades_selecionadas:
    df_filtrado = df[df["Município"].isin(cidades_selecionadas) & df["Safra_ordem"].between(safra_inicio, safra_fim)]

else:
    df_filtrado = df.copy()

geral(df_filtrado)


# ===========================================================
# CULTURA
# ===========================================================
st.subheader("Produção por Cultura", divider=True)

cultura_selecionadas = st.sidebar.selectbox(
    "Selecione a Cultura:",
    options=sorted(culturas),
)

# Base completa
df_base = df_filtrado.copy()

# Filtra apenas a cultura selecionada
df_cultura = df_base[df_base["Cultura"] == cultura_selecionadas]

# Agrega a cultura por município e safra
cultura_agregada = (
    df_cultura.groupby(
        ["Município", "Safra", "Safra_ordem", "Unidade"],
        as_index=False,
    )
    .agg(
        {
            "VBP": "sum",
            "Área (ha)": "sum",
            "Produção": "sum",
            "Abate / Comercialização": "sum",
        }
    )
)

# Base com TODAS as combinações de município e safra
base_completa = (
    df_base[["Município", "Safra", "Safra_ordem"]]
    .drop_duplicates()
)

# Junta base completa com a cultura agregada
cultura_total = base_completa.merge(
    cultura_agregada,
    on=["Município", "Safra", "Safra_ordem"],
    how="left",
)

# Preenche valores ausentes com zero
colunas_zero = [
    "VBP",
    "Área (ha)",
    "Produção",
    "Abate / Comercialização",
]

cultura_total[colunas_zero] = cultura_total[colunas_zero].fillna(0)

# Preenche informações fixas
cultura_total["Cultura"] = cultura_selecionadas

medida = (
    df_cultura["Unidade"].iloc[0]
    if not df_cultura.empty
    else "N/A"
)

cultura_total["Unidade"] = medida

st.text(f"Cultura: {cultura_selecionadas}, Medida: {medida}")

# Envia para o componente/gráfico
cultura(cultura_total, cultura_selecionadas)


# ===========================================================
# ESTADO
# ===========================================================
st.subheader("Números Estaduais", divider=True)
estado(df[df["Safra_ordem"].between(safra_inicio, safra_fim)])



# ===========================================================
# Indicadores
# ===========================================================
st.subheader("Indicadores Estatísticos do VBP Estadual", divider=True)
indicadores()

# ===========================================================
# RODAPE
# ===========================================================
rodape()
