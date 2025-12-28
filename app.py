import streamlit as st
import plotly.express as px
from components.data import carregar_dados, encontrar_cidade_mais_proxima
from components.estado import estado
from components.geral import geral
from components.exportar import exportacao


# Configuração da página
st.set_page_config(
    page_title="PMCS - VBP - SEAB",
    page_icon="📊",
    layout="wide",
)


# Salvar Cache dos dados
@st.cache_data(show_spinner="Carregando dados...")
def obter_dados():
    return carregar_dados()


# Carregar dados
df = obter_dados()


st.title("VBP Valor Bruto da Produção")


cidade = (df["Município"].dropna().astype(str).sort_values().unique())
cultura = (df["Cultura"].dropna().astype(str).sort_values().unique())

cidade_default = encontrar_cidade_mais_proxima(cidade, "CENTENARIO DO SUL")
cidades_selecionadas = st.multiselect("Selecione o(s) Município(s):", options=sorted(cidade), default=cidade_default)

if cidades_selecionadas:
    df_filtrado = df[df["Município"].isin(cidades_selecionadas)]
else:
    df_filtrado = df.copy()

geral(df_filtrado)

# =======================================================================================================================================

st.subheader("Produção por Cultura", divider=True)

cultura_selecionadas = st.selectbox("Selecione a Cultura:", options=sorted(cultura))

cultura_filtro = df_filtrado[df_filtrado["Cultura"] == cultura_selecionadas]

cultura_total = (cultura_filtro.groupby(["Município", "Safra", "Cultura", "Unidade"], as_index=False).agg(
    {
        "VBP": "sum",
        "Área (ha)": "sum",
        "Produção": "sum",
        "Abate / Comercialização": "sum",
    })
)


def coluna_com_dados(df, colunas):
    for coluna in colunas:
        if coluna not in df.columns:
            continue

        serie = df[coluna]

        if serie.notna().any() and serie.sum() != 0:
            return coluna

    return None


colunas_prioridade = [
    "Área (ha)",
    "Abate / Comercialização",
    "Produção",
]

# Filtra a linha da cultura selecionada
linha = df[df["Cultura"] == cultura_selecionadas]
medida = linha["Unidade"].iloc[0] if not linha.empty else "N/A"
st.text(f"Cultura: {cultura_selecionadas}, Medida: {medida}")

col01, col02 = st.columns(2)
col03 = st.columns(1)[0]


with col01:
    if "VBP" in cultura_total.columns and (cultura_total["VBP"].fillna(0) > 0).any():
        fig2 = px.bar(
            cultura_total,
            x="Safra",
            y="VBP",
            color="Município",
            barmode="group",
            title=f"VBP - {cultura_selecionadas}",
            custom_data=["Município"],
        )

        fig2.update_traces(
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Safra: %{x}<br>"
                "VBP: %{y:,.2f}<extra></extra>"
            )
        )

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Não há dados de VBP para exibição.")


with col02:
    coluna_y = coluna_com_dados(
        cultura_total,
        colunas_prioridade,
    )

    if coluna_y is not None:
        fig = px.line(
            cultura_total,
            x="Safra",
            y=coluna_y,
            color="Município",
            title=f"{coluna_y} - {cultura_selecionadas}",
            markers=True,
            custom_data=["Município"],
        )

        fig.update_traces(
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"  # Município
                "Safra: %{x}<br>"
                f"{coluna_y}: %{{y:,.2f}}<extra></extra>"  # note o %{{y}} com duas chaves
            )
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Não há dados disponíveis para exibição.")


with col03:
    # Verifica se existe algum valor não nulo e maior que zero em Produção
    if "Produção" in cultura_total.columns and (cultura_total["Produção"].fillna(0) > 0).any():

        fig3 = px.area(
            cultura_total.sort_values("Safra"),
            x="Safra",
            y="Produção",
            color="Município",
            title=f"Produção - {cultura_selecionadas}",
            custom_data=["Município", "Unidade"],
        )

        fig3.update_traces(
            stackgroup=None,
            opacity=0.7,
            hovertemplate=(
                "<b>Município:</b> %{customdata[0]}<br>"
                "<b>Safra:</b> %{x}<br>"
                "<b>Produção:</b> %{y:,.2f} %{customdata[1]}<br>"
                "<extra></extra>"
            ),
        )

        fig3.update_layout(
            xaxis_title="Safra",
            yaxis_title="Produção",
        )

        st.plotly_chart(
            fig3,
            use_container_width=True,
            key=f"grafico_area_producao_{cultura_selecionadas}"
        )

    else:
        st.info("Não há dados de Produção para exibição.")

estado(df)

st.markdown(
    '📊 Fonte dos dados: <a href="https://www.agricultura.pr.gov.br/vbp" target="_blank">'
    'Valor Bruto da Produção Agropecuária (VBP) – SEAB/PR'
    '</a>',
    unsafe_allow_html=True,
)

exportacao(df)

st.markdown(
    "<p style='text-align: center;'>Desenvolvido por Denis Muniz Silva</p>",
    unsafe_allow_html=True,
)
