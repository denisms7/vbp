import streamlit as st
import pandas as pd


def exportacao(df: pd.DataFrame):

    csv = df.to_csv(index=False, sep=";", encoding="utf-8-sig")

    st.download_button(
        label="📥 Exportar Dados",
        data=csv,
        file_name="Dados-VBP.csv",
        mime="text/csv",
    )
