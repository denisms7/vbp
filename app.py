import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata


def remover_acentos(texto):
    if texto is None:
        return texto

    texto_normalizado = unicodedata.normalize("NFD", texto)
    texto_sem_acentos = "".join(
        caractere
        for caractere in texto_normalizado
        if unicodedata.category(caractere) != "Mn"
    )

    return texto_sem_acentos


@st.cache_data
def carregar_dados() -> pd.DataFrame:
    df_2019 = pd.read_excel("data/vbp_2019.xlsx")
    df_2020 = pd.read_excel("data/vbp_2020.xlsx")
    df_2021 = pd.read_excel("data/vbp_2021.xlsx")
    df_2022 = pd.read_excel("data/vbp_2022.xlsx")
    df_2023 = pd.read_excel("data/vbp_2023.xlsx")
    df_2024 = pd.read_excel("data/vbp_2024.xlsx")

    def padronizar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        for coluna in COLUNAS_PADRAO:
            if coluna not in df.columns:
                df[coluna] = pd.NA

        return df[COLUNAS_PADRAO]

    dfs = [
        df_2019,
        df_2020,
        df_2021,
        df_2022,
        df_2023,
        df_2024,
    ]

    COLUNAS_PADRAO = [
        "Safra",
        "Código Município",
        "Município",
        "NR",
        "Grupo",
        "Subgrupo",
        "Subg - detalhe\n",
        "NR Seab",
        "Região",
        "Código Cultura",
        "Cultura",
        "Unidade",
        "Área (ha)",
        "Rebanho Estático",
        "Abate / Comercialização",
        "Peso",
        "Produção",
        "VBP",
    ]

    df = pd.concat(
        [padronizar_dataframe(df) for df in dfs],
        ignore_index=True,
    )

    # =========================
    # TRATAMENTO DE DADOS
    # =========================

    # Área (ha) → float
    df["Área (ha)"] = (
        df["Área (ha)"]
        .astype(str)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    df["Área (ha)"] = pd.to_numeric(df["Área (ha)"], errors="coerce").fillna(0.0)

    # Safra → ano inicial (int)
    df['Safra'] = df['Safra'].apply(lambda x: str(x).replace('/', '').replace('-', '')).fillna(0)

    df["Safra"] = (
        df["Safra"]
        .astype(str)
        .str.extract(r"(\d{4})")[0]
        .str.replace(r"(\d{2})(\d{2})", r"\1-\2", regex=True)
    )

    df["Safra_ordem"] = (
        df["Safra"]
        .str.extract(r"(\d{2})")[0]
        .astype(int)
    )

    # Remover acentos e tornar maiusculo
    df["Cultura"] = df["Cultura"].str.upper()
    df["Cultura"] = df["Cultura"].apply(remover_acentos)

    # Remover excesso de espaços
    df["Cultura"] = (df["Cultura"].str.strip().str.replace(r"\s+", " ", regex=True))

    # Correcao nomes errados
    df["Cultura"] = df["Cultura"].replace("ALHO PORO", "ALHO PORRO")
    df["Cultura"] = df["Cultura"].replace("CRISANTEMO VASO", "CRISANTEMO (VASO)")
    df["Cultura"] = df["Cultura"].replace("MANDIOCA CONSUMO HUMANO", "MANDIOCA CONSUMO (HUMANO)")

    return df


df = carregar_dados()


# Configuração da página
st.set_page_config(
    page_title="Dashboard - Modelo",
    page_icon="📊",
    layout="wide",
)

st.subheader("VBP Valor Bruto da Produção", divider=True)


cidade = (
    df["Município"]
    .dropna()
    .astype(str)
    .sort_values()
    .unique()
)

cultura = (
    df["Cultura"]
    .dropna()
    .astype(str)
    .sort_values()
    .unique()
)


cidades_selecionadas = st.multiselect(
    "Selecione o(s) Município(s):",
    options=sorted(cidade),
    default=["Centenário do Sul"]
)


if cidades_selecionadas:
    df_filtrado = df[df["Município"].isin(cidades_selecionadas)]
else:
    df_filtrado = df.copy()

col01, col02 = st.columns(2)

with col01:
    vbp_total_vbp = (
        df_filtrado.groupby(["Município", "Safra"], as_index=False)["VBP"].sum()
    )

    fig1 = px.bar(
        vbp_total_vbp,
        x="Safra",
        y="VBP",
        color="Município",
        title="VBP Total por Safra",
        barmode="group",
        custom_data=["Município"],
    )

    fig1.update_layout(
        xaxis_title="Safra",
        yaxis_title="VBP",
        legend_title_text="Município",
    )

    fig1.update_traces(
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Safra: %{x}<br>"
            "VBP: %{y:,.2f}<extra></extra>"
        )
    )
    st.plotly_chart(fig1, use_container_width=True)


with col02:

    vbp_total_area = (
        df_filtrado.groupby(["Município", "Safra"], as_index=False)["Área (ha)"].sum()
    )

    fig02 = px.line(
        vbp_total_area,
        x="Safra",
        y="Área (ha)",
        color="Município",
        title="Área (ha) Total por Safra",
        custom_data=["Município"],
    )

    fig02.update_traces(
        hovertemplate=(
            "<b>Município:</b> %{customdata[0]}<br>"
            "<b>Safra:</b> %{x}<br>"
            "<b>Área (ha):</b> %{y:,.2f}<br>"
            "<extra></extra>"
        ),
        mode="lines+markers",
        marker=dict(size=6),
    )

    fig02.update_layout(
        xaxis_title="Safra",
        yaxis_title="Área (ha)",
        legend_title_text="Município",
        hovermode="x unified",
    )

    st.plotly_chart(fig02, use_container_width=True)


