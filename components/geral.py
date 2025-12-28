import streamlit as st
import pandas as pd
import plotly.express as px


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
