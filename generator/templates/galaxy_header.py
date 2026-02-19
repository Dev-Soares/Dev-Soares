"""SVG template: Galaxy Header — the signature spiral galaxy banner (850x420)."""

import math
from generator.utils import spiral_points, deterministic_random, esc, resolve_arm_colors

# ── Module-level constants ──
# Altura ampliada significativamente para criar margens verticais generosas
WIDTH, HEIGHT = 850, 420 
# Centro deslocado para baixo para dar espaço ao título no topo
CENTER_X, CENTER_Y = 425, 215 
# Raio reduzido para afastar os braços e labels das bordas laterais
MAX_RADIUS = 180 
SPIRAL_TURNS = 0.85
NUM_POINTS = 30
# Escalas ajustadas para uma espiral mais aberta e centralizada
X_SCALE, Y_SCALE = 1.65, 0.52 
START_ANGLES = [25, 150, 265]


def _build_glow_filters(galaxy_arms, arm_colors):
    """Build the star glow filters, one per arm."""
    glow_filters = []
    for i, arm in enumerate(galaxy_arms):
        color = arm_colors[i]
        glow_filters.append(
            f'    <filter id="star-glow-{i}" x="-100%" y="-100%" width="300%" height="300%">\n'
            f'      <feGaussianBlur stdDeviation="3" result="blur"/>\n'
            f'      <feFlood flood-color="{color}" flood-opacity="0.5" result="color"/>\n'
            f'      <feComposite in="color" in2="blur" operator="in" result="glow"/>\n'
            f'      <feMerge>\n'
            f'        <feMergeNode in="glow"/>\n'
            f'        <feMergeNode in="SourceGraphic"/>\n'
            f'      </feMerge>\n'
            f'    </filter>'
        )
    return "\n".join(glow_filters)


def _build_starfield(username, width, height, theme):
    """Build all 3 star depth layers."""
    star_layers = [
        {"count": 50, "label": "bg", "r_min": 0.3, "r_max": 0.8, "o_min": 0.08, "o_max": 0.3, "dur_min": 5.0, "dur_max": 9.0},
        {"count": 25, "label": "mid", "r_min": 0.6, "r_max": 1.2, "o_min": 0.15, "o_max": 0.5, "dur_min": 3.5, "dur_max": 7.0},
        {"count": 15, "label": "fg", "r_min": 1.0, "r_max": 1.8, "o_min": 0.4, "o_max": 0.7, "dur_min": 2.0, "dur_max": 4.5},
    ]

    stars = []
    for layer in star_layers:
        n, lbl = layer["count"], layer["label"]
        sx = deterministic_random(f"{username}_sx_{lbl}", n, 20, width - 20)
        sy = deterministic_random(f"{username}_sy_{lbl}", n, 20, height - 20)
        sr = deterministic_random(f"{username}_sr_{lbl}", n, layer["r_min"], layer["r_max"])
        so = deterministic_random(f"{username}_so_{lbl}", n, layer["o_min"], layer["o_max"])
        sd = deterministic_random(f"{username}_sd_{lbl}", n, layer["dur_min"], layer["dur_max"])

        accent_colors = {0: theme.get("synapse_cyan", "#00d4ff"), 4: theme.get("dendrite_violet", "#a78bfa"), 8: theme.get("axon_amber", "#ffb020")}
        for i in range(n):
            fill = accent_colors.get(i % 12, "#ffffff")
            delay = f"{sd[i] * 0.3:.1f}s"
            stars.append(f'    <circle cx="{sx[i]:.1f}" cy="{sy[i]:.1f}" r="{sr[i]:.2f}" fill="{fill}" opacity="{so[i]:.2f}" class="star-{lbl}" style="animation-delay: {delay}"/>')
    return "\n".join(stars)


