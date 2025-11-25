"""
EXEMPLO DE MODIFICAÇÃO DO dashboard.py
Copie e adapte estas partes para seu dashboard existente
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ========================================
# NOVOS IMPORTS NECESSÁRIOS
# ========================================
from auth import check_password, mostrar_info_usuario, pagina_gerenciar_usuarios
from dashboard_financeiro import aba_financeira
from database_extended import ScoutingDatabaseExtended

# ========================================
# PROTEÇÃO COM LOGIN (LOGO NO INÍCIO)
# ========================================
# Antes de qualquer coisa, verifica autenticação
if not check_password():
    st.stop()

# ========================================
# CONFIGURAÇÃO DA PÁGINA
# ========================================
st.set_page_config(
    page_title="Scout Pro - Sport Club do Recife",
    page_icon="⚽",
    layout="wide"
)

# ========================================
# INICIALIZAÇÃO DO BANCO
# ========================================
# Use a versão estendida do banco
db = ScoutingDatabaseExtended()

# ========================================
# SIDEBAR
# ========================================
with st.sidebar:
    st.title("⚽ Scout Pro")
    st.markdown("---")
    
    # Mostra informações do usuário logado
    mostrar_info_usuario()
    
    st.markdown("---")
    
    # Sincronização de dados
    st.markdown("### 🔄 Sincronização")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Sync Seguro", help="Atualiza dados preservando avaliações"):
            with st.spinner("Sincronizando..."):
                try:
                    # Busca dados do Google Sheets
                    df = db.get_dados_google_sheets()
                    
                    # USA SINCRONIZAÇÃO SEGURA (não perde dados!)
                    sucesso, mensagem = db.importar_dados_planilha_seguro(df)
                    
                    if sucesso:
                        st.success(mensagem)
                        # Registra log
                        db.registrar_acao(
                            usuario_id=st.session_state.usuario['id'],
                            acao='sincronizar',
                            tabela='jogadores',
                            registro_id=None
                        )
                    else:
                        st.error(mensagem)
                except Exception as e:
                    st.error(f"Erro na sincronização: {e}")
    
    with col2:
        if st.button("⚠️ Sync Total", help="ATENÇÃO: Substitui TODOS os dados"):
            if st.session_state.usuario['nivel'] == 'admin':
                # Apenas admin pode fazer sync total
                st.warning("⚠️ Isso irá sobrescrever todos os dados!")
                if st.button("Confirmar"):
                    with st.spinner("Sincronizando..."):
                        try:
                            df = db.get_dados_google_sheets()
                            db.importar_dados_planilha(df)  # Método antigo
                            st.success("✅ Sincronização total concluída")
                        except Exception as e:
                            st.error(f"Erro: {e}")
            else:
                st.error("Apenas admin pode fazer sync total")
    
    st.markdown("---")
    
    # Estatísticas rápidas
    st.markdown("### 📊 Estatísticas")
    
    try:
        stats = db.estatisticas_financeiras()
        st.metric("Total de Jogadores", stats['total'])
        
        percentual_salario = (stats['com_salario'] / stats['total'] * 100) if stats['total'] > 0 else 0
        st.metric("Com Info Salarial", f"{percentual_salario:.0f}%")
        
        percentual_agente = (stats['com_agente'] / stats['total'] * 100) if stats['total'] > 0 else 0
        st.metric("Com Agente", f"{percentual_agente:.0f}%")
    except:
        pass

# ========================================
# CONTEÚDO PRINCIPAL
# ========================================

# Menu de navegação
menu = st.sidebar.radio(
    "📋 Navegação",
    [
        "🏠 Home",
        "📊 Dashboard Principal",
        "💰 Gestão Financeira",
        "👥 Gerenciar Usuários" if st.session_state.usuario['nivel'] == 'admin' else None
    ],
    key="menu_nav"
)

# Remove None da lista
menu = [m for m in [menu] if m is not None][0]

# ========================================
# PÁGINA: HOME
# ========================================
if menu == "🏠 Home":
    st.title("🏠 Bem-vindo ao Scout Pro")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("👤 **Usuário Logado**")
        st.write(f"**{st.session_state.usuario['nome']}**")
        st.caption(f"Nível: {st.session_state.usuario['nivel'].upper()}")
    
    with col2:
        st.info("📅 **Data e Hora**")
        st.write(datetime.now().strftime("%d/%m/%Y"))
        st.caption(datetime.now().strftime("%H:%M:%S"))
    
    with col3:
        st.info("⚽ **Clube**")
        st.write("Sport Club do Recife")
        st.caption("Ilha do Retiro")
    
    st.markdown("---")
    
    # Cards de acesso rápido
    st.subheader("🚀 Acesso Rápido")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.menu_nav = "📊 Dashboard Principal"
            st.rerun()
    
    with col2:
        if st.button("💰 Financeiro", use_container_width=True):
            st.session_state.menu_nav = "💰 Gestão Financeira"
            st.rerun()
    
    with col3:
        if st.button("🔄 Sincronizar", use_container_width=True):
            # Trigger sincronização
            pass
    
    with col4:
        if st.session_state.usuario['nivel'] == 'admin':
            if st.button("👥 Usuários", use_container_width=True):
                st.session_state.menu_nav = "👥 Gerenciar Usuários"
                st.rerun()

# ========================================
# PÁGINA: DASHBOARD PRINCIPAL
# ========================================
elif menu == "📊 Dashboard Principal":
    
    # AQUI VAI TODO O SEU CÓDIGO EXISTENTE DO DASHBOARD
    # Suas abas, gráficos, análises, etc.
    
    st.title("📊 Dashboard de Scouting")
    
    # Exemplo de abas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Visão Geral",
        "👥 Lista de Jogadores",
        "🏆 Ranking",
        "🆚 Comparador",
        "📈 Análises"
    ])
    
    with tab1:
        st.subheader("📊 Visão Geral")
        # Seu código da aba de visão geral
        pass
    
    with tab2:
        st.subheader("👥 Lista de Jogadores")
        # Seu código da lista de jogadores
        pass
    
    with tab3:
        st.subheader("🏆 Ranking")
        # Seu código de ranking
        pass
    
    with tab4:
        st.subheader("🆚 Comparador")
        # Seu código do comparador
        pass
    
    with tab5:
        st.subheader("📈 Análises")
        # Suas análises
        pass

# ========================================
# PÁGINA: GESTÃO FINANCEIRA (NOVA)
# ========================================
elif menu == "💰 Gestão Financeira":
    # Chama a aba financeira completa
    aba_financeira()

# ========================================
# PÁGINA: GERENCIAR USUÁRIOS (NOVA - ADMIN)
# ========================================
elif menu == "👥 Gerenciar Usuários":
    if st.session_state.usuario['nivel'] == 'admin':
        pagina_gerenciar_usuarios()
    else:
        st.error("❌ Acesso negado. Apenas administradores.")

# ========================================
# FOOTER
# ========================================
st.markdown("---")
st.caption("⚽ Scout Pro - Sport Club do Recife | Desenvolvido por Caio Felipe")
