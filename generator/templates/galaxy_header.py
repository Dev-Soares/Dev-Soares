"""SVG template: Galaxy Header — the signature spiral galaxy banner (850x450)."""

import math
from generator.utils import spiral_points, deterministic_random, esc, resolve_arm_colors

# ── Module-level constants ──
WIDTH, HEIGHT = 850, 450 
CENTER_X, CENTER_Y = 425, 225 
MAX_RADIUS = 170 
SPIRAL_TURNS = 0.85
NUM_POINTS = 30
X_SCALE, Y_SCALE = 1.6, 0.55 
START_ANGLES = [25, 150, 265]

def _build_glow_filters(galaxy_arms, arm_colors):
    glow_filters = []
    for i, arm in enumerate(galaxy_arms):
        color = arm_colors[i]
        glow_filters.append(
            f'    <filter id="star-glow-{i}" x="-100%" y="-100%" width="300%" height="300%">\n'
            f'      <feGaussianBlur stdDeviation="3" result="blur"/>\n'
            f'      <feFlood flood-color="{color}" flood-opacity="0.5" result="color"/>\n'
            f'      <feComposite in="color" in2="blur" operator="in" result="glow"/>\n'
            f'      <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>\n'
            f'    </filter>'
        )
    return "\n".join(glow_filters)

def _build_starfield(username, width, height, theme):
    star_layers = [
        {"count": 50, "label": "bg", "r": (0.3, 0.8), "o": (0.08, 0.3), "dur": (5.0, 9.0)},
        {"count": 25, "label": "mid", "r": (0.6, 1.2), "o": (0.15, 0.5), "dur": (3.5, 7.0)},
    ]
    stars = []
    for layer in star_layers:
        n, lbl = layer["count"], layer["label"]
        sx = deterministic_random(f"{username}_sx_{lbl}", n, 30, width - 30)
        sy = deterministic_random(f"{username}_sy_{lbl}", n, 30, height - 30)
        sr = deterministic_random(f"{username}_sr_{lbl}", n, *layer["r"])
        so = deterministic_random(f"{username}_so_{lbl}", n, *layer["o"])
        sd = deterministic_random(f"{username}_sd_{lbl}", n, *layer["dur"])
        for i in range(n):
            delay = f"{sd[i] * 0.3:.1f}s"
            stars.append(f'    <circle cx="{sx[i]:.1f}" cy="{sy[i]:.1f}" r="{sr[i]:.2f}" fill="#ffffff" opacity="{so[i]:.2f}" class="star-{lbl}" style="animation-delay: {delay}"/>')
    return "\n".join(stars)

def _build_tech_labels(galaxy_arms, arm_colors, all_arm_points, cx, cy):
    arm_dots = []
    for arm_idx, arm in enumerate(galaxy_arms):
        color, points, items = arm_colors[arm_idx], all_arm_points[arm_idx], arm.get("items", [])
        if not items: continue
        available = len(points) - 12
        spacing = max(1, available // len(items))
        for i, item in enumerate(items):
            pt_idx = min(10 + i * spacing, len(points) - 1)
            px, py = points[pt_idx]
            dx, dy = px - cx, py - cy
            dist = math.sqrt(dx * dx + dy * dy) or 1
            lx, ly = px + (dx/dist) * 35, py + (dy/dist) * 35
            anchor = "start" if dx > 30 else ("end" if dx < -30 else "middle")
            arm_dots.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{color}" opacity="0.8"/>')
            arm_dots.append(f'    <line x1="{px:.1f}" y1="{py:.1f}" x2="{lx:.1f}" y2="{ly:.1f}" stroke="{color}" stroke-width="1" opacity="0.2" stroke-dasharray="2 2"/>')
            arm_dots.append(f'    <text x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="{anchor}" fill="{color}" font-size="13" font-family="monospace" font-weight="900">{esc(item)}</text>')
    return "\n".join(arm_dots)

def _build_galaxy_core(cx, cy, theme, initial):
    return (
        f'    <circle cx="{cx}" cy="{cy}" r="65" fill="url(#core-haze-gradient)" opacity="0.4"/>\n'
        f'    <circle cx="{cx}" cy="{cy}" r="18" fill="{theme["nebula"]}" stroke="{theme["star_dust"]}" stroke-width="1"/>\n'
        f'    <circle cx="{cx}" cy="{cy}" r="6" fill="{theme["synapse_cyan"]}" filter="url(#core-bright-glow)"/>\n'
        f'    <text x="{cx}" y="{cy + 7}" text-anchor="middle" fill="{theme["synapse_cyan"]}" font-size="20" font-weight="bold" font-family="monospace">{initial}</text>'
    )

def render(config: dict, theme: dict, galaxy_arms: list, projects: list) -> str:
    """Esta é a função que o erro dizia estar faltando."""
    username, profile = config.get("username", "user"), config.get("profile", {})
    name, tagline, philosophy = profile.get("name", username), profile.get("tagline", ""), profile.get("philosophy", "")
    initial = name[0].upper() if name else "?"
    arm_colors = resolve_arm_colors(galaxy_arms, theme)
    
    all_arm_points = [
        spiral_points(CENTER_X, CENTER_Y, START_ANGLES[i % 3], NUM_POINTS, MAX_RADIUS, SPIRAL_TURNS, X_SCALE, Y_SCALE) 
        for i in range(len(galaxy_arms))
    ]

    stars = _build_starfield(username, WIDTH, HEIGHT, theme)
    arm_dots = _build_tech_labels(galaxy_arms, arm_colors, all_arm_points, CENTER_X, CENTER_Y)
    core = _build_galaxy_core(CENTER_X, CENTER_Y, theme, initial)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <style>
      .star-bg {{ animation: twinkle 8s infinite; }}
      @keyframes twinkle {{ 0%, 100% {{ opacity: 0.1; }} 50% {{ opacity: 0.4; }} }}
    </style>
    <filter id="core-bright-glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="6"/></filter>
    <radialGradient id="core-haze-gradient"><stop offset="0%" stop-color="{theme['synapse_cyan']}" stop-opacity="0.6"/><stop offset="100%" stop-color="{theme['synapse_cyan']}" stop-opacity="0"/></radialGradient>
    {_build_glow_filters(galaxy_arms, arm_colors)}
  </defs>
  <rect width="100%" height="100%" rx="20" fill="{theme['void']}"/>
  {stars}
  {arm_dots}
  {core}
  <text x="{CENTER_X}" y="70" text-anchor="middle" fill="{theme['text_bright']}" font-size="36" font-weight="900" font-family="sans-serif">{esc(name)}</text>
  <text x="{CENTER_X}" y="105" text-anchor="middle" fill="{theme['text_dim']}" font-size="18" font-family="sans-serif" font-weight="600">{esc(tagline)}</text>
  <text x="{CENTER_X}" y="{HEIGHT - 50}" text-anchor="middle" fill="{theme['text_faint']}" font-size="14" font-family="monospace" font-style="italic">{esc(philosophy)}</text>
</svg>'''
