"""
Sistema de Autenticação - Scout Pro
Gerenciamento de usuários e controle de acesso
COM PERSISTÊNCIA DE LOGIN VIA COOKIES (CORRIGIDO)
"""

import os
import psycopg2
import hashlib
import streamlit as st
from datetime import datetime, timedelta

# Importar gerenciador de cookies
try:
    import extra_streamlit_components as stx
    COOKIES_ENABLED = True
except ImportError:
    COOKIES_ENABLED = False
    print("⚠️ extra-streamlit-components não instalado. Login não persistirá entre abas.")


# ============================================
# GERENCIADOR DE COOKIES (CORRIGIDO)
# ============================================

def get_cookie_manager():
    """
    Retorna instância do gerenciador de cookies.
    IMPORTANTE: NÃO usar @st.cache_resource aqui!
    O CookieManager precisa ser instanciado a cada sessão.
    """
    if not COOKIES_ENABLED:
        return None
    
    # Usar key única para evitar conflitos
    return stx.CookieManager(key="scout_pro_cookie_manager")


def gerar_token_sessao(username, user_id):
    """Gera token seguro para a sessão"""
    secret = "scout_pro_2024_secret_key"
    # Usar data fixa (só o dia) para o token ser válido o dia todo
    data = f"{username}_{user_id}_{datetime.now().strftime('%Y%m%d')}_{secret}"
    return hashlib.sha256(data.encode()).hexdigest()[:32]


def verificar_token_sessao(username, user_id, token):
    """Verifica se o token da sessão é válido"""
    token_esperado = gerar_token_sessao(username, user_id)
    return token == token_esperado


def salvar_sessao_cookie(usuario):
    """Salva sessão do usuário em cookies"""
    if not COOKIES_ENABLED:
        return False
    
    cookie_manager = get_cookie_manager()
    if cookie_manager is None:
        return False
    
    try:
        token = gerar_token_sessao(usuario['username'], usuario['id'])
        
        # Cookies expiram em 7 dias
        expira_em = datetime.now() + timedelta(days=7)
        
        # Salvar todos os dados em cookies separados
        cookie_manager.set("scout_user", usuario['username'], expires_at=expira_em)
        cookie_manager.set("scout_user_id", str(usuario['id']), expires_at=expira_em)
        cookie_manager.set("scout_token", token, expires_at=expira_em)
        cookie_manager.set("scout_nome", usuario['nome'] or usuario['username'], expires_at=expira_em)
        cookie_manager.set("scout_nivel", usuario['nivel'] or 'scout', expires_at=expira_em)
        
        return True
    except Exception as e:
        print(f"Erro ao salvar cookie: {e}")
        return False


def recuperar_sessao_cookie():
    """
    Tenta recuperar sessão do usuário dos cookies.
    CORRIGIDO: Lida com o timing assíncrono dos cookies.
    """
    if not COOKIES_ENABLED:
        return None
    
    cookie_manager = get_cookie_manager()
    if cookie_manager is None:
        return None
    
    try:
        # Pegar todos os cookies de uma vez
        all_cookies = cookie_manager.get_all()
        
        if not all_cookies:
            return None
        
        username = all_cookies.get("scout_user")
        user_id = all_cookies.get("scout_user_id")
        token = all_cookies.get("scout_token")
        nome = all_cookies.get("scout_nome")
        nivel = all_cookies.get("scout_nivel")
        
        # Verificar se temos os dados necessários
        if not username or not user_id or not token:
            return None
        
        # Converter user_id para int
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            return None
        
        # Verificar se o token é válido
        if verificar_token_sessao(username, user_id_int, token):
            return {
                'id': user_id_int,
                'username': username,
                'nome': nome or username,
                'nivel': nivel or 'scout',
                'email': None
            }
        
    except Exception as e:
        print(f"Erro ao recuperar cookie: {e}")
    
    return None


def limpar_sessao_cookie():
    """Remove cookies de sessão"""
    if not COOKIES_ENABLED:
        return
    
    cookie_manager = get_cookie_manager()
    if cookie_manager is None:
        return
    
    try:
        # Deletar todos os cookies de autenticação
        cookie_manager.delete("scout_user")
        cookie_manager.delete("scout_user_id")
        cookie_manager.delete("scout_token")
        cookie_manager.delete("scout_nome")
        cookie_manager.delete("scout_nivel")
    except Exception as e:
        print(f"Erro ao limpar cookies: {e}")


# ============================================
# CLASSE DE AUTENTICAÇÃO (ORIGINAL)
# ============================================

