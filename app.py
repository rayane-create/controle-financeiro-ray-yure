import sqlite3
from datetime import date, datetime
import pandas as pd
import plotly.express as px
import streamlit as st

# -------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA & IDENTIDADE VISUAL
# -------------------------------------------------------------
st.set_page_config(
    page_title="Ray & Yure | Finanças",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Fundo suave e fontes modernas */
    .stApp {
        background: linear-gradient(135deg, #f8faff 0%, #f0f4f8 100%);
        font-family: 'Inter', -apple-system, sans-serif;
    }
    
    /* Top Banner Personalizado */
    .header-banner {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.25);
        margin-bottom: 25px;
    }
    .header-title { font-size: 1.8rem; font-weight: 800; margin-bottom: 4px; }
    .header-subtitle { font-size: 0.95rem; opacity: 0.9; }

    /* Cards de Métricas Estilizados */
    .metric-box {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
        border: 1px solid #E2E8F0;
        transition: transform 0.2s ease;
    }
    .metric-box:hover {
        transform: translateY(-2px);
    }
    .metric-title {
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-val {
        font-size: 1.7rem;
        font-weight: 800;
    }
    
    /* Cores dos cards */
    .card-total { border-top: 5px solid #3B82F6; }
    .card-total .metric-title { color: #2563EB; }
    .card-total .metric-val { color: #1E293B; }

    .card-pendente { border-top: 5px solid #F59E0B; }
    .card-pendente .metric-title { color: #D97706; }
    .card-pendente .metric-val { color: #B45309; }

    .card-pago { border-top: 5px solid #10B981; }
    .card-pago .metric-title { color: #059669; }
    .card-pago .metric-val { color: #047857; }

    .card-saldo-pos { border-top: 5px solid #06B6D4; }
    .card-saldo-pos .metric-title { color: #0891B2; }
    .card-saldo-pos .metric-val { color: #0E7490; }

    .card-saldo-neg { border-top: 5px solid #EF4444; }
    .card-saldo-neg .metric-title { color: #DC2626; }
    .card-saldo-neg .metric-val { color: #B91C1C; }

    /* Estilização da tabela de dados */
    div[data-testid="stDataEditor"] {
        background: #ffffff;
        border-radius: 12px;
        padding: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        border: 1px solid #E2E8F0;
    }
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

    c.execute("SELECT COUNT(*) FROM contas")
    if c.fetchone()[0] == 0:
        hoje = date.today().strftime("%Y-%m-%d")
        dados_iniciais = [
            ("Aluguel", "Moradia", 1390.0, hoje, "Aguardando Pagamento", "Fixo"),
            ("Água e luz", "Moradia", 256.0, hoje, "Aguardando Pagamento", "Fixo"),
            ("Faculdade", "Educação", 665.0, hoje, "Aguardando Pagamento", "Fixo"),
            ("Mãe", "Família / Ajuda", 50.0, hoje, "Aguardando Pagamento", "Fixo"),
            ("Atrasados", "Dívidas / Pendências", 240.0, hoje, "Aguardando Pagamento", "Variável"),
            ("Shopee", "Compras", 536.0, hoje, "Aguardando Pagamento", "Variável"),
            ("Nubank", "Cartão de Crédito", 1374.0, hoje, "Aguardando Pagamento", "Cartão"),
            ("Neon", "Cartão de Crédito", 2134.0, hoje, "Aguardando Pagamento", "Cartão"),
            ("Digio", "Cartão de Crédito", 250.0, hoje, "Aguardando Pagamento", "Cartão"),
            ("Bmg", "Cartão de Crédito", 720.0, hoje, "Aguardando Pagamento", "Cartão"),
            ("Bv", "Cartão de Crédito", 507.0, hoje, "Aguardando Pagamento", "Cartão"),
            ("Dm", "Outros", 250.0, hoje, "Aguardando Pagamento", "Variável"),
            ("Recarga pay", "Serviços", 136.0, hoje, "Aguardando Pagamento", "Variável"),
            ("Mercado pago", "Cartão de Crédito", 540.0, hoje, "Aguardando Pagamento", "Cartão"),
            ("Santander", "Cartão de Crédito", 830.0, hoje, "Aguardando Pagamento", "Cartão"),
            ("Caixa", "Cartão de Crédito", 1284.0, hoje, "Aguardando Pagamento", "Cartão"),
            ("Bb", "Cartão de Crédito", 5000.0, hoje, "Aguardando Pagamento", "Cartão"),
            ("Moto", "Transporte", 400.0, hoje, "Aguardando Pagamento", "Fixo"),
            ("Brasil card", "Cartão de Crédito", 1575.0, hoje, "Aguardando Pagamento", "Cartão"),
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
    # Conversão crucial para evitar o erro com DateColumn
    df["vencimento"] = pd.to_datetime(df["vencimento"]).dt.date
    return df


def update_db(df):
    conn = sqlite3.connect(DB_NAME)
    df_save = df.copy()
    df_save["vencimento"] = df_save["vencimento"].astype(str)
    df_save.to_sql("contas", conn, if_exists="replace", index=False)
    conn.close()


def insert_conta(descricao, categoria, valor, vencimento, status, tipo):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO contas (descricao, categoria, valor, vencimento, status, tipo)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (descricao, categoria, valor, str(vencimento), status, tipo),
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
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div style="background: white; padding: 32px; border-radius: 16px; border: 1px solid #E2E8F0; box-shadow: 0 10px 25px rgba(0,0,0,0.05); text-align: center;">
                <h2 style="color: #1E3A8A; margin-bottom: 4px;">💑 Ray & Yure</h2>
                <p style="color: #64748B; font-size: 0.95rem;">Controle Financeiro Familiar</p>
                <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 20px 0;">
            """,
            unsafe_allow_html=True,
        )

        email = st.text_input("E-mail", placeholder="seu-email@gmail.com")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")

        if st.button("Acessar Painel", use_container_width=True, type="primary"):
            if (
                email.strip().lower() == "rayanealmeida.adm@gmail.com"
                and senha.strip() == "873401"
            ):
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciais inválidas. Verifique o e-mail ou a senha digitada.")

        st.markdown("</div>", unsafe_allow_html=True)


if not st.session_state.autenticado:
    tela_login()
    st.stop()

# -------------------------------------------------------------
# PAINEL AUTENTICADO
# -------------------------------------------------------------
df_contas = load_data()

# Barra lateral estilizada
with st.sidebar:
    st.markdown(
        """
        <div style="padding: 10px 0; text-align: center;">
            <h3 style="color: #1E3A8A; margin: 0;">💑 Ray & Yure</h3>
            <span style="background: #E0E7FF; color: #3730A3; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 600;">Modo Ativo</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.write("")

    st.subheader("💵 Disponibilidade")
    saldo_conta = st.number_input(
        "Saldo em Conta / Renda Líquida (R$):",
        min_value=0.0,
        value=0.0,
        step=100.0,
        help="Informe o valor que você tem em conta para quitar as contas.",
    )

    st.divider()
    st.subheader("➕ Nova Despesa")
    with st.form("form_nova_conta", clear_on_submit=True):
        nova_desc = st.text_input("Descrição (Ex: Compras, Cartão)")
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
        novo_status = st.selectbox("Status", ["Aguardando Pagamento", "Pago", "Atrasado"])
        novo_tipo = st.selectbox("Tipo", ["Cartão", "Fixo", "Variável", "Emergência"])

        submit = st.form_submit_button("Adicionar Despesa", use_container_width=True)
        if submit:
            if nova_desc.strip():
                insert_conta(nova_desc, nova_cat, novo_valor, novo_venc, novo_status, novo_tipo)
                st.success("Conta adicionada com sucesso!")
                st.rerun()
            else:
                st.error("Por favor, preencha a descrição.")

    st.divider()
    if st.button("🚪 Sair do Painel", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# -------------------------------------------------------------
# CÁLCULOS E PAINEL PRINCIPAL
# -------------------------------------------------------------
total_deve = float(df_contas["valor"].sum())
total_pago = float(df_contas[df_contas["status"] == "Pago"]["valor"].sum())
total_pendente = float(df_contas[df_contas["status"] != "Pago"]["valor"].sum())
diferenca = saldo_conta - total_pendente

# Banner de Boas-Vindas
st.markdown(
    """
    <div class="header-banner">
        <div class="header-title">Olá, Ray & Yure ✨</div>
        <div class="header-subtitle">Gestão financeira do mês, liquidações e planejamento inteligente.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Cards de Métricas com layout colorido
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class="metric-box card-total">
            <div class="metric-title">Total Geral</div>
            <div class="metric-val">R$ {total_deve:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    st.markdown(
        f"""
        <div class="metric-box card-pendente">
            <div class="metric-title">Aguardando Pagamento</div>
            <div class="metric-val">R$ {total_pendente:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    st.markdown(
        f"""
        <div class="metric-box card-pago">
            <div class="metric-title">Já Liquidado</div>
            <div class="metric-val">R$ {total_pago:,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    card_style = "card-saldo-pos" if diferenca >= 0 else "card-saldo-neg"
    status_label = "Sobra em Caixa" if diferenca >= 0 else "Falta para Fechar"
    st.markdown(
        f"""
        <div class="metric-box {card_style}">
            <div class="metric-title">{status_label}</div>
            <div class="metric-val">R$ {abs(diferenca):,.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# -------------------------------------------------------------
# ANÁLISE CONSULTIVA
# -------------------------------------------------------------
if saldo_conta == 0:
    st.info("💡 **Dica:** Adicione seu **saldo em conta** na barra lateral para calcular se sobra ou falta dinheiro no mês.")
elif diferenca < 0:
    st.error(f"⚠️ **Atenção:** O saldo atual não cobre todas as pendências. Faltam **R$ {abs(diferenca):,.2f}**.")
    with st.expander("📌 Guia Estratégico: O que priorizar?", expanded=True):
        st.markdown(
            f"""
            - **1º Moradia e Sobrevivência:** Garanta Aluguel (R$ 1.390,00) e Água/Luz (R$ 256,00). Manter as contas essenciais em dia evita cortes e perda de estabilidade.
            - **2º Atenção Máxima aos Cartões (Total: R$ {df_contas[df_contas['categoria']=='Cartão de Crédito']['valor'].sum():,.2f}):**
                - Se não conseguir quitar faturas de valores mais altos (BB R$ 5.000, Neon R$ 2.134, Brasil Card R$ 1.575), **não deixe cair no crédito rotativo sem negociar**.
                - O parcelamento direto da fatura pelo app do banco tem taxas substancialmente menores do que o juro padrão do rotativo.
            - **3º Gastos Variáveis:** Suspenda compras parceladas (Shopee e afins) nos próximos ciclos até reduzir a proporção de cartões para menos de 30% da renda.
            """
        )
else:
    st.success("🎉 **Excelente!** O saldo disponível é suficiente para pagar todas as contas pendentes do período.")

# -------------------------------------------------------------
# GRÁFICOS INTERATIVOS
# -------------------------------------------------------------
st.write("")
col_g1, col_g2 = st.columns([1, 1])

with col_g1:
    st.subheader("📊 Gastos por Categoria")
    df_cat = df_contas.groupby("categoria")["valor"].sum().reset_index()
    fig_pie = px.pie(
        df_cat,
        values="valor",
        names="categoria",
        hole=0.45,
        color_discrete_sequence=px.colors.sequential.Teal,
    )
    fig_pie.update_traces(textposition="inside", textinfo="percent+label")
    fig_pie.update_layout(margin=dict(t=15, b=15, l=15, r=15), showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_g2:
    st.subheader("🔥 Maiores Despesas do Mês")
    df_top = df_contas.sort_values(by="valor", ascending=True).tail(7)
    fig_bar = px.bar(
        df_top,
        x="valor",
        y="descricao",
        orientation="h",
        text_auto=".2f",
        color="valor",
        color_continuous_scale="Viridis",
    )
    fig_bar.update_layout(
        margin=dict(t=15, b=15, l=15, r=15),
        xaxis_title="Valor (R$)",
        yaxis_title="",
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------------------------------------
# TABELA INTERATIVA (EDIÇÃO DIRETA COM PERSISTÊNCIA)
# -------------------------------------------------------------
st.subheader("📋 Tabela Gerenciadora de Contas")
st.caption("Você pode alterar status, datas e valores diretamente nas células. Ao terminar, clique no botão azul abaixo para salvar.")

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
    "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f", required=True),
    "vencimento": st.column_config.DateColumn("Vencimento", required=True, format="DD/MM/YYYY"),
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

if st.button("💾 Salvar Alterações", type="primary", use_container_width=True):
    update_db(df_editado)
    st.toast("Dados atualizados com sucesso!", icon="✅")
    st.rerun()
