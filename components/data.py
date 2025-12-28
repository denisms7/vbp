import pandas as pd
import unicodedata
from difflib import get_close_matches


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


def encontrar_cidade_mais_proxima(cidades, texto_base, cutoff=0.6):
    cidades_norm = {
        cidade: remover_acentos(cidade)
        for cidade in cidades
    }

    texto_norm = remover_acentos(texto_base)

    matches = get_close_matches(
        texto_norm,
        cidades_norm.values(),
        n=1,
        cutoff=cutoff,
    )

    if not matches:
        return []

    # recuperar o nome original
    for cidade, cidade_norm in cidades_norm.items():
        if cidade_norm == matches[0]:
            return [cidade]

    return []


def padronizar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

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

    for coluna in COLUNAS_PADRAO:
        if coluna not in df.columns:
            df[coluna] = pd.NA

    return df[COLUNAS_PADRAO]


def carregar_dados() -> pd.DataFrame:
    df_2012 = pd.read_excel("data/vbp_2012.xlsx")
    df_2013 = pd.read_excel("data/vbp_2013.xlsx")
    df_2014 = pd.read_excel("data/vbp_2014.xlsx")

    df_2015 = pd.read_excel("data/vbp_2015.xlsx")
    df_2016 = pd.read_excel("data/vbp_2016.xlsx")
    df_2017 = pd.read_excel("data/vbp_2017.xlsx")
    df_2018 = pd.read_excel("data/vbp_2018.xlsx")

    df_2019 = pd.read_excel("data/vbp_2019.xlsx")
    df_2020 = pd.read_excel("data/vbp_2020.xlsx")
    df_2021 = pd.read_excel("data/vbp_2021.xlsx")
    df_2022 = pd.read_excel("data/vbp_2022.xlsx")
    df_2023 = pd.read_excel("data/vbp_2023.xlsx")
    df_2024 = pd.read_excel("data/vbp_2024.xlsx")

    dfs = [
        # df_2012,
        df_2013,
        df_2014,
        df_2015,
        df_2016,
        df_2017,
        df_2018,
        df_2019,
        df_2020,
        df_2021,
        df_2022,
        df_2023,
        df_2024,
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
    df["VBP"] = pd.to_numeric(df["VBP"], errors="coerce").fillna(0.0)
    df["Produção"] = pd.to_numeric(df["Produção"], errors="coerce").fillna(0.0)
    df["Abate / Comercialização"] = pd.to_numeric(df["Abate / Comercialização"], errors="coerce").fillna(0.0)

    # Safra → ano inicial (int)
    df['Safra'] = df['Safra'].apply(lambda x: str(x).replace('/', '').replace('-', '')).fillna(0)

    df["Safra_ordem"] = df["Safra"].str[:4].astype(int)

    df["Safra"] = (
        df["Safra"]
        .astype(str)
        .str.extract(r"(\d{4})")[0]
        .str.replace(r"(\d{2})(\d{2})", r"\1-\2", regex=True)
    )

    # Remover acentos e tornar maiusculo
    df["Cultura"] = df["Cultura"].str.upper()
    df["Cultura"] = df["Cultura"].apply(remover_acentos)

    # Remover acentos e tornar maiusculo
    df["Município"] = df["Município"].str.upper()
    df["Município"] = df["Município"].apply(remover_acentos)

    # Remover excesso de espaços
    df["Cultura"] = (df["Cultura"].str.strip().str.replace(r"\s+", " ", regex=True))

    # Correcao Nomes
    df["Município"] = df["Município"].replace("RANCHO ALEGRE DO OESTE", "RANCHO ALEGRE D'OESTE")
    df["Município"] = df["Município"].replace("SANTA CRUZ DO MONTE CASTELO", "SANTA CRUZ DE MONTE CASTELO")
    df["Município"] = df["Município"].replace("SANTA IZABEL DO IVAI", "SANTA ISABEL DO IVAI")
    df["Município"] = df["Município"].replace("SANTA TEREZINHA DO ITAIPU", "SANTA TEREZINHA DE ITAIPU")
    df["Município"] = df["Município"].replace("SAO JORGE DO OESTE", "SAO JORGE D'OESTE")
    df["Município"] = df["Município"].replace("SAUDADES DO IGUACU", "SAUDADE DO IGUACU")

    df["Cultura"] = df["Cultura"].replace("ALHO PORO", "ALHO PORRO")
    df["Cultura"] = df["Cultura"].replace("CRISANTEMO VASO", "CRISANTEMO (VASO)")
    df["Cultura"] = df["Cultura"].replace("MANDIOCA CONSUMO HUMANO", "MANDIOCA CONSUMO (HUMANO)")
    df["Cultura"] = df["Cultura"].replace("CARANGUEIJO", "CARANGUEJO")
    df["Cultura"] = df["Cultura"].replace("MANDIOCA INDUSTRIA", "MANDIOCA INDUSTRIA/CONSUMO ANIMAL")

    df = df.drop(columns=["NR", "NR Seab"])

    return df
