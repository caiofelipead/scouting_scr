#!/usr/bin/env python3
from database import ScoutingDatabase

db = ScoutingDatabase()
df = db.buscar_todos_jogadores()

print('📊 Verificação dos campos corrigidos:')
print('='*60)

print('\nPé dominante:')
print(df['pe_dominante'].value_counts().head())
print(f'Vazios: {df["pe_dominante"].isnull().sum()} de {len(df)}')

print('\n' + '='*60)
print('Fim de Contrato:')
print(df['data_fim_contrato'].value_counts().head())
print(f'Vazios: {df["data_fim_contrato"].isnull().sum()} de {len(df)}')

print('\n' + '='*60)
print('Amostra completa:')
print(df[['nome', 'pe_dominante', 'data_fim_contrato', 'clube']].head(10))
