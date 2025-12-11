# 🎨 Refatoração UI com Streamlit Shadcn UI

## Objetivo

Modernizar a interface do dashboard abandonando o CSS manual e adotando componentes do `streamlit-shadcn-ui` para um design minimalista estilo Vercel/Linear.

---

## 📦 Instalação

```bash
# Atualizar ferramentas de build primeiro
pip install --upgrade setuptools wheel

# Instalar streamlit-shadcn-ui
pip install streamlit-shadcn-ui
```

**Nota:** Se houver erro com `htbuilder`, tente:
```bash
pip install --no-build-isolation streamlit-shadcn-ui
```

---

## 🔄 Mudanças Implementadas

### 1. **Função `exibir_perfil_jogador` → `exibir_perfil_jogador_refatorado`**

#### ❌ ANTES (Código Antigo)

```python
# 200+ linhas de CSS inline
st.markdown("""
<style>
    .profile-container { ... }
    .player-photo { ... }
    .stat-card { ... }
    .status-badge { ... }
    # ... etc
</style>
""", unsafe_allow_html=True)

# Métricas em HTML manual
st.markdown(f"""
<div class="stat-card">
    <span class="stat-label">Idade</span>
    <span class="stat-value">{idade_safe}</span>
</div>
""", unsafe_allow_html=True)

# Status com HTML manual
st.markdown(f"""
<div class="status-badge" style="background: {config['bg']}; color: {config['color']};">
    <span>{config['text']}</span>
</div>
""", unsafe_allow_html=True)

# Tabs nativas do Streamlit
tab1, tab2, tab3, tab4 = st.tabs(["📝 Nova Avaliação", "📊 Histórico", ...])
```

#### ✅ DEPOIS (Código Refatorado)

```python
# CSS MÍNIMO - apenas spacing essencial
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; }
    div[data-testid="stVerticalBlock"] > div:empty { display: none !important; }
</style>
""", unsafe_allow_html=True)

# Métricas com Shadcn UI Cards
ui.card(
    title="Idade",
    content=f"{idade}",
    description="anos",
    key="card_idade"
).render()

# Status com Badges do Shadcn
ui.badges(
    badge_list=[(badge_text, badge_variant)],
    class_name="flex gap-2",
    key="status_badge"
)

# Tabs do Shadcn UI
selected_tab = ui.tabs(
    options=['Nova Avaliação', 'Histórico', 'Evolução', 'Análise Avançada'],
    default_value='Nova Avaliação',
    key="perfil_tabs"
)
```

#### 📊 Benefícios

- **-85% de CSS manual** (~200 linhas → ~10 linhas)
- **Componentes reutilizáveis** (ui.card, ui.badges, ui.tabs)
- **Design consistente** automaticamente
- **Responsivo por padrão**
- **Manutenção mais fácil**

---

### 2. **Função `exibir_lista_com_fotos` → `exibir_lista_com_fotos_refatorado`**

#### ❌ ANTES (Código Antigo)

```python
# HTML complexo para cards
st.markdown(f"""
<div style="position: relative; width: 100%; padding-top: 133.33%; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    <img src="{foto_url}"
         style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;"
         onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
         alt="{nome_jogador}">
    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: none; align-items: center; justify-content: center; font-size: 60px; color: white; font-weight: bold;">
        {inicial}
    </div>
</div>
""", unsafe_allow_html=True)

# Botões nativos
if st.button("Ver Perfil", key=f"perfil_{id}", use_container_width=True):
    # ...

if st.button("⭐️", key=f"addwish_{id}", use_container_width=True):
    # ...
```

#### ✅ DEPOIS (Código Refatorado)

```python
# Card do Shadcn UI como container
with ui.card(key=f"player_card_{jogador['id_jogador']}"):
    # Foto simples
    if foto_url:
        st.image(foto_url, use_container_width=True)
    else:
        # Fallback com gradiente
        st.markdown(f"""
        <div style="width: 100%; padding-top: 133.33%; position: relative;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 8px;">
            <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                        font-size: 60px; color: white; font-weight: bold;">
                {inicial}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Botões com variants do Shadcn
    if ui.button(text="Ver Perfil", key=f"perfil_{id}", variant="default"):
        # ...

    if ui.button(text="⭐", key=f"addwish_{id}", variant="secondary"):
        # ...
```

#### 📊 Benefícios

- **Cards estruturados** com `ui.card()` como container
- **Botões com variants** (`default`, `secondary`, `destructive`)
- **Menos HTML manual**
- **Grid spacing consistente**

---

## 🎨 Componentes Shadcn UI Utilizados

### 1. **ui.card()**

```python
ui.card(
    title="Título",
    content="Valor Principal",
    description="Descrição/Contexto",
    key="unique_key"
).render()
```

**Uso:** Métricas, KPIs, estatísticas do jogador

---

### 2. **ui.badges()**

```python
ui.badges(
    badge_list=[
        ("Contrato Ativo", "default"),      # Verde
        ("Último Ano", "secondary"),        # Cinza
        ("Vence em Breve", "destructive"),  # Vermelho
    ],
    class_name="flex gap-2",
    key="badges_key"
)
```

**Uso:** Status do contrato, tags, categorias

**Variants disponíveis:**
- `default` - Cinza padrão
- `secondary` - Cinza secundário
- `destructive` - Vermelho (ações destrutivas)
- `outline` - Apenas borda

---

### 3. **ui.tabs()**

