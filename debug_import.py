#!/usr/bin/env python3
import os
os.environ['GOOGLE_SHEET_URL'] = 'https://docs.google.com/spreadsheets/d/1jNAxJIRoZxYH1jKwPCBrd4Na1ko04EDAYaUCVGsJdIA'

from google_sheets_sync_railway import GoogleSheetsSync

sync = GoogleSheetsSync()
sync.conectar_planilha()
df = sync.ler_dados_planilha()

print('📊 Dados lidos da planilha:')
print('='*70)

# Mostrar primeira linha de dados
print('\nPrimeira linha completa:')
for col in df.columns:
    valor = df[col].iloc[0]
    print(f'  {col}: {valor}')

print('\n' + '='*70)
print('Valores específicos que precisamos:')
print(f'  Pé dominante (1ª linha): {df["Pé dominante"].iloc[0]}')
print(f'  Fim de Contrato (1ª linha): {df["Fim de Contrato"].iloc[0]}')

print('\n' + '='*70)
print('Estatísticas:')
print(f'  Total de linhas: {len(df)}')
print(f'  Pé dominante vazios: {df["Pé dominante"].isnull().sum()}')
print(f'  Fim de Contrato vazios: {df["Fim de Contrato"].isnull().sum()}')
