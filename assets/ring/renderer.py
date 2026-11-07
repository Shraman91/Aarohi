import os, sys, time, shutil
import numpy as np

TAU = 2 * np.pi
# Extended 12-step ramp for finer metallic and diamond contrast
RAMP = np.array(list(" .':-=+*#%@M"))
SS = 2                                    # 2x2 supersampling
rng = np.random.default_rng(7)

# ------------------------------------------------------------------ helpers
def smooth(k):
    k = np.clip(k, 0, 1); return k * k * (3 - 2 * k)

def unit(v): 
    v = np.asarray(v, float); return v / np.linalg.norm(v)

def blur(a, r, axis):                     
    pad = [(0, 0)] * a.ndim; pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad), axis=axis); n = a.shape[axis]
    return (np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis) - np.take(c, np.arange(n), axis)) / (2 * r + 1)

# ------------------------------------------------------------------ deterministic geometry
def band(R=0.86, r=0.082, na=420, nb=90):
    a, b = [x.ravel() for x in np.meshgrid(np.linspace(0, TAU, na, endpoint=False),
                                           np.linspace(0, TAU, nb, endpoint=False))]
    nor = np.stack([np.cos(b) * np.cos(a), np.cos(b) * np.sin(a), np.sin(b)], 1)
    # Tapered cathedral band
    taper = 1.0 + 0.14 * np.sin(a)
    r_eff = r * taper[:, None]
    p = np.stack([R * np.cos(a), R * np.sin(a), np.zeros_like(a)], 1) + r_eff * nor * np.array([1.0, 1.0, 1.15])
    d = np.abs((a - np.pi / 2 + np.pi) % TAU - np.pi) / np.pi      # 0 at top .. 1 at bottom
    n = len(a)
    return p, nor, np.zeros(n, int), 0.20 + 1.6 * (1.0 - d), np.zeros(n)

def facet(tri, res=28):
    a, b, c = map(np.array, tri)
    u, v = [x.ravel() for x in np.meshgrid(np.linspace(0, 1, res), np.linspace(0, 1, res))]
    keep = u + v <= 1.0
    u, v = u[keep], v[keep]
    nrm = np.cross(b - a, c - a); nrm /= np.linalg.norm(nrm)
    pts = a + u[:, None] * (b - a) + v[:, None] * (c - a)
    return pts, nrm

def edge_line(p1, p2, n_pts=45):
    p1, p2 = np.asarray(p1, float), np.asarray(p2, float)
    t = np.linspace(0, 1, n_pts)[:, None]
    pts = p1 + t * (p2 - p1)
    mid = 0.5 * (p1 + p2)
    nrm = unit(mid - np.array([0, 1.15, 0]))
    return pts, np.tile(nrm, (n_pts, 1))

def gem(cy=1.18, girdle=0.50, table=0.28, crown=0.22, depth=0.45, m=16):
    # Enlarged, classic round-brilliant cut with explicit facet-edge highlights for maximum visibility
    ctr = np.array([0, cy, 0.0]); P, N, F = [], [], []
    for i in range(m):
        a0, a1 = TAU * i / m, TAU * (i + 1) / m
        g0 = [girdle * np.cos(a0), cy, girdle * np.sin(a0)]
        g1 = [girdle * np.cos(a1), cy, girdle * np.sin(a1)]
        t0 = [table * np.cos(a0), cy + crown, table * np.sin(a0)]
        t1 = [table * np.cos(a1), cy + crown, table * np.sin(a1)]
        top, cul = [0, cy + crown, 0], [0, cy - depth, 0]
        
        # 1. Flat facets with distinct normals (creates the flashing gem look)
        for idx_f, tri in enumerate([(g0, g1, t0), (g1, t1, t0), (t0, t1, top), (g0, cul, g1)]):
            p, nrm = facet(tri, res=28)
            if np.dot(nrm, np.mean(tri, 0) - ctr) < 0: nrm = -nrm        
            P.append(p); N.append(np.tile(nrm, (len(p), 1)))
            # High-contrast alternating facet phases so neighboring facets contrast sharply
            F.append(np.full(len(p), ((i * 7 + idx_f * 3) % (m * 4)) / (m * 4)))
            
        # 2. Crisp wireframe ridges along facet boundaries (F = -1 flags bright facet edges)
        for e1, e2 in [(g0, g1), (t0, t1), (g0, t0), (g1, t0), (g0, cul)]:
            ep, en = edge_line(e1, e2, n_pts=36)
            P.append(ep); N.append(en); F.append(np.full(len(ep), -1.0))

    P, N, F = map(np.concatenate, (P, N, F))
    order = 2.0 + 0.85 * (P[:, 1] - (cy - depth)) / (crown + depth)
    return P, N, np.ones(len(P), int), order, F

