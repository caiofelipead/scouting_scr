"""
Módulo de Avaliação Massiva de Atletas
Permite avaliar múltiplos jogadores de forma rápida e eficiente
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from psycopg2.extras import execute_batch


# ============================================
# FUNÇÃO DE CARREGAMENTO (ESCOPO GLOBAL)
# ============================================

@st.cache_data(ttl=300, show_spinner=False)
def carregar_jogadores(_db):
    """Carrega jogadores do banco com cache"""
    query = """
    SELECT 
        j.id_jogador,
        j.nome,
        v.posicao,
        v.clube,
        j.idade_atual as idade
    FROM jogadores j
    LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
    ORDER BY j.nome
    """
    return pd.read_sql(query, _db.engine)


# ============================================
# FUNÇÃO PRINCIPAL DA ABA
# ============================================

def criar_aba_avaliacao_massiva(db):
    """
    Aba para avaliação massiva de atletas
    """
    st.title("📋 Avaliação Massiva de Atletas")
    
    # Sidebar com informações do avaliador
    st.sidebar.header("Informações da Avaliação")
    avaliador = st.sidebar.text_input("Nome do Avaliador", value="Caio Felipe")
    data_avaliacao = st.sidebar.date_input("Data da Avaliação", value=datetime.now())
    
    # Carregar lista de jogadores do banco
    df_jogadores = carregar_jogadores(db)
    
    # Verificar se há jogadores
    if len(df_jogadores) == 0:
        st.warning("Nenhum jogador encontrado no banco de dados.")
        return
    
    # Modo de operação
    modo = st.radio(
        "Modo de Avaliação",
        ["Tabela Editável", "Formulário Individual"],
        horizontal=True
    )
    
    if modo == "Tabela Editável":
        avaliacao_tabela(df_jogadores, avaliador, data_avaliacao, db)
    else:
        avaliacao_formulario(df_jogadores, avaliador, data_avaliacao, db)


def avaliacao_tabela(df_jogadores, avaliador, data_avaliacao, db):
    """
    Modo de avaliação por tabela editável
    """
    st.subheader("📊 Avaliação por Tabela")
    st.info("💡 Selecione os jogadores e preencha as notas diretamente na tabela")
    
    # Seleção de jogadores
    col1, col2 = st.columns([3, 1])
    with col1:
        # Filtros
        posicoes = ['Todas'] + sorted(df_jogadores['posicao'].dropna().unique().tolist())
        posicao_filtro = st.selectbox("Filtrar por Posição", posicoes)
        
        if posicao_filtro != 'Todas':
            df_filtrado = df_jogadores[df_jogadores['posicao'] == posicao_filtro]
        else:
            df_filtrado = df_jogadores
    
    with col2:
        st.metric("Jogadores", len(df_filtrado))
    
    # Seleção múltipla
    jogadores_selecionados = st.multiselect(
        "Selecione os jogadores para avaliar",
        options=df_filtrado['id_jogador'].tolist(),
        format_func=lambda x: f"{df_filtrado[df_filtrado['id_jogador']==x]['nome'].values[0]} - {df_filtrado[df_filtrado['id_jogador']==x]['posicao'].values[0] if pd.notna(df_filtrado[df_filtrado['id_jogador']==x]['posicao'].values[0]) else 'N/A'}"
    )
    
    if jogadores_selecionados:
        # Criar dataframe para avaliação
        df_avaliacao = df_filtrado[df_filtrado['id_jogador'].isin(jogadores_selecionados)][
            ['id_jogador', 'nome', 'posicao', 'clube']
        ].copy()
        
        # Adicionar colunas de avaliação
        df_avaliacao['Técnico'] = 3.0
        df_avaliacao['Tático'] = 3.0
        df_avaliacao['Físico'] = 3.0
        df_avaliacao['Mental'] = 3.0
        df_avaliacao['Observações'] = ''
        
        st.markdown("### Preencha as avaliações")
        st.caption("Escala: 1 (Muito Abaixo) a 5 (Excepcional)")
        
        # Editor de dados
        edited_df = st.data_editor(
            df_avaliacao,
            column_config={
                "id_jogador": st.column_config.NumberColumn("ID", disabled=True),
                "nome": st.column_config.TextColumn("Nome", disabled=True),
                "posicao": st.column_config.TextColumn("Posição", disabled=True),
                "clube": st.column_config.TextColumn("Clube", disabled=True),
                "Técnico": st.column_config.NumberColumn(
                    "Técnico",
                    min_value=1.0,
                    max_value=5.0,
                    step=0.5,
                    format="%.1f"
                ),
                "Tático": st.column_config.NumberColumn(
                    "Tático",
                    min_value=1.0,
                    max_value=5.0,
                    step=0.5,
                    format="%.1f"
                ),
                "Físico": st.column_config.NumberColumn(
                    "Físico",
                    min_value=1.0,
                    max_value=5.0,
                    step=0.5,
                    format="%.1f"
                ),
                "Mental": st.column_config.NumberColumn(
                    "Mental",
                    min_value=1.0,
                    max_value=5.0,
                    step=0.5,
                    format="%.1f"
                ),
                "Observações": st.column_config.TextColumn("Observações", width="large")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Resumo
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Jogadores Avaliados", len(edited_df))
        with col2:
            media_geral = edited_df[['Técnico', 'Tático', 'Físico', 'Mental']].mean().mean()
            st.metric("Média Geral", f"{media_geral:.2f}")
        with col3:
            st.metric("Avaliador", avaliador)
        
        # Botões de ação
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Salvar Avaliações", type="primary", use_container_width=True):
                salvar_avaliacoes_lote(edited_df, avaliador, data_avaliacao, db)
        
        with col2:
            if st.button("📥 Exportar para CSV", use_container_width=True):
                exportar_csv(edited_df, avaliador, data_avaliacao)


def avaliacao_formulario(df_jogadores, avaliador, data_avaliacao, db):
    """
    Modo de avaliação por formulário individual sequencial
    """
    st.subheader("📝 Avaliação Individual")
    
    # Inicializar estado
    if 'avaliacoes_temp' not in st.session_state:
        st.session_state.avaliacoes_temp = []
    if 'indice_atual' not in st.session_state:
        st.session_state.indice_atual = 0
    
    # Seleção de jogadores
    posicoes = ['Todas'] + sorted(df_jogadores['posicao'].dropna().unique().tolist())
    posicao_filtro = st.selectbox("Filtrar por Posição", posicoes)
    
    if posicao_filtro != 'Todas':
        df_filtrado = df_jogadores[df_jogadores['posicao'] == posicao_filtro]
    else:
        df_filtrado = df_jogadores
    
    jogadores_selecionados = st.multiselect(
        "Selecione os jogadores para avaliar",
        options=df_filtrado['id_jogador'].tolist(),
        format_func=lambda x: f"{df_filtrado[df_filtrado['id_jogador']==x]['nome'].values[0]} - {df_filtrado[df_filtrado['id_jogador']==x]['posicao'].values[0] if pd.notna(df_filtrado[df_filtrado['id_jogador']==x]['posicao'].values[0]) else 'N/A'}"
    )
    
    if jogadores_selecionados:
        # Mostrar progresso
        progress = len(st.session_state.avaliacoes_temp) / len(jogadores_selecionados)
        st.progress(progress, text=f"Avaliados: {len(st.session_state.avaliacoes_temp)}/{len(jogadores_selecionados)}")
        
        # Determinar próximo jogador a avaliar
        jogadores_restantes = [j for j in jogadores_selecionados if j not in [a['id_jogador'] for a in st.session_state.avaliacoes_temp]]
        
        if jogadores_restantes:
            jogador_id = jogadores_restantes[0]
            jogador_info = df_filtrado[df_filtrado['id_jogador'] == jogador_id].iloc[0]
            
            st.markdown(f"### Avaliando: {jogador_info['nome']}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Posição:** {jogador_info['posicao'] if pd.notna(jogador_info['posicao']) else 'N/A'}")
            with col2:
                st.info(f"**Clube:** {jogador_info['clube'] if pd.notna(jogador_info['clube']) else 'N/A'}")
            with col3:
                st.info(f"**Idade:** {jogador_info.get('idade', 'N/A')}")
            
            # Formulário de avaliação
            with st.form(key=f"form_{jogador_id}"):
                st.markdown("#### Notas (1 a 5)")
                
                col1, col2 = st.columns(2)
                with col1:
                    tecnico = st.slider("⚽ Técnico", 1.0, 5.0, 3.0, 0.5)
                    tatico = st.slider("🧠 Tático", 1.0, 5.0, 3.0, 0.5)
                with col2:
                    fisico = st.slider("💪 Físico", 1.0, 5.0, 3.0, 0.5)
                    mental = st.slider("🎯 Mental", 1.0, 5.0, 3.0, 0.5)
                
                observacoes = st.text_area("Observações", height=100)
                
                submitted = st.form_submit_button("✅ Confirmar e Próximo", use_container_width=True)
                
                if submitted:
                    avaliacao = {
                        'id_jogador': jogador_id,
                        'nome': jogador_info['nome'],
                        'posicao': jogador_info['posicao'] if pd.notna(jogador_info['posicao']) else 'N/A',
                        'clube': jogador_info['clube'] if pd.notna(jogador_info['clube']) else 'N/A',
                        'Técnico': tecnico,
                        'Tático': tatico,
                        'Físico': fisico,
                        'Mental': mental,
                        'Observações': observacoes
                    }
                    st.session_state.avaliacoes_temp.append(avaliacao)
                    st.rerun()
        
        else:
            st.success("✅ Todos os jogadores foram avaliados!")
            
            # Mostrar resumo
            if st.session_state.avaliacoes_temp:
                st.markdown("### Resumo das Avaliações")
                df_resumo = pd.DataFrame(st.session_state.avaliacoes_temp)
                st.dataframe(df_resumo, use_container_width=True)
                
                # Botões finais
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("💾 Salvar Tudo", type="primary", use_container_width=True):
                        salvar_avaliacoes_lote(df_resumo, avaliador, data_avaliacao, db)
                        st.session_state.avaliacoes_temp = []
                        st.rerun()
                
                with col2:
                    if st.button("🔄 Resetar", use_container_width=True):
                        st.session_state.avaliacoes_temp = []
                        st.rerun()
                
                with col3:
                    if st.button("📥 Exportar CSV", use_container_width=True):
                        exportar_csv(df_resumo, avaliador, data_avaliacao)


def salvar_avaliacoes_lote(df, avaliador, data_avaliacao, db):
    """
    Salva múltiplas avaliações no banco de dados
    """
    try:
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        
        # Preparar dados para inserção
        avaliacoes = []
        for _, row in df.iterrows():
            avaliacao = (
                int(row['id_jogador']),
                float(row['Técnico']),
                float(row['Tático']),
                float(row['Físico']),
                float(row['Mental']),
                str(row.get('Observações', '')),
                avaliador,
                data_avaliacao
            )
            avaliacoes.append(avaliacao)
        
        # Query de inserção
        insert_query = """
        INSERT INTO avaliacoes (
            id_jogador, 
            nota_tecnico, 
            nota_tatico, 
            nota_fisico, 
            nota_mental,
            observacoes,
            avaliador,
            data_avaliacao
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Executar em lote
        execute_batch(cursor, insert_query, avaliacoes)
        conn.commit()
        
        st.success(f"✅ {len(avaliacoes)} avaliações salvas com sucesso!")
        st.balloons()
        
    except Exception as e:
        conn.rollback()
        st.error(f"❌ Erro ao salvar avaliações: {str(e)}")
    finally:
        cursor.close()
        conn.close()


def exportar_csv(df, avaliador, data_avaliacao):
    """
    Exporta avaliações para CSV
    """
    df_export = df.copy()
    df_export['Avaliador'] = avaliador
    df_export['Data'] = data_avaliacao
    
    csv = df_export.to_csv(index=False).encode('utf-8')
    
    st.download_button(
        label="⬇️ Baixar CSV",
        data=csv,
        file_name=f"avaliacoes_{data_avaliacao}_{avaliador.replace(' ', '_')}.csv",
        mime="text/csv"
    )