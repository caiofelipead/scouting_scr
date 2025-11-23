"""
Baixar Fotos do Transfermarkt - Versão com Scraping
Busca a URL correta da foto na página do jogador
"""

import os
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.database.database import ScoutingDatabase


def extrair_id_da_url(tm_value):
    """
    Extrai o ID numérico do Transfermarkt de uma URL ou string

    Exemplos:
    - https://www.transfermarkt.com.br/adriano/profil/spieler/1046580 -> 1046580
    - 1046580 -> 1046580
    """
    if pd.isna(tm_value) or str(tm_value).strip() == "":
        return None

    tm_str = str(tm_value).strip()

    # Tentar extrair ID numérico da URL
    match = re.search(r"/spieler/(\d+)", tm_str)
    if match:
        return match.group(1)

    # Se não encontrar na URL, verificar se já é um ID numérico
    if tm_str.isdigit():
        return tm_str

    return None


def extrair_url_foto_da_pagina(tm_id):
    """
    Acessa a página do jogador e extrai a URL completa da foto
    """
    url_pagina = f"https://www.transfermarkt.com.br/player/profil/spieler/{tm_id}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url_pagina, headers=headers, timeout=15)

        if response.status_code != 200:
            return None, f"Status {response.status_code}"

        soup = BeautifulSoup(response.content, "html.parser")

        # Procurar pela tag img com a foto do jogador
        # Padrão: <img src='https://img.a.transfermarkt.technology/portrait/big/68290-1692601435.jpg?lm=1' ...>

        # Método 1: Buscar no modal da foto
        modal_img = soup.find("img", {"src": re.compile(r"portrait/big/.*\.jpg")})
        if modal_img and modal_img.get("src"):
            url_foto = modal_img["src"]
            # Remover parâmetros de query (?lm=1)
            url_foto = url_foto.split("?")[0]
            return url_foto, "OK"

        # Método 2: Buscar em data-src
        modal_img = soup.find("img", {"data-src": re.compile(r"portrait/big/.*\.jpg")})
        if modal_img and modal_img.get("data-src"):
            url_foto = modal_img["data-src"]
            url_foto = url_foto.split("?")[0]
            return url_foto, "OK"

        # Método 3: Buscar qualquer img com portrait/big
        for img in soup.find_all("img"):
            src = img.get("src", "") or img.get("data-src", "")
            if "portrait/big" in src and ".jpg" in src:
                url_foto = src.split("?")[0]
                return url_foto, "OK"

        return None, "URL não encontrada no HTML"

    except requests.Timeout:
        return None, "Timeout"
    except Exception as e:
        return None, str(e)


def baixar_foto_com_scraping(tm_value, id_jogador, nome_jogador):
    """
    Baixa foto fazendo scraping da página do jogador
    """
    # Extrair ID numérico da URL ou string
    tm_id = extrair_id_da_url(tm_value)

    if not tm_id:
        return False, "ID inválido"

    # Extrair URL da foto da página
    url_foto, motivo = extrair_url_foto_da_pagina(tm_id)

    if not url_foto:
        return False, motivo

    # Baixar a foto
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.get(url_foto, headers=headers, timeout=10)

        if response.status_code == 200 and len(response.content) > 1000:
            foto_path = f"fotos/{id_jogador}.jpg"
            with open(foto_path, "wb") as f:
                f.write(response.content)
            return True, "OK"
        else:
            return False, f"Status {response.status_code}"

    except Exception as e:
        return False, str(e)


def baixar_todas_fotos_scraping(delay=2.0, max_jogadores=None):
    """
    Baixa fotos de todos os jogadores usando scraping
    """
    print("\n" + "=" * 60)
    print("📸 DOWNLOAD DE FOTOS - MÉTODO SCRAPING")
    print("=" * 60)

    # Criar pasta
    os.makedirs("fotos", exist_ok=True)

    # Conectar ao banco
    db = ScoutingDatabase()
    conn = db.connect()

    # Buscar jogadores com TM ID
    query = """
    SELECT id_jogador, nome, transfermarkt_id 
    FROM jogadores 
    WHERE transfermarkt_id IS NOT NULL AND transfermarkt_id != ''
    """

    if max_jogadores:
        query += f" LIMIT {max_jogadores}"

    jogadores = pd.read_sql_query(query, conn)
    conn.close()

    total = len(jogadores)

    if total == 0:
        print("\n❌ Nenhum jogador com Transfermarkt ID encontrado!")
        print("\n💡 SOLUÇÃO:")
        print("   1. Abra sua planilha do Google Sheets")
        print("   2. Adicione coluna 'TM' (ou similar)")
        print("   3. Preencha com IDs do Transfermarkt")
        print("   4. Execute: python import_data.py")
        print("   5. Execute este script novamente\n")
        return

    print(f"\n📊 {total} jogadores com Transfermarkt ID")
    print(f"⏱️  Delay entre requisições: {delay}s")
    print(f"⏱️  Tempo estimado: {int(total * delay / 60)} minutos")
    print(f"\n⚠️  IMPORTANTE:")
    print(f"   - Este método faz scraping das páginas")
    print(f"   - É mais lento mas mais confiável")
    print(f"   - Respeita rate limiting do site")

    resposta = input("\nPressione ENTER para começar (ou Ctrl+C para cancelar)...")

    sucessos = 0
    falhas = 0
    erros = {}

    print("\n🔄 Baixando fotos...\n")

    for idx, (_, jogador) in enumerate(jogadores.iterrows(), 1):
        id_jog = jogador["id_jogador"]
        nome = jogador["nome"]
        tm_value = jogador["transfermarkt_id"]

        # Extrair ID para exibição
        tm_id = extrair_id_da_url(tm_value)
        tm_display = tm_id if tm_id else tm_value

        print(f"[{idx}/{total}] {nome} (TM: {tm_display})...", end=" ", flush=True)

        sucesso, motivo = baixar_foto_com_scraping(tm_value, id_jog, nome)

        if sucesso:
            print("✅")
            sucessos += 1
        else:
            print(f"❌ ({motivo})")
            falhas += 1
            erros[motivo] = erros.get(motivo, 0) + 1

        # Delay para não sobrecarregar
        if idx < total:
            time.sleep(delay)

    # Resumo
    print("\n" + "=" * 60)
    print("📊 RESUMO")
    print("=" * 60)
    print(f"✅ Sucessos: {sucessos}/{total} ({sucessos / total * 100:.1f}%)")
    print(f"❌ Falhas: {falhas}/{total} ({falhas / total * 100:.1f}%)")

    if erros:
        print("\n❌ Motivos das falhas:")
        for motivo, qtd in sorted(erros.items(), key=lambda x: -x[1]):
            print(f"   - {motivo}: {qtd}")

    if sucessos > 0:
        print(f"\n✅ {sucessos} fotos salvas em: fotos/")

    print("=" * 60 + "\n")