def prongs(cy=1.18, girdle=0.50, nu=50, nphi=18):
    P, N = [], []
    # 4 sculpted claw prongs hugging the wider diamond girdle
    for k in range(4):
        a = TAU * (k + 0.5) / 4
        base = np.array([0.82 * np.cos(a), 0.82 * np.sin(a), 0.0])
        tip = np.array([(girdle + 0.02) * np.cos(a), cy + 0.07, (girdle + 0.02) * np.sin(a)])
        u, phi = [x.ravel() for x in np.meshgrid(np.linspace(0, 1, nu), np.linspace(0, TAU, nphi, endpoint=False))]
        d = (tip - base) / np.linalg.norm(tip - base)
        s = np.cross(d, [0, 0, 1.0]); s /= np.linalg.norm(s)
        w = np.cross(s, d)
        nrm = np.cos(phi)[:, None] * s + np.sin(phi)[:, None] * w
        curve = np.sin(u * np.pi)[:, None] * np.array([0.04 * np.cos(a), 0.01, 0.04 * np.sin(a)])
        pts = base + u[:, None] * (tip - base) + curve + nrm * 0.020
        P.append(pts); N.append(nrm)

    P, N = np.concatenate(P), np.concatenate(N)
    order = 1.65 + 0.45 * (P[:, 1] - 0.6) / 0.7
    return P, N, np.full(len(P), 2), order, np.zeros(len(P))

parts = [band(), gem(), prongs()]
P0, N0, KIND, TAU_I, FPH = [np.concatenate(x) for x in zip(*parts)]
P0[:, 1] -= 0.18                                           # Center the ring vertically
SV = rng.normal(size=(len(P0), 3)) * 0.42                  # Gentle scatter vector for intro

# More glints concentrated on the diamond
GL = np.concatenate([rng.choice(np.flatnonzero(KIND == 1), 60, replace=False),
                     rng.choice(np.flatnonzero(KIND == 0), 14, replace=False)])
GPH, GT = rng.uniform(0, TAU, len(GL)), rng.uniform(1.2, 2.5, len(GL))

OB_N, OB_TR = 68, 7                                         
ob_th, ob_ph = rng.uniform(0, TAU, (2, OB_N)); ob_r = rng.uniform(1.18, 1.50, OB_N); ob_tl = rng.uniform(-1, 1, OB_N)
ob_w = rng.choice([-1, 1], OB_N) * rng.uniform(.5, 1.0, OB_N)

L1 = unit([0.15, 0.82, 0.55])
L3 = unit([-0.6, -0.3, 0.7])                               

def rot(yaw, tilt):
    cy, sy, cx, sx = np.cos(yaw), np.sin(yaw), np.cos(tilt), np.sin(tilt)
    return np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]]) @ np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])

# ------------------------------------------------------------------ Typography
TOP_BANNER = [
    r"          _ _ _                            _          ",
    r"         (_) | |                          | |         ",
    r"__      ___ _| |    _   _  ___  _   _     | |__   ___ ",
    r"\ \ /\ / / | | |   | | | |/ _ \| | | |    | '_ \ / _ \ ",
    r" \ V  V /| | | |   | |_| | (_) | |_| |    | |_) |  __/",
    r"  \_/\_/ |_|_|_|    \__, |\___/ \__,_|    |_.__/ \___|",
    r"                     __/ |                            ",
    r"                    |___/                             "
]

BOT_BANNER = [
    r" __  __  _____  _   _  _____  ___  ",
    r"|  \/  ||_   _|| \ | ||  ___||__ \ ",
    r"| |\/| |  | |  |  \| || |__     ) |",
    r"| |  | |  | |  | . ` ||  __|   / / ",
    r"| |  | | _| |_ | |\  || |___  |_|  ",
    r"|_|  |_||_____||_| \_||_____| (_)  "
]

