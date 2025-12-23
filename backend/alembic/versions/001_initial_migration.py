"""Initial migration - create all tables

Revision ID: 001
Revises:
Create Date: 2025-12-23 02:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for Scout Pro database."""

    # Create usuarios table
    op.create_table(
        'usuarios',
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('senha_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='analista'),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('data_criacao', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('ultimo_acesso', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id_usuario'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_usuarios_email', 'usuarios', ['email'])

    # Create jogadores table
    op.create_table(
        'jogadores',
        sa.Column('id_jogador', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('posicao', sa.String(length=50), nullable=False),
        sa.Column('idade_atual', sa.Integer(), nullable=False),
        sa.Column('data_nascimento', sa.Date(), nullable=True),
        sa.Column('nacionalidade', sa.String(length=100), nullable=True),
        sa.Column('altura_cm', sa.Integer(), nullable=True),
        sa.Column('pe_preferencial', sa.String(length=20), nullable=True),
        sa.Column('valor_mercado_eur', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('clube_atual', sa.String(length=255), nullable=True),
        sa.Column('liga_atual', sa.String(length=255), nullable=True),
        sa.Column('contrato_fim', sa.Date(), nullable=True),
        sa.Column('transfermarkt_id', sa.String(length=50), nullable=True),
        sa.Column('foto_url', sa.String(length=500), nullable=True),
        sa.Column('data_atualizacao', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('data_criacao', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id_jogador')
    )
    op.create_index('ix_jogadores_nome', 'jogadores', ['nome'])
    op.create_index('ix_jogadores_posicao', 'jogadores', ['posicao'])
    op.create_index('ix_jogadores_transfermarkt_id', 'jogadores', ['transfermarkt_id'], unique=True)

    # Create avaliacoes table
    op.create_table(
        'avaliacoes',
        sa.Column('id_avaliacao', sa.Integer(), nullable=False),
        sa.Column('id_jogador', sa.Integer(), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('nota_media', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('nota_potencial', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('nota_tatico', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('nota_tecnico', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('nota_fisico', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('nota_mental', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('data_avaliacao', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['id_jogador'], ['jogadores.id_jogador'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_avaliacao')
    )
    op.create_index('ix_avaliacoes_jogador', 'avaliacoes', ['id_jogador'])
    op.create_index('ix_avaliacoes_usuario', 'avaliacoes', ['id_usuario'])

    # Create wishlist table
    op.create_table(
        'wishlist',
        sa.Column('id_wishlist', sa.Integer(), nullable=False),
        sa.Column('id_jogador', sa.Integer(), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('prioridade', sa.String(length=20), nullable=False, server_default='media'),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('data_adicao', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['id_jogador'], ['jogadores.id_jogador'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_wishlist')
    )
    op.create_index('ix_wishlist_jogador', 'wishlist', ['id_jogador'])
    op.create_index('ix_wishlist_usuario', 'wishlist', ['id_usuario'])

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id_tag', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('cor', sa.String(length=7), nullable=True),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id_tag'),
        sa.UniqueConstraint('nome')
    )

    # Create jogador_tags table (many-to-many)
    op.create_table(
        'jogador_tags',
        sa.Column('id_jogador', sa.Integer(), nullable=False),
        sa.Column('id_tag', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id_jogador'], ['jogadores.id_jogador'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['id_tag'], ['tags.id_tag'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_jogador', 'id_tag')
    )

    # Create vinculos_clube table
    op.create_table(
        'vinculos_clube',
        sa.Column('id_vinculo', sa.Integer(), nullable=False),
        sa.Column('id_jogador', sa.Integer(), nullable=False),
        sa.Column('clube', sa.String(length=255), nullable=False),
        sa.Column('liga', sa.String(length=255), nullable=True),
        sa.Column('data_inicio', sa.Date(), nullable=True),
        sa.Column('data_fim', sa.Date(), nullable=True),
        sa.Column('tipo_vinculo', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['id_jogador'], ['jogadores.id_jogador'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_vinculo')
    )

    # Create alertas table
    op.create_table(
        'alertas',
        sa.Column('id_alerta', sa.Integer(), nullable=False),
        sa.Column('id_jogador', sa.Integer(), nullable=False),
        sa.Column('tipo_alerta', sa.String(length=50), nullable=False),
        sa.Column('mensagem', sa.Text(), nullable=False),
        sa.Column('lido', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('data_criacao', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['id_jogador'], ['jogadores.id_jogador'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_alerta')
    )

    # Create notas_rapidas table
    op.create_table(
        'notas_rapidas',
        sa.Column('id_nota', sa.Integer(), nullable=False),
        sa.Column('id_jogador', sa.Integer(), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('conteudo', sa.Text(), nullable=False),
        sa.Column('data_criacao', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['id_jogador'], ['jogadores.id_jogador'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_nota')
    )

    # Create buscas_salvas table
    op.create_table(
        'buscas_salvas',
        sa.Column('id_busca', sa.Integer(), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('nome_busca', sa.String(length=255), nullable=False),
        sa.Column('filtros_json', sa.Text(), nullable=False),
        sa.Column('data_criacao', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_busca')
    )

    # Create propostas table
    op.create_table(
        'propostas',
        sa.Column('id_proposta', sa.Integer(), nullable=False),
        sa.Column('id_jogador', sa.Integer(), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=False),
        sa.Column('clube_destino', sa.String(length=255), nullable=False),
        sa.Column('valor_proposta_eur', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pendente'),
        sa.Column('observacoes', sa.Text(), nullable=True),
        sa.Column('data_proposta', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['id_jogador'], ['jogadores.id_jogador'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuarios.id_usuario'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id_proposta')
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('propostas')
    op.drop_table('buscas_salvas')
    op.drop_table('notas_rapidas')
    op.drop_table('alertas')
    op.drop_table('vinculos_clube')
    op.drop_table('jogador_tags')
    op.drop_table('tags')
    op.drop_table('wishlist')
    op.drop_table('avaliacoes')
    op.drop_table('jogadores')
    op.drop_table('usuarios')