```python
selected_tab = ui.tabs(
    options=['Tab 1', 'Tab 2', 'Tab 3'],
    default_value='Tab 1',
    key="tabs_key"
)

if selected_tab == 'Tab 1':
    st.write("Conteúdo da Tab 1")
elif selected_tab == 'Tab 2':
    st.write("Conteúdo da Tab 2")
```

**Uso:** Organizar avaliações, histórico, análises

---

### 4. **ui.button()**

```python
if ui.button(
    text="Clique Aqui",
    key="btn_key",
    variant="default"  # ou "secondary", "destructive", "outline"
):
    # Ação do botão
    pass
```

**Variants disponíveis:**
- `default` - Botão primário (azul)
- `secondary` - Botão secundário (cinza)
- `destructive` - Ação destrutiva (vermelho)
- `outline` - Apenas borda
- `ghost` - Sem fundo

---

## 🚀 Como Integrar no Dashboard Principal

### Opção 1: Substituição Gradual (Recomendado)

```python
# Em app/dashboard.py

# Importar as funções refatoradas
from dashboard_refatorado import (
    exibir_perfil_jogador_refatorado,
    exibir_lista_com_fotos_refatorado
)

# Usar as novas funções
if st.session_state.pagina == "perfil":
    exibir_perfil_jogador_refatorado(db, jogador_id, debug=False)
elif st.session_state.pagina == "lista":
    exibir_lista_com_fotos_refatorado(df, db, debug=False)
```

### Opção 2: Feature Flag

```python
# Adicionar no início do dashboard.py
USE_NEW_UI = st.sidebar.checkbox("🎨 Usar Nova UI (Shadcn)", value=False)

if st.session_state.pagina == "perfil":
    if USE_NEW_UI:
        exibir_perfil_jogador_refatorado(db, jogador_id)
    else:
        exibir_perfil_jogador(db, jogador_id)  # Função antiga
```

---

## 📝 Checklist de Migração

### Fase 1: Preparação
- [x] Pesquisar documentação streamlit-shadcn-ui
- [x] Criar funções refatoradas
- [ ] Instalar `streamlit-shadcn-ui` no ambiente
- [ ] Testar componentes básicos (card, badge, button)

### Fase 2: Implementação
- [ ] Substituir `exibir_perfil_jogador` → `exibir_perfil_jogador_refatorado`
- [ ] Substituir `exibir_lista_com_fotos` → `exibir_lista_com_fotos_refatorado`
- [ ] Testar todas as interações (botões, tabs, formulários)
- [ ] Verificar responsividade (mobile, tablet, desktop)

### Fase 3: Limpeza
- [ ] Remover CSS obsoleto de `app/styles/custom.css`
- [ ] Remover funções antigas (backup antes)
- [ ] Atualizar imports em todos os arquivos
- [ ] Documentar mudanças no CHANGELOG

---

## 🐛 Troubleshooting

### Problema: `ModuleNotFoundError: No module named 'streamlit_shadcn_ui'`

**Solução:**
```bash
pip install --upgrade setuptools wheel
pip install streamlit-shadcn-ui
```

Se persistir:
```bash
pip install --no-build-isolation streamlit-shadcn-ui
```

---

### Problema: Componentes não aparecem / renderizam em branco

**Solução:**
- Certifique-se de chamar `.render()` nos cards:
  ```python
  ui.card(...).render()  # ✅ Correto
  ui.card(...)           # ❌ Não renderiza
  ```

- Verifique se as `keys` são únicas:
  ```python
  ui.card(key="card1")  # ✅ Correto
  ui.card(key="card1")  # ❌ Conflito de key
  ```

---

### Problema: Badges não mudam de cor

**Solução:**
- Use os variants corretos: `"default"`, `"secondary"`, `"destructive"`, `"outline"`
- Certifique-se de que `badge_list` é uma lista de tuplas:
  ```python
  badge_list=[("Texto", "variant")]  # ✅ Correto
  badge_list=["Texto", "variant"]    # ❌ Incorreto
  ```

---

## 📚 Recursos

- **Documentação Oficial:** https://github.com/ObservedObserver/streamlit-shadcn-ui
- **Demo Live:** https://shadcn.streamlit.app/
- **PyPI:** https://pypi.org/project/streamlit-shadcn-ui/
- **Artigo Medium:** [How to Beautify Streamlit Using Shadcn UI](https://medium.com/@ericdennis7/how-to-beautify-streamlit-using-shadcn-ui-c70a6e828b77)

---

## 🎯 Próximos Passos

1. **Testar** as funções refatoradas localmente
2. **Refinar** o layout baseado em feedback visual
3. **Expandir** para outras funções:
   - `tab_ranking` → usar `ui.card` para métricas
   - `tab_shadow_team` → usar `ui.select` para seleção
   - Filtros → usar `ui.input` e `ui.checkbox`
4. **Remover** CSS obsoleto progressivamente
5. **Documentar** padrões de design para consistência

---

## ✨ Resultado Esperado

- **UI Minimalista** estilo Vercel/Linear
- **-85% menos CSS manual**
- **Componentes reutilizáveis** e consistentes
- **Fácil manutenção** e extensibilidade
- **Design profissional** e moderno

---

**Autor:** Refatoração UI - Dezembro 2025
**Biblioteca:** streamlit-shadcn-ui v0.1.19+
**Compatibilidade:** Streamlit 1.28.0+