# ------------------------------------------------------------------ render
def render(t, W, H):
    s = 0.68 * min(W / 3.2, 2 * H / 3.2)
    
    R = rot(0.65 * t, -0.26 + 0.05 * np.sin(0.5 * t))
    bob = 0.025 * np.sin(1.2 * t)
    ease = smooth((t - TAU_I) / 0.75)
    sweep = -1.5 + 3.4 * ((t * 0.38) % 1.0)                       
    L2 = unit([np.cos(0.9 * t), 0.5, np.sin(0.9 * t)])

    i0 = np.flatnonzero(ease > 0.002)
    pos = (P0[i0] + SV[i0] * ((1 - ease[i0]) ** 2)[:, None]) @ R.T; n = N0[i0] @ R.T
    # Keep all diamond points (KIND == 1) so internal pavilion reflections shine through like a real gem
    keep = (KIND[i0] >= 1) | (n[:, 2] > -0.15)                    
    idx, pos, n = i0[keep], pos[keep], n[keep]; pos[:, 1] += bob
    ks, nz = KIND[idx], np.clip(n[:, 2], 0, 1)
    
    streak = np.exp(-(((pos[:, 0] * .85 + pos[:, 1] * .5) - sweep) / 0.11) ** 2)
    
    # Platinum band shading (slightly toned down so the diamond pops as the brightest centerpiece)
    diff1 = np.clip(n @ L1, 0, 1)
    spec1 = diff1 ** 12
    rim = (1 - nz) ** 3.5
    lum = 0.12 + 0.38 * diff1 + 0.32 * spec1 + 0.20 * np.clip(n @ L3, 0, 1) + 0.28 * rim + 0.60 * streak
    col = np.ones((len(idx), 3))
    
    # High-visibility, crystalline diamond shading
    g = ks == 1
    if g.any():
        ng, fp = n[g], FPH[idx][g]
        is_edge = fp < 0
        # Use abs() dot product so internal back-facets reflect light (total internal reflection)
        sp1 = np.abs(ng @ L1) ** 2.5
        sp2 = np.abs(ng @ L2) ** 4.0
        fire = (0.5 + 0.5 * np.sin(10 * (ng @ L2) + 3.2 * t + TAU * fp)) ** 4
        facet_lum = 0.34 + 0.50 * sp1 + 0.55 * sp2 + 0.65 * fire + 0.85 * streak[g]
        # Crisp bright wireframe ridges along the table, girdle, and pavilion ribs
        edge_lum = 0.72 + 0.28 * np.abs(ng @ L1) + 0.40 * streak[g]
        lum[g] = np.where(is_edge, edge_lum, facet_lum)
        
    pr = ks == 2
    lum[pr] = 0.32 + 0.38 * np.clip(n[pr] @ L1, 0, 1) + 0.40 * streak[pr]
    lum = np.clip(lum, 0, 1) * ease[idx]

    # Orbiting sparkles
    th = ob_th[:, None] + ob_w[:, None] * t - np.sign(ob_w)[:, None] * np.arange(OB_TR) * 0.07
    r_, tl = ob_r[:, None], ob_tl[:, None]
    op = np.stack([r_ * np.cos(th), r_ * np.sin(th) * np.sin(tl) - .05, r_ * np.sin(th) * np.cos(tl)], -1).reshape(-1, 3)
    op = op @ rot(0, -0.26 + 0.05 * np.sin(0.5 * t)).T; op[:, 1] += bob
    tw = 0.5 + 0.5 * np.sin(3 * t + ob_ph)[:, None]
    ol = ((0.25 + 0.70 * tw) * (1 - np.arange(OB_TR) / OB_TR) ** 1.5 * smooth((t - 2.8) / 1.2)).reshape(-1)
    oc = np.ones((len(op), 3))
    pos, lum, col = np.vstack([pos, op]), np.concatenate([lum, ol]), np.vstack([col, oc])

    # Supersampled z-buffer
    Hs, Ws = H * SS, W * SS; M = len(lum)
    X, Y = pos[:, 0] * s + W / 2, -pos[:, 1] * s * 0.5 + H / 2
    ok = np.flatnonzero((X >= 0) & (X < W) & (Y >= 0) & (Y < H))
    order = ok[np.argsort(pos[ok, 2])]                             
    cid = (Y[order] * SS).astype(int) * Ws + (X[order] * SS).astype(int)
    buf = np.full(Hs * Ws, M); buf[cid] = order
    Lb = np.append(lum, 0)[buf]
    sumL = Lb.reshape(H, SS, W, SS).sum((1, 3))
    
    Lc = np.clip(sumL / (SS ** 2) * 1.45, 0, 1) ** 0.80

    # Soft bloom aura around the diamond and ring
    def b2(a): return blur(blur(a, 2, 1), 1, 0)
    bl = b2(Lc)
    Lf = np.clip(Lc + bl * 0.28, 0, 1)

    nr = len(RAMP) - 1
    chars = RAMP[np.clip(np.round(Lf * nr).astype(int), 0, nr)]
    
    shade = np.clip(0.25 + 0.75 * Lf, 0, 1)
    rgb = np.repeat(shade[..., None], 3, axis=-1)

    # 8-point star glints on the diamond & band
    gp = (P0[GL] + SV[GL] * ((1 - ease[GL]) ** 2)[:, None]) @ R.T; gn = N0[GL] @ R.T; gp[:, 1] += bob
    gi = np.maximum(np.clip(np.sin(TAU * t / GT + GPH), 0, 1) ** 8,
                    0.95 * np.exp(-(((gp[:, 0] * .85 + gp[:, 1] * .5) - sweep) / 0.10) ** 2)) * (gn[:, 2] > 0.10) * (ease[GL] > 0.9)
    def put(r, c, ch, lv):
        if 0 <= r < H and 0 <= c < W: 
            chars[r, c] = ch
            rgb[r, c] = np.array([1.0, 1.0, 1.0]) * np.clip(.50 + .50 * lv, 0, 1)
    
    for k in np.flatnonzero(gi > 0.12):
        v = gi[k]; c0, r0 = int(gp[k, 0] * s + W / 2), int(-gp[k, 1] * s * .5 + H / 2)
        for j in range(1, 2 + int(v * 5)):
            put(r0, c0 + j, '-' if j < 3 else '.', v * (1 - j / 7))
            put(r0, c0 - j, '-' if j < 3 else '.', v * (1 - j / 7))
        for j in range(1, 1 + int(v * 2.5)): 
            put(r0 + j, c0, '|', v * (1 - j / 4))
            put(r0 - j, c0, '|', v * (1 - j / 4))
        if v > 0.50:
            for dr, dc, ch in [(1, 1, '\\'), (-1, -1, '\\'), (1, -1, '/'), (-1, 1, '/')]:
                put(r0 + dr, c0 + dc, ch, v * 0.70)
        put(r0, c0, '*', v)
    
    # ------------------------------------------------------------------ Banners Overlay (Solid Red, No Fade)
    start_r_top = 1
    start_c_top = (W - len(TOP_BANNER[0])) // 2
    for i, line in enumerate(TOP_BANNER):
        r = start_r_top + i
        if 0 <= r < H:
            reveal = int(max(0, (t - 2.6 - i * 0.08)) * 55) 
            for j, ch in enumerate(line):
                if ch != ' ' and j < reveal:
                    c = start_c_top + j
                    if 0 <= c < W:
                        chars[r, c] = ch
                        lvl = 0.85 + 0.15 * np.sin(3.0 * t - c * 0.05)
                        rgb[r, c] = [lvl, 0.06, 0.12]

    start_r_bot = max(0, H - len(BOT_BANNER) - 1)
    start_c_bot = (W - len(BOT_BANNER[0])) // 2
    for i, line in enumerate(BOT_BANNER):
        r = start_r_bot + i
        if 0 <= r < H:
            reveal = int(max(0, (t - 3.6 - i * 0.08)) * 55) 
            for j, ch in enumerate(line):
                if ch != ' ' and j < reveal:
                    c = start_c_bot + j
                    if 0 <= c < W:
                        chars[r, c] = ch
                        lvl = 0.85 + 0.15 * np.sin(3.0 * t - c * 0.05)
                        rgb[r, c] = [lvl, 0.06, 0.12]

    return chars, rgb

