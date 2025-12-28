import streamlit as st
import pandas as pd
import plotly.express as px


def plotly_hover_template(valor: str) -> str:
    """
    Retorna um hover template padronizado para Plotly.
    """
    return f"<b>Safra:</b> %{{x}}<br><b>{valor}:</b> %{{y:,.2f}}<extra></extra>"


def estado(df: pd.DataFrame):
    st.subheader("Números Estaduais", divider=True)

    col01, col02 = st.columns(2)
    col03, col04 = st.columns(2)

    # Agrupamento por Safra
    vbp_por_safra = df.groupby("Safra", as_index=False)["VBP"].agg(
        vbp_medio="mean",
        vbp_maximo="max",
    )

    # Gráfico VBP Médio
    with col01:
        if not vbp_por_safra.empty and vbp_por_safra["vbp_medio"].notna().any():
            fig10 = px.line(
                vbp_por_safra,
                x="Safra",
                y="vbp_medio",
                markers=True,
                title="VBP Médio por Safra",
            )
            fig10.update_traces(hovertemplate=plotly_hover_template("VBP Médio"))
            fig10.update_layout(
                yaxis_title="VBP (R$)",
                hovermode="x unified",
                legend_title_text="Indicadores",
            )
            st.plotly_chart(fig10, use_container_width=True, key="vbp_medio")
        else:
            st.info("Não há dados de VBP Médio para exibição.")

    # Gráfico VBP Máximo
    with col02:
        if not vbp_por_safra.empty and vbp_por_safra["vbp_maximo"].notna().any():
            fig11 = px.line(
                vbp_por_safra,
                x="Safra",
                y="vbp_maximo",
                markers=True,
                title="VBP Máximo por Safra",
            )
            fig11.update_traces(hovertemplate=plotly_hover_template("VBP Máximo"))
            fig11.update_layout(
                yaxis_title="VBP Máximo (R$)",
                hovermode="x unified",
            )
            st.plotly_chart(fig11, use_container_width=True, key="vbp_maximo")
        else:
            st.info("Não há dados de VBP Máximo para exibição.")

    # Agrupamento para área
    vbp_total_top_10_areas = df.groupby(
        ["Cultura", "Safra", "Safra_ordem"], as_index=False
    )["Área (ha)"].sum()

    top_10_por_safra = (
        vbp_total_top_10_areas.sort_values(
            by=["Safra_ordem", "Área (ha)"], ascending=[True, False]
        )
        .groupby("Safra", as_index=False)
        .head(5)
    )

    # Agrupamento para VBP
    vbp_total_top_10_vbp = df.groupby(
        ["Cultura", "Safra", "Safra_ordem"], as_index=False
    )["VBP"].sum()

    top_10_por_safra_vbp = (
        vbp_total_top_10_vbp.sort_values(
            by=["Safra_ordem", "VBP"], ascending=[True, False]
        )
        .groupby(["Safra_ordem", "Safra"], as_index=False)
        .head(5)
    )

    # Gráfico Top 5 por VBP
    with col03:
        if not top_10_por_safra_vbp.empty and top_10_por_safra_vbp["VBP"].notna().any():
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
            st.plotly_chart(fig_vbp, use_container_width=True, key="top5_vbp")
        else:
            st.info("Não há dados de VBP para Top 5 Culturas.")

    # Gráfico Top 5 por Área
    with col04:
        if not top_10_por_safra.empty and top_10_por_safra["Área (ha)"].notna().any():
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
            st.plotly_chart(fig_area, use_container_width=True, key="top5_area")
        else:
            st.info("Não há dados de Área para Top 5 Culturas.")
