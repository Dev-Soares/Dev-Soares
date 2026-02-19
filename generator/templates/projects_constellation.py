"""SVG template: Featured Systems / Projects Constellation (850x260)."""

from generator.utils import wrap_text, deterministic_random, esc, resolve_arm_colors

# Aumentamos a altura para 260 para dar mais respiro vertical entre os elementos
WIDTH, HEIGHT = 850, 260

def _build_defs(n, card_width, gap, card_colors, theme):
    """Build all defs (filters, gradients, clip paths, CSS)."""
    defs_parts = []

    # Glow filters per card - Intensificado para um visual mais premium
    for i in range(n):
        color = card_colors[i]
        defs_parts.append(f'''    <filter id="proj-glow-{i}" x="-80%" y="-80%" width="260%" height="260%">
      <feGaussianBlur stdDeviation="5" in="SourceGraphic" result="blur"/>
      <feFlood flood-color="{color}" flood-opacity="0.4" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>''')

    # Card background gradients - Mais profundo
    for i in range(n):
        color = card_colors[i]
        defs_parts.append(f'''    <linearGradient id="card-bg-{i}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{theme['star_dust']}" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="{theme['nebula']}" stop-opacity="0.95"/>
    </linearGradient>''')

    # Clip paths per card
    for i in range(n):
        card_x = gap + i * (card_width + gap)
        defs_parts.append(f'''    <clipPath id="card-clip-{i}">
      <rect x="{card_x}" y="70" width="{card_width}" height="160" rx="12" ry="12"/>
    </clipPath>''')

    defs_parts.append('''    <style>
      @keyframes card-appear {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
      }
      @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-5px); }
      }
    </style>''')

    return "\n".join(defs_parts)

def _build_starfield(n, width, height, card_colors, theme):
    stars = []
    layers = [
        {"prefix": "p-star", "count": 20, "margin": 10, "r": (0.3, 0.8), "o": (0.1, 0.3), "d": (4, 7)},
        {"prefix": "p-mstar", "count": 12, "margin": 15, "r": (0.6, 1.3), "o": (0.2, 0.5), "d": (3, 5)},
    ]
    for layer in layers:
        count, pfx = layer["count"], layer["prefix"]
        sx = deterministic_random(f"{pfx}-x", count, layer["margin"], width - layer["margin"])
        sy = deterministic_random(f"{pfx}-y", count, layer["margin"], height - layer["margin"])
        sr = deterministic_random(f"{pfx}-r", count, *layer["r"])
        so = deterministic_random(f"{pfx}-o", count, *layer["o"])
        sd = deterministic_random(f"{pfx}-d", count, *layer["d"])
        for i in range(count):
            fill = card_colors[i % n] if i % 5 == 0 else theme["text_dim"]
            stars.append(f'<circle cx="{sx[i]:.1f}" cy="{sy[i]:.1f}" r="{sr[i]:.1f}" fill="{fill}" opacity="{so[i]:.2f}"><animate attributeName="opacity" values="{so[i]:.2f};0.7;{so[i]:.2f}" dur="{sd[i]:.1f}s" repeatCount="indefinite"/></circle>')
    return "\n".join(stars)

def _build_title_area(n, width, height, theme):
    cyan = theme.get("synapse_cyan", "#00d4ff")
    return f'''
    <text x="35" y="45" fill="{theme['text_faint']}" font-size="12" font-family="monospace" letter-spacing="4" font-weight="bold">FEATURED SYSTEMS</text>
    <circle cx="235" cy="41" r="3" fill="{cyan}"><animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/></circle>
    <text x="{width - 35}" y="45" fill="{theme['text_faint']}" font-size="10" font-family="monospace" text-anchor="end" opacity="0.6">SYS v2.0 // {n} NODES ACTIVE</text>
    <line x1="35" y1="58" x2="{width - 35}" y2="58" stroke="{theme['star_dust']}" stroke-width="1" opacity="0.5"/>'''

