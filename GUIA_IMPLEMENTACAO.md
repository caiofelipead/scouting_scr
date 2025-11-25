# 🚀 Scout Pro - Sistema Completo

## 📋 Novidades Implementadas

### ✅ Funcionalidades Adicionadas:

1. **🔐 Sistema de Autenticação**
   - Login com usuário e senha
   - Controle de níveis (Admin/Scout)
   - Gerenciamento de usuários
   - Logs de acesso

2. **💰 Gestão Financeira Completa**
   - Faixa salarial dos jogadores  
   - Condições de negócio
   - Cláusulas e custos de transferência
   - Filtros por valor

3. **👔 Informações de Agentes**
   - Scraping automático do Transfermarkt
   - Nome, empresa e contatos dos agentes
   - Gestão de comissões

4. **🛡️ Sincronização Segura**
   - Merge inteligente (não perde dados!)
   - Separação dados Sheets vs dados locais
   - Sistema de backup automático

---

## 🔧 INSTALAÇÃO RÁPIDA

### 1. Instalar Dependências

```bash
pip install beautifulsoup4 requests openpyxl
```

### 2. Criar Primeiro Usuário

```bash
python criar_primeiro_usuario.py
```

### 3. Configurar Banco de Dados

As tabelas serão criadas automaticamente quando você executar pela primeira vez.

### 4. Modificar Dashboard Principal

No seu `app/dashboard.py`, adicione no início:

```python
from auth import check_password, mostrar_info_usuario
from dashboard_financeiro import aba_financeira

# PROTEGE O DASHBOARD
if not check_password():
    st.stop()
```

Na sidebar, adicione:

```python
mostrar_info_usuario()
```

Nas abas, adicione a aba financeira:

```python
tab_financeiro = st.tabs(["...", "💰 Financeiro"])[-1]

with tab_financeiro:
    aba_financeira()
```

---

## 💰 COMO USAR A GESTÃO FINANCEIRA

### Adicionar Informações Salariais

1. Aba "💰 Financeiro" > "✏️ Editar Informações"
2. Selecione o jogador
3. Preencha:
   - Salário mínimo/máximo
   - Moeda (BRL, EUR, USD, GBP)
   - Bonificações
   - Custo de transferência
   - Cláusula de rescisão
   - % direitos econômicos
   - Condições de negócio
   - Observações

### Buscar por Faixa Salarial

1. Aba "💰 Financeiro" > "🔍 Buscar"
2. Defina faixa salarial desejada
3. Aplique filtros (posição, idade, agente, etc.)
4. Clique em "🔍 Buscar"

### Análises Financeiras

- Distribuição salarial por posição
- Top 10 maiores salários
- Estatísticas por clube
- Gráficos interativos

---

## 👔 SCRAPING DE AGENTES

### Buscar Agente de Um Jogador

```bash
python scraping_transfermarkt.py "Gabriel Taliari"
```

### Atualizar Todos os Jogadores

```bash
python scraping_transfermarkt.py
# Escolha opção 1 ou 2
```

**O que o script faz:**
- Busca no Transfermarkt usando o `transfermarkt_id`
- Extrai nome do agente e empresa
- Salva automaticamente no banco
- Respeita delays (2-4s entre requisições)

---

## 🛡️ SINCRONIZAÇÃO SEGURA

### Problema Antigo ❌

```python
# Perdia todas as avaliações e dados locais
db.importar_dados_planilha(df)
```

### Solução Nova ✅

```python
from database_extended import ScoutingDatabaseExtended

db_ext = ScoutingDatabaseExtended()
sucesso, msg = db_ext.importar_dados_planilha_seguro(df)
```

**O que mudou:**
- Faz MERGE ao invés de DELETE + INSERT
- Atualiza apenas dados do Sheets (nome, clube, idade, etc.)
- Preserva avaliações, tags, informações financeiras
- Registra log de auditoria

### No Dashboard

Sidebar > "🔄 Sincronização" > "📥 Sync Seguro"

---

## 💾 SISTEMA DE BACKUP

### Criar Backup Manual

```bash
python backup_system.py
# Opção 1: Criar backup completo
```

**O que é salvo:**
- jogadores, avaliacoes, tags, wishlist
- usuarios, logs
- Formato CSV + Excel + ZIP compactado

### Backup Automático

Configure no Railway ou cron:

```bash
# Diário às 3h
0 3 * * * cd /projeto && python backup_system.py
```

### Listar Backups

```bash
python backup_system.py
# Opção 2: Listar backups
```

---

## 📊 ESTRUTURA DO BANCO

### Colunas Financeiras (jogadores)

```
salario_mensal_min       - Salário mínimo
salario_mensal_max       - Salário máximo  
moeda_salario            - BRL, EUR, USD, GBP
bonificacoes             - Bônus por gol, etc.
custo_transferencia      - Custo total
condicoes_negocio        - Forma de pagamento
clausula_rescisoria      - Cláusula
percentual_direitos      - % direitos econômicos
observacoes_financeiras  - Notas
```

### Colunas de Agente

```
agente_nome              - Nome do agente
agente_empresa           - Empresa/agência
agente_telefone          - Telefone
agente_email             - Email
agente_comissao          - % comissão
url_agente               - Link Transfermarkt
agente_atualizado_em     - Data última atualização
```

### Tabelas que NÃO são sobrescritas

```
avaliacoes        - Suas avaliações dos jogadores
tags_jogadores    - Tags personalizadas
wishlist          - Lista de desejos
log_auditoria     - Histórico de mudanças
```

---

## 🐛 PROBLEMAS COMUNS

### "DATABASE_URL não configurada"

Verifique seu `.env`:

```bash
DATABASE_URL=postgresql://user:pass@host:port/db
```

### "Tabela não existe"

Execute uma vez:

```python
from database_extended import ScoutingDatabaseExtended
db = ScoutingDatabaseExtended()
```

### Scraping não encontra agente

- Jogador precisa ter `transfermarkt_id`
- Alguns jogadores não têm agente no site
- Verifique se não está bloqueando o site

### Dados são perdidos na sync

Use SEMPRE `importar_dados_planilha_seguro()`, nunca o método antigo!

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

```
[ ] Instalei dependências (beautifulsoup4, requests, openpyxl)
[ ] Criei primeiro usuário admin
[ ] Modifiquei dashboard.py com autenticação
[ ] Adicionei aba financeira
[ ] Atualizei sincronização para modo seguro
[ ] Testei scraping de agentes
[ ] Configurei backups
[ ] Testei tudo em desenvolvimento
```

---

## 🎯 WORKFLOW RECOMENDADO

1. **Receber informação** do jogador/agente
2. **Atualizar dados financeiros** no sistema
3. **Adicionar tags** relevantes
4. **Incluir na wishlist** se interessante
5. **Fazer avaliação** técnica
6. **Gerar relatório** para diretoria

---

## 💡 DICAS

**Para Scouts:**
- Atualize informações assim que obtiver
- Use observações para detalhes importantes
- Tags ajudam a organizar negociações

**Para Admins:**
- Backups semanais são essenciais
- Monitore logs de acesso
- Revise permissões regularmente

---

## 📞 EXEMPLO COMPLETO DE USO

```bash
# 1. Criar primeiro usuário
python criar_primeiro_usuario.py

# 2. Buscar agentes (opcional)
python scraping_transfermarkt.py "Gabriel Taliari"

# 3. Criar backup
python backup_system.py

# 4. Iniciar dashboard
streamlit run app/dashboard.py

# 5. Fazer login e usar o sistema!
```

---

**Desenvolvido com ⚽ para o Sport Club do Recife**
