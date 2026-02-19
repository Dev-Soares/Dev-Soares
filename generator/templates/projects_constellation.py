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
      <rect x="{card_x}" y="100" width="{card_width}" height="240" rx="25" fill="{color}" opacity="0.03" filter="url(#proj-glow-{i})"/>
      <rect x="{card_x}" y="100" width="{card_width}" height="240" rx="25" fill="url(#card-bg-{i})" stroke="{theme['star_dust']}" stroke-width="2"/>
      
      <g transform="translate(0, 145)">
          <circle cx="{card_cx}" cy="0" r="28" fill="none" stroke="{color}" stroke-width="1" stroke-dasharray="6,4" opacity="0.3">
            <animateTransform attributeName="transform" type="rotate" from="0 {card_cx} 0" to="360 {card_cx} 0" dur="15s" repeatCount="indefinite"/>
          </circle>
          <circle cx="{card_cx}" cy="0" r="10" fill="{color}" filter="url(#proj-glow-{i})"/>
          <circle cx="{card_cx}" cy="0" r="3" fill="#ffffff"/>
      </g>

      <text x="{card_cx}" y="210" fill="{theme['text_bright']}" font-size="19" font-weight="800" font-family="sans-serif" text-anchor="middle">{esc(repo_name)}</text>
      
      <g transform="translate(0, 15)">
          {f'<text x="{card_cx}" y="225" fill="{theme["text_dim"]}" font-size="13" font-family="sans-serif" text-anchor="middle">{esc(desc_lines[0])}</text>' if len(desc_lines) > 0 else ''}
          {f'<text x="{card_cx}" y="245" fill="{theme["text_dim"]}" font-size="13" font-family="sans-serif" text-anchor="middle">{esc(desc_lines[1])}</text>' if len(desc_lines) > 1 else ''}
      </g>

      <rect x="{card_cx - 50}" y="290" width="100" height="24" rx="12" fill="{color}" opacity="0.12"/>
      <text x="{card_cx}" y="306" fill="{color}" font-size="10" font-family="monospace" font-weight="bold" text-anchor="middle" letter-spacing="1">{esc(arm['name']).upper()}</text>
    </g>'''

def render(projects: list, galaxy_arms: list, theme: dict) -> str:
    all_arm_colors = resolve_arm_colors(galaxy_arms, theme)
    n = min(len(projects), 3)
    
    if n == 0:
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}"><rect width="100%" height="100%" fill="{theme["nebula"]}"/><text x="50%" y="50%" fill="{theme["text_faint"]}" text-anchor="middle" font-family="monospace">NO NODES DETECTED</text></svg>'

    card_width = 370 if n == 2 else 255
    gap = (WIDTH - (card_width * n)) / (n + 1)
    
    cards = []
    for i in range(n):
        proj = projects[i]
        arm_idx = proj.get("arm", 0) % len(galaxy_arms)
        cards.append(_build_project_card(i, proj, galaxy_arms[arm_idx], all_arm_colors[arm_idx], card_width, gap + i * (card_width + gap), theme))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>{_build_defs(n, card_width, gap, [all_arm_colors[p.get("arm",0)%len(galaxy_arms)] for p in projects[:n]], theme)}</defs>
  <rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="25" fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="2"/>
  {_build_starfield(n, WIDTH, HEIGHT, [all_arm_colors[p.get("arm",0)%len(galaxy_arms)] for p in projects[:n]], theme)}
  {_build_title_area(n, WIDTH, HEIGHT, theme)}
  {"".join(cards)}
</svg>'''
