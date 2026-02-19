"""SVG template: Mission Telemetry stats card (850x220)."""

from generator.utils import METRIC_ICONS, METRIC_LABELS, METRIC_COLORS, format_number

# Aumentamos a altura para dar mais respiro vertical
WIDTH, HEIGHT = 850, 220

def render(stats: dict, metrics: list, theme: dict) -> str:
    """Render the stats card SVG com melhor design e espaçamento."""
    
    cell_width = WIDTH / len(metrics)
    cells = []
    dividers = []

    for i, key in enumerate(metrics):
        cx = cell_width * i + cell_width / 2
        icon_color = theme.get(METRIC_COLORS.get(key, "synapse_cyan"), "#00d4ff")
        value = format_number(stats.get(key, 0))
        label = METRIC_LABELS.get(key, key.title()).upper()
        icon_path = METRIC_ICONS.get(key, "")
        delay = f"{i * 0.2}s" # Animação escalonada mais rápida

        cells.append(f'''
    <g class="metric-cell" transform="translate({cx}, 0)">
      <rect x="-{cell_width/2.5}" y="55" width="{cell_width/1.25}" height="130" rx="15" fill="{icon_color}" opacity="0.03" />
      
      <g transform="translate(-10, 80)">
        <svg viewBox="0 0 16 16" width="20" height="20" fill="{icon_color}" class="metric-icon" style="animation-delay: {delay}">
          {icon_path}
        </svg>
      </g>
      
      <text x="0" y="135" text-anchor="middle" fill="{icon_color}" font-size="32" font-weight="800" font-family="sans-serif" opacity="0.3" filter="url(#num-glow)">{value}</text>
      <text x="0" y="135" text-anchor="middle" fill="{theme['text_bright']}" font-size="32" font-weight="800" font-family="sans-serif">{value}</text>
      
      <text x="0" y="165" text-anchor="middle" fill="{theme['text_faint']}" font-size="10" font-family="monospace" letter-spacing="2" font-weight="bold">{label}</text>
    </g>''')

        # Divisores verticais mais curtos e elegantes
        if i < len(metrics) - 1:
            dx = cell_width * (i + 1)
            dividers.append(
                f'<line x1="{dx}" y1="80" x2="{dx}" y2="160" stroke="{theme["star_dust"]}" stroke-width="1" opacity="0.3"/>'
            )

    cells_str = "\n".join(cells)
    dividers_str = "\n".join(dividers)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <style>
      .metric-icon {{
        animation: count-glow 4s ease-in-out infinite;
      }}
      @keyframes count-glow {{
        0%, 100% {{ fill-opacity: 0.6; transform: scale(1); }}
        50% {{ fill-opacity: 1; transform: scale(1.1); }}
      }}
      .metric-cell {{
        animation: fade-in 0.8s ease-out forwards;
      }}
      @keyframes fade-in {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
      }}
    </style>
    <filter id="num-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="4"/>
    </filter>
  </defs>

  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="16" ry="16"
        fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1.5"/>

  <g transform="translate(35, 38)">
    <circle cx="-10" cy="-4" r="3" fill="{theme['synapse_cyan']}" />
    <text fill="{theme['text_faint']}" font-size="12" font-family="monospace" letter-spacing="4" font-weight="bold">MISSION TELEMETRY</text>
  </g>

  {dividers_str}

  {cells_str}
</svg>'''
