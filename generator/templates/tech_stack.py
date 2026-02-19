"""SVG template: Language Telemetry + Focus Sectors radar (dynamic height)."""

import math
from generator.utils import calculate_language_percentages, esc, svg_arc_path, resolve_arm_colors

WIDTH = 850

def _build_language_bars(lang_data, theme, left_x, start_y):
    """Build the language bar elements with modern progress tracking style."""
    bar_lines = []
    bar_max_width = 180

    for i, lang in enumerate(lang_data):
        y = start_y + i * 32
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
    parts = []
    for i, ring_r in enumerate(grid_rings):
        opacity = 0.1 + (i * 0.1)
        parts.append(
            f'<circle cx="{rcx}" cy="{rcy}" r="{ring_r}" fill="none" stroke="{theme["text_faint"]}" stroke-width="0.7" stroke-dasharray="4,4" opacity="{opacity}"/>'
        )
    return "\n".join(parts)

def _build_radar_sectors(sector_data, rcx, rcy, radius, theme):
    parts = []
    for sec in sector_data:
        d = svg_arc_path(rcx, rcy, radius, sec["start_deg"], sec["end_deg"])
        parts.append(
            f'<path d="{d}" fill="{sec["color"]}" fill-opacity="0.08" stroke="{sec["color"]}" stroke-opacity="0.4" stroke-width="1"/>'
        )
    return "\n".join(parts)

def _build_radar_needle(rcx, rcy, radius, theme):
    scan_color = theme.get("synapse_cyan", "#00d4ff")
    sweep_d = svg_arc_path(rcx, rcy, radius, 320, 360)
    return f'''
    <g>
      <path d="{sweep_d}" fill="url(#radar-gradient)" fill-opacity="0.4"/>
      <line x1="{rcx}" y1="{rcy}" x2="{rcx}" y2="{rcy - radius}" stroke="{scan_color}" stroke-width="2" stroke-linecap="round"/>
      <circle cx="{rcx}" cy="{rcy - radius}" r="3" fill="{scan_color}" filter="url(#needle-glow)"/>
      <animateTransform attributeName="transform" type="rotate" from="0 {rcx} {rcy}" to="360 {rcx} {rcy}" dur="6s" repeatCount="indefinite"/>
    </g>'''

def _build_radar_labels_and_dots(sector_data, galaxy_arms, rcx, rcy, radius, theme):
    parts = []
    for sec in sector_data:
        mid_deg = (sec["start_deg"] + sec["end_deg"]) / 2
        mid_rad = math.radians(mid_deg - 90)
        label_r = radius + 22
        lx = rcx + label_r * math.cos(mid_rad)
        ly = rcy + label_r * math.sin(mid_rad)
        anchor = "middle" if abs(lx - rcx) < 5 else ("start" if lx > rcx else "end")

        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" fill="{sec["color"]}" font-size="10" font-family="monospace" text-anchor="{anchor}" dominant-baseline="middle">{esc(sec["name"])}</text>')
        parts.append(f'<text x="{lx:.1f}" y="{ly+12:.1f}" fill="{theme["text_faint"]}" font-size="8" font-family="monospace" text-anchor="{anchor}" dominant-baseline="middle">({sec["items"]})</text>')
    
    radii_cycle = [radius*0.4, radius*0.7, radius*0.9]
    for sec_i, sec in enumerate(sector_data):
        arm = galaxy_arms[sec_i]
        items = arm.get("items", [])
        for j, item in enumerate(items):
            usable_start, usable_end = sec["start_deg"] + 10, sec["end_deg"] - 10
            item_angle = (usable_start + usable_end) / 2 if len(items) == 1 else usable_start + (usable_end - usable_start) * j / (len(items) - 1)
            item_rad = math.radians(item_angle - 90)
            dot_r = radii_cycle[j % 3]
            dx, dy = rcx + dot_r * math.cos(item_rad), rcy + dot_r * math.sin(item_rad)
            pulse_begin = (item_angle / 360) * 6 - 0.3
            parts.append(f'<circle cx="{dx:.1f}" cy="{dy:.1f}" r="3" fill="{sec["color"]}" opacity="0.35"><animate attributeName="opacity" values="0.35;1.0;0.35" dur="6s" begin="{pulse_begin if pulse_begin > 0 else 0:.2f}s" repeatCount="indefinite"/></circle>')
    return "\n".join(parts)

def render(languages: dict, galaxy_arms: list, theme: dict, exclude: list, max_display: int) -> str:
    lang_data = calculate_language_percentages(languages, exclude, max_display)
    all_arm_colors = resolve_arm_colors(galaxy_arms, theme)

    left_x, start_y = 40, 85
    radius = 80
    rcx = 630
    
    # AJUSTE AQUI: rcy agora é calculado para ficar centralizado em relação à altura
    # Aumentamos o height total para dar respiro (padding) na parte de baixo
    lang_height = start_y + len(lang_data) * 32 + 40
    radar_center_ideal = 180 # Posição central vertical ideal
    height = max(350, lang_height, radar_center_ideal + radius + 50) 
    rcy = (height / 2) + 20 # Centraliza o radar com um pequeno offset para o título

    sector_data = []
    for i, arm in enumerate(galaxy_arms):
        sector_data.append({
            "name": arm["name"],
            "color": all_arm_colors[i],
            "items": len(arm.get("items", [])),
            "start_deg": i * 120 + 2,
            "end_deg": (i + 1) * 120 - 2,
        })

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}">
  <defs>
    <filter id="needle-glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="2" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
    <radialGradient id="radar-gradient" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="{theme.get('synapse_cyan', '#00d4ff')}" stop-opacity="0"/><stop offset="100%" stop-color="{theme.get('synapse_cyan', '#00d4ff')}" stop-opacity="0.3"/></radialGradient>
  </defs>
  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="15" ry="15" fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1.5"/>
  <g transform="translate(40, 45)"><rect width="3" height="15" fill="{theme['synapse_cyan']}" rx="1"/><text x="12" y="12" fill="{theme['text_faint']}" font-size="11" font-family="monospace" letter-spacing="3" font-weight="bold">LANGUAGE TELEMETRY</text></g>
  <g transform="translate(465, 45)"><rect width="3" height="15" fill="{theme['dendrite_violet']}" rx="1"/><text x="12" y="12" fill="{theme['text_faint']}" font-size="11" font-family="monospace" letter-spacing="3" font-weight="bold">FOCUS SECTORS</text></g>
  <line x1="425" y1="40" x2="425" y2="{height - 40}" stroke="{theme['star_dust']}" stroke-width="1" stroke-dasharray="5,5" opacity="0.3"/>
  {_build_language_bars(lang_data, theme, left_x, start_y)}
  <g opacity="0.9">
    {_build_radar_grid(rcx, rcy, [30, 55, 80], theme)}
    {_build_radar_sectors(sector_data, rcx, rcy, radius, theme)}
    {_build_radar_needle(rcx, rcy, radius, theme)}
    {_build_radar_labels_and_dots(sector_data, galaxy_arms, rcx, rcy, radius, theme)}
  </g>
</svg>'''
