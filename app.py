import streamlit as st
import plotly.express as px
import pandas as pd
from data import carregar_dados, encontrar_cidade_mais_proxima
from estado import estado

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

cidade_default = encontrar_cidade_mais_proxima(cidade,"centenario do sul")

cidades_selecionadas = st.multiselect("Selecione o(s) Município(s):",options=sorted(cidade),default=cidade_default)


if cidades_selecionadas:
    df_filtrado = df[df["Município"].isin(cidades_selecionadas)]
else:
    df_filtrado = df.copy()

col01, col02 = st.columns(2)

vbp_total = (df_filtrado.groupby(["Município", "Safra"], as_index=False)
    .agg(
        {
            "VBP": "sum",
            "Área (ha)": "sum",
        }
    )
)

total_culturas = (
    df_filtrado.groupby(["Município", "Safra"], as_index=False)["Cultura"]
    .nunique()
    .rename(columns={"Cultura": "total_culturas"})
)


with col01:
    fig = px.bar(
        vbp_total,
        x="Safra",
        y="VBP",
        color="Município",
        title="VBP Total por Safra",
        barmode="group",
        custom_data=["Município"],
    )

    fig.update_layout(
        xaxis_title="Safra",
        yaxis_title="VBP",
        legend_title_text="Município",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Safra: %{x}<br>"
            "VBP: %{y:,.2f}<extra></extra>"
        )
    )
    st.plotly_chart(fig, use_container_width=True)


with col02:
    fig = px.line(
        total_culturas,
        x="Safra",
        y="total_culturas",
        color="Município",
        title="Culturas por Safra",
        markers=True,
        custom_data=["Município"],
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Safra: %{x}<br>"
            "Total de Culturas: %{y}<br>"
            "<extra></extra>"
        ),
        mode="lines+markers",
        marker=dict(size=6),
    )

    fig.update_layout(
        xaxis_title="Safra",
        yaxis_title="Total de Culturas",
        legend_title_text="Município",
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)


col03 = st.columns(1)[0]

with col03:
    fig = px.area(
        vbp_total,
        x="Safra",
        y="Área (ha)",
        color="Município",
        title="Área (ha) Total por Safra",
        custom_data=["Município"],
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Safra: %{x}<br>"
            "Área (ha): %{y:,.2f}<br>"
            "<extra></extra>"
        ),
        mode="lines+markers",
        marker=dict(size=6),
    )

    fig.update_layout(
        xaxis_title="Safra",
        yaxis_title="Área (ha)",
        legend_title_text="Município",
    )

    st.plotly_chart(fig, use_container_width=True)







# =======================================================================================================================================


st.subheader("Produção por Cultura", divider=True)

cultura_selecionadas = st.selectbox("Selecione a Cultura:",options=sorted(cultura))

cultura_filtro = df_filtrado[df_filtrado["Cultura"] == cultura_selecionadas]


cultura_total = (cultura_filtro.groupby(["Município", "Safra", "Cultura", "Unidade"], as_index=False)
    .agg(
        { 
            "VBP": "sum",
            "Área (ha)": "sum",
            "Produção": "sum",
            "Abate / Comercialização": "sum",
        }
    )
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

col1, col2 = st.columns(2)

with col1:
    if "VBP" in cultura_total.columns and (cultura_total["VBP"].fillna(0) > 0).any():
        fig2 = px.bar(
            cultura_total,
            x="Safra",
            y="VBP",
            color="Município",
            barmode="group",
            title=f"VBP Total por Safra",
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


with col2:
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
            title=f"{coluna_y} por Safra",
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



# Converte o DataFrame para CSV com ponto e vírgula e UTF-8 BOM
csv = df.to_csv(index=False, sep=";", encoding="utf-8-sig")

st.download_button(
    label="📥 Exportar Dados",
    data=csv,
    file_name="Dados-VBP.csv",
    mime="text/csv",
)




st.markdown(
    "<p style='text-align: center;'>Desenvolvido por Denis Muniz Silva</p>",
    unsafe_allow_html=True,
)
