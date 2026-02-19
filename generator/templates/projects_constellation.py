"""SVG template: Featured Systems / Projects Constellation (850x320)."""

from generator.utils import wrap_text, deterministic_random, esc, resolve_arm_colors

# Altura aumentada para 320 para garantir o máximo de respiro vertical
WIDTH, HEIGHT = 850, 320

def _build_defs(n, card_width, gap, card_colors, theme):
    """Build all defs (filters, gradients, clip paths, CSS)."""
    defs_parts = []

    # Glow filters per card - Efeito neon para destacar os cards
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

    # Card background gradients
    for i in range(n):
        defs_parts.append(f'''    <linearGradient id="card-bg-{i}" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{theme['star_dust']}" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="{theme['nebula']}" stop-opacity="0.95"/>
    </linearGradient>''')

    # CSS para animação de entrada suave
    defs_parts.append('''    <style>
      @keyframes card-appear {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
      }
    </style>''')

    return "\n".join(defs_parts)

def _build_starfield(n, width, height, card_colors, theme):
    """Build a subtle star field background."""
    stars = []
    layers = [
        {"pfx": "p-star", "count": 20, "r": (0.3, 0.8), "o": (0.1, 0.3), "d": (4, 7)},
        {"pfx": "p-mstar", "count": 12, "r": (0.6, 1.3), "o": (0.2, 0.5), "d": (3, 5)},
    ]
    for layer in layers:
        count, pfx = layer["count"], layer["pfx"]
        sx = deterministic_random(f"{pfx}-x", count, 10, width - 10)
        sy = deterministic_random(f"{pfx}-y", count, 10, height - 10)
        sr = deterministic_random(f"{pfx}-r", count, *layer["r"])
        so = deterministic_random(f"{pfx}-o", count, *layer["o"])
        sd = deterministic_random(f"{pfx}-d", count, *layer["d"])
        for i in range(count):
            fill = card_colors[i % n] if i % 5 == 0 else theme["text_dim"]
            stars.append(f'<circle cx="{sx[i]:.1f}" cy="{sy[i]:.1f}" r="{sr[i]:.1f}" fill="{fill}" opacity="{so[i]:.2f}"><animate attributeName="opacity" values="{so[i]:.2f};0.7;{so[i]:.2f}" dur="{sd[i]:.1f}s" repeatCount="indefinite"/></circle>')
    return "\n".join(stars)

def _build_title_area(n, width, height, theme):
    """Build the section header with status info."""
    cyan = theme.get("synapse_cyan", "#00d4ff")
    return f'''
    <text x="40" y="50" fill="{theme['text_faint']}" font-size="12" font-family="monospace" letter-spacing="4" font-weight="bold">FEATURED SYSTEMS</text>
    <circle cx="240" cy="46" r="3" fill="{cyan}"><animate attributeName="opacity" values="1;0.3;1" dur="2s" repeatCount="indefinite"/></circle>
    <text x="{width - 40}" y="50" fill="{theme['text_faint']}" font-size="10" font-family="monospace" text-anchor="end" opacity="0.6">NODES ONLINE: {n}</text>
    <line x1="40" y1="65" x2="{width - 40}" y2="65" stroke="{theme['star_dust']}" stroke-width="1" opacity="0.5"/>'''

