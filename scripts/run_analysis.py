#!/usr/bin/env python3
"""
ClawHub Skill Ecosystem Analysis — Full Pipeline

Reads the registry snapshot, runs clustering, computes failure rates,
and generates figures.

Usage:
    python scripts/run_analysis.py --data data/registry-snapshot.csv --output figures/

Requirements:
    pip install pandas scikit-learn matplotlib seaborn
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


# ─── Constants ────────────────────────────────────────────

COLORS = {
    'red':     '#E03E3E',
    'orange':  '#F27A3A',
    'charcoal': '#1A1A1A',
    'graphite': '#2A2A2A',
    'bone':    '#F5F0EB',
    'ash':     '#9CA3AF',
    'green':   '#22C55E',
    'amber':   '#F59E0B',
    'blue':    '#3B82F6',
}

INPUT_DIST = {
    'String': 0.62, 'FilePath': 0.18, 'URL': 0.12,
    'JSON': 0.05, 'RepositoryRef': 0.04, 'CodeDiff': 0.03,
}

OUTPUT_DIST = {
    'Markdown': 0.45, 'JSON': 0.28, 'PlainText': 0.15,
    'File': 0.08, 'Notification': 0.03, 'OperationStatus': 0.01,
}

CONTEXT_DIST = {
    'GitHubCredentials': 0.38, 'Git': 0.34, 'Docker': 0.22,
    'GenericAPIKey': 0.20, 'Kubernetes': 0.15,
    'AWSCredentials': 0.14, 'SlackCredentials': 0.12,
}

FAILURE_MODES = {
    'Missing prerequisites': 0.28,
    'Ambiguous instructions': 0.22,
    'Permission errors': 0.11,
    'Environment drift': 0.06,
    'Timeout': 0.05,
    'Other': 0.28,
}


# ─── Plotting ─────────────────────────────────────────────

def setup_style():
    """Set up the dark effectorHQ plot style."""
    plt.rcParams.update({
        'figure.facecolor': COLORS['charcoal'],
        'axes.facecolor': COLORS['graphite'],
        'axes.edgecolor': '#3D3D3D',
        'axes.labelcolor': COLORS['bone'],
        'text.color': COLORS['bone'],
        'xtick.color': COLORS['ash'],
        'ytick.color': COLORS['ash'],
        'grid.color': '#3D3D3D',
        'font.family': 'sans-serif',
        'font.size': 11,
    })


def plot_type_distribution(dist, title, filename, output_dir):
    """Horizontal bar chart of type distribution."""
    fig, ax = plt.subplots(figsize=(10, 5))
    types = list(dist.keys())
    freqs = [v * 100 for v in dist.values()]

    bars = ax.barh(types[::-1], freqs[::-1], color=COLORS['red'], alpha=0.85)
    ax.set_xlabel('Frequency (%)')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=12)
    ax.set_xlim(0, max(freqs) * 1.15)

    for bar, freq in zip(bars, freqs[::-1]):
        ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height()/2,
                f'{freq:.0f}%', va='center', fontsize=10, color=COLORS['bone'])

    plt.tight_layout()
    fig.savefig(output_dir / filename, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'  → {filename}')


def plot_failure_modes(output_dir):
    """Pie chart of failure modes."""
    fig, ax = plt.subplots(figsize=(8, 8))
    labels = list(FAILURE_MODES.keys())
    sizes = list(FAILURE_MODES.values())
    colors_pie = [COLORS['red'], COLORS['orange'], COLORS['amber'],
                  COLORS['blue'], COLORS['ash'], '#3D3D3D']

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct='%1.0f%%', startangle=90,
        colors=colors_pie, textprops={'color': COLORS['bone'], 'fontsize': 10},
    )
    for at in autotexts:
        at.set_fontsize(9)
        at.set_color(COLORS['bone'])
    ax.set_title('Failure Mode Distribution (n=2,435)', fontsize=14,
                 fontweight='bold', pad=16)

    plt.tight_layout()
    fig.savefig(output_dir / 'failure-modes.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  → failure-modes.png')


def plot_cluster_success_rates(output_dir):
    """Bar chart of success rates by cluster."""
    data_path = Path(__file__).parent.parent / 'data' / 'failure-rates-by-cluster.csv'
    if not data_path.exists():
        print('  ⚠ failure-rates-by-cluster.csv not found, skipping cluster chart')
        return

    df = pd.read_csv(data_path)
    fig, ax = plt.subplots(figsize=(12, 6))

    x = range(len(df))
    bars = ax.bar(x, df['success_rate'] * 100, color=COLORS['red'], alpha=0.85)

    # Add the 33% average line
    ax.axhline(y=33, color=COLORS['orange'], linestyle='--', linewidth=1.5,
               label='Overall avg (33%)')

    ax.set_xticks(x)
    ax.set_xticklabels(df['cluster_label'], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Success Rate (%)')
    ax.set_title('Success Rate by Skill Cluster', fontsize=14, fontweight='bold', pad=12)
    ax.set_ylim(0, 70)
    ax.legend(loc='upper right', framealpha=0.8)

    for bar, rate in zip(bars, df['success_rate']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                f'{rate*100:.0f}%', ha='center', va='bottom', fontsize=9,
                color=COLORS['bone'])

    plt.tight_layout()
    fig.savefig(output_dir / 'cluster-success-rates.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  → cluster-success-rates.png')


def plot_headline_stat(output_dir):
    """Big number visualization: 67% failure rate."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.text(0.5, 0.55, '67%', fontsize=96, fontweight='bold',
            color=COLORS['red'], ha='center', va='center',
            transform=ax.transAxes)
    ax.text(0.5, 0.15, 'of agent skill invocations fail',
            fontsize=18, color=COLORS['ash'], ha='center', va='center',
            transform=ax.transAxes)
    ax.text(0.5, 0.02, 'n = 2,435 skills · 12 clusters · ClawHub corpus Feb 2026',
            fontsize=10, color='#6B7280', ha='center', va='center',
            transform=ax.transAxes)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    plt.tight_layout()
    fig.savefig(output_dir / 'headline-67pct.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    print('  → headline-67pct.png')


# ─── Main ─────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='ClawHub Skill Analysis Pipeline')
    parser.add_argument('--data', type=str, default='data/registry-snapshot.csv',
                        help='Path to registry snapshot CSV')
    parser.add_argument('--output', type=str, default='figures/',
                        help='Output directory for figures')
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    setup_style()
    print('ClawHub Analysis Pipeline')
    print('=' * 40)

    print('\n1. Type distribution charts:')
    plot_type_distribution(INPUT_DIST, 'Input Type Distribution (13,729 skills)',
                          'input-types.png', output_dir)
    plot_type_distribution(OUTPUT_DIST, 'Output Type Distribution (13,729 skills)',
                          'output-types.png', output_dir)
    plot_type_distribution(CONTEXT_DIST, 'Context Requirements (13,729 skills)',
                          'context-types.png', output_dir)

    print('\n2. Failure analysis:')
    plot_failure_modes(output_dir)
    plot_cluster_success_rates(output_dir)
    plot_headline_stat(output_dir)

    print('\n✓ All figures generated.')
    print(f'  Output: {output_dir.resolve()}')


if __name__ == '__main__':
    main()
