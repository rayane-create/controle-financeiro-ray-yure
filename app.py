import sqlite3
from datetime import date, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st

# -------------------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA & IDENTIDADE VISUAL
# -------------------------------------------------------------
st.set_page_config(
    page_title="Ray & Yure | Finanças",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #F8FAFC;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* Menu Lateral Leve */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F1F5F9 0%, #E2E8F0 100%) !important;
        border-right: 1px solid #CBD5E1;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] label {
        color: #1E293B !important;
    }
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] .stDateInput input,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px;
    }

    /* Top Banner Original */
    .header-banner {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.25);
        margin-bottom: 22px;
    }
    .header-title { font-size: 1.8rem; font-weight: 800; margin-bottom: 4px; }
    .header-subtitle { font-size: 0.95rem; opacity: 0.9; }

    /* Badge discreto de limite */
    .limite-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(4px);
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 8px;
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    /* Cards de Métricas */
    .metric-box {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
        border: 1px solid #E2E8F0;
    }
    .metric-title {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 6px;
    }
    .metric-val {
        font-size: 1.6rem;
        font-weight: 800;
    }

    .card-total { border-top: 4px solid #3B82F6; }
    .card-total .metric-title { color: #2563EB; }
    .card-total .metric-val { color: #0F172A; }

    .card-pendente { border-top: 4px solid #F59E0B; }
    .card-pendente .metric-title { color: #D97706; }
    .card-pendente .metric-val { color: #B45309; }

    .card-pago { border-top: 4px solid #10B981; }
    .card-pago .metric-title { color: #059669; }
    .card-pago .metric-val { color: #047857; }

    .card-saldo-pos { border-top: 4px solid #06B6D4; }
    .card-saldo-pos .metric-title { color: #0891B2; }
    .card-saldo-pos .metric-val { color: #0E7490; }

    .card-saldo-neg { border-top: 4px solid #EF4444; }
    .card-saldo-neg .metric-title { color: #DC2626; }
    .card-saldo-neg .metric-val { color: #B91C1C; }

    /* Alertas de Vencimento */
    .alert-card {
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .alert-vencidas { background: #FEF2F2; border-left: 5px solid #EF4444; color: #991B1B; }
    .alert-hoje { background: #FFFBEB; border-left: 5px solid #F59E0B; color: #92400E; }
    .alert-amanha { background: #EFF6FF; border-left: 5px solid #3B82F6; color: #1E40AF; }
    .alert-pagas { background: #ECFDF5; border-left: 5px solid #10B981; color: #065F46; }

    /* Painel de Filtros */
    .filtro-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 18px 6px 18px;
        margin-bottom: 15px;
    }

    div[data-testid="stDataEditor"] {
        background: #ffffff;
        border-radius: 12px;
        padding: 8px;
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
            mes_ano TEXT NOT NULL,
            descricao TEXT NOT NULL,
            categoria TEXT NOT NULL,
            valor REAL NOT NULL,
            limite_disponivel REAL DEFAULT 0.0,
            vencimento TEXT NOT NULL,
            status TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    """
    )

    c.execute("PRAGMA table_info(contas)")
    colunas_existentes = [col[1] for col in c.fetchall()]

    if "mes_ano" not in colunas_existentes:
        c.execute("ALTER TABLE contas ADD COLUMN mes_ano TEXT DEFAULT '11/2026'")
    if "limite_disponivel" not in colunas_existentes:
        c.execute("ALTER TABLE contas ADD COLUMN limite_disponivel REAL DEFAULT 0.0")

    c.execute("SELECT COUNT(*) FROM contas")
    if c.fetchone()[0] == 0:
        mes_atual = "11/2026"
        venc_padrao = "2026-11-20"
        dados_iniciais = [
            (mes_atual, "Aluguel", "Moradia", 1390.0, 0.0, venc_padrao, "Aguardando Pagamento", "Fixo"),
            (mes_atual, "Água e luz", "Moradia", 256.0, 0.0, venc_padrao, "Aguardando Pagamento", "Fixo"),
            (mes_atual, "Faculdade", "Educação", 665.0, 0.0, venc_padrao, "Aguardando Pagamento", "Fixo"),
            (mes_atual, "Mãe", "Família / Ajuda", 50.0, 0.0, venc_padrao, "Aguardando Pagamento", "Fixo"),
            (mes_atual, "Atrasados", "Dívidas / Pendências", 240.0, 0.0, venc_padrao, "Atrasado", "Variável"),
            (mes_atual, "Shopee", "Compras", 536.0, 0.0, venc_padrao, "Aguardando Pagamento", "Variável"),
            (mes_atual, "Nubank", "Cartão de Crédito", 1374.0, 0.0, venc_padrao, "Aguardando Pagamento", "Cartão"),
            (mes_atual, "Neon", "Cartão de Crédito", 2134.0, 0.0, venc_padrao, "Aguardando Pagamento", "Cartão"),
            (mes_atual, "Digio", "Cartão de Crédito", 250.0, 0.0, venc_padrao, "Aguardando Pagamento", "Cartão"),
            (mes_atual, "Bmg", "Cartão de Crédito", 720.0, 0.0, venc_padrao, "Aguardando Pagamento", "Cartão"),
            (mes_atual, "Bv", "Cartão de Crédito", 507.0, 0.0, venc_padrao, "Aguardando Pagamento", "Cartão"),
            (mes_atual, "Dm", "Outros", 250.0, 0.0, venc_padrao, "Aguardando Pagamento", "Variável"),
            (mes_atual, "Recarga pay", "Serviços", 136.0, 0.0, venc_padrao, "Aguardando Pagamento", "Variável"),
            (mes_atual, "Mercado pago", "Cartão de Crédito", 540.0, 0.0, venc_padrao, "Aguardando Pagamento", "Cartão"),
            (mes_atual, "Santander", "Cartão de Crédito", 830.0, 0.0, venc_padrao, "Aguardando Pagamento", "Cartão"),
            (mes_atual, "Caixa", "Cartão de Crédito", 1284.0, 0.0, venc_padrao, "Aguardando Pagamento", "Cartão"),
            (mes_atual, "Bb", "Cartão de Crédito", 5000.0, 0.0, venc_padrao, "Aguardando Pagamento", "Cartão"),
            (mes_atual, "Moto", "Transporte", 400.0, 0.0, venc_padrao, "Aguardando Pagamento", "Fixo"),
            (mes_atual, "Brasil card", "Cartão de Crédito", 1575.0, 0.0, venc_padrao, "Aguardando Pagamento", "Cartão"),
        ]
        c.executemany(
            """
            INSERT INTO contas (mes_ano, descricao, categoria, valor, limite_disponivel, vencimento, status, tipo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            dados_iniciais,
        )
        conn.commit()
    conn.close()


def load_all_data():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM contas", conn)
    conn.close()
    if not df.empty:
        df["vencimento"] = pd.to_datetime(df["vencimento"]).dt.date
    return df


def update_db_filtered(df_editado_completo, mes_selecionado):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM contas WHERE mes_ano = ?", (mes_selecionado,))

    df_save = df_editado_completo.copy()
    df_save["mes_ano"] = mes_selecionado
    df_save["vencimento"] = df_save["vencimento"].astype(str)

    colunas_salvar = ["mes_ano", "descricao", "categoria", "valor", "limite_disponivel", "vencimento", "status", "tipo"]
    df_save[colunas_salvar].to_sql("contas", conn, if_exists="append", index=False)
    conn.commit()
    conn.close()


def insert_conta(mes_ano, descricao, categoria, valor, limite, vencimento, status, tipo):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        """
        INSERT INTO contas (mes_ano, descricao, categoria, valor, limite_disponivel, vencimento, status, tipo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (mes_ano, descricao, categoria, valor, limite, str(vencimento), status, tipo),
    )
    conn.commit()
    conn.close()


def clonar_fixos(mes_origem, mes_destino):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT descricao, categoria, valor, limite_disponivel, tipo FROM contas WHERE mes_ano = ? AND tipo = 'Fixo'", (mes_origem,))
    fixos = c.fetchall()

    hoje = date.today().strftime("%Y-%m-%d")
    novos = []
    for f in fixos:
        novos.append((mes_destino, f[0], f[1], f[2], f[3], hoje, "Aguardando Pagamento", f[4]))

    c.executemany(
        """
        INSERT INTO contas (mes_ano, descricao, categoria, valor, limite_disponivel, vencimento, status, tipo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """,
        novos,
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
            <div style="background: white; padding: 34px; border-radius: 16px; border: 1px solid #E2E8F0; box-shadow: 0 10px 25px rgba(0,0,0,0.06); text-align: center;">
                <h2 style="color: #1E3A8A; margin-bottom: 4px;">💑 Ray & Yure</h2>
                <p style="color: #64748B; font-size: 0.95rem;">Painel de Controle Financeiro</p>
                <hr style="border: none; border-top: 1px solid #E2E8F0; margin: 20px 0;">
            """,
            unsafe_allow_html=True,
        )

        email = st.text_input("E-mail", placeholder="seu-email@gmail.com")
        senha = st.text_input("Senha", type="password", placeholder="Digite sua senha")

        email_correto = st.secrets.get("auth", {}).get("email", "rayanealmeida.adm@gmail.com")
        senha_correta = st.secrets.get("auth", {}).get("senha", "873401")

        if st.button("Acessar Painel", use_container_width=True, type="primary"):
            if email.strip().lower() == email_correto.strip().lower() and senha.strip() == str(senha_correta).strip():
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Credenciais inválidas. Verifique o e-mail ou a senha digitada.")

        st.markdown("</div>", unsafe_allow_html=True)


if not st.session_state.autenticado:
    tela_login()
    st.stop()

# -------------------------------------------------------------
# BARRA LATERAL (MENU LEVE COM EXPANDER)
# -------------------------------------------------------------
hoje = date.today()
amanha = hoje + timedelta(days=1)

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 10px 0 14px 0; text-align: center;">
            <h2 style="color: #1E3A8A; margin: 0; font-size: 1.4rem;">💑 Ray & Yure</h2>
            <p style="color: #64748B; font-size: 0.85rem; margin-top: 2px;">Planejamento & Contas</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("🗓️ Mês de Referência")
    meses_disponiveis = [
        "11/2026 (Novembro)",
        "12/2026 (Dezembro)",
        "01/2027 (Janeiro)",
        "02/2027 (Fevereiro)",
        "03/2027 (Março)",
    ]
    mes_opcao = st.selectbox("Selecione o mês:", meses_disponiveis, index=0)
    mes_selecionado = mes_opcao.split(" ")[0]

    st.write("")
    st.subheader("💵 Disponibilidade")
    saldo_conta = st.number_input(
        f"Saldo em Conta / Receita ({mes_selecionado}):",
        min_value=0.0,
        value=0.0,
        step=100.0,
        help="Informe o valor que você tem em conta disponível para esse mês.",
    )

    st.divider()

    with st.expander("➕ Nova Despesa (Clique para abrir)", expanded=False):
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
            novo_valor = st.number_input("Valor da Conta (R$)", min_value=0.01, step=10.0)
            novo_limite = st.number_input("Limite Disp. Cartão (R$)", min_value=0.0, step=50.0)
            novo_venc = st.date_input("Vencimento", value=hoje)
            novo_status = st.selectbox("Status", ["Aguardando Pagamento", "Pago", "Atrasado"])
            novo_tipo = st.selectbox("Tipo", ["Cartão", "Fixo", "Variável", "Emergência"])

            submit = st.form_submit_button("Cadastrar Despesa", use_container_width=True)
            if submit:
                if nova_desc.strip():
                    insert_conta(mes_selecionado, nova_desc, nova_cat, novo_valor, novo_limite, novo_venc, novo_status, novo_tipo)
                    st.success(f"Conta inserida em {mes_selecionado}!")
                    st.rerun()
                else:
                    st.error("Preencha a descrição da conta.")

    st.divider()
    if mes_selecionado == "12/2026":
        if st.button("📋 Copiar Custos Fixos de Nov para Dez", use_container_width=True):
            clonar_fixos("11/2026", "12/2026")
            st.success("Custos fixos copiados para Dezembro!")
            st.rerun()

    if st.button("🚪 Sair do Painel", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# -------------------------------------------------------------
# CÁLCULOS
# -------------------------------------------------------------
df_todos = load_all_data()
df_mes = df_todos[df_todos["mes_ano"] == mes_selecionado].copy() if not df_todos.empty else pd.DataFrame()

total_deve = float(df_mes["valor"].sum()) if not df_mes.empty else 0.0
total_pago = float(df_mes[df_mes["status"] == "Pago"]["valor"].sum()) if not df_mes.empty else 0.0
total_pendente = float(df_mes[df_mes["status"] != "Pago"]["valor"].sum()) if not df_mes.empty else 0.0
total_limite_cartoes = float(df_mes[df_mes["categoria"] == "Cartão de Crédito"]["limite_disponivel"].sum()) if not df_mes.empty else 0.0
diferenca = saldo_conta - total_pendente

if not df_mes.empty:
    contas_pendentes = df_mes[df_mes["status"] != "Pago"]
    contas_vencidas = contas_pendentes[(contas_pendentes["vencimento"] < hoje) | (contas_pendentes["status"] == "Atrasado")]
    contas_hoje = contas_pendentes[contas_pendentes["vencimento"] == hoje]
    contas_amanha = contas_pendentes[contas_pendentes["vencimento"] == amanha]
    contas_pagas = df_mes[df_mes["status"] == "Pago"]
else:
    contas_pendentes = contas_vencidas = contas_hoje = contas_amanha = contas_pagas = pd.DataFrame()

# Top Banner Original com Badge de Limite Disponível
nome_mes = mes_opcao.split(' ')[1].replace('(', '').replace(')', '')
st.markdown(
    f"""
    <div class="header-banner">
        <div class="header-title">Ray & Yure | Painel de {nome_mes} ✨</div>
        <div class="header-subtitle">Controle de vencimentos, limites de cartão e planejamento do mês.</div>
        <div class="limite-badge">💳 Limite Disponível Total em Cartões: R$ {total_limite_cartoes:,.2f}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Cards de Métricas Principais
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-box card-total"><div class="metric-title">Total em Contas</div><div class="metric-val">R$ {total_deve:,.2f}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-box card-pendente"><div class="metric-title">Aguardando Pagamento</div><div class="metric-val">R$ {total_pendente:,.2f}</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-box card-pago"><div class="metric-title">Já Liquidado</div><div class="metric-val">R$ {total_pago:,.2f}</div></div>', unsafe_allow_html=True)
with c4:
    card_style = "card-saldo-pos" if diferenca >= 0 else "card-saldo-neg"
    status_label = "Sobra em Caixa" if diferenca >= 0 else "Falta para Fechar"
    st.markdown(f'<div class="metric-box {card_style}"><div class="metric-title">{status_label}</div><div class="metric-val">R$ {abs(diferenca):,.2f}</div></div>', unsafe_allow_html=True)

st.write("")

# -------------------------------------------------------------
# ANÁLISE CONDICIONAL DISCRETA
# -------------------------------------------------------------
if saldo_conta == 0:
    st.info("ℹ️ Insira na barra lateral o seu **Saldo em Conta / Receitas** para calcular se haverá sobra ou déficit de caixa.")
elif diferenca < 0:
    st.error(f"⚠️ **Atenção Ray e Yure:** Faltam **R$ {abs(diferenca):,.2f}** para cobrir todas as pendências deste ciclo.")
    with st.expander("💡 Diagnóstico do Especialista: O que fazer primeiro?", expanded=False):
        total_cartoes = df_mes[df_mes["categoria"] == "Cartão de Crédito"]["valor"].sum() if not df_mes.empty else 0.0
        st.markdown(
            f"""
        1. **Sobrevivência e Teto Primeiro**: Garanta imediatamente Moradia (Aluguel: R$ 1.390,00 e Luz/Água: R$ 256,00) e Transporte (R$ 400,00).
        2. **Alerta Crítico em Cartões (Total: R$ {total_cartoes:,.2f})**:
           - O rotativo possui juros altíssimos.
           - Se não houver saldo para quitar tudo à vista, **não pague apenas o mínimo**. Ligue nos bancos antes do vencimento e solicite o parcelamento pré-fixado.
        3. **Freio Imediato**: Congele compras parceladas (Shopee, etc.) até a soma dos cartões normalizar.
        """
        )
else:
    st.success(f"🎉 **Excelente!** O saldo disponível cobre 100% das contas com sobra de **R$ {diferenca:,.2f}**.")
    with st.expander("🎯 Sugestão para a sobra de caixa:", expanded=False):
        st.markdown(
            """
        - **Reserva de Emergência**: Guarde uma parte em uma aplicação com liquidez diária (100% CDI).
        - **Quitação de Cartões Menores**: Antecipe faturas menores para diminuir a quantidade de boletos a acompanhar no próximo mês.
        """
        )

st.write("")

# -------------------------------------------------------------
# ALERTAS DE VENCIMENTO
# -------------------------------------------------------------
st.subheader("Alertas & Prazos de Vencimento")

a1, a2, a3, a4 = st.columns(4)

with a1:
    qtd_vencidas = len(contas_vencidas)
    val_vencidas = contas_vencidas['valor'].sum() if qtd_vencidas > 0 else 0.0
    st.markdown(
        f"""
        <div class="alert-card alert-vencidas">
            <span style="font-size: 1.05rem;">⚠️ {qtd_vencidas} Vencida(s)</span><br>
            <span style="font-size: 0.85rem; font-weight: normal;">R$ {val_vencidas:,.2f} em atraso</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Ver quais são", expanded=False):
        if qtd_vencidas > 0:
            for _, r in contas_vencidas.iterrows():
                st.markdown(f"• **{r['descricao']}**: R$ {r['valor']:,.2f} *(Venceu: {r['vencimento'].strftime('%d/%m')})*")
        else:
            st.caption("Nenhuma conta vencida! 👏")

with a2:
    qtd_hoje = len(contas_hoje)
    val_hoje = contas_hoje['valor'].sum() if qtd_hoje > 0 else 0.0
    st.markdown(
        f"""
        <div class="alert-card alert-hoje">
            <span style="font-size: 1.05rem;">⏰ {qtd_hoje} Vencem Hoje</span><br>
            <span style="font-size: 0.85rem; font-weight: normal;">R$ {val_hoje:,.2f} para pagar</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Ver quais são", expanded=False):
        if qtd_hoje > 0:
            for _, r in contas_hoje.iterrows():
                st.markdown(f"• **{r['descricao']}**: R$ {r['valor']:,.2f}")
        else:
            st.caption("Nenhuma conta vencendo hoje.")

with a3:
    qtd_amanha = len(contas_amanha)
    val_amanha = contas_amanha['valor'].sum() if qtd_amanha > 0 else 0.0
    st.markdown(
        f"""
        <div class="alert-card alert-amanha">
            <span style="font-size: 1.05rem;">📅 {qtd_amanha} Vencem Amanhã</span><br>
            <span style="font-size: 0.85rem; font-weight: normal;">R$ {val_amanha:,.2f} para amanhã</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Ver quais são", expanded=False):
        if qtd_amanha > 0:
            for _, r in contas_amanha.iterrows():
                st.markdown(f"• **{r['descricao']}**: R$ {r['valor']:,.2f}")
        else:
            st.caption("Nenhuma conta para amanhã.")

with a4:
    qtd_pagas = len(contas_pagas)
    st.markdown(
        f"""
        <div class="alert-card alert-pagas">
            <span style="font-size: 1.05rem;">✅ {qtd_pagas} Já Pagas</span><br>
            <span style="font-size: 0.85rem; font-weight: normal;">R$ {total_pago:,.2f} quitados</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Ver quais são", expanded=False):
        if qtd_pagas > 0:
            for _, r in contas_pagas.iterrows():
                st.markdown(f"• **{r['descricao']}**: R$ {r['valor']:,.2f}")
        else:
            st.caption("Nenhuma conta marcada como paga ainda.")

st.write("")

# -------------------------------------------------------------
# GRÁFICOS
# -------------------------------------------------------------
if not df_mes.empty:
    col_g1, col_g2 = st.columns([1, 1])

    with col_g1:
        st.subheader("Distribuição por Categoria")
        df_cat = df_mes.groupby("categoria")["valor"].sum().reset_index()
        fig_pie = px.pie(
            df_cat,
            values="valor",
            names="categoria",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Prism,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(margin=dict(t=15, b=15, l=15, r=15), showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_g2:
        st.subheader("Top Despesas do Mês")
        df_top = df_mes.sort_values(by="valor", ascending=True).tail(7)
        fig_bar = px.bar(
            df_top,
            x="valor",
            y="descricao",
            orientation="h",
            text_auto=".2f",
            color="valor",
            color_continuous_scale="Tealgrn",
        )
        fig_bar.update_layout(
            margin=dict(t=15, b=15, l=15, r=15),
            xaxis_title="Valor (R$)",
            yaxis_title="",
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# -------------------------------------------------------------
# TABELA DE CONTAS COM FILTROS EM CADA COLUNA
# -------------------------------------------------------------
st.subheader(f"📋 Tabela de Contas - {mes_selecionado}")
st.caption("Use os filtros abaixo para encontrar despesas específicas por categoria, status, tipo ou descrição.")

# Painel de Filtros Rápidos
with st.container():
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)

    with f_col1:
        opcoes_cat = ["Todas"] + sorted(list(df_mes["categoria"].unique())) if not df_mes.empty else ["Todas"]
        filtro_tabela_cat = st.selectbox("Filtrar Categoria:", opcoes_cat, key="filtro_tab_cat")

    with f_col2:
        opcoes_status = ["Todos", "Aguardando Pagamento", "Pago", "Atrasado"]
        filtro_tabela_status = st.selectbox("Filtrar Status:", opcoes_status, key="filtro_tab_status")

    with f_col3:
        opcoes_tipo = ["Todos", "Cartão", "Fixo", "Variável", "Emergência"]
        filtro_tabela_tipo = st.selectbox("Filtrar Tipo:", opcoes_tipo, key="filtro_tab_tipo")

    with f_col4:
        busca_texto = st.text_input("Buscar por Descrição:", placeholder="Ex: Nubank, Aluguel...", key="filtro_tab_busca")

# Aplicação dos Filtros
df_tabela_filtrada = df_mes.copy() if not df_mes.empty else pd.DataFrame()

if not df_tabela_filtrada.empty:
    if filtro_tabela_cat != "Todas":
        df_tabela_filtrada = df_tabela_filtrada[df_tabela_filtrada["categoria"] == filtro_tabela_cat]
    if filtro_tabela_status != "Todos":
        df_tabela_filtrada = df_tabela_filtrada[df_tabela_filtrada["status"] == filtro_tabela_status]
    if filtro_tabela_tipo != "Todos":
        df_tabela_filtrada = df_tabela_filtrada[df_tabela_filtrada["tipo"] == filtro_tabela_tipo]
    if busca_texto.strip():
        df_tabela_filtrada = df_tabela_filtrada[df_tabela_filtrada["descricao"].str.contains(busca_texto.strip(), case=False, na=False)]

colunas_config = {
    "id": st.column_config.NumberColumn("ID", disabled=True),
    "mes_ano": st.column_config.TextColumn("Mês/Ano", disabled=True),
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
    "valor": st.column_config.NumberColumn("Valor a Pagar (R$)", format="R$ %.2f", required=True),
    "limite_disponivel": st.column_config.NumberColumn("Limite Disp. no Cartão (R$)", format="R$ %.2f", default=0.0),
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

df_editado_filtrado = st.data_editor(
    df_tabela_filtrada,
    column_config=colunas_config,
    use_container_width=True,
    num_rows="dynamic",
    key=f"tabela_{mes_selecionado}_{filtro_tabela_cat}_{filtro_tabela_status}_{filtro_tabela_tipo}_{busca_texto}",
)

if st.button("💾 Salvar Alterações Deste Mês", type="primary", use_container_width=True):
    # Mescla com segurança o que foi editado no conjunto geral do mês
    df_final_salvar = df_mes.copy()
    if not df_editado_filtrado.empty:
        # Se algum id existente foi atualizado
        for _, row in df_editado_filtrado.iterrows():
            if pd.notna(row.get("id")):
                idx = df_final_salvar[df_final_salvar["id"] == row["id"]].index
                if len(idx) > 0:
                    for col in ["descricao", "categoria", "valor", "limite_disponivel", "vencimento", "status", "tipo"]:
                        df_final_salvar.loc[idx, col] = row[col]
            else:
                # Nova linha adicionada na visão filtrada
                df_final_salvar = pd.concat([df_final_salvar, pd.DataFrame([row])], ignore_index=True)
                
    update_db_filtered(df_final_salvar, mes_selecionado)
    st.toast("Alterações salvas com sucesso no banco de dados!", icon="✅")
    st.rerun()

# Realce visual direto: contas com status "Pago" ficam verdes
if not df_mes.empty and (df_mes["status"] == "Pago").any():
    def highlight_pagos(row):
        if row["status"] == "Pago":
            return ["background-color: #DCFCE7; color: #166534; font-weight: 600;"] * len(row)
        return [""] * len(row)

    cols_view = ["descricao", "categoria", "valor", "limite_disponivel", "vencimento", "status", "tipo"]
    df_pagos_view = df_mes[cols_view].style.apply(highlight_pagos, axis=1).format({
        "valor": "R$ {:,.2f}",
        "limite_disponivel": "R$ {:,.2f}",
    })
    st.caption("Visão geral com destaque verde nas contas já liquidadas:")
    st.dataframe(df_pagos_view, use_container_width=True)

# -------------------------------------------------------------
# CALCULADORA / SIMULADOR COM "SELECIONAR TODAS"
# -------------------------------------------------------------
st.write("")
with st.expander("🧮 Calculadora & Simulador de Pagamentos (Clique para simular)", expanded=False):
    st.markdown("Filtre por categoria e use a opção de **Selecionar Todas** para calcular o impacto total rapidamente.")

    if not df_mes.empty:
        todas_cats = ["Todas"] + sorted(list(df_mes["categoria"].unique()))
        filtro_cat = st.selectbox("Filtrar por Categoria na Simulação:", todas_cats)

        df_simulacao = df_mes.copy()
        if filtro_cat != "Todas":
            df_simulacao = df_simulacao[df_simulacao["categoria"] == filtro_cat]

        c_sel1, c_sel2 = st.columns([1.5, 3])
        with c_sel1:
            marcar_todas = st.checkbox("☑️ Selecionar Todas da Seleção", value=False, key="check_todas")

        df_simulacao["Pagar?"] = marcar_todas

        sim_col_config = {
            "Pagar?": st.column_config.CheckboxColumn("Pagar?", default=marcar_todas),
            "descricao": st.column_config.TextColumn("Descrição", disabled=True),
            "categoria": st.column_config.TextColumn("Categoria", disabled=True),
            "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f", disabled=True),
            "status": st.column_config.TextColumn("Status", disabled=True),
        }

        tabela_sim = st.data_editor(
            df_simulacao[["Pagar?", "descricao", "categoria", "valor", "status"]],
            column_config=sim_col_config,
            use_container_width=True,
            disabled=["descricao", "categoria", "valor", "status"],
            key=f"tabela_simulador_{marcar_todas}_{filtro_cat}",
        )

        selecionados = tabela_sim[tabela_sim["Pagar?"] == True]
        total_selecionado = selecionados["valor"].sum()
        sobra_simulada = saldo_conta - total_selecionado

        st.markdown("---")
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Contas Selecionadas", f"{len(selecionados)} conta(s)")
        sc2.metric("Total da Simulação", f"R$ {total_selecionado:,.2f}")

        if saldo_conta > 0:
            sc3.metric(
                "Saldo Restante Após Quitação",
                f"R$ {sobra_simulada:,.2f}",
                delta=f"{'Sobra' if sobra_simulada >= 0 else 'Falta'} R$ {abs(sobra_simulada):,.2f}",
                delta_color="normal" if sobra_simulada >= 0 else "inverse"
            )
        else:
            sc3.info("Informe o Saldo em Conta na lateral para ver o impacto.")
    else:
        st.info("Nenhuma conta registrada para este mês.")
