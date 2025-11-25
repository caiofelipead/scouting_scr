#!/usr/bin/env python3
"""
Script para adicionar as 7 tabs originais ao dashboard atual
Mantém: PostgreSQL, filtros funcionais, sincronização
Adiciona: Todas as 7 tabs do código anterior
"""

print("🔧 Iniciando merge das tabs...")

# Ler arquivo atual
with open('app/dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()

print("✅ Arquivo atual lido")

# Código das tabs para inserir
tabs_code = '''
    # ==================== SISTEMA DE TABS ====================
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Visão Geral",
        "👥 Lista de Jogadores",
        "🏆 Ranking",
        "🆚 Comparador",
        "⚽ Shadow Team",
        "🚨 Alertas",
        "📈 Análises"
    ])
    
    # ========== TAB 1: VISÃO GERAL ==========
    with tab1:
        st.subheader("📊 Visão Geral do Sistema")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total de Jogadores", len(df_filtrado))
        with col2:
            if 'idade_atual' in df_filtrado.columns and len(df_filtrado) > 0:
                st.metric("Idade Média", f"{df_filtrado['idade_atual'].mean():.1f} anos")
        with col3:
            if 'nacionalidade' in df_filtrado.columns:
                st.metric("Nacionalidades", df_filtrado['nacionalidade'].nunique())
        with col4:
            if 'clube' in df_filtrado.columns:
                st.metric("Clubes", df_filtrado['clube'].nunique())
        st.markdown("---")
        if 'posicao' in df_filtrado.columns and len(df_filtrado) > 0:
            st.subheader("Distribuição por Posição")
            pos_counts = df_filtrado['posicao'].value_counts()
            col_a, col_b = st.columns([2,1])
            with col_a:
                st.bar_chart(pos_counts)
            with col_b:
                st.dataframe(pos_counts.to_frame('Quantidade'), use_container_width=True)
    
    # ========== TAB 2: LISTA DE JOGADORES ==========
    with tab2:
        st.subheader("👥 Lista Completa de Jogadores")
        
'''

# Encontrar onde inserir
marker = "    # Exibir tabela de jogadores"
if marker not in content:
    print("⚠️  Tentando marcador alternativo...")
    marker = "    st.subheader(f\"📊 Jogadores Encontrados: {len(df_filtrado)}\")"

if marker not in content:
    print("❌ Erro: Nenhum marcador encontrado")
    exit(1)

print(f"✅ Marcador encontrado")

# Inserir tabs
content = content.replace(marker, tabs_code + marker)

# Indentar conteúdo da tab2 (adicionar 8 espaços)
lines = content.split('\n')
result = []
found_tab2 = False
indent_section = False

for i, line in enumerate(lines):
    if 'with tab2:' in line and i < len(lines)-1 and 'Lista Completa' in lines[i+1]:
        result.append(line)
        found_tab2 = True
        continue
    
    if found_tab2 and not indent_section and (marker.strip() in line or 'st.subheader(f"📊' in line):
        indent_section = True
    
    if indent_section and 'if __name__' in line:
        # Adicionar tabs 3-7 antes do if __name__
        result.append('''
    # ========== TAB 3: RANKING ==========
    with tab3:
        st.subheader("🏆 Ranking de Jogadores")
        st.info("🚧 Funcionalidade em desenvolvimento")
        with st.expander("📋 Roadmap"):
            st.markdown("**Features:** Ranking por posição, Top jogadores, Custo-benefício")
    
    # ========== TAB 4: COMPARADOR ==========
    with tab4:
        st.subheader("🆚 Comparador de Jogadores")
        st.info("🚧 Funcionalidade em desenvolvimento")
        with st.expander("📋 Roadmap"):
            st.markdown("**Features:** Comparação lado a lado, Gráficos radar, Análise estat")
    
    # ========== TAB 5: SHADOW TEAM ==========
    with tab5:
        st.subheader("⚽ Shadow Team Builder")
        st.info("🚧 Funcionalidade em desenvolvimento")
        with st.expander("📋 Roadmap"):
            st.markdown("**Features:** Montar time ideal, Formações táticas, Orçamento")
    
    # ========== TAB 6: ALERTAS ==========
    with tab6:
        st.subheader("🚨 Sistema de Alertas")
        st.info("🚧 Funcionalidade em desenvolvimento")
        with st.expander("📋 Roadmap"):
            st.markdown("**Features:** Contratos expirando, Disponíveis, Oportunidades")
    
    # ========== TAB 7: ANÁLISES ==========
    with tab7:
        st.subheader("📈 Análises Avançadas")
        st.info("🚧 Funcionalidade em desenvolvimento")
        with st.expander("📋 Roadmap"):
            st.markdown("**Features:** Estatísticas avançadas, Tendências, Relatórios PDF")

''')
        indent_section = False
    
    if indent_section and line.startswith('    ') and line.strip():
        result.append('    ' + line)
    else:
        result.append(line)

content = '\n'.join(result)

# Salvar
with open('app/dashboard.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n" + "="*60)
print("✅ SUCESSO! Tabs adicionadas ao dashboard!")
print("="*60)
print("\n📋 Tabs:")
print("  1. 📊 Visão Geral - KPIs funcionais")
print("  2. 👥 Lista de Jogadores - tabela funcional")
print("  3-7. Placeholders com roadmap")
print("\n🔧 Próximos passos:")
print("  1. python3 -m py_compile app/dashboard.py")
print("  2. git add app/dashboard.py")
print("  3. git commit -m 'feat: adiciona 7 tabs ao dashboard'")
print("  4. git push")
