#!/usr/bin/env python3
from database import ScoutingDatabase

# Dados de teste
dados_teste = {
    'nome': 'TESTE JOGADOR',
    'nacionalidade': 'Brasil',
    'ano_nascimento': 1995,
    'idade_atual': 30,
    'altura': 180,
    'pe_dominante': 'direito',  # CAMPO CRÍTICO
    'transfermarkt_id': 'teste123'
}

print('📝 Dados que serão inseridos:')
for k, v in dados_teste.items():
    print(f'   {k}: {v}')

db = ScoutingDatabase()

print('\n💾 Inserindo jogador...')
id_jogador = db.inserir_jogador(dados_teste)

if id_jogador:
    print(f'✅ Jogador inserido com ID: {id_jogador}')

    # Buscar de volta para verificar
    print('\n🔍 Verificando o que foi salvo...')
    df = db.buscar_todos_jogadores()
    jogador = df[df['id_jogador'] == id_jogador].iloc[0]

    print('\n📊 Dados recuperados do banco:')
    print(f'   Nome: {jogador["nome"]}')
    print(f'   Pé dominante: {jogador["pe_dominante"]}')
    print(f'   Altura: {jogador["altura"]}')

    if jogador["pe_dominante"] == 'direito':
        print('\n✅ PÉ DOMINANTE FOI SALVO CORRETAMENTE!')
    else:
        print(f'\n❌ PÉ DOMINANTE NÃO FOI SALVO! Valor: {jogador["pe_dominante"]}')
else:
    print('❌ Falha ao inserir jogador')