def testar_um_jogador(tm_value):
    """
    Testa o scraping para um jogador específico
    """
    print("\n" + "=" * 60)
    print("🧪 TESTE DE SCRAPING - UM JOGADOR")
    print("=" * 60)

    # Extrair ID numérico
    tm_id = extrair_id_da_url(tm_value)

    if not tm_id:
        print(f"\n❌ Não foi possível extrair ID de: {tm_value}\n")
        return False

    print(f"\n📋 Transfermarkt ID extraído: {tm_id}")
    print(
        f"🌐 URL da página: https://www.transfermarkt.com.br/player/profil/spieler/{tm_id}\n"
    )

    print("1️⃣ Acessando página do jogador...")
    url_foto, motivo = extrair_url_foto_da_pagina(tm_id)

    if not url_foto:
        print(f"   ❌ Falha: {motivo}\n")
        return False

    print(f"   ✅ URL encontrada!")
    print(f"   📸 {url_foto}\n")

    print("2️⃣ Baixando foto...")

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url_foto, headers=headers, timeout=10)

        if response.status_code == 200:
            tamanho = len(response.content)
            print(f"   ✅ Baixado! Tamanho: {tamanho:,} bytes")

            # Salvar temporariamente
            os.makedirs("fotos", exist_ok=True)
            with open("fotos/teste.jpg", "wb") as f:
                f.write(response.content)
            print(f"   💾 Salvo em: fotos/teste.jpg\n")

            return True
        else:
            print(f"   ❌ Status: {response.status_code}\n")
            return False

    except Exception as e:
        print(f"   ❌ Erro: {e}\n")
        return False


def menu_principal():
    """Menu interativo"""
    print("\n" + "=" * 60)
    print("📸 BAIXAR FOTOS - MÉTODO SCRAPING")
    print("=" * 60)
    print("\n1 - Testar com Neymar (TM ID: 68290)")
    print("2 - Testar com outro jogador (digite o TM ID ou URL)")
    print("3 - Baixar primeiras 5 fotos (teste rápido)")
    print("4 - Baixar primeiras 20 fotos (teste médio)")
    print("5 - Baixar TODAS as fotos (modo lento - 2s delay)")
    print("6 - Baixar TODAS as fotos (modo normal - 1.5s delay)")
    print("0 - Sair")
    print("=" * 60)

    opcao = input("\nEscolha uma opção: ").strip()

    if opcao == "1":
        testar_um_jogador("68290")

    elif opcao == "2":
        tm_input = input("\nDigite o Transfermarkt ID ou URL: ").strip()
        if tm_input:
            testar_um_jogador(tm_input)

    elif opcao == "3":
        baixar_todas_fotos_scraping(delay=2.0, max_jogadores=5)

    elif opcao == "4":
        baixar_todas_fotos_scraping(delay=2.0, max_jogadores=20)

    elif opcao == "5":
        baixar_todas_fotos_scraping(delay=2.0)

    elif opcao == "6":
        baixar_todas_fotos_scraping(delay=1.5)

    elif opcao == "0":
        print("\n👋 Até logo!\n")
        return False

    else:
        print("\n❌ Opção inválida!\n")

    return True


if __name__ == "__main__":
    try:
        continuar = True

        while continuar:
            continuar = menu_principal()

            if continuar:
                input("\n\nPressione ENTER para voltar ao menu...")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrompido pelo usuário.\n")
    except Exception as e:
        print(f"\n\n❌ Erro: {e}\n")
        import traceback

        traceback.print_exc()