def _build_nebulae(cx, cy, theme):
    """Return the outer_nebula and inner_nebula SVG strings."""
    outer_nebula = (
        f'    <circle cx="{cx - 200}" cy="{cy - 50}" r="150" fill="{theme["dendrite_violet"]}" opacity="0.015" filter="url(#nebula-outer)"/>\n'
        f'    <circle cx="{cx + 220}" cy="{cy + 30}" r="130" fill="{theme["axon_amber"]}" opacity="0.012" filter="url(#nebula-outer)"/>\n'
        f'    <circle cx="{cx}" cy="{cy + 60}" r="180" fill="{theme["synapse_cyan"]}" opacity="0.01" filter="url(#nebula-outer)"/>'
    )
    inner_nebula = (
        f'    <circle cx="{cx}" cy="{cy}" r="90" fill="{theme["synapse_cyan"]}" opacity="0.04" filter="url(#nebula-inner)"/>\n'
        f'    <circle cx="{cx - 80}" cy="{cy - 30}" r="70" fill="{theme["dendrite_violet"]}" opacity="0.035" filter="url(#nebula-inner)"/>\n'
        f'    <circle cx="{cx + 90}" cy="{cy + 25}" r="65" fill="{theme["axon_amber"]}" opacity="0.03" filter="url(#nebula-inner)"/>'
    )
    return outer_nebula, inner_nebula


def _build_shooting_stars():
    """Build the shooting star lines."""
    shoot_data = [(100, 80, 250, 100, 6), (700, 70, 200, 90, 8), (350, 350, 180, 70, 7)]
    shoot_stars = []
    for idx, (sx_pos, sy_pos, tx, ty, dur) in enumerate(shoot_data):
        shoot_stars.append(f'    <line x1="{sx_pos}" y1="{sy_pos}" x2="{sx_pos + 20}" y2="{sy_pos + 5}" stroke="url(#shoot-grad)" stroke-width="1.2" stroke-linecap="round" class="shooting-star" style="animation-delay: {idx * 2.5}s; --shoot-tx: {tx}px; --shoot-ty: {ty}px; animation-duration: {dur}s"/>')
    return "\n".join(shoot_stars)


def _points_to_path(points):
    """Build a quadratic Bezier SVG path string."""
    d = f"M {points[0][0]:.1f} {points[0][1]:.1f}"
    for j in range(1, len(points)):
        px, py = points[j - 1]
        x, y = points[j]
        cpx, cpy = (px + x) / 2, (py + y) / 2
        d += f" Q {px:.1f} {py:.1f} {cpx:.1f} {cpy:.1f}"
    d += f" L {points[-1][0]:.1f} {points[-1][1]:.1f}"
    return d


def _build_spiral_arms(galaxy_arms, arm_colors, all_arm_points):
    """Build arm paths and particles."""
    arm_paths, arm_particles = [], []
    opacity_steps, width_steps = [0.50, 0.40, 0.30, 0.20], [2.2, 1.9, 1.6, 1.3]

    for arm_idx, arm in enumerate(galaxy_arms):
        color, points = arm_colors[arm_idx], all_arm_points[arm_idx]
        if len(points) < 2: continue
        full_path_d = _points_to_path(points)
        pts_per_seg = len(points) // 4
        for seg in range(4):
            start_i = seg * pts_per_seg
            end_i = min(start_i + pts_per_seg + 1, len(points))
            seg_pts = points[start_i:end_i]
            if len(seg_pts) < 2: continue
            seg_d = _points_to_path(seg_pts)
            op, sw = opacity_steps[seg], width_steps[seg]
            arm_paths.append(f'    <path d="{seg_d}" fill="none" stroke="{color}" stroke-width="{sw:.1f}" opacity="{op:.2f}" stroke-linecap="round"><animate attributeName="opacity" values="{op - 0.1:.2f};{op + 0.1:.2f};{op - 0.1:.2f}" dur="8s" begin="{arm_idx}s" repeatCount="indefinite"/></path>')
        for p_idx in range(2):
            delay = arm_idx * 4 + p_idx * 6
            arm_particles.append(f'    <circle r="1.8" fill="{color}" opacity="0.6"><animateMotion dur="12s" begin="{delay}s" repeatCount="indefinite" path="{full_path_d}"/><animate attributeName="opacity" values="0;0.7;0.3;0" dur="12s" begin="{delay}s" repeatCount="indefinite"/></circle>')
    return "\n".join(arm_paths), "\n".join(arm_particles)


