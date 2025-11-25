"""
Sistema de Autenticação - Scout Pro
Gerenciamento de usuários e controle de acesso
"""

import streamlit as st
import hashlib
import psycopg2
from datetime import datetime
import os


class AuthManager:
    """Gerenciador de autenticação e usuários"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self._criar_tabela_usuarios()
    
    def get_connection(self):
        """Estabelece conexão com o banco PostgreSQL"""
        return psycopg2.connect(self.database_url)
    
    def _criar_tabela_usuarios(self):
        """Cria tabela de usuários se não existir"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(64) NOT NULL,
                    nome_completo VARCHAR(100),
                    email VARCHAR(100),
                    nivel_acesso VARCHAR(20) DEFAULT 'scout',
                    ativo BOOLEAN DEFAULT TRUE,
                    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ultimo_acesso TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS log_acessos (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER REFERENCES usuarios(id),
                    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    acao VARCHAR(50),
                    detalhes TEXT
                )
            """)
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Erro ao criar tabelas: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def _hash_senha(self, senha):
        """Gera hash SHA-256 da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def criar_usuario(self, username, senha, nome_completo, email=None, nivel_acesso='scout'):
        """Cria novo usuário no sistema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            senha_hash = self._hash_senha(senha)
            cursor.execute("""
                INSERT INTO usuarios (username, password_hash, nome_completo, email, nivel_acesso)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, senha_hash, nome_completo, email, nivel_acesso))
            conn.commit()
            return True
        except psycopg2.IntegrityError:
            conn.rollback()
            return False
        except Exception as e:
            conn.rollback()
            print(f"Erro ao criar usuário: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def verificar_login(self, username, senha):
        """Verifica credenciais do usuário"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            senha_hash = self._hash_senha(senha)
            
            cursor.execute("""
                SELECT id, nome_completo, email, nivel_acesso 
                FROM usuarios 
                WHERE username = %s AND password_hash = %s AND ativo = TRUE
            """, (username, senha_hash))
            
            resultado = cursor.fetchone()
            
            if resultado:
                cursor.execute("""
                    UPDATE usuarios 
                    SET ultimo_acesso = CURRENT_TIMESTAMP 
                    WHERE id = %s
                """, (resultado[0],))
                
                cursor.execute("""
                    INSERT INTO log_acessos (usuario_id, acao, detalhes)
                    VALUES (%s, 'login', 'Login realizado com sucesso')
                """, (resultado[0],))
                
                conn.commit()
                
                return {
                    'id': resultado[0],
                    'nome': resultado[1],
                    'email': resultado[2],
                    'nivel': resultado[3],
                    'username': username
                }
            return None
        except Exception as e:
            print(f"Erro ao verificar login: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    def listar_usuarios(self):
        """Lista todos os usuários"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, nome_completo, email, nivel_acesso, 
                       ativo, criado_em, ultimo_acesso
                FROM usuarios
                ORDER BY criado_em DESC
            """)
            
            usuarios = []
            for row in cursor.fetchall():
                usuarios.append({
                    'id': row[0],
                    'username': row[1],
                    'nome': row[2],
                    'email': row[3],
                    'nivel': row[4],
                    'ativo': row[5],
                    'criado_em': row[6],
                    'ultimo_acesso': row[7]
                })
            return usuarios
        finally:
            cursor.close()
            conn.close()


def check_password():
    """Função para proteger o dashboard com login"""
    
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.usuario = None
    
    if st.session_state.authenticated:
        return True
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🔐 Scout Pro")
        st.markdown("### Sistema de Scouting")
        st.markdown("---")
        
        with st.form("login_form"):
            username = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
            submit = st.form_submit_button("🚀 Entrar", use_container_width=True)
            
            if submit:
                if not username or not senha:
                    st.error("⚠️ Preencha todos os campos")
                else:
                    auth = AuthManager()
                    usuario = auth.verificar_login(username, senha)
                    
                    if usuario:
                        st.session_state.authenticated = True
                        st.session_state.usuario = usuario
                        st.success(f"✅ Bem-vindo, {usuario['nome']}!")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos")
        
        st.markdown("---")
        st.caption("⚽ Sport Club do Recife")
        st.caption("🔒 Sistema Protegido")
    
    return False


def mostrar_info_usuario():
    """Mostra informações do usuário logado na sidebar"""
    if st.session_state.authenticated:
        usuario = st.session_state.usuario
        
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 Usuário")
            st.write(f"**{usuario['nome']}**")
            st.caption(f"@{usuario['username']}")
            st.caption(f"🎫 {usuario['nivel'].upper()}")
            
            if st.button("🚪 Sair", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.usuario = None
                st.rerun()


def pagina_gerenciar_usuarios():
    """Página de gerenciamento de usuários (apenas admin)"""
    
    if not st.session_state.authenticated:
        st.error("Acesso negado")
        return
    
    if st.session_state.usuario['nivel'] != 'admin':
        st.error("❌ Apenas administradores podem acessar esta página")
        return
    
    st.title("👥 Gerenciamento de Usuários")
    
    auth = AuthManager()
    
    with st.expander("➕ Criar Novo Usuário"):
        with st.form("novo_usuario"):
            col1, col2 = st.columns(2)
            
            with col1:
                novo_username = st.text_input("Username")
                novo_nome = st.text_input("Nome Completo")
                novo_email = st.text_input("Email")
            
            with col2:
                nova_senha = st.text_input("Senha", type="password")
                confirma_senha = st.text_input("Confirmar Senha", type="password")
                nivel = st.selectbox("Nível de Acesso", ["scout", "admin"])
            
            submit = st.form_submit_button("Criar Usuário", use_container_width=True)
            
            if submit:
                if nova_senha != confirma_senha:
                    st.error("As senhas não coincidem")
                elif len(nova_senha) < 6:
                    st.error("A senha deve ter pelo menos 6 caracteres")
                else:
                    if auth.criar_usuario(novo_username, nova_senha, novo_nome, novo_email, nivel):
                        st.success(f"✅ Usuário {novo_username} criado com sucesso!")
                    else:
                        st.error("❌ Erro ao criar usuário. Username já existe.")
    
    st.markdown("### 📋 Usuários Cadastrados")
    usuarios = auth.listar_usuarios()
    
    for usuario in usuarios:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 2])
            
            with col1:
                status = "🟢" if usuario['ativo'] else "🔴"
                st.write(f"{status} **{usuario['nome']}**")
                st.caption(f"@{usuario['username']}")
            
            with col2:
                st.write(f"📧 {usuario['email'] or 'N/A'}")
                st.caption(f"🎫 {usuario['nivel']}")
            
            with col3:
                if usuario['ultimo_acesso']:
                    st.caption(f"Último acesso:")
                    st.caption(usuario['ultimo_acesso'].strftime("%d/%m/%y %H:%M"))
            
            st.markdown("---")
