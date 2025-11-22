# 📘 Guia de Instalação - Scout Pro

## Pré-requisitos

- Python 3.8 ou superior
- Git
- Conta Google (para Google Sheets)

## Instalação Passo a Passo

### 1. Clone o Repositório
```bash
git clone https://github.com/caiofelipead/scouting_scr.git
cd scouting_scr
```

### 2. Instale as Dependências
```bash
make install
# ou
pip install -r requirements.txt
```

### 3. Configure as Credenciais
```bash
# Copie o exemplo
cp .env.example .env

# Edite com suas configurações
nano .env
```

Configure:
- `SPREADSHEET_ID` - ID da sua planilha Google Sheets
- `GOOGLE_CREDENTIALS_PATH` - Caminho para credentials.json

### 4. Valide a Instalação
```bash
make validate
```

### 5. Inicie o Dashboard
```bash
make dashboard
```

Acesse: http://localhost:8501

## Solução de Problemas

### Erro: Module not found
```bash
make install
```

### Erro: Credentials not found
Adicione o arquivo `credentials.json` na raiz do projeto.

### Dashboard não abre
Verifique se a porta 8501 está livre.
