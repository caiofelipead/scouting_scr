"""
Visualizações Avançadas - Scout Pro
====================================
Gráficos modernos inspirados em scoutingstats.ai

Inclui:
- Gráficos de Percentil
- Heatmaps de Performance
- Scatter Plots Comparativos
- Cards de Estatísticas Modernas
- Gráficos de Barras com Gradientes

Autor: Scout Pro
Data: 2025-12-09
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import streamlit as st


# ========================================
# 1. GRÁFICOS DE PERCENTIL
# ========================================

def criar_grafico_percentil(
    jogador_stats: Dict,
    benchmark_stats: pd.DataFrame,
    dimensoes: List[str] = None
) -> go.Figure:
    """
    Cria gráfico de percentil mostrando onde o jogador está em relação à distribuição

    Args:
        jogador_stats: Dicionário com estatísticas do jogador
        benchmark_stats: DataFrame com estatísticas de todos jogadores (para calcular percentis)
        dimensoes: Lista de dimensões a mostrar (padrão: ['nota_tatico', 'nota_tecnico', 'nota_fisico', 'nota_mental'])

    Returns:
        Figura Plotly
    """
    if dimensoes is None:
        dimensoes = ['nota_tatico', 'nota_tecnico', 'nota_fisico', 'nota_mental', 'nota_potencial']

    percentis = []
    labels = []
    cores = []

    for dim in dimensoes:
        if dim in jogador_stats and dim in benchmark_stats.columns:
            valor_jogador = jogador_stats[dim]

            # Calcula percentil (quantos % estão abaixo desse valor)
            percentil = (benchmark_stats[dim] < valor_jogador).mean() * 100

            percentis.append(percentil)

            # Label formatado
            label = dim.replace('nota_', '').replace('_', ' ').title()
            labels.append(f"{label}<br><sub>{valor_jogador:.1f}/5.0</sub>")

            # Cor baseada no percentil
            if percentil >= 90:
                cores.append('#10b981')  # Verde escuro - Elite
            elif percentil >= 75:
                cores.append('#3b82f6')  # Azul - Muito bom
            elif percentil >= 50:
                cores.append('#f59e0b')  # Laranja - Mediano
            else:
                cores.append('#ef4444')  # Vermelho - Abaixo da média

    # Cria gráfico de barras horizontal
    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=labels,
        x=percentis,
        orientation='h',
        marker=dict(
            color=cores,
            line=dict(color='rgba(255,255,255,0.3)', width=2)
        ),
        text=[f"{p:.0f}%" for p in percentis],
        textposition='outside',
        textfont=dict(size=14, color='white', family='Arial Black'),
        hovertemplate='<b>%{y}</b><br>Percentil: %{x:.1f}%<extra></extra>'
    ))

    # Adiciona linhas de referência
    for ref_line, ref_label in [(90, 'Elite (Top 10%)'), (75, 'Muito Bom (Top 25%)'), (50, 'Mediano')]:
        fig.add_vline(
            x=ref_line,
            line_dash="dash",
            line_color="rgba(255,255,255,0.2)",
            line_width=1,
            annotation_text=ref_label,
            annotation_position="top",
            annotation_font_size=10,
            annotation_font_color="rgba(255,255,255,0.5)"
        )

    fig.update_layout(
        title=dict(
            text="<b>Análise de Percentil</b><br><sub>Posição do jogador em relação ao benchmark</sub>",
            font=dict(size=20, color='white'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="Percentil (%)",
            range=[0, 100],
            gridcolor='rgba(255,255,255,0.1)',
            titlefont=dict(size=14, color='white'),
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            titlefont=dict(size=14, color='white'),
            tickfont=dict(color='white', size=12)
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(l=150, r=80, t=100, b=60),
        showlegend=False
    )

    return fig


# ========================================
# 2. HEATMAP DE PERFORMANCE
# ========================================

def criar_heatmap_performance(
    jogadores_df: pd.DataFrame,
    dimensoes: List[str] = None,
    max_jogadores: int = 15
) -> go.Figure:
    """
    Cria heatmap mostrando performance de múltiplos jogadores em várias dimensões

    Args:
        jogadores_df: DataFrame com jogadores e suas avaliações
        dimensoes: Dimensões a exibir
        max_jogadores: Número máximo de jogadores a mostrar

    Returns:
        Figura Plotly
    """
    if dimensoes is None:
        dimensoes = ['nota_tatico', 'nota_tecnico', 'nota_fisico', 'nota_mental', 'nota_potencial']

    # Limita número de jogadores
    df_plot = jogadores_df.head(max_jogadores).copy()

    # Prepara dados para heatmap
    valores = df_plot[dimensoes].values
    nomes = df_plot['nome'].values

    # Labels das dimensões
    labels_dim = [d.replace('nota_', '').replace('_', ' ').title() for d in dimensoes]

    # Cria heatmap
    fig = go.Figure(data=go.Heatmap(
        z=valores,
        x=labels_dim,
        y=nomes,
        colorscale=[
            [0, '#ef4444'],      # Vermelho (baixo)
            [0.4, '#f59e0b'],    # Laranja
            [0.6, '#fbbf24'],    # Amarelo
            [0.8, '#3b82f6'],    # Azul
            [1, '#10b981']       # Verde (alto)
        ],
        text=valores,
        texttemplate='%{text:.1f}',
        textfont=dict(size=11, color='white', family='Arial Black'),
        hovertemplate='<b>%{y}</b><br>%{x}: %{z:.2f}/5.0<extra></extra>',
        colorbar=dict(
            title="Nota",
            titleside="right",
            tickmode="linear",
            tick0=0,
            dtick=1,
            len=0.7,
            titlefont=dict(color='white'),
            tickfont=dict(color='white')
        )
    ))

    fig.update_layout(
        title=dict(
            text="<b>Heatmap de Performance</b><br><sub>Comparação multidimensional</sub>",
            font=dict(size=20, color='white'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title="",
            side='top',
            tickfont=dict(size=12, color='white')
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=11, color='white'),
            autorange="reversed"  # Primeiro jogador no topo
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=max(400, len(df_plot) * 35),
        margin=dict(l=150, r=100, t=100, b=60)
    )

    return fig


# ========================================
# 3. SCATTER PLOT COMPARATIVO
# ========================================

def criar_scatter_plot_comparativo(
    jogadores_df: pd.DataFrame,
    dim_x: str = 'nota_tecnico',
    dim_y: str = 'nota_fisico',
    highlight_jogadores: List[str] = None,
    posicao_filtro: Optional[str] = None
) -> go.Figure:
    """
    Cria scatter plot comparando 2 dimensões simultaneamente

    Args:
        jogadores_df: DataFrame com jogadores
        dim_x: Dimensão para eixo X
        dim_y: Dimensão para eixo Y
        highlight_jogadores: Lista de nomes para destacar
        posicao_filtro: Filtrar por posição específica

    Returns:
        Figura Plotly
    """
    df_plot = jogadores_df.copy()

    # Filtra por posição se especificado
    if posicao_filtro and 'posicao' in df_plot.columns:
        df_plot = df_plot[df_plot['posicao'] == posicao_filtro]

    # Separa jogadores destacados
    if highlight_jogadores:
        df_highlight = df_plot[df_plot['nome'].isin(highlight_jogadores)]
        df_normal = df_plot[~df_plot['nome'].isin(highlight_jogadores)]
    else:
        df_highlight = pd.DataFrame()
        df_normal = df_plot

    fig = go.Figure()

    # Jogadores normais (fundo)
    if not df_normal.empty:
        fig.add_trace(go.Scatter(
            x=df_normal[dim_x],
            y=df_normal[dim_y],
            mode='markers',
            name='Outros Jogadores',
            marker=dict(
                size=10,
                color='rgba(100, 100, 100, 0.4)',
                line=dict(width=1, color='rgba(255,255,255,0.3)')
            ),
            text=df_normal['nome'],
            hovertemplate='<b>%{text}</b><br>%{xaxis.title.text}: %{x:.2f}<br>%{yaxis.title.text}: %{y:.2f}<extra></extra>'
        ))

    # Jogadores destacados (frente)
    if not df_highlight.empty:
        fig.add_trace(go.Scatter(
            x=df_highlight[dim_x],
            y=df_highlight[dim_y],
            mode='markers+text',
            name='Jogadores Selecionados',
            marker=dict(
                size=16,
                color='#3b82f6',
                line=dict(width=2, color='white'),
                symbol='star'
            ),
            text=df_highlight['nome'],
            textposition='top center',
            textfont=dict(size=10, color='white', family='Arial Black'),
            hovertemplate='<b>%{text}</b><br>%{xaxis.title.text}: %{x:.2f}<br>%{yaxis.title.text}: %{y:.2f}<extra></extra>'
        ))

    # Labels formatados
    label_x = dim_x.replace('nota_', '').replace('_', ' ').title()
    label_y = dim_y.replace('nota_', '').replace('_', ' ').title()

    # Linhas de média
    media_x = df_plot[dim_x].mean()
    media_y = df_plot[dim_y].mean()

    fig.add_hline(y=media_y, line_dash="dash", line_color="rgba(255,255,255,0.3)", line_width=1)
    fig.add_vline(x=media_x, line_dash="dash", line_color="rgba(255,255,255,0.3)", line_width=1)

    # Anotações dos quadrantes
    fig.add_annotation(x=4.5, y=4.5, text="Elite", showarrow=False,
                      font=dict(size=12, color='rgba(16, 185, 129, 0.6)', family='Arial Black'))
    fig.add_annotation(x=1.5, y=1.5, text="Desenvolver", showarrow=False,
                      font=dict(size=12, color='rgba(239, 68, 68, 0.6)', family='Arial Black'))

    fig.update_layout(
        title=dict(
            text=f"<b>{label_x} vs {label_y}</b><br><sub>Análise comparativa bidimensional</sub>",
            font=dict(size=20, color='white'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=label_x,
            range=[0, 5.5],
            gridcolor='rgba(255,255,255,0.1)',
            titlefont=dict(size=14, color='white'),
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            title=label_y,
            range=[0, 5.5],
            gridcolor='rgba(255,255,255,0.1)',
            titlefont=dict(size=14, color='white'),
            tickfont=dict(color='white')
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=500,
        margin=dict(l=80, r=80, t=100, b=80),
        showlegend=True,
        legend=dict(
            font=dict(color='white'),
            bgcolor='rgba(0,0,0,0.3)'
        )
    )

    return fig


# ========================================
# 4. CARDS DE ESTATÍSTICAS MODERNAS
# ========================================

def criar_card_estatistica(
    titulo: str,
    valor_principal: float,
    valor_secundario: Optional[str] = None,
    percentil: Optional[float] = None,
    trending: Optional[str] = None,  # 'up', 'down', 'stable'
    cor_principal: str = '#3b82f6'
) -> str:
    """
    Cria HTML para um card de estatística moderna (estilo scoutingstats.ai)

    Args:
        titulo: Título da métrica
        valor_principal: Valor principal a exibir
        valor_secundario: Valor secundário (ex: "por jogo", "Top 10%")
        percentil: Percentil (0-100) para barra de progresso
        trending: Tendência ('up', 'down', 'stable')
        cor_principal: Cor hex do card

    Returns:
        String HTML do card
    """
    # Ícone de tendência
    trending_icon = ""
    if trending == 'up':
        trending_icon = "📈"
    elif trending == 'down':
        trending_icon = "📉"
    elif trending == 'stable':
        trending_icon = "➡️"

    # Barra de percentil
    percentil_bar = ""
    if percentil is not None:
        percentil_cor = cor_principal
        if percentil >= 90:
            percentil_cor = '#10b981'
        elif percentil >= 75:
            percentil_cor = '#3b82f6'
        elif percentil >= 50:
            percentil_cor = '#f59e0b'
        else:
            percentil_cor = '#ef4444'

        percentil_bar = f"""
        <div style="margin-top: 8px;">
            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 3px; overflow: hidden;">
                <div style="background: {percentil_cor}; width: {percentil}%; height: 100%; transition: width 0.5s;"></div>
            </div>
            <div style="text-align: right; font-size: 10px; color: rgba(255,255,255,0.6); margin-top: 2px;">
                Top {100-percentil:.0f}%
            </div>
        </div>
        """

    html = f"""
    <div style="
        background: linear-gradient(135deg, {cor_principal}20 0%, {cor_principal}40 100%);
        border-left: 4px solid {cor_principal};
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: transform 0.2s, box-shadow 0.2s;
        height: 100%;
    " onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 8px 24px rgba(0,0,0,0.4)';"
       onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.3)';">

        <div style="display: flex; justify-content: space-between; align-items: start;">
            <div style="font-size: 13px; color: rgba(255,255,255,0.7); text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">
                {titulo}
            </div>
            <div style="font-size: 20px;">
                {trending_icon}
            </div>
        </div>

        <div style="font-size: 36px; font-weight: bold; color: white; margin: 12px 0; font-family: 'Arial Black', sans-serif;">
            {valor_principal}
        </div>

        {f'<div style="font-size: 14px; color: rgba(255,255,255,0.8);">{valor_secundario}</div>' if valor_secundario else ''}

        {percentil_bar}
    </div>
    """

    return html


def criar_grid_cards_estatisticas(stats: Dict, benchmarks: Optional[pd.DataFrame] = None) -> str:
    """
    Cria grid completo de cards de estatísticas

    Args:
        stats: Dicionário com estatísticas do jogador
        benchmarks: DataFrame para calcular percentis

    Returns:
        HTML completo do grid
    """
    cards_html = []

    # Card 1: Média Geral
    media = stats.get('media_geral', 0)
    percentil_media = None
    if benchmarks is not None and 'media_geral' in benchmarks.columns:
        percentil_media = (benchmarks['media_geral'] < media).mean() * 100

    cards_html.append(criar_card_estatistica(
        titulo="Média Geral",
        valor_principal=f"{media:.2f}",
        valor_secundario="Avaliação Scout Pro",
        percentil=percentil_media,
        trending='up' if media >= 4.0 else 'stable',
        cor_principal='#667eea'
    ))

    # Card 2: Potencial
    potencial = stats.get('nota_potencial', 0)
    percentil_pot = None
    if benchmarks is not None and 'nota_potencial' in benchmarks.columns:
        percentil_pot = (benchmarks['nota_potencial'] < potencial).mean() * 100

    cards_html.append(criar_card_estatistica(
        titulo="Potencial",
        valor_principal=f"{potencial:.1f}",
        valor_secundario="Capacidade de Desenvolvimento",
        percentil=percentil_pot,
        trending='up' if potencial >= 4.0 else 'stable',
        cor_principal='#f59e0b'
    ))

    # Card 3: Gols (se disponível)
    if 'gols' in stats:
        cards_html.append(criar_card_estatistica(
            titulo="Gols",
            valor_principal=str(stats['gols']),
            valor_secundario=f"{stats.get('partidas_jogadas', 0)} partidas",
            cor_principal='#10b981'
        ))

    # Card 4: Assistências (se disponível)
    if 'assistencias' in stats:
        cards_html.append(criar_card_estatistica(
            titulo="Assistências",
            valor_principal=str(stats['assistencias']),
            valor_secundario=f"xA: {stats.get('expected_assists', 0):.1f}",
            cor_principal='#3b82f6'
        ))

    # Monta grid
    grid_html = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0;">'
    grid_html += ''.join(cards_html)
    grid_html += '</div>'

    return grid_html


# ========================================
# 5. GRÁFICO DE BARRAS COM GRADIENTE
# ========================================

def criar_barras_gradiente(
    jogadores_df: pd.DataFrame,
    metrica: str = 'media_geral',
    top_n: int = 10,
    titulo: str = None
) -> go.Figure:
    """
    Cria gráfico de barras com gradiente de cores baseado no valor

    Args:
        jogadores_df: DataFrame com jogadores
        metrica: Métrica a exibir
        top_n: Número de jogadores a mostrar
        titulo: Título personalizado

    Returns:
        Figura Plotly
    """
    # Ordena e pega top N
    df_plot = jogadores_df.nlargest(top_n, metrica).copy()

    # Normaliza valores para cor (0-1)
    valores = df_plot[metrica].values
    valores_norm = (valores - valores.min()) / (valores.max() - valores.min()) if valores.max() > valores.min() else np.ones(len(valores))

    # Cores gradientes
    cores = [f'rgb({int(255*(1-v))}, {int(100 + 155*v)}, {int(50 + 180*v)})' for v in valores_norm]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        y=df_plot['nome'],
        x=valores,
        orientation='h',
        marker=dict(
            color=cores,
            line=dict(color='rgba(255,255,255,0.3)', width=2)
        ),
        text=[f"{v:.2f}" for v in valores],
        textposition='outside',
        textfont=dict(size=13, color='white', family='Arial Black'),
        hovertemplate='<b>%{y}</b><br>%{x:.2f}<extra></extra>'
    ))

    label_metrica = metrica.replace('_', ' ').title()

    fig.update_layout(
        title=dict(
            text=f"<b>{titulo or f'Top {top_n} - {label_metrica}'}</b>",
            font=dict(size=20, color='white'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=label_metrica,
            gridcolor='rgba(255,255,255,0.1)',
            titlefont=dict(size=14, color='white'),
            tickfont=dict(color='white')
        ),
        yaxis=dict(
            titlefont=dict(size=14, color='white'),
            tickfont=dict(color='white', size=11),
            autorange="reversed"
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=max(400, len(df_plot) * 40),
        margin=dict(l=150, r=100, t=80, b=60),
        showlegend=False
    )

    return fig