def _build_project_card(i, proj, arm, color, card_width, card_x, theme):
    """Build a single project card with expanded spacing."""
    card_cx = card_x + card_width / 2
    repo_name = proj["repo"].split("/")[-1] if "/" in proj["repo"] else proj["repo"]
    desc = proj.get("description", "")
    
    # Ajuste dinâmico de quebra de texto para o card
    max_chars = int(card_width / 8.5)
    desc_lines = wrap_text(desc, max_chars)
    delay = f"{i * 0.2}s"

    return f'''
    <g opacity="0" style="animation: card-appear 0.8s ease {delay} forwards">
      <rect x="{card_x}" y="85" width="{card_width}" height="200" rx="20" fill="{color}" opacity="0.05" filter="url(#proj-glow-{i})"/>
      
      <rect x="{card_x}" y="85" width="{card_width}" height="200" rx="20" fill="url(#card-bg-{i})" stroke="{theme['star_dust']}" stroke-width="2"/>
      
      <g transform="translate(0, 5)">
          <circle cx="{card_cx}" cy="125" r="22" fill="none" stroke="{color}" stroke-width="1" stroke-dasharray="4,4" opacity="0.4">
            <animateTransform attributeName="transform" type="rotate" from="0 {card_cx} 125" to="360 {card_cx} 125" dur="10s" repeatCount="indefinite"/>
          </circle>
          <circle cx="{card_cx}" cy="125" r="8" fill="{color}" filter="url(#proj-glow-{i})">
            <animate attributeName="r" values="7;9;7" dur="3s" repeatCount="indefinite"/>
          </circle>
          <circle cx="{card_cx}" cy="125" r="3" fill="#ffffff"/>
      </g>

      <text x="{card_cx}" y="175" fill="{theme['text_bright']}" font-size="17" font-weight="bold" font-family="sans-serif" text-anchor="middle">{esc(repo_name)}</text>
      
      <g transform="translate(0, 15)">
          {f'<text x="{card_cx}" y="190" fill="{theme["text_dim"]}" font-size="12" font-family="sans-serif" text-anchor="middle">{esc(desc_lines[0])}</text>' if len(desc_lines) > 0 else ''}
          {f'<text x="{card_cx}" y="208" fill="{theme["text_dim"]}" font-size="12" font-family="sans-serif" text-anchor="middle">{esc(desc_lines[1])}</text>' if len(desc_lines) > 1 else ''}
      </g>

      <rect x="{card_cx - 45}" y="245" width="90" height="22" rx="11" fill="{color}" opacity="0.1"/>
      <text x="{card_cx}" y="260" fill="{color}" font-size="10" font-family="monospace" font-weight="bold" text-anchor="middle">{esc(arm['name']).upper()}</text>
    </g>'''

def render(projects: list, galaxy_arms: list, theme: dict) -> str:
    """Render the projects constellation SVG."""
    all_arm_colors = resolve_arm_colors(galaxy_arms, theme)
    n = min(len(projects), 3)
    
    if n == 0:
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}"><rect width="100%" height="100%" rx="20" fill="{theme["nebula"]}"/><text x="50%" y="50%" fill="{theme["text_faint"]}" text-anchor="middle" font-family="monospace">NO ACTIVE PROJECTS FOUND</text></svg>'

    # Largura adaptativa para os cards
    card_width = 360 if n == 2 else 250
    total_width = card_width * n
    gap = (WIDTH - total_width) / (n + 1)
    
    cards = []
    for i in range(n):
        proj = projects[i]
        arm_idx = proj.get("arm", 0) % len(galaxy_arms)
        arm = galaxy_arms[arm_idx]
        color = all_arm_colors[arm_idx]
        card_x = gap + i * (card_width + gap)
        
        cards.append(_build_project_card(i, proj, arm, color, card_width, card_x, theme))

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>{_build_defs(n, card_width, gap, [all_arm_colors[p.get("arm",0)%len(galaxy_arms)] for p in projects[:n]], theme)}</defs>
  
  <rect x="0.5" y="0.5" width="{WIDTH-1}" height="{HEIGHT-1}" rx="20" fill="{theme['nebula']}" stroke="{theme['star_dust']}" stroke-width="1.5"/>
  
  {_build_starfield(n, WIDTH, HEIGHT, [all_arm_colors[p.get("arm",0)%len(galaxy_arms)] for p in projects[:n]], theme)}
  {_build_title_area(n, WIDTH, HEIGHT, theme)}
  
  {"".join(cards)}
</svg>'''