st.subheader("Produção por Cultura", divider=True)


cultura_selecionadas = st.selectbox(
    "Selecione a Cultura:",
    options=sorted(cultura),
)

if cultura_selecionadas:
    df_filtrado = df_filtrado[
        df_filtrado["Cultura"] == cultura_selecionadas]

col1, col2 = st.columns(2)

with col1:
    fig2 = px.bar(
        df_filtrado,
        x="Safra",
        y="VBP",
        color="Município",
        barmode="group",
        title=f"VBP - {cultura_selecionadas}",
    )
    st.plotly_chart(fig2, use_container_width=True)


with col2:
    if ("Abate / Comercialização" in df_filtrado.columns and df_filtrado["Abate / Comercialização"].notna().any()):
        fig3 = px.line(
            df_filtrado,
            x="Safra",
            y="Abate / Comercialização",
            color="Município",
            title=f"Abate / Comercialização - {cultura_selecionadas}",
        )

    elif ("Rebanho Estático" in df_filtrado.columns and df_filtrado["Rebanho Estático"].notna().any()):
        fig3 = px.line(
            df_filtrado,
            x="Safra",
            y="Rebanho Estático",
            color="Município",
            title=f"Rebanho Estático - {cultura_selecionadas}",
        )

    else:
        fig3 = px.line(
            df_filtrado,
            x="Safra",
            y="Área (ha)",
            color="Município",
            title=f"Área (ha) - {cultura_selecionadas}",
        )

    st.plotly_chart(fig3, use_container_width=True)


st.subheader("Números Estaduais", divider=True)


col10, col11 = st.columns(2)

vbp_por_safra = (
    df.groupby("Safra", as_index=False)["VBP"]
    .agg(
        vbp_medio="mean",
        vbp_maximo="max",
    )
)

with col10:
    fig10 = px.line(
        vbp_por_safra,
        x="Safra",
        y="vbp_medio",
        markers=True,
        title="VBP Médio por Safra",
    )

    fig10.update_traces(
        hovertemplate=(
            "<b>Safra:</b> %{x}<br>"
            "<b>VBP Médio:</b> R$ %{y:,.2f}<br>"
            "<extra></extra>"
        )
    )

    fig10.update_layout(
        yaxis_title="VBP (R$)",
        hovermode="x unified",
        legend_title_text="Indicadores",
    )

    st.plotly_chart(fig10, use_container_width=True)


with col11:
    fig11 = px.line(
        vbp_por_safra,
        x="Safra",
        y="vbp_maximo",
        markers=True,
        title="VBP Máximo por Safra",
    )

    fig11.update_traces(
        hovertemplate=(
            "<b>Safra:</b> %{x}<br>"
            "<b>VBP Máximo:</b> R$ %{y:,.2f}<br>"
            "<extra></extra>"
        )
    )

    fig11.update_layout(
        yaxis_title="VBP Máximo (R$)",
        hovermode="x unified",
    )

    st.plotly_chart(fig11, use_container_width=True)


col12, col13 = st.columns(2)


vbp_total_top_10_areas = (
    df.groupby(
        ["Cultura", "Safra", "Safra_ordem"],
        as_index=False
    )["Área (ha)"]
    .sum()
)

top_10_por_safra = (
    vbp_total_top_10_areas
    .sort_values(
        by=["Safra_ordem", "Área (ha)"],
        ascending=[True, False]
    )
    .groupby("Safra", as_index=False)
    .head(5)
)

vbp_total_top_10_vbp = (
    df.groupby(
        ["Cultura", "Safra", "Safra_ordem"],
        as_index=False
    )["VBP"]
    .sum()
)

top_10_por_safra_vbp = (
    vbp_total_top_10_vbp
    .sort_values(
        by=["Safra_ordem", "VBP"],
        ascending=[True, False]
    )
    .groupby(["Safra_ordem", "Safra"], as_index=False)
    .head(5)
)


with col12:
    fig_area = px.bar(
        top_10_por_safra.sort_values(by=["Safra_ordem"]),
        x="Safra_ordem",
        y="Área (ha)",
        color="Cultura",
        barmode="group",
        title="Top 5 Culturas por Área (ha) em cada Safra",
    )

    fig_area.update_layout(
        xaxis_title="Safra",
        yaxis_title="Área (ha)",
        legend_title_text="Cultura",
    )

    st.plotly_chart(fig_area, use_container_width=True)


with col13:
    fig_vbp = px.bar(
        top_10_por_safra_vbp.sort_values(by=["Safra_ordem"]),
        x="Safra_ordem",
        y="VBP",
        color="Cultura",
        barmode="group",
        title="Top 5 Culturas por VBP em cada Safra",
    )

    fig_vbp.update_layout(
        xaxis_title="Safra",
        yaxis_title="VBP",
        legend_title_text="Cultura",
    )

    st.plotly_chart(fig_vbp, use_container_width=True)


st.markdown(
    '📊 Fonte dos dados: <a href="https://www.agricultura.pr.gov.br/vbp" target="_blank">'
    'Valor Bruto da Produção Agropecuária (VBP) – SEAB/PR'
    '</a>',
    unsafe_allow_html=True,
)
