"""SVG template: Language Telemetry + Focus Sectors radar (dynamic height)."""

import math
from generator.utils import calculate_language_percentages, esc, svg_arc_path, resolve_arm_colors

WIDTH = 850

def _build_language_bars(lang_data, theme, left_x, start_y):
    """Build the language bar elements with modern progress tracking style."""
    bar_lines = []
    bar_max_width = 180  # Ajustado para dar mais respiro lateral

    for i, lang in enumerate(lang_data):
        y = start_y + i * 32  # Espaçamento maior entre linhas (de 22 para 32)
        bar_w = max(4, (lang["percentage"] / 100) * bar_max_width)
        delay = f"{i * 0.15}s"

        bar_lines.append(f'''
    <g transform="translate({left_x}, {y})">
      <text x="0" y="0" fill="{theme['text_dim']}" font-size="12" font-family="sans-serif" font-weight="bold" dominant-baseline="middle">{esc(lang['name'])}</text>
      
      <rect x="100" y="-6" width="{bar_max_width}" height="10" rx="5" fill="{theme['star_dust']}" opacity="0.4"/>
      
      <rect x="100" y="-6" width="{bar_w}" height="10" rx="5" fill="{lang['color']}" opacity="0.9">
        <animate attributeName="width" from="0" to="{bar_w}" dur="1s" begin="{delay}" fill="freeze" calcMode="spline" keySplines="0.4 0 0.2 1"/>
      </rect>
      
      <text x="295" y="0" fill="{theme['text_faint']}" font-size="11" font-family="monospace" font-weight="bold" dominant-baseline="middle">{lang['percentage']}%</text>
    </g>''')

    return "\n".join(bar_lines)

def _build_radar_grid(rcx, rcy, grid_rings, theme):
    """Build the radar grid with a subtle glow effect."""
    parts = []
    for i, ring_r in enumerate(grid_rings):
        opacity = 0.1 + (i * 0.1)
        parts.append(
            f'<circle cx="{rcx}" cy="{rcy}" r="{ring_r}" '
            f'fill="none" stroke="{theme["text_faint"]}" '
            f'stroke-width="0.7" stroke-dasharray="4,4" opacity="{opacity}"/>'
        )
    return "\n".join(parts)

def _build_radar_sectors(sector_data, rcx, rcy, radius, theme):
    """Build sectors with a gradient-like fill effect."""
    parts = []
    for sec in sector_data:
        d = svg_arc_path(rcx, rcy, radius, sec["start_deg"], sec["end_deg"])
        parts.append(
            f'<path d="{d}" fill="{sec["color"]}" fill-opacity="0.08" '
            f'stroke="{sec["color"]}" stroke-opacity="0.4" stroke-width="1"/>'
        )
    return "\n".join(parts)

def _build_radar_needle(rcx, rcy, radius, theme):
    """Enhanced radar needle with a stronger pulse."""
    scan_color = theme.get("synapse_cyan", "#00d4ff")
    sweep_d = svg_arc_path(rcx, rcy, radius, 320, 360) # Sweep maior

    return f'''
    <g>
      <path d="{sweep_d}" fill="url(#radar-gradient)" fill-opacity="0.4"/>
      <line x1="{rcx}" y1="{rcy}" x2="{rcx}" y2="{rcy - radius}" stroke="{scan_color}" stroke-width="2" stroke-linecap="round"/>
      <circle cx="{rcx}" cy="{rcy - radius}" r="3" fill="{scan_color}" filter="url(#needle-glow)"/>
      <animateTransform attributeName="transform" type="rotate" from="0 {rcx} {rcy}" to="360 {rcx} {rcy}" dur="6s" repeatCount="indefinite"/>
    </g>'''

def render(languages: dict, galaxy_arms: list, theme: dict, exclude: list, max_display: int) -> str:
    lang_data = calculate_language_percentages(languages, exclude, max_display)
    all_arm_colors = resolve_arm_colors(galaxy_arms, theme)

    # Configuração de Layout
    left_x = 40
    start_y = 85
    rcx, rcy = 630, 160
    radius = 80 # Radar maior (de 65 para 80)
    
    # Dinamic height: garantindo que seja mais alto e elegante
    lang_height = start_y + len(lang_data) * 32 + 40
    height = max(300, lang_height) # Altura mínima de 300px

    # Dados dos setores do radar
    sector_data = []
    for i, arm in enumerate(galaxy_arms):
        sector_data.append({
            "name": arm["name"],
            "color": all_arm_colors[i],
            "items": len(arm.get("items", [])),
            "start_deg": i * 120 + 2,
            "end_deg": (i + 1) * 120 - 2,
        })

    from generator.templates.tech_stack import _build_radar_grid, _build_radar_sectors, _build_radar_needle, _build_radar_labels_and_dots
    
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <defs>
    <filter id="needle-glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <radialGradient id="radar-gradient" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{theme.get('synapse_cyan', '#00d4ff')}" stop-opacity="0"/>
      <stop offset="100%" stop-color="{theme.get('synapse_cyan', '#00d4ff')}" stop-opacity="0.3"/>
    </radialGradient>
  </defs>

  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="15" ry="15" fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1.5"/>

  <g transform="translate(40, 45)">
    <rect width="3" height="15" fill="{theme['synapse_cyan']}" rx="1"/>
    <text x="12" y="12" fill="{theme['text_faint']}" font-size="11" font-family="monospace" letter-spacing="3" font-weight="bold">LANGUAGE TELEMETRY</text>
  </g>

  <g transform="translate(465, 45)">
    <rect width="3" height="15" fill="{theme['dendrite_violet']}" rx="1"/>
    <text x="12" y="12" fill="{theme['text_faint']}" font-size="11" font-family="monospace" letter-spacing="3" font-weight="bold">FOCUS SECTORS</text>
  </g>

  <line x1="425" y1="40" x2="425" y2="{height - 40}" stroke="{theme['star_dust']}" stroke-width="1" stroke-dasharray="5,5" opacity="0.3"/>

  {_build_language_bars(lang_data, theme, left_x, start_y)}

  <g opacity="0.9">
    {_build_radar_grid(rcx, rcy, [30, 55, 80], theme)}
    {_build_radar_sectors(sector_data, rcx, rcy, 80, theme)}
    {_build_radar_needle(rcx, rcy, 80, theme)}
    {_build_radar_labels_and_dots(sector_data, galaxy_arms, rcx, rcy, 80, theme)}
  </g>
</svg>'''
