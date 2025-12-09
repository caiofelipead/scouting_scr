## 📍 Onde Encontrar as Novas Visualizações

### Localização da Nova Aba "🎯 Análise Avançada"

A nova aba **NÃO** aparece no menu principal. Ela fica **dentro do perfil individual do jogador**.

### 🗺️ Caminho Completo:

```
1. Inicie o dashboard:
   streamlit run app/dashboard.py

2. No menu lateral → Selecione "Pesquisa e Perfil Individual"

3. Busque por um jogador (ex: digite o nome)

4. Clique no CARD do jogador para abrir o perfil completo

5. No perfil do jogador, você verá 4 ABAS:
   ┌─────────────────────────────────────────────────┐
   │  📝 Nova Avaliação  │  📊 Histórico  │           │
   │  📈 Evolução        │  🎯 Análise Avançada  ← AQUI!
   └─────────────────────────────────────────────────┘

6. Clique na aba "🎯 Análise Avançada"
```

### ⚠️ Importante:

**A aba só aparece DENTRO do perfil de um jogador específico**, não no menu principal!

### 🎯 O que você verá na aba "Análise Avançada":

1. 📊 **Cards de Métricas** - Com percentis visuais
2. 📈 **Gráfico de Percentil** - Comparação com benchmark da posição
3. 🎯 **Scatter Plot** - Análise bidimensional (Técnico vs Físico, etc)
4. 🔥 **Heatmap** - Comparação visual com top 15 jogadores

### 📝 Requisitos:

- ✅ Jogador deve ter pelo menos 1 avaliação registrada
- ✅ Para comparações, precisa ter outros jogadores na mesma posição avaliados
- ✅ Banco de dados já está migrado (feito!)

---

## 🚀 Teste Rápido:

1. `streamlit run app/dashboard.py`
2. Busque qualquer jogador que já tenha avaliação
3. Clique no card dele
4. Procure a 4ª aba: **"🎯 Análise Avançada"**
