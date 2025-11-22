import time
import requests
from bs4 import BeautifulSoup
import gspread
from google.oauth2.service_account import Credentials
import re

# --- CONFIGURAÇÕES ---
ARQUIVO_CREDENCIAIS = 'credentials.json'
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/1jNAxJIRoZxYH1jKwPCBrd4Na1ko04EDAYaUCVGsJdIA/edit?gid=0#gid=0"
NOME_ABA = "Atletas"

# Cabeçalhos para não ser bloqueado pelo Transfermarkt
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def conectar_sheets():
    """Conecta ao Google Sheets"""
    print("🔌 Conectando ao Google Sheets...")
    try:
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = Credentials.from_service_account_file(ARQUIVO_CREDENCIAIS, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_url(URL_PLANILHA)

        try:
            worksheet = sheet.worksheet(NOME_ABA)
        except:
            worksheet = sheet.get_worksheet(0)
            print(f"⚠️ Aba '{NOME_ABA}' não encontrada. Usando a primeira aba: '{worksheet.title}'")

        return worksheet
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return None


def limpar_texto(texto):
    """Limpa quebras de linha e espaços extras"""
    if texto:
        return texto.replace('\n', '').strip()
    return ""


def limpar_posicao(texto):
    """
    Limpa a posição para pegar apenas o termo específico.
    Ex: 'Atacante - Centroavante' -> 'Centroavante'
    """
    if not texto: return ""
    if ' - ' in texto:
        return texto.split(' - ')[-1].strip()
    return texto.replace('Meia', 'Meio-Campo').strip()


def extrair_dados_tm(url):
    """Faz o scraping dos dados do jogador no Transfermarkt"""
    print(f"   🌍 Acessando: {url}...")

    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            print(f"   ❌ Erro HTTP: {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        dados = {}

        # --- 1. Nome Principal ---
        try:
            h1 = soup.find('h1', class_='data-header__headline-wrapper')
            if h1:
                dados['nome'] = limpar_texto(h1.get_text().split('\n')[-1])
            else:
                dados['nome'] = soup.find('title').get_text().split('-')[0].strip()
        except:
            dados['nome'] = "Erro Nome"

        # --- 2. Clube e Liga ---
        try:
            header_club = soup.find('span', class_='data-header__club')
            if header_club:
                dados['clube'] = header_club.find('a').get_text(strip=True)
            else:
                dados['clube'] = "Sem Clube"

            header_league = soup.find('span', class_='data-header__league')
            if header_league:
                dados['liga'] = header_league.find('a').get_text(strip=True)
            else:
                dados['liga'] = "N/A"
        except:
            dados['clube'] = "N/A"
            dados['liga'] = "N/A"

        # --- 3. Dados da Tabela Lateral ---
        def buscar_info(soup, padroes):
            for info_box in soup.find_all('div', class_=['info-table', 'info-table--right-space']):
                for label in info_box.find_all('span', class_='info-table__content--regular'):
                    texto_label = limpar_texto(label.get_text())
                    # Verifica se o texto do site contém algum dos padrões procurados
                    if any(p in texto_label for p in padroes):
                        valor = label.find_next_sibling('span', class_='info-table__content--bold')
                        if valor:
                            return limpar_texto(valor.get_text())
            return ""

        # Altura
        raw_altura = buscar_info(soup, ['Altura', 'Height'])
        dados['altura'] = raw_altura.replace(',', '.').replace('m', '').strip()

        # Pé
        dados['pe'] = buscar_info(soup, ['Pé', 'Foot'])

        # Posição
        raw_posicao = buscar_info(soup, ['Posição', 'Position'])
        dados['posicao'] = limpar_posicao(raw_posicao)

        # Nacionalidade
        try:
            nacionalidade_label = soup.find('span', string=re.compile(r'Nacionalidade|Citizenship'))
            if nacionalidade_label:
                flag_img = nacionalidade_label.find_next_sibling('span').find('img')
                dados['nacionalidade'] = flag_img['title']
            else:
                dados['nacionalidade'] = ""
        except:
            dados['nacionalidade'] = ""

        # Contrato
        dados['fim_contrato'] = buscar_info(soup, ['Contrato até', 'Contract expires'])

        # --- CORREÇÃO DA IDADE E ANO ---
        # Prioriza buscar "Nasc./Idade" pois contém ambos os dados de forma estruturada
        nasc_texto = buscar_info(soup, ['Nasc./Idade', 'Date of birth'])
        dados['idade'] = ""
        dados['ano'] = ""

        if nasc_texto:
            # Padrão: "01/01/2000 (24)" -> Extrai o que está entre parenteses
            match_idade = re.search(r'\((\d+)\)', nasc_texto)
            if match_idade:
                dados['idade'] = match_idade.group(1)

            # Extrai o ano de 4 dígitos
            match_ano = re.search(r'/(\d{4})', nasc_texto)
            if match_ano:
                dados['ano'] = match_ano.group(1)

        # Fallback: Se não achou idade acima, tenta buscar campo "Idade" isolado
        if not dados['idade']:
            idade_texto = buscar_info(soup, ['Idade', 'Age'])
            # Garante que pegou apenas números
            match_num = re.search(r'\d+', idade_texto)
            if match_num:
                dados['idade'] = match_num.group(0)

        return dados

    except Exception as e:
        print(f"   ❌ Erro de scraping: {e}")
        return None


def main():
    print("\n" + "=" * 60)
    print("🤖 ROBO SCOUT - ATUALIZADO (ALTURA/PÉ J/K)")
    print("=" * 60)

    ws = conectar_sheets()
    if not ws: return

    print("📥 Lendo dados da planilha...")

    # Configuração de colunas
    COLUNA_LINKS_TM = 15  # Coluna O
    COLUNA_NOMES = 2  # Coluna B

    coluna_links = ws.col_values(COLUNA_LINKS_TM)
    coluna_nomes = ws.col_values(COLUNA_NOMES)

    max_len = max(len(coluna_links), len(coluna_nomes))
    coluna_links += [''] * (max_len - len(coluna_links))
    coluna_nomes += [''] * (max_len - len(coluna_nomes))

    contador = 0

    for i in range(1, max_len):
        link = coluna_links[i]
        nome_atual = coluna_nomes[i]
        linha_excel = i + 1

        # Se tem link na Coluna O e Nome na Coluna B vazio
        if "transfermarkt" in str(link) and (not nome_atual or nome_atual.strip() == ""):
            print(f"\n🔍 Processando Linha {linha_excel}...")

            dados = extrair_dados_tm(link)

            if dados:
                print(f"   ✅ Encontrado: {dados['nome']} ({dados['posicao']} - {dados['idade']} anos)")

                updates = [
                    {'range': f'B{linha_excel}', 'values': [[dados['nome']]]},  # Nome
                    {'range': f'C{linha_excel}', 'values': [[dados['posicao']]]},  # Posição
                    {'range': f'D{linha_excel}', 'values': [[dados['nacionalidade']]]},  # Nacionalidade
                    {'range': f'E{linha_excel}', 'values': [[dados['idade']]]},  # Idade (Corrigida)
                    {'range': f'F{linha_excel}', 'values': [[dados['ano']]]},  # Ano

                    {'range': f'G{linha_excel}', 'values': [[dados['clube']]]},  # Clube
                    {'range': f'H{linha_excel}', 'values': [[dados['liga']]]},  # Liga
                    {'range': f'I{linha_excel}', 'values': [[dados['fim_contrato']]]},  # Contrato

                    # --- CORREÇÃO COLUNAS ---
                    {'range': f'J{linha_excel}', 'values': [[dados['altura']]]},  # Altura (Coluna J)
                    {'range': f'K{linha_excel}', 'values': [[dados['pe']]]},  # Pé (Coluna K)
                ]

                try:
                    ws.batch_update(updates)
                    print("   💾 Salvo na planilha!")
                    contador += 1
                    time.sleep(2)
                except Exception as e:
                    print(f"   ❌ Erro ao salvar: {e}")
            else:
                print("   ⚠️ Não foi possível ler os dados deste link.")

    if contador == 0:
        print("\n🤷 Nenhum link novo para processar.")
        print("   Dica: Cole links na coluna 'TM' (Coluna O) e deixe a coluna 'Nome' (Coluna B) vazia.")
    else:
        print(f"\n🎉 Sucesso! {contador} jogadores cadastrados.")
        print("   Agora rode 'python import_data.py' para atualizar o sistema.")


if __name__ == "__main__":
    main()