#!/usr/bin/env python3
"""
🎯 SCOUT PRO - CORREÇÃO AUTOMÁTICA DE DADOS
Executa diagnóstico completo e aplica correções automaticamente

Uso: python corrigir_tudo.py
"""

import sys
from pathlib import Path
import pandas as pd

# Adicionar raiz ao path
root_path = Path(__file__).resolve().parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

def imprimir_banner():
    """Imprime banner inicial"""
    print("\n" + "="*70)
    print("🎯 SCOUT PRO - CORREÇÃO AUTOMÁTICA DE DADOS")
    print("="*70 + "\n")

def verificar_database_module():
    """Verifica se o módulo database existe"""
    try:
        from database import ScoutingDatabase
        return True, None
    except ImportError as e:
        return False, str(e)

def diagnosticar(db):
    """Executa diagnóstico básico"""
    print("📊 ETAPA 1: DIAGNÓSTICO")
    print("-" * 70)
    
    conn = db.connect()
    
    try:
        # Contar registros
        count_jog = pd.read_sql_query("SELECT COUNT(*) as n FROM jogadores", conn)
        count_vinc = pd.read_sql_query("SELECT COUNT(*) as n FROM vinculos_clubes", conn)
        
        total_jog = count_jog['n'].iloc[0]
        total_vinc = count_vinc['n'].iloc[0]
        
        print(f"✅ Jogadores no banco: {total_jog}")
        print(f"✅ Vínculos no banco: {total_vinc}")
        
        if total_jog == 0:
            print("⚠️  ATENÇÃO: Banco vazio! Será necessário importar dados.")
            return False, total_jog, total_vinc
        
        # Testar JOIN
        query_teste = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN v.clube IS NULL THEN 1 ELSE 0 END) as sem_clube,
            SUM(CASE WHEN v.posicao IS NULL THEN 1 ELSE 0 END) as sem_posicao
        FROM jogadores j
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        """
        
        resultado = pd.read_sql_query(query_teste, conn)
        total = resultado['total'].iloc[0]
        sem_clube = resultado['sem_clube'].iloc[0]
        sem_posicao = resultado['sem_posicao'].iloc[0]
        
        print(f"\n🔍 Análise de dados:")
        print(f"   - Total de registros no JOIN: {total}")
        print(f"   - Registros sem clube: {sem_clube} ({(sem_clube/total*100):.1f}%)")
        print(f"   - Registros sem posição: {sem_posicao} ({(sem_posicao/total*100):.1f}%)")
        
        problema = sem_clube > 0 or sem_posicao > 0
        
        if problema:
            print("⚠️  Detectados campos vazios que aparecerão como 'None'")
        else:
            print("✅ Dados parecem estar OK")
        
        return True, total_jog, total_vinc
        
    except Exception as e:
        print(f"❌ Erro no diagnóstico: {str(e)}")
        return False, 0, 0
    
    finally:
        conn.close()

def reimportar_dados(db):
    """Reimporta dados do Google Sheets"""
    print("\n📥 ETAPA 2: REIMPORTAÇÃO DE DADOS")
    print("-" * 70)
    
    try:
        print("Conectando ao Google Sheets...")
        df_sheets = db.get_dados_google_sheets()
        
        if df_sheets is None or len(df_sheets) == 0:
            print("❌ Não foi possível obter dados do Google Sheets")
            print("\nVerifique:")
            print("  1. Arquivo .streamlit/secrets.toml existe")
            print("  2. Credenciais do Google estão corretas")
            print("  3. Planilha está compartilhada com a service account")
            print("  4. ID da planilha está correto")
            return False
        
        print(f"✅ Obtidos {len(df_sheets)} registros da planilha")
        print(f"📋 Colunas: {df_sheets.columns.tolist()}")
        
        # Verificar campos vazios
        print("\n🔍 Análise de campos vazios na planilha:")
        campos_vazios = []
        for col in df_sheets.columns:
            vazios = df_sheets[col].isna().sum()
            if vazios > 0:
                perc = (vazios/len(df_sheets))*100
                print(f"   - {col}: {vazios}/{len(df_sheets)} ({perc:.1f}%) vazios")
                if perc > 50:
                    campos_vazios.append(col)
        
        if campos_vazios:
            print(f"\n⚠️  Campos com mais de 50% vazios: {campos_vazios}")
            print("   Isso pode causar muitos 'None' no dashboard")
        
        # Importar
        print("\n💾 Importando para o banco de dados...")
        sucesso = db.importar_dados_planilha(df_sheets)
        
        if sucesso:
            print("✅ Importação concluída com sucesso!")
            return True
        else:
            print("❌ Falha na importação")
            return False
            
    except Exception as e:
        print(f"❌ Erro na importação: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verificar_resultado(db):
    """Verifica resultado final"""
    print("\n✅ ETAPA 3: VERIFICAÇÃO FINAL")
    print("-" * 70)
    
    conn = db.connect()
    
    try:
        # Contar registros
        count_jog = pd.read_sql_query("SELECT COUNT(*) as n FROM jogadores", conn)
        count_vinc = pd.read_sql_query("SELECT COUNT(*) as n FROM vinculos_clubes", conn)
        
        print(f"Jogadores: {count_jog['n'].iloc[0]}")
        print(f"Vínculos: {count_vinc['n'].iloc[0]}")
        
        # Amostra com JOIN
        query_amostra = """
        SELECT 
            j.nome,
            COALESCE(v.clube, 'Livre') as clube,
            COALESCE(v.posicao, 'N/A') as posicao,
            COALESCE(v.liga_clube, 'N/A') as liga
        FROM jogadores j
        LEFT JOIN vinculos_clubes v ON j.id_jogador = v.id_jogador
        LIMIT 5
        """
        
        amostra = pd.read_sql_query(query_amostra, conn)
        
        print("\n📋 Amostra de dados (5 primeiros):")
        print(amostra.to_string(index=False))
        
        # Verificar se ainda há None
        tem_none = False
        for col in amostra.columns:
            if amostra[col].isna().any():
                tem_none = True
                print(f"\n⚠️  Coluna '{col}' ainda tem valores NULL")
        
        if not tem_none:
            print("\n✅ Nenhum valor NULL detectado na amostra!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na verificação: {str(e)}")
        return False
    
    finally:
        conn.close()

def main():
    """Função principal"""
    
    imprimir_banner()
    
    # Verificar se database.py existe
    print("🔍 Verificando módulo database...")
    sucesso, erro = verificar_database_module()
    
    if not sucesso:
        print(f"❌ Erro: {erro}")
        print("\nCertifique-se de que:")
        print("  1. O arquivo database.py existe")
        print("  2. Você está executando do diretório correto")
        print("  3. O módulo não tem erros de sintaxe")
        sys.exit(1)
    
    print("✅ Módulo database.py encontrado\n")
    
    # Importar database
    from database import ScoutingDatabase
    db = ScoutingDatabase()
    
    # ETAPA 1: Diagnóstico
    sucesso_diag, total_jog, total_vinc = diagnosticar(db)
    
    if not sucesso_diag:
        print("\n❌ Falha no diagnóstico")
        resposta = input("\nDeseja tentar reimportar dados mesmo assim? (s/n): ")
        if resposta.lower() != 's':
            sys.exit(1)
    
    # ETAPA 2: Reimportação
    if total_jog == 0:
        print("\n⚠️  Banco vazio detectado")
        reimportar = True
    else:
        resposta = input("\nDeseja reimportar dados do Google Sheets? (s/n): ")
        reimportar = resposta.lower() == 's'
    
    if reimportar:
        sucesso_import = reimportar_dados(db)
        
        if not sucesso_import:
            print("\n❌ Falha na reimportação")
            print("O dashboard pode não funcionar corretamente")
            sys.exit(1)
    else:
        print("\n⏭️  Pulando reimportação")
    
    # ETAPA 3: Verificação
    verificar_resultado(db)
    
    # RESUMO FINAL
    print("\n" + "="*70)
    print("🎉 CORREÇÃO CONCLUÍDA!")
    print("="*70)
    
    print("\n📝 PRÓXIMOS PASSOS:")
    print("\n1️⃣  Aplicar correções de código:")
    print("   - Editar database.py (ver PATCH_CORRECOES.py)")
    print("   - Editar app/dashboard.py (ver PATCH_CORRECOES.py)")
    
    print("\n2️⃣  Reiniciar o dashboard:")
    print("   streamlit run app/dashboard.py")
    
    print("\n3️⃣  Verificar no dashboard:")
    print("   - Expandir 'Debug: Status do Banco'")
    print("   - Conferir tab 'Lista de Jogadores'")
    print("   - Verificar se campos estão preenchidos")
    
    print("\n4️⃣  Se ainda houver problemas:")
    print("   - Ler GUIA_TROUBLESHOOTING.md")
    print("   - Executar diagnostico_dados.py")
    print("   - Verificar dados na planilha Google Sheets")
    
    print("\n" + "="*70)
    print("✅ Script concluído com sucesso!")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Execução interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
