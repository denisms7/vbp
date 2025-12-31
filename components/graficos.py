import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def coluna_com_dados(df, colunas):

    for coluna in colunas:
        if coluna not in df.columns:
            continue
        serie = df[coluna]

        if serie.notna().any() and serie.sum() != 0:
            return coluna

    return None


COLUNAS_PRIORIDADE = [
    "Área (ha)",
    "Abate / Comercialização",
    "Produção",
]


def geral(df: pd.DataFrame):

    col01, col02 = st.columns(2)
    col03 = st.columns(1)[0]

    vbp_total = (df.groupby(["Município", "Safra"], as_index=False).agg(
        {
            "VBP": "sum",
            "Área (ha)": "sum",
        }
    ))

    total_culturas = (
        df.groupby(["Município", "Safra"], as_index=False)["Cultura"]
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
        )

        st.plotly_chart(fig, use_container_width=True)

    with col03:
        fig = px.line(
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


def cultura(cultura_total: pd.DataFrame, cultura_selecionadas):
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
            COLUNAS_PRIORIDADE,
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
                    f"{coluna_y}: %{{y:,.2f}}<extra></extra>"
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


def estado(df: pd.DataFrame):

    col01, col02 = st.columns(2)
    col03, col04 = st.columns(2)

    # Agrupamento por Safra
    vbp_por_safra = df.groupby("Safra", as_index=False)["VBP"].agg(
        vbp_medio="mean",
        vbp_mediana="median",
        vbp_maximo="max",
        vbp_desvio_padrao="std",
    )

    vbp_por_safra["coef_variacao"] = (
        vbp_por_safra["vbp_desvio_padrao"] / vbp_por_safra["vbp_medio"]
    )

    # Gráfico VBP Médio
    with col01:
        if not vbp_por_safra.empty and vbp_por_safra["vbp_medio"].notna().any():
            fig10 = go.Figure()

            # VBP Médio
            fig10.add_trace(
                go.Scatter(
                    x=vbp_por_safra["Safra"],
                    y=vbp_por_safra["vbp_medio"],
                    mode="lines+markers",
                    name="Média",
                    hovertemplate="Média<br>R$ %{y:,.2f}<extra></extra>",
                )
            )

            # VBP Mediana
            fig10.add_trace(
                go.Scatter(
                    x=vbp_por_safra["Safra"],
                    y=vbp_por_safra["vbp_mediana"],
                    mode="lines+markers",
                    name="Mediana",
                    hovertemplate="Mediana<br>R$ %{y:,.2f}<extra></extra>",
                )
            )

            # Coeficiente de Variação (eixo secundário)
            fig10.add_trace(
                go.Scatter(
                    x=vbp_por_safra["Safra"],
                    y=vbp_por_safra["coef_variacao"] * 100,
                    mode="lines+markers",
                    name="Coef. Variação (%)",
                    yaxis="y2",
                    hovertemplate="Coef. Variação<br>%{y:.2f}%<extra></extra>",
                )
            )

            fig10.update_layout(
                title="VBP Médio, Mediana e Coeficiente de Variação por Safra",
                xaxis_title="Safra",
                yaxis=dict(
                    title="VBP (R$)",
                    tickprefix="R$ ",
                ),
                yaxis2=dict(
                    title="Variação (%)",
                    overlaying="y",
                    side="right",
                ),
                legend_title_text="Indicadores",
                hovermode="x unified",
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

            fig11.update_traces(
                hovertemplate=(
                    "<b>VBP Máximo</b><br>"
                    "Valor: R$ %{y:,.2f}<br>"
                    "<extra></extra>"
                )
            )

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


def indicadores():

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    # =========================
    # MÉDIA
    # =========================
    with col1:
        st.markdown("### 🔹 Média")
        st.markdown(
            "Representa o valor médio do VBP em uma safra."
        )
        st.latex(
            r"\text{Média} = \frac{\sum_{i=1}^{n} VBP_i}{n}"
        )
        st.markdown(
            "📌 Sensível a valores extremos (*outliers*)."
        )

    # =========================
    # MEDIANA
    # =========================
    with col2:
        st.markdown("### 🔹 Mediana")
        st.markdown(
            "Valor central da distribuição do VBP."
        )

        st.markdown("Se $n$ é ímpar:")
        st.latex(
            r"\text{Mediana} = VBP_{\frac{n+1}{2}}"
        )

        st.markdown("Se $n$ é par:")
        st.latex(
            r"\text{Mediana} = \frac{VBP_{\frac{n}{2}} + VBP_{\frac{n}{2}+1}}{2}"
        )

        st.markdown(
            "📌 Não é afetada por *outliers*."
        )

    # =========================
    # DESVIO PADRÃO
    # =========================
    with col3:
        st.markdown("### 🔹 Desvio Padrão ($\sigma$)")
        st.markdown(
            "Mede a dispersão dos valores em relação à média."
        )
        st.latex(
            r"\sigma = \sqrt{\frac{\sum_{i=1}^{n} (VBP_i - \bar{x})^2}{n - 1}}"
        )
        st.markdown(
            "📌 Quanto maior, maior a variabilidade."
        )

    # =========================
    # COEF. VARIAÇÃO
    # =========================
    with col4:
        st.markdown("### 🔹 Coeficiente de Variação (CV)")
        st.markdown(
            "Mede a variabilidade **relativa** dos dados."
        )
        st.latex(
            r"CV = \frac{\sigma}{\bar{x}} \times 100"
        )
        st.markdown(
            """
            📌 Interpretação:
            - CV < 20% → baixa variabilidade  
            - 20% ≤ CV < 100% → moderada  
            - CV ≥ 100% → alta variabilidade
            """
        )

    st.markdown("---")

    st.info(
        """
        **Interpretação Geral**

        - Média muito maior que a mediana indica **assimetria à direita**
        - CV elevado indica **alta dispersão** e presença de valores extremos
        - Comum em dados econômicos e produtivos
        """
    )



def rodape():
    st.markdown(
        "<p style='text-align: center;'>Desenvolvido por Denis Muniz Silva</p>",
        unsafe_allow_html=True,
    )
