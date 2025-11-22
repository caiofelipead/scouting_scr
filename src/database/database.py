"""
Sistema de Banco de Dados para Scouting
Gerencia conexões com SQLite e integração segura com Google Sheets
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import streamlit as st
import gspread

class ScoutingDatabase:
    def __init__(self, db_path='scouting.db'):
        """Inicializa conexão com banco de dados SQLite e Google Sheets"""
        self.db_path = db_path
        self.criar_tabelas()
        
        # --- INTEGRAÇÃO GOOGLE SHEETS (HÍBRIDA: NUVEM/LOCAL) ---
        self.gc = None
        self.sh = None
        
        try:
            # 1. Tenta conectar usando Streamlit Secrets (Nuvem)
            if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
                creds_dict = st.secrets["gcp_service_account"]
                self.gc = gspread.service_account_from_dict(creds_dict)
            
            # 2. Se falhar ou não tiver secrets, tenta arquivo local (PC)
            else:
                self.gc = gspread.service_account(filename='service_account.json')

            # Tenta abrir a planilha pelo nome
            # IMPORTANTE: O nome aqui deve ser igual ao título da sua planilha no Google
            self.sh = self.gc.open("Scout Database") 
            
        except Exception as e:
            # Não quebra o app se falhar, apenas avisa (o SQLite continua funcionando)
            print(f"⚠️ Aviso: Conexão com Google Sheets não estabelecida: {e}")
    
    def get_dados_google_sheets(self):
        """Método auxiliar para puxar dados da planilha como DataFrame"""
        if not self.sh:
            return None
        
        try:
            # Pega a primeira aba da planilha
            worksheet = self.sh.sheet1 
            # Pega todos os registros
            dados = worksheet.get_all_records()
            # Converte para DataFrame
            return pd.DataFrame(dados)
        except Exception as e:
            print(f"Erro ao ler dados da planilha: {e}")
            return None

    def connect(self):
        """Cria conexão com o banco SQLite"""
        return sqlite3.connect(self.db_path)
    
    def verificar_e_criar_colunas(self):
        """Verifica e adiciona colunas faltantes em tabelas existentes"""
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            # Verificar se a coluna 'ativo' existe na tabela alertas
            cursor.execute("PRAGMA table_info(alertas)")
            colunas = [col[1] for col in cursor.fetchall()]
            
            if 'ativo' not in colunas:
                cursor.execute("ALTER TABLE alertas ADD COLUMN ativo BOOLEAN DEFAULT 1")
                conn.commit()
        except sqlite3.OperationalError:
            pass
        
        # ========= NOVO: Verificar se nota_potencial existe na tabela avaliacoes =========
        try:
            cursor.execute("PRAGMA table_info(avaliacoes)")
            colunas_aval = [col[1] for col in cursor.fetchall()]

            if 'nota_potencial' not in colunas_aval:
                print("⚠️  Adicionando coluna nota_potencial na tabela avaliacoes...")
                cursor.execute("ALTER TABLE avaliacoes ADD COLUMN nota_potencial REAL CHECK(nota_potencial >= 1 AND nota_potencial <= 5)")
                conn.commit()
                print("✅ Coluna nota_potencial adicionada com sucesso!")
        except sqlite3.OperationalError:
            pass
        # ===============================================================================

        conn.close()

    def criar_tabelas(self):
        """Cria todas as tabelas necessárias"""
        conn = self.connect()
        cursor = conn.cursor()

        # Tabela de jogadores
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS jogadores (
            id_jogador INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            nacionalidade TEXT,
            ano_nascimento INTEGER,
            idade_atual INTEGER,
            altura INTEGER,
            pe_dominante TEXT,
            transfermarkt_id TEXT
        )
        """)

        # Tabela de vínculos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vinculos (
            id_vinculo INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogador INTEGER,
            clube TEXT,
            liga_clube TEXT,
            posicao TEXT,
            data_fim_contrato DATE,
            status_contrato TEXT,
            FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador)
        )
        """)

        # Tabela de alertas
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertas (
            id_alerta INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogador INTEGER,
            tipo_alerta TEXT,
            descricao TEXT,
            prioridade TEXT,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ativo BOOLEAN DEFAULT 1,
            FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador)
        )
        """)

        # Tabela de avaliações
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id_avaliacao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_jogador INTEGER NOT NULL,
            data_avaliacao DATE NOT NULL,
            nota_potencial REAL CHECK(nota_potencial >= 1 AND nota_potencial <= 5),
            nota_tatico REAL CHECK(nota_tatico >= 1 AND nota_tatico <= 5),
            nota_tecnico REAL CHECK(nota_tecnico >= 1 AND nota_tecnico <= 5),
            nota_fisico REAL CHECK(nota_fisico >= 1 AND nota_fisico <= 5),
            nota_mental REAL CHECK(nota_mental >= 1 AND nota_mental <= 5),
            observacoes TEXT,
            avaliador TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (id_jogador) REFERENCES jogadores(id_jogador)
        )
        """)

        conn.commit()
        conn.close()

        # Verificar e adicionar colunas faltantes em tabelas existentes
        self.verificar_e_criar_colunas()

    def criar_tabela_avaliacoes(self):
        """Cria tabela de avaliações se não existir (método adicional para compatibilidade)"""
        # Redireciona para o criar_tabelas principal para evitar código duplicado
        self.criar_tabelas()

    def salvar_avaliacao(self, id_jogador, data_avaliacao, nota_potencial, nota_tatico, nota_tecnico,
                          nota_fisico, nota_mental, observacoes="", avaliador=""):
        """Salva uma nova avaliação"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO avaliacoes 
        (id_jogador, data_avaliacao, nota_potencial, nota_tatico, nota_tecnico, nota_fisico, nota_mental, observacoes, avaliador)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_jogador, data_avaliacao, nota_potencial, nota_tatico, nota_tecnico, nota_fisico, nota_mental, observacoes, avaliador))

        conn.commit()
        conn.close()

    def get_avaliacoes_jogador(self, id_jogador):
        """Retorna todas as avaliações de um jogador"""
        conn = self.connect()
        try:
            df = pd.read_sql_query("""
            SELECT * FROM avaliacoes 
            WHERE id_jogador = ?
            ORDER BY data_avaliacao DESC
            """, conn, params=(id_jogador,))
        except:
            df = pd.DataFrame()
        conn.close()
        return df

    def get_ultima_avaliacao(self, id_jogador):
        """Retorna a última avaliação de um jogador"""
        conn = self.connect()
        try:
            df = pd.read_sql_query("""
            SELECT * FROM avaliacoes 
            WHERE id_jogador = ?
            ORDER BY data_avaliacao DESC
            LIMIT 1
            """, conn, params=(id_jogador,))
        except:
            df = pd.DataFrame()
        conn.close()
        return df

    def deletar_avaliacao(self, id_avaliacao):
        """Deleta uma avaliação específica"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM avaliacoes WHERE id_avaliacao = ?", (id_avaliacao,))
        conn.commit()
        conn.close()

    def limpar_dados(self):
        """Remove todos os dados das tabelas"""
        conn = self.connect()
        cursor = conn.cursor()

        tabelas = ['alertas', 'vinculos', 'jogadores', 'avaliacoes']
        for tabela in tabelas:
            try:
                cursor.execute(f"DELETE FROM {tabela}")
            except:
                pass

        conn.commit()
        conn.close()

    def inserir_jogador(self, id_jogador, nome, nacionalidade, ano_nascimento,
                        idade_atual, altura, pe_dominante, transfermarkt_id=None):
        """Insere ou atualiza um jogador"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT OR REPLACE INTO jogadores 
        (id_jogador, nome, nacionalidade, ano_nascimento, idade_atual, altura, pe_dominante, transfermarkt_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_jogador, nome, nacionalidade, ano_nascimento, idade_atual, altura, pe_dominante, transfermarkt_id))

        conn.commit()
        conn.close()

    def inserir_vinculo(self, id_jogador, clube, liga_clube, posicao,
                        data_fim_contrato, status_contrato):
        """Insere vínculo de um jogador"""
        conn = self.connect()
        cursor = conn.cursor()

        # Primeiro remove vínculos antigos do jogador
        cursor.execute("DELETE FROM vinculos WHERE id_jogador = ?", (id_jogador,))

        # Insere novo vínculo
        cursor.execute("""
        INSERT INTO vinculos 
        (id_jogador, clube, liga_clube, posicao, data_fim_contrato, status_contrato)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (id_jogador, clube, liga_clube, posicao, data_fim_contrato, status_contrato))

        conn.commit()
        conn.close()

    def get_jogadores_com_vinculos(self):
        """Retorna todos os jogadores com seus vínculos"""
        conn = self.connect()

        query = """
        SELECT 
            j.id_jogador,
            j.nome,
            j.nacionalidade,
            j.idade_atual,
            j.altura,
            j.pe_dominante,
            v.clube,
            v.liga_clube,
            v.posicao,
            v.data_fim_contrato,
            v.status_contrato
        FROM jogadores j
        LEFT JOIN vinculos v ON j.id_jogador = v.id_jogador
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        return df

    def get_estatisticas_gerais(self):
        """Retorna estatísticas gerais do banco de dados"""
        conn = self.connect()
        cursor = conn.cursor()

        stats = {
            'total_jogadores': 0,
            'total_vinculos_ativos': 0,
            'contratos_vencendo': 0,
            'alertas_ativos': 0
        }

        try:
            cursor.execute("SELECT COUNT(*) FROM jogadores")
            stats['total_jogadores'] = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM vinculos WHERE status_contrato = 'ativo'")
            stats['total_vinculos_ativos'] = cursor.fetchone()[0]

            cursor.execute("""
            SELECT COUNT(*) FROM vinculos 
            WHERE status_contrato IN ('ultimo_ano', 'ultimos_6_meses')
            """)
            stats['contratos_vencendo'] = cursor.fetchone()[0]

            # Alertas
            try:
                cursor.execute("SELECT COUNT(*) FROM alertas WHERE ativo = 1")
            except:
                cursor.execute("SELECT COUNT(*) FROM alertas")
            stats['alertas_ativos'] = cursor.fetchone()[0]
            
        except:
            pass

        conn.close()
        return stats

    def criar_alerta(self, id_jogador, tipo_alerta, descricao, prioridade='media'):
        """Cria um novo alerta"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("""
            INSERT INTO alertas (id_jogador, tipo_alerta, descricao, prioridade, ativo)
            VALUES (?, ?, ?, ?, 1)
            """, (id_jogador, tipo_alerta, descricao, prioridade))
        except:
            cursor.execute("""
            INSERT INTO alertas (id_jogador, tipo_alerta, descricao, prioridade)
            VALUES (?, ?, ?, ?)
            """, (id_jogador, tipo_alerta, descricao, prioridade))

        conn.commit()
        conn.close()

    def get_alertas_ativos(self):
        """Retorna todos os alertas ativos"""
        conn = self.connect()

        try:
            query = """
            SELECT 
                a.id_alerta,
                a.id_jogador,
                j.nome as jogador,
                a.tipo_alerta,
                a.descricao,
                a.prioridade,
                a.data_criacao
            FROM alertas a
            JOIN jogadores j ON a.id_jogador = j.id_jogador
            WHERE a.ativo = 1
            ORDER BY 
                CASE a.prioridade
                    WHEN 'alta' THEN 1
                    WHEN 'media' THEN 2
                    WHEN 'baixa' THEN 3
                END,
                a.data_criacao DESC
            """
            df = pd.read_sql_query(query, conn)
        except:
            df = pd.DataFrame()

        conn.close()
        return df

    def desativar_alerta(self, id_alerta):
        """Desativa um alerta"""
        conn = self.connect()
        cursor = conn.cursor()

        try:
            cursor.execute("UPDATE alertas SET ativo = 0 WHERE id_alerta = ?", (id_alerta,))
        except:
            cursor.execute("DELETE FROM alertas WHERE id_alerta = ?", (id_alerta,))

        conn.commit()
        conn.close()

    def importar_dados_planilha(self, df):
        """Importa dados do DataFrame da planilha para o banco"""
        print(f"\n💾 Importando {len(df)} jogadores para o banco de dados...")

        sucesso = 0
        erros = 0
        linhas_ignoradas = 0

        for idx, row in df.iterrows():
            try:
                # Validar ID (campo obrigatório)
                id_str = str(row.get('ID', '')).strip()
                if not id_str or id_str == '' or id_str == 'nan':
                    linhas_ignoradas += 1
                    continue

                try:
                    id_jogador = int(float(id_str))
                except (ValueError, TypeError):
                    linhas_ignoradas += 1
                    continue

                # Validar nome (campo obrigatório)
                nome = str(row.get('Nome', '')).strip()
                if not nome or nome == '' or nome == 'nan':
                    linhas_ignoradas += 1
                    continue

                # Extrair dados do jogador com tratamento de valores vazios
                nacionalidade = str(row.get('Nacionalidade', '')) if pd.notna(row.get('Nacionalidade')) else ''

                # Ano de nascimento
                ano_nascimento = None
                try:
                    ano_str = str(row.get('Ano', '')).strip()
                    if ano_str and ano_str != 'nan' and ano_str != '':
                        ano_nascimento = int(float(ano_str))
                except (ValueError, TypeError):
                    pass

                # Idade atual
                idade_atual = None
                try:
                    idade_str = str(row.get('Idade', '')).strip()
                    if idade_str and idade_str != 'nan' and idade_str != '':
                        idade_atual = int(float(idade_str))
                except (ValueError, TypeError):
                    pass

                # Altura
                altura = None
                try:
                    altura_str = str(row.get('Altura', '')).strip()
                    if altura_str and altura_str != 'nan' and altura_str != '':
                        altura_float = float(altura_str)
                        if altura_float < 3:
                            altura = int(altura_float * 100)  # 1.75 -> 175
                        else:
                            altura = int(altura_float)
                except (ValueError, TypeError):
                    pass

                pe_dominante = str(row.get('Pé', '')) if pd.notna(row.get('Pé')) else ''
                transfermarkt_id = str(row.get('TM', '')) if pd.notna(row.get('TM')) else None

                # Inserir jogador
                self.inserir_jogador(
                    id_jogador=id_jogador,
                    nome=nome,
                    nacionalidade=nacionalidade,
                    ano_nascimento=ano_nascimento,
                    idade_atual=idade_atual,
                    altura=altura,
                    pe_dominante=pe_dominante,
                    transfermarkt_id=transfermarkt_id
                )

                # Extrair dados do vínculo
                clube = str(row.get('Clube', '')) if pd.notna(row.get('Clube')) else ''
                liga_clube = str(row.get('Liga do Clube', '')) if pd.notna(row.get('Liga do Clube')) else ''
                posicao = str(row.get('Posição', '')) if pd.notna(row.get('Posição')) else ''
                fim_contrato = str(row.get('Fim de contrato', '')) if pd.notna(row.get('Fim de contrato')) else ''

                status_contrato = self._determinar_status_contrato(fim_contrato)

                # Inserir vínculo
                if clube and posicao:
                    self.inserir_vinculo(
                        id_jogador=id_jogador,
                        clube=clube,
                        liga_clube=liga_clube,
                        posicao=posicao,
                        data_fim_contrato=fim_contrato,
                        status_contrato=status_contrato
                    )

                self._criar_alertas_automaticos(id_jogador, row, status_contrato)

                sucesso += 1

            except Exception as e:
                erros += 1
                nome_erro = row.get('Nome', 'desconhecido')
                print(f"❌ Erro ao importar jogador {nome_erro}: {str(e)}")

        print(f"\n✅ Importação concluída!")
        print(f"   • Sucessos: {sucesso}")
        print(f"   • Erros: {erros}")
        print(f"   • Linhas vazias ignoradas: {linhas_ignoradas}")

        return sucesso > 0

    def _determinar_status_contrato(self, fim_contrato_str):
        """Determina o status do contrato baseado na data de fim"""
        try:
            if not fim_contrato_str or fim_contrato_str == '' or fim_contrato_str == 'nan':
                return 'indefinido'

            from dateutil import parser
            fim_contrato = parser.parse(fim_contrato_str)
            hoje = datetime.now()

            diferenca = fim_contrato - hoje

            if diferenca.days < 0:
                return 'expirado'
            elif diferenca.days <= 180:  # 6 meses
                return 'ultimos_6_meses'
            elif diferenca.days <= 365:  # 1 ano
                return 'ultimo_ano'
            else:
                return 'ativo'

        except:
            return 'indefinido'

    def _criar_alertas_automaticos(self, id_jogador, row, status_contrato):
        """Cria alertas automáticos baseados nos dados do jogador"""

        if status_contrato in ['ultimos_6_meses', 'ultimo_ano']:
            self.criar_alerta(
                id_jogador=id_jogador,
                tipo_alerta='Contrato',
                descricao=f'Contrato vence em {row.get("Fim de contrato", "data não especificada")}',
                prioridade='alta' if status_contrato == 'ultimos_6_meses' else 'media'
            )

        potencial = str(row.get('Potencial', '')).lower()
        if 'alto' in potencial or 'alta' in potencial:
            self.criar_alerta(
                id_jogador=id_jogador,
                tipo_alerta='Potencial',
                descricao=f'Jogador com potencial alto: {potencial}',
                prioridade='media'
            )

    def criar_alertas_automaticos(self):
        """Método público para criar alertas automáticos após importação completa"""
        print("\n🚨 Gerando alertas automáticos...")

        conn = self.connect()

        query = """
        SELECT 
            j.id_jogador,
            j.nome,
            v.data_fim_contrato,
            v.status_contrato
        FROM jogadores j
        LEFT JOIN vinculos v ON j.id_jogador = v.id_jogador
        """

        df = pd.read_sql_query(query, conn)
        conn.close()

        alertas_criados = 0

        for _, row in df.iterrows():
            status = row['status_contrato']
            if status in ['ultimos_6_meses', 'ultimo_ano', 'expirado']:
                self.criar_alerta(
                    id_jogador=row['id_jogador'],
                    tipo_alerta='Contrato',
                    descricao=f'Contrato: {status.replace("_", " ")}',
                    prioridade='alta' if status == 'ultimos_6_meses' else 'media'
                )
                alertas_criados += 1

        print(f"✅ {alertas_criados} alertas automáticos criados!")

        return alertas_criados
