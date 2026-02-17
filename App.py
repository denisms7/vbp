import streamlit as st


pages = {
    "Valor Bruto da Produção": [
        st.Page("pages/Dashboard.py", title="Dashboard"),
        st.Page("pages/Dados.py", title="Fonte de Dados"),
    ],
}

pg = st.navigation(pages)
pg.run()