def _build_project_card(i, proj, arm, color, card_width, card_x, theme):
    card_cx = card_x + card_width / 2
    repo_name = proj["repo"].split("/")[-1] if "/" in proj["repo"] else proj["repo"]
    desc = proj.get("description", "")
    max_chars = int(card_width / 8)
    desc_lines = wrap_text(desc, max_chars)
    delay = f"{i * 0.2}s"

    return f'''
    <g opacity="0" style="animation: card-appear 0.8s ease {delay} forwards">
      <rect x="{card_x}" y="75" width="{card_width}" height="155" rx="12" ry="12" fill="{color}" opacity="0.05" filter="url(#proj-glow-{i})"/>
      
      <rect x="{card_x}" y="75" width="{card_width}" height="155" rx="12" ry="12" fill="url(#card-bg-{i})" stroke="{theme['star_dust']}" stroke-width="1.5"/>
      
      <g transform="translate(0, -5)">
          <circle cx="{card_cx}" cy="110" r="16" fill="none" stroke="{color}" stroke-width="1" stroke-dasharray="4,4" opacity="0.4">
            <animateTransform attributeName="transform" type="rotate" from="0 {card_cx} 110" to="360 {card_cx} 110" dur="10s" repeatCount="indefinite"/>
          </circle>
          <circle cx="{card_cx}" cy="110" r="6" fill="{color}" filter="url(#proj-glow-{i})">
            <animate attributeName="r" values="5;7;5" dur="3s" repeatCount="indefinite"/>
          </circle>
          <circle cx="{card_cx}" cy="110" r="2" fill="#fff"/>
      </g>

      <text x="{card_cx}" y="145" fill="{theme['text_bright']}" font-size="15" font-weight="bold" font-family="sans-serif" text-anchor="middle">{esc(repo_name)}</text>
      
      <g transform="translate(0, 5)">
          {f'<text x="{card_cx}" y="165" fill="{theme["text_dim"]}" font-size="11" font-family="sans-serif" text-anchor="middle">{esc(desc_lines[0])}</text>' if len(desc_lines) > 0 else ''}
          {f'<text x="{card_cx}" y="180" fill="{theme["text_dim"]}" font-size="11" font-family="sans-serif" text-anchor="middle">{esc(desc_lines[1])}</text>' if len(desc_lines) > 1 else ''}
      </g>

      <rect x="{card_cx - 40}" y="200" width="80" height="18" rx="9" fill="{color}" opacity="0.1"/>
      <text x="{card_cx}" y="212" fill="{color}" font-size="9" font-family="monospace" font-weight="bold" text-anchor="middle">{esc(arm['name']).upper()}</text>
    </g>'''

def render(projects: list, galaxy_arms: list, theme: dict) -> str:
    all_arm_colors = resolve_arm_colors(galaxy_arms, theme)
    n = min(len(projects), 3)
    
    if n == 0:
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}"><rect width="100%" height="100%" rx="12" fill="{theme["nebula"]}"/><text x="50%" y="50%" fill="{theme["text_faint"]}" text-anchor="middle" font-family="monospace">NO SYSTEMS DETECTED</text></svg>'

    card_width = 360 if n == 2 else 240
    total_width = card_width * n
    gap = (WIDTH - total_width) / (n + 1)
    
    card_colors = [all_arm_colors[p.get("arm", 0) % len(galaxy_arms)] for p in projects[:n]]
    
    cards = []
    for i in range(n):
        card_x = gap + i * (card_width + gap)
        cards.append(_build_project_card(i, projects[i], galaxy_arms[projects[i].get("arm", 0) % len(galaxy_arms)], card_colors[i], card_width, card_x, theme))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>{_build_defs(n, card_width, gap, card_colors, theme)}</defs>
  <rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="15" fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1.5"/>
  {_build_starfield(n, WIDTH, HEIGHT, card_colors, theme)}
  {_build_title_area(n, WIDTH, HEIGHT, theme)}
  {"".join(cards)}
</svg>'''
