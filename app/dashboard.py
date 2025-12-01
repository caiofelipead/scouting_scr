# (Arquivo muito longo, vou enviar apenas as linhas corrigidas)
# Linhas 1760-1770 corrigidas:

        col_idade1, col_idade2 = st.columns(2)
        with col_idade1:
            idade_min = st.number_input(
                "Idade Mínima", 
                min_value=15, 
                max_value=45, 
                value=st.session_state.get('filtros_busca', {}).get('idade_min', 18),
                key="busca_idade_min"
            )
        with col_idade2:
            idade_max = st.number_input(
                "Idade Máxima", 
                min_value=15, 
                max_value=45, 
                value=st.session_state.get('filtros_busca', {}).get('idade_max', 35),
                key="busca_idade_max"
            )
        
        media_min = st.slider(
            "Média Mínima (Avaliação)",
            min_value=1.0,
            max_value=5.0,
            value=st.session_state.get('filtros_busca', {}).get('media_min', 3.0),
            step=0.5,
            key="busca_media_min",
            help="Apenas jogadores com média igual ou superior"
        )