class AuthManager:
    def __init__(self):
        """Inicializa o gerenciador de autenticação"""
        # Tenta pegar DATABASE_URL do st.secrets (Streamlit Cloud) primeiro
        try:
            self.database_url = st.secrets["DATABASE_URL"]
        except (KeyError, FileNotFoundError):
            # Fallback para variável de ambiente (.env local)
            from dotenv import load_dotenv
            load_dotenv()
            self.database_url = os.getenv('DATABASE_URL')
        
        if not self.database_url:
            raise ValueError("❌ DATABASE_URL não configurada! Configure em Secrets (Cloud) ou .env (Local)")
        
        self._criar_tabela_usuarios()
    
    def get_connection(self):
        """Retorna conexão com PostgreSQL"""
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


# ============================================
# FUNÇÃO PRINCIPAL DE LOGIN (CORRIGIDA)
# ============================================

def check_password():
    """
    Função para proteger o dashboard com login.
    CORRIGIDO: Persistência de cookies funcionando corretamente.
    """
    
    # Inicializar session_state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.usuario = None
    
    # Se já autenticado na sessão atual, retorna True
    if st.session_state.authenticated and st.session_state.usuario:
        return True
    
    # CORRIGIDO: Tentar recuperar sessão dos cookies
    # Isso é executado ANTES de mostrar o formulário
    usuario_cookie = recuperar_sessao_cookie()
    
    if usuario_cookie:
        st.session_state.authenticated = True
        st.session_state.usuario = usuario_cookie
        # Não chamar st.rerun() aqui para evitar loop
        return True
    
    # Se chegou aqui, precisa mostrar o formulário de login
    _mostrar_formulario_login()
    
    return False


def _mostrar_formulario_login():
    """Renderiza o formulário de login"""

    # CSS DARK MODE para tela de login
    st.markdown("""
    <style>
    /* Forçar tema escuro na tela de login */
    .stApp {
        background-color: #0f172a !important;
    }

    .main {
        background-color: #0f172a !important;
    }

    /* Inputs escuros */
    .stTextInput input {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        border: 2px solid #334155 !important;
        border-radius: 8px;
    }

    .stTextInput input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }

    /* Checkbox */
    .stCheckbox {
        color: #e2e8f0 !important;
    }

    /* Botão de submit */
    .stButton button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
    }

    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(59, 130, 246, 0.4);
    }

    /* Títulos */
    h1, h2, h3 {
        color: #f1f5f9 !important;
    }

    /* Linha horizontal */
    hr {
        border-color: #334155 !important;
    }

    /* Mensagens de erro/sucesso */
    .stAlert {
        background-color: #1e293b !important;
        color: #f1f5f9 !important;
        border-radius: 8px;
    }

    /* Caption */
    .stCaption {
        color: #94a3b8 !important;
    }

    /* Form */
    .stForm {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid #334155 !important;
        border-radius: 12px;
        padding: 1.5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("# 🔐 Scout Pro")
        st.markdown("### Sistema de Scouting")
        st.markdown("---")
        
        with st.form("login_form"):
            username = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
            senha = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
            lembrar = st.checkbox("🔄 Manter conectado", value=True)
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
                        
                        # Salvar sessão em cookie se "manter conectado"
                        if lembrar:
                            sucesso_cookie = salvar_sessao_cookie(usuario)
                            if not sucesso_cookie:
                                st.warning("⚠️ Cookies não puderam ser salvos. Login não persistirá entre abas.")
                        
                        st.success(f"✅ Bem-vindo, {usuario['nome']}!")
                        st.rerun()
                    else:
                        st.error("❌ Usuário ou senha incorretos")
        
        st.markdown("---")
        st.caption("⚽ Sport Club do Recife")
        st.caption("🔒 Sistema Protegido")


def mostrar_info_usuario():
    """Mostra informações do usuário logado na sidebar"""
    if st.session_state.authenticated and st.session_state.usuario:
        usuario = st.session_state.usuario
        
        with st.sidebar:
            st.markdown("### 👤 Usuário")
            st.write(f"**{usuario['nome']}**")
            st.caption(f"@{usuario['username']}")
            st.caption(f"🎫 {usuario['nivel'].upper()}")
            
            if st.button("🚪 Sair", use_container_width=True):
                # Limpar cookies ao fazer logout
                limpar_sessao_cookie()
                st.session_state.authenticated = False
                st.session_state.usuario = None
                st.rerun()
            
            st.markdown("---")


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
