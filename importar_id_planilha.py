import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
GOOGLE_SHEET_URL = os.getenv('GOOGLE_SHEET_URL')

print('🔄 Importando id_planilha e atualizando banco...')

# Ler jogadores do banco
engine = create_engine(DATABASE_URL)
df_banco = pd.read_sql('SELECT id_jogador, nome FROM jogadores', engine)

# Ler planilha Google Sheets como CSV
try:
    # Converta sua URL do Google Sheets para exportação (CSV)
    # Exemplo: https://docs.google.com/spreadsheets/d/ID/edit#gid=SHEETID
    # Vira: https://docs.google.com/spreadsheets/d/ID/export?format=csv&gid=SHEETID
    sheet_csv_url = GOOGLE_SHEET_URL.replace('/edit#gid=', '/export?format=csv&gid=')
    df_planilha = pd.read_csv(sheet_csv_url)
except Exception as e:
    print(f'❌ Erro ao ler planilha Google Sheets: {e}')
    print('Tente gerar o link CSV de forma pública e colar na variável GOOGLE_SHEET_URL.')
    exit(1)

# Normalizar nomes para correspondência
norm = lambda s: str(s).strip().lower()
df_banco['nome_norm'] = df_banco['nome'].map(norm)
df_planilha['nome_norm'] = df_planilha['Nome'].map(norm)
mapa_nome2id = dict(zip(df_planilha['nome_norm'], df_planilha['ID']))

# Atualizar banco
atualizados = 0
with engine.connect() as conn:
    for _, row in df_banco.iterrows():
        id_jogador = row['id_jogador']
        nome_norm = row['nome_norm']
        id_planilha = mapa_nome2id.get(nome_norm)
        if id_planilha:
            conn.execute(
                text('UPDATE jogadores SET id_planilha = :id_planilha WHERE id_jogador = :id_jogador'),
                {'id_planilha': int(id_planilha), 'id_jogador': int(id_jogador)}
            )
            atualizados += 1
    conn.commit()
print(f'✅ Atualizados {atualizados} jogadores com id_planilha!')
print('\\n📝 Agora atualize o dashboard para buscar fotos por id_planilha.')