# ------------------------------------------------------------------ output
def emit(chars, rgb, mono=False):
    H, W = chars.shape
    if mono: return "\x1b[97m" + "\n".join("".join(r) for r in chars)
    
    q = (np.clip(rgb, 0, 1) * 255).astype(np.int32) // 4 * 4
    key = (q[..., 0] << 16) | (q[..., 1] << 8) | q[..., 2]
    pos = np.maximum.accumulate(np.where(chars == " ", -1, np.arange(W)[None, :]), axis=1)
    fill = np.where(pos < 0, 0, np.take_along_axis(key, np.maximum(pos, 0), 1))
    chg = np.ones((H, W), bool); chg[:, 1:] = fill[:, 1:] != fill[:, :-1]
    rows = []
    for y in range(H):
        line, cs = "".join(chars[y]), np.flatnonzero(chg[y]); ends = np.append(cs[1:], W); out = []
        for a, e in zip(cs, ends):
            k = int(fill[y, a]); out.append(f"\x1b[38;2;{k >> 16};{(k >> 8) & 255};{k & 255}m{line[a:e]}")
        rows.append("".join(out))
    return "\x1b[0m" + "\n".join(rows)

def main():
    os.system("")                                         
    mono = False 
    out = sys.stdout; last = None
    out.write("\x1b[?1049h\x1b[?25l\x1b[2J")
    try:
        t0 = time.perf_counter(); nxt = t0
        while True:
            c, r = shutil.get_terminal_size((100, 40)); W, H = max(40, c - 1), max(20, r - 1)
            if (W, H) != last: out.write("\x1b[2J"); last = (W, H)
            chars, rgb = render(time.perf_counter() - t0, W, H)
            out.write("\x1b[H" + emit(chars, rgb, mono)); out.flush()
            nxt += 1 / 30; wait = nxt - time.perf_counter()
            if wait > 0: time.sleep(wait)
            else: nxt = time.perf_counter()
    except KeyboardInterrupt:
        pass
    finally:
        out.write("\x1b[0m\x1b[?25h\x1b[?1049l")

if __name__ == "__main__":
    main()