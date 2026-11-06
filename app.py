# -------------------------------------------------------------
# CALCULADORA / SIMULADOR (APENAS CONTAS PENDENTES / NÃO PAGAS)
# -------------------------------------------------------------
st.write("")
with st.expander("🧮 Calculadora & Simulador de Pagamentos (Clique para abrir)", expanded=False):
    # Filtra automaticamente para excluir contas já pagas
    df_sim_pendentes = df_mes[df_mes["status"] != "Pago"].copy() if not df_mes.empty else pd.DataFrame()

    if not df_sim_pendentes.empty:
        st.markdown("Selecione quais despesas pendentes deseja simular para calcular o desembolso e o impacto no seu saldo:")

        todas_cats = ["Todas"] + sorted(list(df_sim_pendentes["categoria"].unique()))
        filtro_sim_cat = st.selectbox("Categoria da Simulação:", todas_cats, key="filtro_sim")

        df_sim = df_sim_pendentes.copy()
        if filtro_sim_cat != "Todas":
            df_sim = df_sim[df_sim["categoria"] == filtro_sim_cat]

        marcar_todas = st.checkbox("☑️ Selecionar Todas da Seleção", value=False, key="check_todas_sim")
        df_sim["Pagar?"] = marcar_todas

        sim_col_config = {
            "Pagar?": st.column_config.CheckboxColumn("Pagar?", default=marcar_todas),
            "descricao": st.column_config.TextColumn("Descrição", disabled=True),
            "categoria": st.column_config.TextColumn("Categoria", disabled=True),
            "valor": st.column_config.NumberColumn("Valor (R$)", format="R$ %.2f", disabled=True),
            "status": st.column_config.TextColumn("Status", disabled=True),
        }

        tab_sim = st.data_editor(
            df_sim[["Pagar?", "descricao", "categoria", "valor", "status"]],
            column_config=sim_col_config,
            use_container_width=True,
            disabled=["descricao", "categoria", "valor", "status"],
            key=f"sim_{marcar_todas}_{filtro_sim_cat}_{len(df_sim)}",
        )

        sel = tab_sim[tab_sim["Pagar?"] == True]
        tot_sel = sel["valor"].sum()
        sobra = saldo_conta - tot_sel

        st.markdown("---")
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Contas Selecionadas", f"{len(sel)} conta(s)")
        sc2.metric("Total da Simulação", f"R$ {tot_sel:,.2f}")
        if saldo_conta > 0:
            sc3.metric(
                "Saldo Restante",
                f"R$ {sobra:,.2f}",
                delta=f"{'Sobra' if sobra >= 0 else 'Falta'} R$ {abs(sobra):,.2f}",
                delta_color="normal" if sobra >= 0 else "inverse",
            )
        else:
            sc3.info("Informe o Saldo em Conta na lateral para ver o impacto.")
    else:
        st.success("🎉 Todas as contas deste mês já foram pagas! Nenhuma pendência para simular.")
