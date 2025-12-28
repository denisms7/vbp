import streamlit as st
import plotly.express as px
from components.data import carregar_dados, encontrar_cidade_mais_proxima
from components.estado import estado
from components.geral import geral


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


st.title("Valor Bruto da Produção")

st.markdown(
    """
    O **Valor Bruto da Produção (VBP)** é um índice de frequência anual, calculado com base na produção agrícola municipal e nos preços recebidos pelos produtores paranaenses. Engloba produtos da agricultura, da pecuária, da silvicultura, do extrativismo vegetal, da olericultura, da fruticultura, de plantas aromáticas, medicinais e ornamentais, da pesca etc.

    Além de fornecer dados sobre a produção agropecuária de todos os Municípios do estado do Paraná, tal índice compõe o **Fundo de Participação dos Municípios**. O Valor Bruto da Produção tem uma participação de 8% no cálculo usado para a determinação do índice final a ser aplicado sobre a arrecadação do ICMS, que resulta na cota-parte devida a cada Município.
    """
)


st.subheader("Produção por Município", divider=True)


cidade = (df["Município"].dropna().astype(str).sort_values().unique())
cultura = (df["Cultura"].dropna().astype(str).sort_values().unique())
safras = (df["Safra"].dropna().astype(str).sort_values().unique())

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
    df_filtrado = df[
        df["Município"].isin(cidades_selecionadas) &
        df["Safra_ordem"].between(safra_inicio, safra_fim)
        ]
else:
    df_filtrado = df.copy()

geral(df_filtrado)



# =======================================================================================================================================



st.subheader("Produção por Cultura", divider=True)

cultura_selecionadas = st.sidebar.selectbox("Selecione a Cultura:", options=sorted(cultura))

cultura_filtro = df_filtrado[df_filtrado["Cultura"] == cultura_selecionadas]

cultura_total = (cultura_filtro.groupby(["Município", "Safra", "Safra_ordem", "Cultura", "Unidade"], as_index=False).agg(
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

        df_plot = cultura_total.sort_values("Safra_ordem")

        fig2 = px.bar(
            df_plot,
            x="Safra_ordem",
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

        fig2.update_layout(
            xaxis_title="Safra",
            yaxis_title="VBP",
        )

        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Não há dados de VBP para exibição.")


with col02:
    coluna_y = coluna_com_dados(
        cultura_total,
        colunas_prioridade,
    )

    df_plot = cultura_total.sort_values("Safra_ordem")

    if coluna_y is not None:
        fig = px.bar(
            df_plot,
            x="Safra_ordem",
            y=coluna_y,
            color="Município",
            barmode="group",
            title=f"{coluna_y} - {cultura_selecionadas}",
            custom_data=["Município"],
        )

        fig.update_traces(
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"  # Município
                "Safra: %{x}<br>"
                f"{coluna_y}: %{{y:,.2f}}<extra></extra>"  # note o %{{y}} com duas chaves
            )
        )

        fig.update_layout(
            xaxis_title="Safra",
            yaxis_title=f"{coluna_y}",
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Não há dados disponíveis para exibição.")


with col03:
    # Verifica se existe algum valor não nulo e maior que zero em Produção
    if "Produção" in cultura_total.columns and (cultura_total["Produção"].fillna(0) > 0).any():

        df_plot = cultura_total.sort_values("Safra_ordem")

        fig3 = px.area(
            df_plot,
            x="Safra",
            y="Produção",
            color="Município",
            markers=True,
            title=f"Produção - {cultura_selecionadas}",
            custom_data=["Município", "Unidade"],
        )

        fig3.update_xaxes(
            categoryorder="array",
            categoryarray=df_plot["Safra"],
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
            key=f"grafico_area_producao_{cultura_selecionadas}",
        )


estado(df[df["Safra_ordem"].between(safra_inicio, safra_fim)])

st.markdown(
    "<p style='text-align: center;'>Desenvolvido por Denis Muniz Silva</p>",
    unsafe_allow_html=True,
)
