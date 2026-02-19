"""SVG template: Featured Systems / Projects Constellation (850x380)."""

from generator.utils import wrap_text, deterministic_random, esc, resolve_arm_colors

# Altura aumentada para 380px para garantir distanciamento total entre elementos
WIDTH, HEIGHT = 850, 380

def _build_defs(n, card_width, gap, card_colors, theme):
    """Build all defs (filters, gradients, clip paths, CSS)."""
    defs_parts = []

    for i in range(n):
        color = card_colors[i]
        defs_parts.append(f'''    <filter id="proj-glow-{i}" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="6" in="SourceGraphic" result="blur"/>
      <feFlood flood-color="{color}" flood-opacity="0.3" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>''')

    for i in range(n):
        defs_parts.append(f'''    <linearGradient id="card-bg-{i}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{theme['star_dust']}" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="{theme['nebula']}" stop-opacity="0.98"/>
    </linearGradient>''')

    defs_parts.append('''    <style>
      @keyframes card-appear {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
      }
    </style>''')
    return "\n".join(defs_parts)

def _build_starfield(n, width, height, card_colors, theme):
    stars = []
    sx = deterministic_random("p-x", 30, 10, width - 10)
    sy = deterministic_random("p-y", 30, 10, height - 10)
    for i in range(30):
        fill = card_colors[i % n] if i % 6 == 0 else theme["text_dim"]
        stars.append(f'<circle cx="{sx[i]:.1f}" cy="{sy[i]:.1f}" r="0.8" fill="{fill}" opacity="0.3"/>')
    return "\n".join(stars)

def _build_title_area(n, width, height, theme):
    cyan = theme.get("synapse_cyan", "#00d4ff")
    return f'''
    <g transform="translate(45, 55)">
        <text fill="{theme['text_faint']}" font-size="13" font-family="monospace" letter-spacing="5" font-weight="bold">FEATURED SYSTEMS</text>
        <circle cx="255" cy="-4" r="3" fill="{cyan}"><animate attributeName="opacity" values="1;0.2;1" dur="2.5s" repeatCount="indefinite"/></circle>
        <line x1="0" y1="20" x2="{width - 90}" y2="20" stroke="{theme['star_dust']}" stroke-width="1.5" opacity="0.4"/>
    </g>'''

def _build_project_card(i, proj, arm, color, card_width, card_x, theme):
    """Build a single project card with extreme spacing."""
    card_cx = card_x + card_width / 2
    repo_name = proj["repo"].split("/")[-1] if "/" in proj["repo"] else proj["repo"]
    desc = proj.get("description", "")
    
    max_chars = int(card_width / 9)
    desc_lines = wrap_text(desc, max_chars)
    delay = f"{i * 0.25}s"

    return f'''
    <g opacity="0" style="animation: card-appear 1s ease {delay} forwards">
