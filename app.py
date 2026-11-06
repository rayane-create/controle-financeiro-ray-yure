import sqlite3
from datetime import date, datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# -------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA & ESTILO
# -------------------------------------------------------------
st.set_page_config(
    page_title="Finanças Ray & Yure",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .metric-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border-left: 5px solid #2B6CB0;
    }
    .metric-title { font-size: 0.85rem; color: #718096; font-weight: 600; text-transform: uppercase; }
    .metric-val { font-size: 1.6rem; font-weight: 700; color: #1A202C; }
    </style>
""",
    unsafe_allow_html=True,
)

# -------------------------------------------------------------
# BANCO DE DADOS PERSISTENTE (SQLite)
# -------------------------------------------------------------
DB_NAME = "contas.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS contas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            valor REAL NOT NULL,
            vencimento TEXT NOT NULL,
            status TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    """
    )

    # Verificar se tabela está vazia; se sim, popula com os dados iniciais
    c.execute("SELECT COUNT(*) FROM contas")
    if c.fetchone()[0] == 0:
        hoje = date.today().strftime("%Y-%m-%d")
        dados_iniciais = [
            ("Aluguel", "Moradia", 1390.0, hoje, "Aguardando Pagamento", "Fixo"),
            (
                "Água e luz",
                "Moradia",
                256.0,
                hoje,
                "Aguardando Pagamento",
                "Fixo",
            ),
            (
                "Faculdade",
                "Educação",
                665.0,
                hoje,
                "Aguardando Pagamento",
                "Fixo",
            ),
            (
                "Mãe",
                "Família / Ajuda",
                50.0,
                hoje,
                "Aguardando Pagamento",
                "Fixo",
            ),
            (
                "Atrasados",
                "Dívidas / Pendências",
                240.0,
                hoje,
                "Aguardando Pagamento",
                "Variável",
            ),
            (
                "Shopee",
                "Compras",
                536.0,
                hoje,
                "Aguardando Pagamento",
                "Variável",
            ),
            (
                "Nubank",
                "Cartão de Crédito",
                1374.0,
                hoje,
                "Aguardando Pagamento",
                "Cartão",
            ),
            (
                "Neon",
                "Cartão de Crédito",
                2134.0,
                hoje,
                "Aguardando Pagamento",
                "Cartão",
            ),
            (
                "Digio",
                "Cartão de Crédito",
                250.0,
                hoje,
                "Aguardando Pagamento",
                "Cartão",
            ),
            (
                "Bmg",
                "Cartão de Crédito",
                720.0,
                hoje,
                "Aguardando Pagamento",
                "Cartão",
            ),
            (
                "Bv",
                "Cartão de Crédito",
                507.0,
                hoje,
                "Aguardando Pagamento",
                "Cartão",
            ),
            ("Dm", "Outros", 250.0, hoje, "Aguardando Pagamento", "Variável"),
            (
                "Recarga pay",
                "Serviços",
                136.0,
                hoje,
                "Aguardando Pagamento",
                "Variável",
            ),
            (
                "Mercado pago",
                "Cartão de Crédito",
                540.0,
                hoje,
                "Aguardando Pagamento",
                "Cartão",
            ),
            (
                "Santander",
                "Cartão de Crédito",
                830.0,
                hoje,
                "Aguardando Pagamento",
                "Cartão",
            ),
            (
                "Caixa",
                "Cartão de Crédito",
                1284.0,
                hoje,
                "Aguardando Pagamento",
                "Cartão",
            ),
            (
                "Bb",
                "Cartão de Crédito",
                5000.0,
                hoje,
                "Aguardando Pagamento",
                "Cartão",
            ),
            (
                "Moto",
                "Transporte",
                400.0,
                hoje,
                "Aguardando Pagamento",
                "Fixo",
            ),
            (
                "Brasil card",
                "Cartão de Crédito",
                1575.0,
                hoje,
                "Aguardando Pagamento",
                "Cartão",
            ),
        ]
        c.executemany(
            """
            INSERT INTO contas (descricao, categoria, valor, vencimento, status, tipo)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            dados_iniciais,
        )
        conn.commit()
    conn.close()


def load_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM contas", conn)
    conn.close()
    return df


def update_db(df):
    conn = sqlite3.connect(DB_NAME)
    df.to_sql("contas", conn, if_exists="replace", index=False)
    conn.close()


def insert_conta(descricao, categoria, valor, vencimento, status, tipo):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO contas (descricao, categoria, valor, vencimento, status, tipo)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (descricao, categoria, valor, vencimento, status, tipo),
    )
    conn.commit()
    conn.close()


init_db()

# -------------------------------------------------------------
# LOGIN & AUTENTICAÇÃO
# -------------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False


def tela_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            "### 🔒 Painel Financeiro Ray & Yure", unsafe_allow_html=True
        )
        st.caption("Acesso restrito para o casal.")

        email = st.text_input("E-mail")
        senha = st.text_input("Senha", type="password")

        if st.button("Entrar no Painel", use_container_width=True):
            if (
                email.strip().lower() == "rayanealmeida.adm@gmail.com"
                and senha.strip() == "873401"
            ):
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("E-mail ou senha inválidos.")


if not st.session_state.autenticado:
    tela_login()
    st.stop()

# -------------------------------------------------------------
# PAINEL PRINCIPAL (AUTENTICADO)
# -------------------------------------------------------------
df_contas = load_data()

# Barra Lateral (Menu & Entradas)
with st.sidebar:
    st.markdown("### 💑 Ray & Yure")
    st.caption("Controle & Gestão Financeira Pessoal")
    st.divider()

    st.subheader("💵 Disponibilidade Atual")
    saldo_conta = st.number_input(
        "Saldo em Conta / Receitas (R$):", min_value=0.0, value=0.0, step=100.0
    )

    st.divider()
    st.subheader("➕ Nova Conta")
    with st.form("form_nova_conta", clear_on_submit=True):
        nova_desc = st.text_input("Descrição (Ex: Cartão X, Mercado)")
        nova_cat = st.selectbox(
            "Categoria",
            [
                "Cartão de Crédito",
                "Moradia",
                "Transporte",
                "Educação",
                "Alimentação",
                "Compras",
                "Família / Ajuda",
                "Dívidas / Pendências",
                "Serviços",
                "Outros",
            ],
        )
        novo_valor = st.number_input("Valor (R$)", min_value=0.01, step=10.0)
        novo_venc = st.date_input("Data de Vencimento", value=date.today())
        novo_status = st.selectbox(
            "Status", ["Aguardando Pagamento", "Pago", "Atrasado"]
        )
        novo_tipo = st.selectbox(
            "Tipo", ["Cartão", "Fixo", "Variável", "Emergência"]
        )

        submit = st.form_submit_button("Cadastrar Despesa")
        if submit:
            if nova_desc.strip():
                insert_conta(
                    nova_desc,
                    nova_cat,
                    novo_valor,
                    str(novo_venc),
                    novo_status,
                    novo_tipo,
                )
                st.success("Conta cadastrada!")
                st.rerun()
            else:
                st.error("Informe a descrição.")

    st.divider()
    if st.button("Encerrar Sessão", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# -------------------------------------------------------------
# CÁLCULOS E MÉTRICAS
# -------------------------------------------------------------
total_deve = df_contas["valor"].sum()
total_pago = df_contas[df_contas["status"] == "Pago"]["valor"].sum()
total_pendente = df_contas[df_contas["status"] != "Pago"]["valor"].sum()
diferenca = saldo_conta - total_pendente

# Cabeçalho
st.markdown("## 📊 Visão Geral do Mês")
st.markdown(
    "Acompanhamento em tempo real das contas e estratégias de liquidação."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total em Contas", f"R$ {total_deve:,.2f}")
c2.metric(
    "Aguardando Pagamento", f"R$ {total_pendente:,.2f}", delta_color="inverse"
)
c3.metric("Já Liquidado (Pago)", f"R$ {total_pago:,.2f}")
c4.metric(
    "Resultado / Saldo Final",
    f"R$ {diferenca:,.2f}",
    delta=f"{'Falta R$ ' + f'{abs(diferenca):,.2f}' if diferenca < 0 else 'Sobra R$ ' + f'{diferenca:,.2f}'}",
    delta_color="normal" if diferenca >= 0 else "inverse",
)

st.write("")

# -------------------------------------------------------------
# ANÁLISE INTELIGENTE & DIRECIONAMENTO
# -------------------------------------------------------------
if diferenca < 0 and saldo_conta > 0:
    st.error(f"⚠️ **Atenção Ray e Yure:** Faltam **R$ {abs(diferenca):,.2f}** para cobrir todas as pendências deste ciclo.")
    with st.expander("💡 Diagnóstico do Especialista: O que fazer primeiro?", expanded=True):
        st.markdown(
            f"""
        1. **Sobrevivência e Teto Primeiro**: Garanta imediatamente Moradia (Aluguel: R$ 1.390,00 e Luz/Água: R$ 256,00) e Transporte (R$ 400,00). Sem estabilidade básica, a renda familiar é prejudicada.
        2. **Alerta Crítico em Cartões (Total: R$ {df_contas[df_contas['categoria']=='Cartão de Crédito']['valor'].sum():,.2f})**:
           - O rotativo de cartões como Banco do Brasil (R$ 5.000), Neon (R$ 2.134) e Brasil Card (R$ 1.575) possui juros que passam de 400% ao ano.
           - Se não houver saldo para quitar tudo à vista, **não pague apenas o mínimo**. Ligue nos bancos antes do vencimento e solicite o parcelamento da fatura com taxa prefixada (costuma ser 4x menor que o rotativo).
        3. **Priorização por Impacto de Juros**:
           - Congele compras parceladas na Shopee e cartões até o valor global do cartão baixar de 30% da renda.
        """
        )
elif saldo_conta == 0:
    st.info("ℹ️ Insira na barra lateral o seu **Saldo em Conta / Receitas** para calcular se haverá sobra ou déficit de caixa.")
else:
    st.success("🎉 Excelente! O saldo disponível cobre 100% das contas pendentes do período.")

# -------------------------------------------------------------
# GRÁFICOS & DISTRIBUIÇÃO
# -------------------------------------------------------------
col_g1, col_g2 = st.columns([1, 1])

with col_g1:
    st.subheader("Distribuição por Categoria")
    df_cat = df_contas.groupby("categoria")["valor"].sum().reset_index()
    fig_pie = px.pie(
        df_cat,
        values="valor",
        names="categoria",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_g2:
    st.subheader("Top Despesas do Mês")
    df_top = df_contas.sort_values(by="valor", ascending=True).tail(8)
    fig_bar = px.bar(
        df_top,
        x="valor",
        y="descricao",
        orientation="h",
        text_auto=".2f",
        color="valor",
        color_continuous_scale="Reds",
    )
    fig_bar.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        xaxis_title="Valor (R$)",
        yaxis_title="",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------------------------------------
# TABELA INTERATIVA COM PERSISTÊNCIA DIRETA
# -------------------------------------------------------------
st.subheader("📋 Gerenciador de Contas (Edite e Salve)")
st.caption(
    "Altere status, valores ou datas diretamente na tabela abaixo e clique em **Salvar Alterações** para gravar no banco."
)

colunas_config = {
    "id": st.column_config.NumberColumn("ID", disabled=True),
    "descricao": st.column_config.TextColumn("Descrição", required=True),
    "categoria": st.column_config.SelectboxColumn(
        "Categoria",
        options=[
            "Cartão de Crédito",
            "Moradia",
            "Transporte",
            "Educação",
            "Alimentação",
            "Compras",
            "Família / Ajuda",
            "Dívidas / Pendências",
            "Serviços",
            "Outros",
        ],
        required=True,
    ),
    "valor": st.column_config.NumberColumn(
        "Valor (R$)", format="R$ %.2f", required=True
    ),
    "vencimento": st.column_config.DateColumn("Vencimento", required=True),
    "status": st.column_config.SelectboxColumn(
        "Status",
        options=["Aguardando Pagamento", "Pago", "Atrasado"],
        required=True,
    ),
    "tipo": st.column_config.SelectboxColumn(
        "Tipo",
        options=["Cartão", "Fixo", "Variável", "Emergência"],
        required=True,
    ),
}

df_editado = st.data_editor(
    df_contas,
    column_config=colunas_config,
    use_container_width=True,
    num_rows="dynamic",
    key="tabela_contas",
)

if st.button("💾 Salvar Alterações na Tabela", type="primary"):
    update_db(df_editado)
    st.toast("Todas as alterações foram salvas com sucesso!", icon="✅")
    st.rerun()