def _build_tech_labels(galaxy_arms, arm_colors, all_arm_points, cx, cy):
    """Build tech dots and large labels with extra padding."""
    arm_dots = []
    for arm_idx, arm in enumerate(galaxy_arms):
        color, points, items = arm_colors[arm_idx], all_arm_points[arm_idx], arm.get("items", [])
        if not items: continue
        available = len(points) - 10
        spacing = max(1, available // len(items))
        for i, item in enumerate(items):
            pt_idx = min(8 + i * spacing, len(points) - 1)
            px, py = points[pt_idx]
            dx, dy = px - cx, py - cy
            dist = math.sqrt(dx * dx + dy * dy) or 1
            nx, ny = dx / dist, dy / dist
            # Distância da label aumentada para 28px para evitar colisão com os braços
            label_x, label_y = px + nx * 28, py + ny * 28
            anchor = "start" if dx > 30 else ("end" if dx < -30 else "middle")

            arm_dots.append(f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="3.5" fill="{color}" opacity="0.85"><animate attributeName="opacity" values="0.85;1;0.85" dur="5s" begin="{i * 0.7}s" repeatCount="indefinite"/></circle>')
            arm_dots.append(f'    <line x1="{px:.1f}" y1="{py:.1f}" x2="{label_x:.1f}" y2="{label_y:.1f}" stroke="{color}" stroke-width="0.8" opacity="0.3" stroke-dasharray="2 2"/>')
            # Font-size aumentado para 12 e peso extra negrito para máxima visibilidade
            arm_dots.append(f'    <text x="{label_x:.1f}" y="{label_y + 4:.1f}" text-anchor="{anchor}" fill="{color}" font-size="12" font-family="monospace" font-weight="900" opacity="0.2" filter="url(#label-glow)">{esc(item)}</text>')
            arm_dots.append(f'    <text x="{label_x:.1f}" y="{label_y + 4:.1f}" text-anchor="{anchor}" fill="{color}" font-size="12" font-family="monospace" font-weight="900" opacity="1">{esc(item)}</text>')
    return "\n".join(arm_dots)


def _build_galaxy_core(cx, cy, theme, initial):
    """Build the expanded core layers."""
    return (
        f'    <circle cx="{cx}" cy="{cy}" r="60" fill="url(#core-haze-gradient)" opacity="0.4"/>\n'
        f'    <circle cx="{cx}" cy="{cy}" r="35" fill="url(#core-inner-gradient)" opacity="0.6"/>\n'
        f'    <ellipse cx="{cx}" cy="{cy}" rx="30" ry="26" fill="none" stroke="{theme["synapse_cyan"]}" stroke-width="1.8" opacity="0.6" stroke-dasharray="6 4" class="core-ring"/>\n'
        f'    <circle cx="{cx}" cy="{cy}" r="22" fill="none" stroke="{theme["dendrite_violet"]}" stroke-width="1.2" opacity="0.5" class="core-ring-inner"/>\n'
        f'    <circle cx="{cx}" cy="{cy}" r="16" fill="{theme["nebula"]}" stroke="{theme["star_dust"]}" stroke-width="0.8"/>\n'
        f'    <circle cx="{cx}" cy="{cy}" r="5" fill="{theme["synapse_cyan"]}" filter="url(#core-bright-glow)" opacity="1"/>\n'
        f'    <text x="{cx}" y="{cy + 7}" text-anchor="middle" fill="{theme["synapse_cyan"]}" font-size="18" font-weight="bold" font-family="monospace">{initial}</text>'
    )


def render(config: dict, theme: dict, galaxy_arms: list, projects: list) -> str:
    """Render the spacious galaxy header."""
    username, profile = config.get("username", "user"), config.get("profile", {})
    name, tagline, philosophy = profile.get("name", username), profile.get("tagline", ""), profile.get("philosophy", "")
    initial = name[0].upper() if name else "?"
    arm_colors = resolve_arm_colors(galaxy_arms, theme)
    all_arm_points = [spiral_points(CENTER_X, CENTER_Y, START_ANGLES[i % 3], NUM_POINTS, MAX_RADIUS, SPIRAL_TURNS, X_SCALE, Y_SCALE) for i in range(len(galaxy_arms))]

    glow_filters = _build_glow_filters(galaxy_arms, arm_colors)
    stars_str = _build_starfield(username, WIDTH, HEIGHT, theme)
    outer_nebula, inner_nebula = _build_nebulae(CENTER_X, CENTER_Y, theme)
    shoot_stars_str = _build_shooting_stars()
    arm_paths, arm_particles = _build_spiral_arms(galaxy_arms, arm_colors, all_arm_points)
    arm_dots = _build_tech_labels(galaxy_arms, arm_colors, all_arm_points, CENTER_X, CENTER_Y)
    core = _build_galaxy_core(CENTER_X, CENTER_Y, theme, initial)

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
  <defs>
    <style>
      .star-bg {{ animation: twinkle-slow 7s ease-in-out infinite; }}
      .star-mid {{ animation: twinkle-mid 5s ease-in-out infinite; }}
      .star-fg {{ animation: twinkle-fast 3s ease-in-out infinite; }}
      @keyframes twinkle-slow {{ 0%, 100% {{ opacity: 0.08; }} 50% {{ opacity: 0.3; }} }}
      @keyframes twinkle-mid {{ 0%, 100% {{ opacity: 0.15; }} 50% {{ opacity: 0.5; }} }}
      @keyframes twinkle-fast {{ 0%, 100% {{ opacity: 0.4; }} 50% {{ opacity: 0.8; }} }}
      .core-ring {{ animation: pulse-core 3s ease-in-out infinite; }}
      .core-ring-inner {{ animation: pulse-core 3s ease-in-out infinite 1.5s; }}
      @keyframes pulse-core {{ 0%, 100% {{ stroke-opacity: 0.3; transform: scale(1); transform-origin: {CENTER_X}px {CENTER_Y}px; }} 50% {{ stroke-opacity: 0.8; transform: scale(1.08); transform-origin: {CENTER_X}px {CENTER_Y}px; }} }}
      .shooting-star {{ opacity: 0; animation: shoot linear infinite; }}
      @keyframes shoot {{ 0% {{ opacity: 0; transform: translate(0, 0); }} 5% {{ opacity: 0.9; }} 15% {{ opacity: 0.6; transform: translate(var(--shoot-tx), var(--shoot-ty)); }} 100% {{ opacity: 0; }} }}
    </style>
    <filter id="nebula-outer"><feGaussianBlur stdDeviation="80"/></filter>
    <filter id="nebula-inner"><feGaussianBlur stdDeviation="40"/></filter>
    <filter id="label-glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.5" result="blur"/></filter>
    <filter id="core-bright-glow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="5"/></filter>
    <radialGradient id="core-haze-gradient" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="{theme['synapse_cyan']}" stop-opacity="0.5"/><stop offset="100%" stop-color="{theme['synapse_cyan']}" stop-opacity="0"/></radialGradient>
    <radialGradient id="core-inner-gradient" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#ffffff" stop-opacity="0.6"/><stop offset="100%" stop-color="{theme['synapse_cyan']}" stop-opacity="0"/></radialGradient>
    <linearGradient id="shoot-grad" x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stop-color="#ffffff" stop-opacity="0.8"/><stop offset="100%" stop-color="#ffffff" stop-opacity="0"/></linearGradient>
    {glow_filters}
  </defs>
  <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="16" ry="16" fill="{theme['void']}"/>
  {outer_nebula}{stars_str}{inner_nebula}{shoot_stars_str}{arm_paths}{arm_particles}{arm_dots}{core}
  <text x="{CENTER_X}" y="55" text-anchor="middle" fill="{theme['text_bright']}" font-size="32" font-weight="900" font-family="sans-serif">{esc(name)}</text>
  <text x="{CENTER_X}" y="85" text-anchor="middle" fill="{theme['text_dim']}" font-size="16" font-family="sans-serif" font-weight="600">{esc(tagline)}</text>
  <text x="{CENTER_X}" y="{HEIGHT - 30}" text-anchor="middle" fill="{theme['text_faint']}" font-size="13" font-family="monospace" font-style="italic">{esc(philosophy)}</text>
</svg>'''
