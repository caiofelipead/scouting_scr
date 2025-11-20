import sqlite3
import re

# Nome do banco de dados
DB_NAME = "scouting.db"


def extrair_id_do_link(link):
    """
    Extrai o ID numérico após '/spieler/' no link do Transfermarkt.
    Ex: .../profil/spieler/68290 -> 68290
    """
    if not link or not isinstance(link, str):
        return None

    # Procura por 'spieler/' seguido de números
    match = re.search(r"spieler/(\d+)", link)
    if match:
        return match.group(1)
    return None


def main():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print(f"--- Atualizando IDs no banco {DB_NAME} ---")

    # 1. Verifica colunas existentes para você escolher qual tem o Link
    cursor.execute("PRAGMA table_info(jogadores)")
    colunas_info = cursor.fetchall()
    colunas = [c[1] for c in colunas_info]

    print("\nColunas encontradas na tabela 'jogadores':")
    print(colunas)

    # Pergunta qual coluna tem o link completo
    coluna_link = input("\nDigite o nome da coluna que tem o LINK COMPLETO (ex: url, link, tm_link): ").strip()

    if coluna_link not in colunas:
        print(f"❌ Erro: A coluna '{coluna_link}' não existe.")
        return

    # 2. Garante que a coluna de destino (transfermarkt_id) existe
    if 'transfermarkt_id' not in colunas:
        print("Criando coluna 'transfermarkt_id'...")
        cursor.execute("ALTER TABLE jogadores ADD COLUMN transfermarkt_id TEXT")

    # 3. Pega todos os jogadores
    print(f"Lendo dados da coluna '{coluna_link}'...")
    cursor.execute(f"SELECT id_jogador, {coluna_link} FROM jogadores WHERE {coluna_link} IS NOT NULL")
    jogadores = cursor.fetchall()

    atualizados = 0
    erros = 0

    print("\nIniciando extração...")

    # 4. Loop para atualizar
    for jog in jogadores:
        id_db = jog[0]
        link = jog[1]

        tm_id = extrair_id_do_link(link)

        if tm_id:
            cursor.execute("UPDATE jogadores SET transfermarkt_id = ? WHERE id_jogador = ?", (tm_id, id_db))
            atualizados += 1
            # Print opcional para acompanhar
            # print(f"ID {id_db}: Link extraído -> {tm_id}")
        else:
            erros += 1

    conn.commit()
    conn.close()

    print("\n" + "=" * 30)
    print(f"✅ Processo finalizado!")
    print(f"🔄 Jogadores atualizados: {atualizados}")
    print(f"⚠️ Links sem ID encontrado: {erros}")
    print("Agora você pode rodar o script de baixar fotos novamente.")


if __name__ == "__main__":
    main()