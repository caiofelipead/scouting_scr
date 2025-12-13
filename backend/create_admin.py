"""
Script para criar usuário administrador
Execute: python backend/create_admin.py
"""
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.usuario import Usuario


def create_admin():
    """Cria usuário administrador padrão"""

    db = SessionLocal()

    try:
        # Verificar se já existe admin
        existing_admin = db.query(Usuario).filter(Usuario.username == "admin").first()

        if existing_admin:
            print("⚠️  Usuário 'admin' já existe!")
            print(f"   ID: {existing_admin.id}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Nível: {existing_admin.nivel}")

            resposta = input("\nDeseja recriar? (isso vai deletar o existente) [s/N]: ")
            if resposta.lower() != 's':
                print("❌ Operação cancelada.")
                return

            db.delete(existing_admin)
            db.commit()
            print("🗑️  Usuário antigo deletado.")

        # Criar novo admin
        admin = Usuario(
            username="admin",
            email="admin@scoutpro.com",
            nome="Administrador",
            senha_hash=hash_password("admin123"),
            nivel="admin",
            ativo=True
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("\n✅ Usuário administrador criado com sucesso!")
        print("=" * 50)
        print(f"ID:       {admin.id}")
        print(f"Username: {admin.username}")
        print(f"Email:    {admin.email}")
        print(f"Senha:    admin123")
        print(f"Nível:    {admin.nivel}")
        print("=" * 50)
        print("\n⚠️  IMPORTANTE: Troque a senha após o primeiro login!")

    except Exception as e:
        print(f"\n❌ Erro ao criar usuário: {e}")
        db.rollback()

    finally:
        db.close()


if __name__ == "__main__":
    print("🔧 Criando usuário administrador...\n")
    create_admin()
