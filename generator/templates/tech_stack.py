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
    """Re-definindo a função que estava faltando no seu arquivo anterior."""
    parts = []
    for sec in sector_data:
        mid_deg = (sec["start_deg"] + sec["end_deg"]) / 2
        mid_rad = math.radians(mid_deg - 90)
        label_r = radius + 22
        lx = rcx + label_r * math.cos(mid_rad)
        ly = rcy + label_r * math.sin(mid_rad)
        anchor = "middle" if abs(lx - rcx) < 5 else ("start" if lx > rcx else "end")

        parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" fill="{sec["color"]}" font-size="10" font-family="monospace" text-anchor="{anchor}" dominant-baseline="middle">{esc(sec["name"])}</text>')
        parts.append(f'<text x="{lx:.1f}" y="{ly+12:.1f}" fill="{theme["text_faint"]}" font-size="8" font-family="monospace" text-anchor="{anchor}" dominant-baseline="middle">({sec
