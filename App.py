import streamlit as st


pages = {
    "Valor Bruto da Produção": [
        st.Page("pages/Dashboard.py", title="Dashboard", icon="📊"),
        st.Page("pages/Dados.py", title="Fonte de Dados", icon="🗂️"),
    ],
}

pg = st.navigation(pages)
pg.run()
