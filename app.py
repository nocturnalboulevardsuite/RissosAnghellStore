# -*- coding: utf-8 -*-
"""
RISSOS ANGHELL STORE · Benjamín Espinoza
──────────────────────────────────────────
Ejecutar:   streamlit run app.py
Tu foto:    sube "benja.jpeg" a la raíz del repositorio (al lado de app.py) o a /assets.
Admin:      contraseña inicial "anghell2026" (cámbiala en Panel › Ajustes).
"""
import base64
import hashlib
import html as htmllib
import io
import json
import random
import re
import secrets
import uuid
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

import streamlit as st
from PIL import Image, ImageOps

st.set_page_config(page_title="Rissos Anghell Store", page_icon=":material/diamond:",
                   layout="wide", initial_sidebar_state="collapsed")

# ══════════════════════════════════════════════════════════════════════════
# 1 · CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
IMG_DIR = DATA_DIR / "images"
ASSETS_DIR = BASE_DIR / "assets"
DB_PATH = DATA_DIR / "db.json"
IMG_DIR.mkdir(parents=True, exist_ok=True)

OWNER = {
    "name": "Benjamín Espinoza",
    "tagline": "Compra y venta de artículos, ropa, perfumes y más.",
    "photo_names": ("benja.jpeg", "benja.jpg", "Benja.jpeg", "Benja.jpg", "benja.png", "benja.webp"),
    "whatsapp": "56936992950",
    "whatsapp_display": "+56 9 3699 2950",
    "instagram": "rissos._.anghell",
    "email": "nocturnalboulevardsuite@gmail.com",
    "city": "Santiago, Chile",
}
COPYRIGHT = "Derechos reservados 2027 · Benjamín Espinoza · @Rissos Anghell Store"
DEFAULT_ADMIN_PASSWORD = "anghell2026"

CATEGORIES = ["Perfumes", "Ropa", "Calzado", "Accesorios", "Figuras", "Tecnología", "Otros"]
SIZED = ("Ropa", "Calzado", "Accesorios")
STATUSES = ["Disponible", "Agotado", "Fuera de stock"]
CONDITIONS = ["Nuevo", "Nuevo sin etiqueta", "Usado, como nuevo", "Usado"]
GENDERS = ["Masculino", "Femenino", "No Binario", "Prefiero no decirlo", "Personalizado"]
SORTS = ["Destacados", "Precio: menor a mayor", "Precio: mayor a menor", "Más recientes"]
MADE_IN = ["China", "Taiwán", "EE.UU.", "Vietnam", "Bangladesh", "India", "Indonesia", "Camboya",
           "Tailandia", "Turquía", "Pakistán", "México", "Brasil", "Chile", "Perú", "Italia",
           "Francia", "España", "Portugal", "Alemania", "Reino Unido", "Japón", "Corea del Sur",
           "Emiratos Árabes", "Otro"]
AVATAR_COLORS = {"Rojo": "#A8182E", "Blanco": "#F4F1EA", "Negro": "#141210", "Azul": "#2C4E9A",
                 "Verde": "#2F6B50", "Morado": "#5B3F8C", "Naranjo": "#C9682A", "Dorado": "#B08D57",
                 "Rosado": "#C77A8E", "Gris": "#7C776F"}


def _svg_url(svg: str) -> str:
    return 'url("data:image/svg+xml,' + quote(svg) + '")'


_SUN = _svg_url('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#8C6B37" '
                'stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2'
                'M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>')
_MOON = _svg_url('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#C21F3A">'
                 '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>')

# Claro: marfil + dorado · Oscuro: negro + rojo
THEMES = {
    "light": {"bg": "#F8F5EE", "bg2": "#F1ECE1", "surface": "#FFFDF8", "text": "#1C1813",
              "muted": "#7A7163", "faint": "#ABA190", "line": "rgba(140,107,55,.18)",
              "line2": "rgba(140,107,55,.34)", "accent": "#9C7A43", "accent2": "#C9A96E",
              "accent-ink": "#FFFDF8", "accent-soft": "rgba(176,141,87,.12)", "chip": "rgba(140,107,55,.08)",
              "shadow": "rgba(60,44,20,.14)", "head": "rgba(248,245,238,.94)", "ok": "#4E7A4B",
              "sw-track": "#EFE6D3", "sw-knob": "#FFFDF8", "sw-x": "0px", "sw-icon": _SUN},
    "dark": {"bg": "#0A0909", "bg2": "#121010", "surface": "#141212", "text": "#F1ECE4",
             "muted": "#8E867B", "faint": "#5C564E", "line": "rgba(241,236,228,.09)",
             "line2": "rgba(241,236,228,.18)", "accent": "#C21F3A", "accent2": "#E0485F",
             "accent-ink": "#FFFFFF", "accent-soft": "rgba(194,31,58,.14)", "chip": "rgba(241,236,228,.06)",
             "shadow": "rgba(0,0,0,.55)", "head": "rgba(10,9,9,.94)", "ok": "#6FBF73",
             "sw-track": "#2A1015", "sw-knob": "#0A0909", "sw-x": "26px", "sw-icon": _MOON},
}

# Íconos dibujados (trazo fino uniforme)
_I = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" '
      'stroke-linecap="round" stroke-linejoin="round">')
ICON = {
    "whatsapp": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.16-.17.2-.35.22-.64.08-.3-.15-1.26-.46-2.39-1.48-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.88 1.21 3.07.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.7.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.41.25-.7.25-1.29.18-1.41-.08-.13-.28-.2-.57-.35zM12.05 21.79h-.01a9.87 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.86 9.86 0 0 1-1.51-5.26c0-5.45 4.44-9.88 9.89-9.88 2.64 0 5.12 1.03 6.99 2.9a9.83 9.83 0 0 1 2.89 6.99c0 5.45-4.44 9.88-9.88 9.88zm8.41-18.3A11.82 11.82 0 0 0 12.05 0C5.5 0 .16 5.34.16 11.89c0 2.1.55 4.14 1.59 5.95L.06 24l6.3-1.65a11.88 11.88 0 0 0 5.69 1.45c6.55 0 11.89-5.34 11.89-11.89 0-3.18-1.24-6.17-3.48-8.42z"/></svg>',
    "instagram": _I + '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.4" cy="6.6" r=".7" fill="currentColor"/></svg>',
    "mail": _I + '<rect x="3" y="5" width="18" height="14" rx="1.5"/><path d="m3.5 6.5 8.5 6 8.5-6"/></svg>',
    "arrow": _I + '<path d="M5 12h14M13 6l6 6-6 6"/></svg>',
    "phone": _I + '<path d="M21 16.5v2.6a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 3.1 3.3 2 2 0 0 1 5.1 1h2.6a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8.8 8.6a16 16 0 0 0 6 6l1.1-1.1a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    "pin": _I + '<path d="M19 10c0 5.5-7 11-7 11s-7-5.5-7-11a7 7 0 0 1 14 0z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    "calendar": _I + '<rect x="3" y="4.5" width="18" height="16.5" rx="1.5"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/></svg>',
    "globe": _I + '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.7 3.6 5.8 3.6 9s-1.1 6.3-3.6 9c-2.5-2.7-3.6-5.8-3.6-9S9.5 5.7 12 3z"/></svg>',
    "ruler": _I + '<path d="M3 17 17 3l4 4L7 21z"/><path d="m7 13 2 2M10 10l2 2M13 7l2 2"/></svg>',
    "tag": _I + '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.2"/></svg>',
    "spark": _I + '<path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/></svg>',
    "box": _I + '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/></svg>',
    "check": _I + '<path d="M20 6 9 17l-5-5"/></svg>',
    "truck": _I + '<path d="M2 6h11v10H2zM13 10h4l4 3v3h-8z"/><circle cx="6" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/></svg>',
    "chat": _I + '<path d="M21 12a8 8 0 0 1-11.5 7.2L4 21l1.8-5.2A8 8 0 1 1 21 12z"/></svg>',
    "gender": _I + '<circle cx="10" cy="14" r="5"/><path d="M14 10l6-6M15 4h5v5"/></svg>',
    "bag": _I + '<path d="M5 8h14l-1 13H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>',
}

# Logo: monograma R·A·S dentro de un sello
LOGO = (
    '<svg class="ra-logo-svg" viewBox="0 0 120 120" fill="none" stroke="currentColor">'
    '<circle class="ra-ring" cx="60" cy="60" r="56" stroke-width="1"/>'
    '<circle cx="60" cy="60" r="50" stroke-width=".5" opacity=".55"/>'
    '<path d="M60 6 l3.2 4 -3.2 4 -3.2 -4z" fill="currentColor" stroke="none"/>'
    '<path d="M60 106 l3.2 4 -3.2 4 -3.2 -4z" fill="currentColor" stroke="none"/>'
    '<text x="60" y="72" text-anchor="middle" fill="currentColor" stroke="none" '
    'font-family="Cormorant Garamond,Didot,Georgia,serif">'
    '<tspan font-size="30" font-weight="500">R</tspan>'
    '<tspan font-size="44" font-style="italic" font-weight="400" dy="2">A</tspan>'
    '<tspan font-size="30" font-weight="500" dy="-2">S</tspan></text>'
    '<path d="M34 84 H86" stroke-width=".6" opacity=".6"/></svg>'
)


# ══════════════════════════════════════════════════════════════════════════
# 2 · UTILIDADES
# ══════════════════════════════════════════════════════════════════════════
def esc(s) -> str:
    return htmllib.escape(str(s or ""))


def html(s: str):
    st.markdown(s, unsafe_allow_html=True)


def money(n) -> str:
    return "$" + f"{int(n or 0):,}".replace(",", ".")


def money_html(n) -> str:
    return "&#36;" + f"{int(n or 0):,}".replace(",", ".")


def norm_phone(s: str) -> str:
    d = re.sub(r"\D", "", s or "")
    return "56" + d if len(d) == 9 and d.startswith("9") else d


def new_id() -> str:
    return uuid.uuid4().hex[:8]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%d/%m/%Y")
    except Exception:
        return iso or ""


def size_label(p) -> str:
    s = (p.get("size") or "").strip()
    return "" if not s else (f"Talla {s}" if p.get("category") in SIZED else s)


def hash_pw(pw: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(8)
    return f"{salt}${hashlib.pbkdf2_hmac('sha256', pw.encode(), salt.encode(), 120_000).hex()}"


def check_pw(pw: str, stored: str | None) -> bool:
    if not stored or "$" not in stored:
        return False
    return secrets.compare_digest(hash_pw(pw, stored.split("$", 1)[0]), stored)


def b64svg(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


# ══════════════════════════════════════════════════════════════════════════
# 3 · IMÁGENES (todo en caché para que la página no tenga lag)
# ══════════════════════════════════════════════════════════════════════════
ILLUS = {
    "tshirt": '<path d="M300 330 L365 292 C380 322 420 322 435 292 L500 330 L565 425 L512 455 L490 425 L490 712 L310 712 L310 425 L288 455 L235 425 Z"/><path d="M365 292 C380 340 420 340 435 292"/>',
    "jeans": '<path d="M318 290 H482 L506 712 H424 L400 440 L376 712 H294 Z"/><path d="M318 330 H482"/><path d="M400 330 V420"/><path d="M332 332 C336 368 358 380 380 382"/><path d="M468 332 C464 368 442 380 420 382"/>',
    "perfume": '<rect x="356" y="268" width="88" height="74" rx="4"/><path d="M380 342 V392 H420 V342"/><path d="M300 392 H500 L516 700 C516 716 504 724 488 724 H312 C296 724 284 716 284 700 Z"/><rect x="340" y="500" width="120" height="110" rx="2"/><path d="M360 540 H440 M372 570 H428" opacity=".6"/>',
    "cap": '<path d="M255 560 C255 420 320 372 400 372 C480 372 545 420 545 560 Z"/><path d="M255 560 C330 590 470 590 545 560 C600 575 620 600 590 615 C520 640 330 640 255 600 Z"/><path d="M400 372 C380 420 372 500 372 572"/><circle cx="400" cy="368" r="10"/>',
    "figure": '<ellipse cx="400" cy="705" rx="140" ry="26"/><circle cx="400" cy="372" r="54"/><path d="M366 334 L344 296 M434 334 L456 296"/><path d="M346 440 C346 428 454 428 454 440 L470 600 L430 600 L420 690 L380 690 L370 600 L330 600 Z"/><path d="M346 452 L292 540 M454 452 L508 540"/>',
    "monitor": '<rect x="236" y="320" width="328" height="226" rx="10"/><rect x="262" y="344" width="276" height="178" rx="3"/><path d="M380 546 L370 640 H430 L420 546"/><path d="M322 650 H478"/>',
    "bag": '<path d="M290 420 H510 L530 712 H270 Z"/><path d="M345 420 V380 C345 330 455 330 455 380 V420"/>',
}
# fondo 1, fondo 2, trazo
PALETTES = [("#F4EEE2", "#E7DAC2", "#8C6B37"), ("#1A1817", "#0E0D0C", "#C9A96E"),
            ("#F7F3EA", "#ECE2D0", "#5A4527"), ("#4A0F1A", "#22070D", "#E8CFA0"),
            ("#EDE8E0", "#D9D1C4", "#2E2820"), ("#EFE6D3", "#DCC9A6", "#6E2330")]


@st.cache_data(show_spinner=False, max_entries=300)
def demo_svg(kind: str, idx: int) -> str:
    a, b, fg = PALETTES[idx % len(PALETTES)]
    return b64svg(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/>'
        f'<stop offset="1" stop-color="{b}"/></linearGradient></defs><rect width="800" height="1000" fill="url(#g)"/>'
        f'<rect x="40" y="40" width="720" height="920" fill="none" stroke="{fg}" stroke-opacity=".22" stroke-width="2"/>'
        f'<g fill="{fg}" fill-opacity=".05" stroke="{fg}" stroke-width="5" stroke-linecap="round" '
        f'stroke-linejoin="round" transform="translate(0 20)">{ILLUS.get(kind, ILLUS["bag"])}</g>'
        f'<text x="400" y="905" font-size="20" letter-spacing="8" text-anchor="middle" fill="{fg}" '
        'fill-opacity=".55" font-family="Georgia,serif">FOTO DE MUESTRA</text></svg>')


@st.cache_data(show_spinner=False, max_entries=800)
def _file_uri(path: str, mtime: float, square: int = 0) -> str:
    p = Path(path)
    if square:  # recorte cuadrado (foto de perfil)
        img = ImageOps.fit(ImageOps.exif_transpose(Image.open(p)).convert("RGB"), (square, square),
                           Image.LANCZOS, centering=(0.5, 0.35))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=88, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    mime = {"png": "image/png", "webp": "image/webp"}.get(p.suffix.lower().lstrip("."), "image/jpeg")
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def img_src(entry: str, thumb: bool = False) -> str:
    if not entry:
        return demo_svg("bag", 0)
    if entry.startswith("demo:"):
        parts = (entry.split(":") + ["0", "0"])[:3]
        return demo_svg(parts[1], int(parts[2]) if parts[2].isdigit() else 0)
    p = DATA_DIR / entry
    if thumb:
        t = p.with_name(p.stem + "_t.jpg")
        if t.exists():
            p = t
    return _file_uri(str(p), p.stat().st_mtime) if p.exists() else demo_svg("bag", 0)


def save_upload(uploaded, max_side: int = 1400) -> str:
    img = ImageOps.exif_transpose(Image.open(uploaded))
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    img = img.convert("RGB")
    stem = uuid.uuid4().hex
    big = img.copy()
    big.thumbnail((max_side, max_side))
    big.save(IMG_DIR / f"{stem}.jpg", "JPEG", quality=86, optimize=True)
    img.thumbnail((520, 520))
    img.save(IMG_DIR / f"{stem}_t.jpg", "JPEG", quality=80, optimize=True)
    return f"images/{stem}.jpg"


def delete_image(entry: str | None):
    if entry and not entry.startswith("demo:"):
        p = DATA_DIR / entry
        for f in (p, p.with_name(p.stem + "_t.jpg")):
            try:
                f.unlink(missing_ok=True)
            except Exception:
                pass


@st.cache_data(show_spinner=False, max_entries=40)
def avatar_svg(color: str) -> str:
    c = color.lstrip("#")
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    fg = "#1C1813" if (r * 299 + g * 587 + b * 114) / 1000 > 170 else "#FFFDF8"
    return b64svg(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><clipPath id="c"><circle cx="50" '
        f'cy="50" r="50"/></clipPath></defs><g clip-path="url(#c)"><rect width="100" height="100" fill="{color}"/>'
        f'<circle cx="50" cy="39" r="16" fill="{fg}" fill-opacity=".9"/>'
        f'<path d="M15 100c0-21 15-34 35-34s35 13 35 34z" fill="{fg}" fill-opacity=".9"/></g></svg>')


def user_avatar(u) -> str:
    return img_src(u["photo"], thumb=True) if u.get("photo") else avatar_svg(u.get("avatar_color") or "#A8182E")


def find_owner_photo() -> Path | None:
    for folder in (BASE_DIR, ASSETS_DIR):
        for name in OWNER["photo_names"]:
            if (folder / name).exists():
                return folder / name
    return None


def owner_photo() -> str:
    p = find_owner_photo()
    if p:
        return _file_uri(str(p), p.stat().st_mtime, 420)
    return b64svg('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" '
                  'fill="#1C1813"/><text x="50" y="62" font-size="32" text-anchor="middle" fill="#C9A96E" '
                  'font-family="Georgia,serif" font-style="italic">BE</text></svg>')


# ══════════════════════════════════════════════════════════════════════════
# 4 · BASE DE DATOS (JSON local)
# ══════════════════════════════════════════════════════════════════════════
def seed_db() -> dict:
    t = now_iso()
    rows = [
        ("Dior Sauvage Parfum 150ml", "Perfumes", 129990, "", "Francia", "Dior", "Nuevo", "Disponible",
         "Perfume original, sellado, 150 ml.",
         "Dior Sauvage en su versión Parfum: más profunda y amaderada que el EDT, con notas de bergamota, sándalo y vainilla. Caja sellada.",
         ["Contenido: 150 ml", "Concentración: Parfum", "Familia: amaderada aromática", "Caja sellada, original"], "perfume", [1, 0, 3]),
        ("Polera roja", "Ropa", 12990, "L", "China", "Rissos Basics", "Nuevo", "Disponible",
         "Algodón peinado, corte regular y color que no se lava.",
         "Polera de algodón peinado de gramaje medio, suave al tacto y con buena caída. El rojo es intenso y se mantiene lavado tras lavado.",
         ["100% algodón", "Corte regular fit", "Cuello redondo reforzado", "Lavar en frío"], "tshirt", [5, 2, 0]),
        ("Pantalón Jean negro", "Ropa", 24990, "42", "Bangladesh", "Denim Co.", "Usado, como nuevo", "Disponible",
         "Jean negro de corte recto, usado dos veces.",
         "Jean negro de mezclilla firme con un toque de elasticidad. Corte recto que funciona con zapatillas o botines. Sin desgaste visible.",
         ["98% algodón, 2% elastano", "Corte recto", "5 bolsillos", "Tiro medio"], "jeans", [1, 4, 2]),
        ("Figura de Freezer", "Figuras", 34990, "", "China", "Banpresto", "Nuevo", "Disponible",
         "Figura de colección de Dragon Ball, en su caja.",
         "Figura de Freezer en su forma final, con detalles pintados y base incluida. Ideal para colección; caja en buen estado.",
         ["Altura aprox.: 18 cm", "Material: PVC", "Base incluida", "Caja original"], "figure", [2, 3, 0]),
        ("Monitor 144Hz", "Tecnología", 159990, "", "Taiwán", "Genérico 24\"", "Usado, como nuevo", "Disponible",
         "24 pulgadas, Full HD, 144 Hz y 1 ms.",
         "Monitor gamer de 24 pulgadas con panel de 144 Hz, ideal para juegos competitivos. Sin píxeles muertos, con cables y caja.",
         ["24\" Full HD 1920×1080", "144 Hz, 1 ms", "HDMI y DisplayPort", "Incluye cables"], "monitor", [4, 1, 0]),
        ("Gorra F1", "Accesorios", 19990, "Ajustable", "Vietnam", "Formula 1", "Nuevo", "Agotado",
         "Gorra de seis paneles con bordado frontal.",
         "Gorra de seis paneles con logo bordado y cierre ajustable trasero. Visera curva y forro interior transpirable.",
         ["Talla única ajustable", "Logo bordado", "Cierre de velcro", "Visera curva"], "cap", [3, 0]),
    ]
    prods = [dict(id=new_id(), name=n, category=c, price=pr, size=sz, made_in=m, brand=br, condition=co,
                  status=stt, short=sh, description=de, details=dt, images=[f"demo:{k}:{i}" for i in pals],
                  created=t) for (n, c, pr, sz, m, br, co, stt, sh, de, dt, k, pals) in rows]
    return {"products": prods, "users": [], "purchases": [], "settings": {}}


def load_db() -> dict:
    if not DB_PATH.exists():
        save_db(seed_db())
    with open(DB_PATH, encoding="utf-8") as f:
        db = json.load(f)
    for k, v in (("products", []), ("users", []), ("purchases", []), ("settings", {})):
        db.setdefault(k, v)
    for p in db["products"]:  # compatibilidad con versiones anteriores
        p["images"] = [e if not e.startswith("demo:") or e.split(":")[1] in ILLUS else "demo:bag:0"
                       for e in p.get("images") or []]
    return db


def save_db(db: dict):
    tmp = DB_PATH.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    tmp.replace(DB_PATH)


def get_product(db, pid):
    return next((p for p in db["products"] if p["id"] == pid), None)


def get_user(db, uid):
    return next((u for u in db["users"] if u["id"] == uid), None)


def find_user_by_phone(db, phone):
    n = norm_phone(phone)
    return next((u for u in db["users"] if u.get("phone") == n), None) if n else None


def user_purchases(db, uid):
    return sorted([p for p in db["purchases"] if p["user_id"] == uid], key=lambda x: x.get("date", ""), reverse=True)


def user_stats(db, uid):
    ps = user_purchases(db, uid)
    return len(ps), sum(int(p.get("qty", 1)) for p in ps), sum(int(p.get("total", 0)) for p in ps)


def check_admin(db, pw: str) -> bool:
    if db["settings"].get("admin_pw"):
        return check_pw(pw, db["settings"]["admin_pw"])
    try:
        expected = st.secrets.get("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)
    except Exception:
        expected = DEFAULT_ADMIN_PASSWORD
    return secrets.compare_digest(pw, expected)


# ══════════════════════════════════════════════════════════════════════════
# 5 · LINKS
# ══════════════════════════════════════════════════════════════════════════
def app_base_url(db) -> str:
    s = (db["settings"].get("base_url") or "").strip()
    if s:
        return s.rstrip("/")
    try:
        u = getattr(st.context, "url", None)
        if u:
            return u.split("?")[0].rstrip("/")
        host = st.context.headers.get("host")
        if host:
            return ("http" if host.startswith(("localhost", "127.", "0.0.0.0")) else "https") + f"://{host}"
    except Exception:
        pass
    return "http://localhost:8501"


def product_link(db, pid) -> str:
    return f"{app_base_url(db)}/?producto={pid}"


def mailto(subject: str, body: str = "") -> str:
    return f"mailto:{OWNER['email']}?subject={quote(subject, safe='')}&body={quote(body, safe='')}"


def gmail_link(subject: str, body: str = "") -> str:
    return (f"https://mail.google.com/mail/?view=cm&fs=1&to={OWNER['email']}"
            f"&su={quote(subject, safe='')}&body={quote(body, safe='')}")


def wa_link(text: str = "") -> str:
    return f"https://wa.me/{OWNER['whatsapp']}" + (f"?text={quote(text, safe='')}" if text else "")


IG_LINK = f"https://www.instagram.com/{OWNER['instagram']}/"


def consult_message(db, p):
    sl = size_label(p)
    subject = f"Consulta de Stock – {p['name']}" + (f" ({sl})" if sl else "")
    lines = ["Hola Benjamín,", "", "Quiero consultar el stock de este producto:", "", f"• Producto: {p['name']}"]
    if sl:
        lines.append(f"• {sl if p.get('category') in SIZED else 'Medida: ' + p['size']}")
    lines += [f"• Precio: {money(p['price'])}", f"• Link: {product_link(db, p['id'])}", ""]
    u = current_user(db)
    if u:
        lines += [f"Mi nombre: {u['name']}", f"Mi teléfono: {u.get('phone_display') or u['phone']}", ""]
    lines.append("¡Gracias!")
    return subject, "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════
# 6 · SESIÓN Y NAVEGACIÓN
# ══════════════════════════════════════════════════════════════════════════
ss = st.session_state
ss.setdefault("theme", "light")
ss.setdefault("role", None)
ss.setdefault("user_id", None)
ss.setdefault("view", "home")


def current_user(db):
    return get_user(db, ss.user_id) if ss.role == "user" else None


def go(view: str, pid: str | None = None):
    ss.view = view
    st.query_params.clear()
    if view == "product" and pid:
        st.query_params["producto"] = pid
    st.rerun()


def flash(msg: str, icon: str = ":material/check_circle:"):
    ss["_flash"] = (msg, icon)


def logout():
    ss.role, ss.user_id = None, None
    flash("Cerraste sesión", ":material/logout:")
    go("home")


def _toggle_theme():
    ss["_curtain"] = ss.theme
    ss.theme = "dark" if ss.theme == "light" else "light"


# ══════════════════════════════════════════════════════════════════════════
# 7 · ESTILOS  (solo se animan transform y opacity → fluido, sin lag)
# ══════════════════════════════════════════════════════════════════════════
CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&family=Jost:wght@300;400;500;600&display=swap');
:root{--ease:cubic-bezier(.25,.8,.25,1);--slow:cubic-bezier(.65,0,.35,1);--serif:'Cormorant Garamond',Didot,Georgia,serif;--sans:'Jost','Futura','Century Gothic',system-ui,sans-serif}
html{font-size:15px;scroll-behavior:smooth}
.stApp,[data-testid="stMain"]{overflow-x:hidden!important}
[class*="st-key-grid_"]{gap:2.4rem!important}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--bg)!important;color:var(--text)!important;font-family:var(--sans)}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer,[data-testid="stStatusWidget"],[data-testid="stSidebarCollapsedControl"],[data-testid="stAppDeployButton"]{display:none!important}
.block-container,[data-testid="stMainBlockContainer"]{padding:0 1.4rem 1.5rem!important;max-width:1160px!important}
[data-testid="stVerticalBlock"]{gap:.8rem}
.stApp [data-testid="stMarkdownContainer"] p,.stApp [data-testid="stMarkdownContainer"] li{color:var(--text);font-size:.95rem;font-weight:300}
[data-testid="stWidgetLabel"] p{color:var(--muted)!important;font-size:.72rem!important;font-weight:500!important;letter-spacing:.12em;text-transform:uppercase}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:var(--muted)!important;font-size:.78rem!important}
::selection{background:var(--accent);color:var(--accent-ink)}
::-webkit-scrollbar{width:8px;height:8px}::-webkit-scrollbar-thumb{background:var(--line2);border-radius:8px}
:focus-visible{outline:1.5px solid var(--accent)!important;outline-offset:2px}
.st-key-scrolltop{position:absolute!important;height:0!important;overflow:hidden;visibility:hidden;pointer-events:none}

/* Formularios */
.stApp input,.stApp textarea{color:var(--text)!important;-webkit-text-fill-color:var(--text)!important;caret-color:var(--accent);font-size:.92rem!important;font-family:var(--sans)!important}
.stApp input::placeholder,.stApp textarea::placeholder{color:var(--faint)!important;-webkit-text-fill-color:var(--faint)!important}
[data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="base-input"],[data-baseweb="select"]>div,[data-testid$="RootElement"]{background:var(--surface)!important;border:1px solid var(--line2)!important;border-radius:2px!important}
[data-testid$="RootElement"]:focus-within,[data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within,[data-baseweb="select"]>div:focus-within{border-color:var(--accent)!important;box-shadow:0 0 0 3px var(--accent-soft)!important}
.react-aria-ComboBox [role="group"],[data-testid="stSelectbox"] [role="group"],[data-testid="stMultiSelect"] [role="group"]{background:var(--surface)!important;border:1px solid var(--line2)!important;border-radius:2px!important;min-height:2.5rem}
.react-aria-ComboBox [role="group"]:focus-within{border-color:var(--accent)!important;box-shadow:0 0 0 3px var(--accent-soft)!important}
.react-aria-ComboBox button{color:var(--muted)!important;background:transparent!important}
[role="listbox"],.react-aria-Popover,.react-aria-ListBox{background:var(--surface)!important;border-color:var(--line2)!important;border-radius:2px!important}
[role="option"]{color:var(--text)!important}
[role="option"][data-focused="true"],[role="option"][aria-selected="true"],[role="option"]:hover{background:var(--chip)!important}
[data-baseweb="select"] *{color:var(--text)!important}
[data-baseweb="select"] svg{fill:var(--muted)!important}
[data-baseweb="popover"] ul,[data-baseweb="popover"] [data-baseweb="menu"]{background:var(--surface)!important;border:1px solid var(--line2);border-radius:2px}
[data-baseweb="popover"] li{color:var(--text)!important;background:transparent!important}
[data-baseweb="popover"] li:hover,[data-baseweb="popover"] li[aria-selected="true"]{background:var(--chip)!important}
[data-testid="stNumberInput"] button{background:var(--bg2)!important;color:var(--text)!important;border-color:var(--line)!important}
[data-testid="stRadio"] label p,[data-testid="stCheckbox"] label p,[data-testid="stToggle"] label p{color:var(--text)!important;font-weight:400!important;font-size:.88rem!important;letter-spacing:0;text-transform:none}
[data-testid="stFileUploaderDropzone"]{background:var(--bg2)!important;border:1px dashed var(--line2)!important;border-radius:2px!important}
[data-testid="stFileUploaderDropzone"] *{color:var(--muted)!important}
[data-testid="stFileUploaderFile"] *{color:var(--text)!important}
[data-baseweb="calendar"],[data-baseweb="calendar"] *{background-color:var(--surface)!important;color:var(--text)!important}

/* Botones: rectos, finos, con letras espaciadas */
.stButton button,.stFormSubmitButton button,.stDownloadButton button{background:transparent!important;color:var(--text)!important;border:1px solid var(--line2)!important;border-radius:2px!important;min-height:2.4rem;padding:.3rem 1rem!important;transition:border-color .3s var(--ease),background-color .3s var(--ease),color .3s var(--ease),transform .3s var(--ease)!important}
.stButton button p,.stFormSubmitButton button p,.stDownloadButton button p{color:inherit!important;font-family:var(--sans)!important;font-weight:500!important;font-size:.74rem!important;letter-spacing:.14em;text-transform:uppercase}
.stButton button:hover,.stFormSubmitButton button:hover,.stDownloadButton button:hover{border-color:var(--accent)!important;color:var(--accent)!important}
.stButton button:active{transform:scale(.98)}
.stApp button[kind="primary"],.stApp button[kind="primaryFormSubmit"],.stApp [data-testid^="stBaseButton-primary"]{background:var(--text)!important;color:var(--bg)!important;border-color:var(--text)!important}
.stApp button[kind="primary"]:hover,.stApp button[kind="primaryFormSubmit"]:hover,.stApp [data-testid^="stBaseButton-primary"]:hover{background:var(--accent)!important;border-color:var(--accent)!important;color:var(--accent-ink)!important}
[data-testid="stButtonGroup"] button[role="radio"]{border-radius:0!important;background:transparent!important;border:none!important;border-bottom:1px solid transparent!important;color:var(--muted)!important;padding:.2rem .1rem!important;margin-right:1rem;min-height:1.8rem!important}
[data-testid="stButtonGroup"] button[role="radio"] p{color:inherit!important;font-size:.78rem!important;letter-spacing:.14em;text-transform:uppercase;font-weight:500!important}
[data-testid="stButtonGroup"] button[role="radio"]:hover{color:var(--text)!important}
[data-testid="stButtonGroup"] button[aria-checked="true"]{color:var(--text)!important;border-bottom-color:var(--accent)!important}

/* Pestañas, expanders, contenedores */
.stTabs [data-baseweb="tab-list"]{gap:1.4rem;border-bottom:1px solid var(--line);background:transparent}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;padding:.6rem 0}
.stTabs [data-baseweb="tab"] p{color:inherit!important;font-size:.75rem!important;letter-spacing:.14em;text-transform:uppercase;font-weight:500!important}
.stTabs [aria-selected="true"]{color:var(--text)!important}
.stTabs [data-baseweb="tab-highlight"]{background:var(--accent)!important;height:1px}
.stTabs [data-baseweb="tab-border"]{display:none}
[data-testid="stExpander"] details{background:var(--surface)!important;border:1px solid var(--line)!important;border-radius:2px!important}
[data-testid="stExpander"] summary,[data-testid="stExpander"] summary p,[data-testid="stExpander"] summary span{color:var(--text)!important;font-size:.85rem;font-weight:500}
[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stForm"]{border-color:var(--line)!important;border-radius:2px!important;background:var(--surface)}
[data-testid="stMetric"]{background:var(--surface);border:1px solid var(--line);border-radius:2px;padding:14px 18px}
[data-testid="stMetricValue"]{color:var(--text)!important;font-family:var(--serif);font-size:2rem!important}
[data-testid="stMetricLabel"] p{color:var(--muted)!important;letter-spacing:.12em;text-transform:uppercase;font-size:.7rem!important}
[data-testid="stCode"] pre{background:var(--bg2)!important;border-radius:2px!important;border:1px solid var(--line)}
[data-testid="stCode"] code{color:var(--text)!important;white-space:pre-wrap!important;word-break:break-all;font-size:.78rem!important}
[data-testid="stAlert"]{border-radius:2px!important}
hr{border-color:var(--line)!important;margin:1.2rem 0!important}

/* Barra superior */
.ra-announce{margin:0 -100vw;padding:.45rem 100vw;background:var(--text);color:var(--bg);text-align:center;font-size:.68rem;letter-spacing:.22em;text-transform:uppercase;font-weight:500}
.ra-announce b{color:var(--accent2);font-weight:500}
.st-key-hdr{position:sticky;top:0;z-index:999;background:var(--head);border-bottom:1px solid var(--line);margin:0!important;padding:.55rem 0}
.st-key-hdr [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;align-items:center;gap:.5rem!important}
.st-key-hdr [data-testid="stColumn"]{min-width:0!important}
.st-key-hdr .stButton button{border-color:transparent!important;min-height:2.1rem;padding:.2rem .6rem!important}
.st-key-hdr .stButton button:hover{border-color:var(--line2)!important}
.ra-logo{display:flex;align-items:center;justify-content:center;gap:.75rem;color:var(--accent)}
.ra-logo-svg{width:46px;height:46px;flex-shrink:0}
.ra-ring{stroke-dasharray:352;stroke-dashoffset:352;animation:draw 2.4s var(--slow) .2s forwards}
.ra-word{display:flex;flex-direction:column;line-height:1}
.ra-word b{font-family:var(--serif);font-weight:500;font-size:1.32rem;letter-spacing:.24em;color:var(--text)}
.ra-word span{font-size:.58rem;letter-spacing:.58em;color:var(--accent);margin-top:.3rem;font-weight:500}
.ra-hdr-note{font-size:.68rem;letter-spacing:.18em;text-transform:uppercase;color:var(--muted)}

/* Switch de tema */
.st-key-theme_sw button{position:relative;width:54px!important;min-width:54px!important;height:28px!important;min-height:28px!important;padding:0!important;border-radius:999px!important;background:var(--sw-track)!important;border:1px solid var(--line2)!important;overflow:hidden}
.st-key-theme_sw button p,.st-key-theme_sw button span{font-size:0!important;opacity:0}
.st-key-theme_sw button::after{content:"";position:absolute;top:3px;left:3px;width:20px;height:20px;border-radius:50%;background:var(--sw-icon) center/12px no-repeat,var(--sw-knob);box-shadow:0 2px 6px rgba(0,0,0,.22);transform:translateX(var(--sw-x));transition:transform .55s var(--slow)}
.st-key-theme_sw button:hover{border-color:var(--accent)!important}
.st-key-theme_sw{display:flex;justify-content:flex-end}

/* Cortina del cambio de tema */
.ra-curtain{position:fixed;inset:0;z-index:99998;pointer-events:none;animation:curtain .95s var(--slow) forwards}
.ra-curtain-line{position:fixed;left:0;right:0;top:0;height:1px;z-index:99999;pointer-events:none;box-shadow:0 0 18px 2px var(--accent);animation:sweep .95s var(--slow) forwards}

/* Presentación */
.ra-intro{display:grid;grid-template-columns:1.05fr 1fr;gap:2.5rem;align-items:center;padding:2.4rem 0 2.2rem;border-bottom:1px solid var(--line);animation:fade .9s var(--ease) both}
.ra-owner{display:flex;gap:1.3rem;align-items:flex-start}
.ra-sq{position:relative;flex-shrink:0;width:136px;height:136px}
.ra-sq::before{content:"";position:absolute;inset:8px -8px -8px 8px;border:1px solid var(--accent);opacity:.55}
.ra-sq img{position:relative;width:100%;height:100%;object-fit:cover;display:block;border-radius:2px}
.ra-owner-body{flex:1;min-width:0}
.ra-intro>*{min-width:0}
.ra-kicker{font-size:.66rem;letter-spacing:.24em;text-transform:uppercase;color:var(--accent);font-weight:500}
.ra-owner-name{font-family:var(--serif);font-size:2.1rem;line-height:1;color:var(--text);margin:.3rem 0 .2rem;font-weight:500}
.ra-owner-tag{font-size:.86rem;color:var(--muted);font-weight:300;margin-bottom:.9rem}
.ra-stack{display:flex;flex-direction:column;gap:.4rem;max-width:330px}
.ra-ct{display:flex;align-items:center;gap:.7rem;padding:.5rem .75rem;border:1px solid var(--line2);background:var(--surface);color:var(--text)!important;text-decoration:none!important;transition:border-color .35s var(--ease),transform .35s var(--ease)}
.ra-ct .ic{width:30px;height:30px;display:grid;place-items:center;border-radius:50%;background:var(--chip);color:var(--accent);flex-shrink:0;transition:background-color .35s var(--ease),color .35s var(--ease)}
.ra-ct .ic svg{width:15px;height:15px}
.ra-ct .tx{flex:1;min-width:0;line-height:1.2}
.ra-ct .tx b{display:block;font-size:.66rem;letter-spacing:.18em;text-transform:uppercase;font-weight:500;color:var(--muted)}
.ra-ct .tx span{display:block;font-size:.86rem;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ra-ct .go{width:14px;height:14px;color:var(--faint);transition:transform .35s var(--ease),color .35s var(--ease)}
.ra-ct:hover{border-color:var(--accent);transform:translateX(3px)}
.ra-ct:hover .ic{background:var(--accent);color:var(--accent-ink)}
.ra-ct:hover .go{transform:translateX(3px);color:var(--accent)}
.ra-manifest h2{font-family:var(--serif)!important;font-size:clamp(1.9rem,3.4vw,2.6rem)!important;line-height:1.08!important;font-weight:400!important;color:var(--text)!important;margin:0 0 .7rem!important;padding:0!important}
.ra-manifest h2 em{color:var(--accent)}
.ra-manifest p{color:var(--muted)!important;font-weight:300;line-height:1.7;max-width:46ch;margin-bottom:1.1rem}
.ra-promises{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line)}
.ra-promises div{padding:.9rem .6rem .2rem 0;font-size:.8rem;color:var(--text);line-height:1.35}
.ra-promises svg{width:18px;height:18px;color:var(--accent);display:block;margin-bottom:.4rem}
.ra-promises small{display:block;color:var(--muted);font-size:.72rem;margin-top:.15rem}

/* Encabezados */
.ra-sec{text-align:center;margin:2.6rem 0 .6rem}
.ra-sec .k{font-size:.66rem;letter-spacing:.26em;text-transform:uppercase;color:var(--accent);font-weight:500}
.ra-sec .t{font-family:var(--serif);font-size:2.3rem;font-weight:400;color:var(--text);line-height:1.1;margin-top:.25rem}
.ra-sec .s{color:var(--muted);font-size:.84rem;font-weight:300;margin-top:.3rem}
.ra-orn{display:flex;align-items:center;justify-content:center;gap:.6rem;color:var(--accent);margin:.6rem 0 0}
.ra-orn::before,.ra-orn::after{content:"";width:46px;height:1px;background:currentColor;opacity:.5}
.ra-orn i{width:6px;height:6px;transform:rotate(45deg);border:1px solid currentColor}
.ra-left{text-align:left;margin:.4rem 0}
.ra-count{font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);text-align:right;padding-top:.4rem}

/* Tarjetas */
[class*="st-key-card_"]{position:relative;gap:.55rem!important;animation:fade .7s var(--ease) both}
[class*="st-key-view_"]{position:absolute!important;inset:0;z-index:2;margin:0!important}
[class*="st-key-view_"] div,[class*="st-key-view_"] button{width:100%!important;height:100%!important}
[class*="st-key-view_"] button{opacity:0!important;cursor:pointer}
[class*="st-key-card_"]:has(button:focus-visible){outline:1.5px solid var(--accent);outline-offset:4px}
.ra-img{position:relative;aspect-ratio:4/5;overflow:hidden;background:var(--bg2);border-radius:2px}
.ra-img img{width:100%;height:100%;object-fit:cover;display:block;transform:scale(1.001);transition:transform 1.4s var(--ease)}
.ra-img img.r{animation:inR .5s var(--ease)}
.ra-img img.l{animation:inL .5s var(--ease)}
[class*="st-key-card_"]:hover .ra-img img{transform:scale(1.045)}
.ra-img.sold img{filter:grayscale(1);opacity:.75}
.ra-badge{position:absolute;top:10px;left:10px;font-size:.6rem;letter-spacing:.18em;text-transform:uppercase;font-weight:500;padding:4px 8px;background:var(--surface);color:var(--text)}
.ra-badge.out{background:var(--text);color:var(--bg)}
.ra-dots{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);display:flex;gap:5px}
.ra-dots i{width:5px;height:5px;border-radius:50%;background:rgba(255,255,255,.55);transition:transform .4s var(--ease),background-color .4s}
.ra-dots i.on{background:#fff;transform:scale(1.35)}
.ra-quick{position:absolute;left:10px;right:10px;bottom:10px;padding:.55rem;text-align:center;background:var(--surface);color:var(--text);font-size:.64rem;letter-spacing:.2em;text-transform:uppercase;font-weight:500;opacity:0;transform:translateY(8px);transition:opacity .45s var(--ease),transform .45s var(--ease)}
[class*="st-key-card_"]:hover .ra-quick{opacity:1;transform:none}
[class*="st-key-card_"]:hover .ra-dots{opacity:0}
.ra-info{text-align:center;padding:0 .3rem}
.ra-brand{font-size:.62rem;letter-spacing:.22em;text-transform:uppercase;color:var(--muted);font-weight:500}
.ra-name{font-family:var(--serif);font-size:1.22rem;font-weight:500;color:var(--text);line-height:1.15;margin:.15rem 0 .35rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ra-chips{display:flex;flex-wrap:wrap;justify-content:center;gap:4px;margin-bottom:.4rem}
.chip{display:inline-flex;align-items:center;gap:4px;font-size:.66rem;padding:2px 7px;border:1px solid var(--line2);color:var(--muted);letter-spacing:.04em;white-space:nowrap}
.chip svg{width:10px;height:10px}
.chip.size{border-color:var(--accent);color:var(--accent);font-weight:500}
.ra-price{font-size:.92rem;letter-spacing:.06em;color:var(--text);font-weight:500}

/* Flechas del carrusel */
[class*="st-key-arw_"],[class*="st-key-garw_"]{position:relative;z-index:3;margin-top:-3.25rem!important;padding:0 .6rem;pointer-events:none}
[class*="st-key-garw_"]{margin-top:-3.9rem!important;padding:0 .9rem}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;justify-content:space-between!important}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) [data-testid="stColumn"]{width:auto!important;flex:0 0 auto!important;min-width:0!important}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) button{pointer-events:auto;width:30px!important;height:30px!important;min-height:30px!important;padding:0!important;border-radius:50%!important;background:rgba(255,253,248,.92)!important;color:#1C1813!important;border:none!important;opacity:0;transform:scale(.85)}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) button p,:is([class*="st-key-arw_"],[class*="st-key-garw_"]) button span{color:#1C1813!important}
[class*="st-key-card_"]:hover [class*="st-key-arw_"] button,[class*="st-key-garw_"] button{opacity:1;transform:none}
[class*="st-key-garw_"] button{width:40px!important;height:40px!important;min-height:40px!important}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) button:hover{background:#fff!important;transform:scale(1.08)!important}
[class*="st-key-card_"]:hover [class*="st-key-arw_"]{margin-top:-5.6rem!important}
@media (hover:none){[class*="st-key-arw_"] button{opacity:1;transform:none}.ra-quick{display:none}}

/* Ficha de producto */
.ra-crumb{font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin:1.2rem 0 .2rem}
.ra-crumb b{color:var(--text);font-weight:500}
.ra-thumbs{display:flex;gap:6px;margin-top:.6rem;overflow-x:auto}
.ra-thumbs img{width:54px;height:68px;object-fit:cover;opacity:.45;border:1px solid transparent;flex-shrink:0;transition:opacity .35s var(--ease)}
.ra-thumbs img.on{opacity:1;border-color:var(--accent)}
.ra-d{animation:fade .7s var(--ease) both}
.ra-d-brand{font-size:.7rem;letter-spacing:.24em;text-transform:uppercase;color:var(--accent);font-weight:500}
.ra-d-name{font-family:var(--serif);font-size:clamp(2.1rem,3.8vw,2.9rem);font-weight:400;line-height:1.03;color:var(--text);margin:.3rem 0 .7rem}
.ra-d-price{display:flex;align-items:center;gap:.9rem;margin-bottom:.9rem}
.ra-d-price b{font-size:1.35rem;letter-spacing:.04em;font-weight:500;color:var(--text)}
.ra-pill{font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;font-weight:500;padding:4px 9px;display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line2);color:var(--muted)}
.ra-pill.ok{color:var(--ok);border-color:currentColor}
.ra-pill.ok::before{content:"";width:5px;height:5px;border-radius:50%;background:currentColor}
.ra-d .ra-chips{justify-content:flex-start}
.ra-d-short{color:var(--muted);font-size:.95rem;font-weight:300;line-height:1.7;margin:.6rem 0 1.2rem;max-width:50ch}
.ra-cta{position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;gap:.6rem;width:100%;padding:.95rem 1rem;background:var(--text);color:var(--bg)!important;font-size:.74rem;letter-spacing:.22em;text-transform:uppercase;font-weight:500;text-decoration:none!important;transition:background-color .4s var(--ease)}
.ra-cta svg{width:16px;height:16px}
.ra-cta::after{content:"";position:absolute;inset:0;background:linear-gradient(105deg,transparent 40%,rgba(255,255,255,.22) 50%,transparent 60%);transform:translateX(-110%);transition:transform 1.1s var(--ease)}
.ra-cta:hover{background:var(--accent);color:var(--accent-ink)!important}
.ra-cta:hover::after{transform:translateX(110%)}
.ra-cta-row{display:grid;grid-template-columns:1fr 1fr;gap:.45rem;margin-top:.45rem}
.ra-cta.ghost{background:transparent;color:var(--text)!important;border:1px solid var(--line2);padding:.75rem .8rem}
.ra-cta.ghost:hover{border-color:var(--accent);color:var(--accent)!important;background:transparent}
.ra-specs{display:grid;grid-template-columns:repeat(3,1fr);border-top:1px solid var(--line);border-left:1px solid var(--line);margin:1.4rem 0}
.ra-specs div{border-right:1px solid var(--line);border-bottom:1px solid var(--line);padding:.7rem .8rem}
.ra-specs small{display:flex;align-items:center;gap:5px;color:var(--muted);font-size:.6rem;letter-spacing:.16em;text-transform:uppercase;margin-bottom:3px}
.ra-specs small svg{width:11px;height:11px;color:var(--accent)}
.ra-specs span{color:var(--text);font-size:.88rem}
.ra-desc h4{font-family:var(--sans)!important;font-size:.66rem!important;letter-spacing:.22em;text-transform:uppercase;font-weight:500!important;color:var(--accent)!important;margin:.6rem 0 .4rem!important;padding:0!important}
.ra-desc p{color:var(--text)!important;font-weight:300;line-height:1.8;font-size:.93rem;max-width:62ch}
.ra-desc ul{list-style:none;padding:0;margin:0}
.ra-desc li{padding:.45rem 0;border-bottom:1px solid var(--line);font-size:.88rem;display:flex;gap:.7rem}
.ra-desc li::before{content:"";width:5px;height:5px;margin-top:.55rem;transform:rotate(45deg);border:1px solid var(--accent);flex-shrink:0}

/* Cómo comprar */
.ra-steps{display:grid;grid-template-columns:repeat(3,1fr);gap:0;border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin-top:1rem}
.ra-step{padding:1.4rem 1.2rem;border-right:1px solid var(--line)}
.ra-step:last-child{border-right:none}
.ra-step .n{font-family:var(--serif);font-size:2.2rem;color:var(--accent);line-height:1;font-style:italic}
.ra-step b{display:block;font-weight:500;font-size:.95rem;color:var(--text);margin:.4rem 0 .2rem}
.ra-step span{font-size:.84rem;color:var(--muted);font-weight:300;line-height:1.55}

/* Perfiles, listas, tablas */
.ra-prof{display:flex;gap:1.1rem;align-items:center;flex-wrap:wrap;border:1px solid var(--line);background:var(--surface);padding:1.1rem 1.2rem;margin:1rem 0;animation:fade .6s var(--ease) both}
.ra-prof>img{width:68px;height:68px;border-radius:50%;object-fit:cover;box-shadow:0 0 0 3px var(--surface),0 0 0 4px var(--accent)}
.ra-prof .n{font-family:var(--serif);font-size:1.75rem;line-height:1.05;color:var(--text)}
.ra-prof .d{color:var(--muted);font-size:.8rem;margin-top:.3rem;display:flex;gap:.9rem;flex-wrap:wrap}
.ra-prof .d span{display:inline-flex;align-items:center;gap:5px}
.ra-prof .d svg{width:13px;height:13px;color:var(--accent)}
.ra-prof .k{display:flex;gap:1.6rem;margin-left:auto}
.ra-prof .k div{text-align:right}
.ra-prof .k b{display:block;font-family:var(--serif);font-size:1.5rem;color:var(--text);font-weight:500}
.ra-prof .k small{color:var(--muted);font-size:.62rem;letter-spacing:.16em;text-transform:uppercase}
.ra-row{display:flex;align-items:center;gap:.8rem;padding:.55rem;border:1px solid var(--line);background:var(--surface)}
.ra-row img{width:42px;height:52px;object-fit:cover;flex-shrink:0}
.ra-row .m{flex:1;min-width:0}
.ra-row .m b{display:block;color:var(--text);font-weight:500;font-size:.9rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ra-row .m small{color:var(--muted);font-size:.76rem}
.ra-row .v{font-weight:500;color:var(--text);font-size:.9rem;white-space:nowrap}
.ra-row.flat{border:none;padding:0;background:none}
.ra-table-wrap{overflow-x:auto;border:1px solid var(--line);background:var(--surface)}
.ra-table{width:100%;border-collapse:collapse;font-size:.84rem}
.ra-table th{text-align:left;color:var(--muted);font-weight:500;font-size:.62rem;letter-spacing:.16em;text-transform:uppercase;padding:.7rem .8rem;border-bottom:1px solid var(--line);white-space:nowrap}
.ra-table td{padding:.55rem .8rem;border-bottom:1px solid var(--line);color:var(--text);white-space:nowrap}
.ra-table tr:last-child td{border-bottom:none}
.ra-table tbody tr:hover td{background:var(--chip)}
.ra-table img{width:24px;height:24px;border-radius:50%;vertical-align:middle;margin-right:6px;object-fit:cover}
.ra-podium{display:grid;grid-template-columns:repeat(3,1fr);gap:.6rem;margin:.6rem 0 1rem}
.ra-pod{border:1px solid var(--line);background:var(--surface);padding:.9rem;display:flex;align-items:center;gap:.8rem}
.ra-pod.first{border-color:var(--accent)}
.ra-pod img{width:42px;height:42px;border-radius:50%;object-fit:cover}
.ra-pod .p{font-family:var(--serif);font-style:italic;font-size:1.8rem;color:var(--accent);width:1.2rem}
.ra-pod b{display:block;color:var(--text);font-size:.9rem;font-weight:500}
.ra-pod small{color:var(--muted);font-size:.74rem}
.st-key-authbox{border:1px solid var(--line);background:var(--surface);padding:1.6rem 1.5rem 1.3rem;margin-top:2rem;animation:fade .6s var(--ease) both}
.ra-auth{text-align:center;color:var(--accent)}
.ra-auth .ra-logo-svg{width:54px;height:54px}
.ra-auth h3{font-family:var(--serif)!important;font-size:2rem!important;font-weight:400!important;color:var(--text)!important;margin:.3rem 0 .1rem!important;padding:0!important}
.ra-auth p{color:var(--muted)!important;font-size:.85rem;font-weight:300}
.ra-avprev{display:flex;align-items:center;gap:.6rem;margin:-.2rem 0 .3rem}
.ra-avprev img{width:40px;height:40px;border-radius:50%;box-shadow:0 0 0 1px var(--line2)}
.ra-avprev span{color:var(--muted);font-size:.8rem}
.ra-empty{text-align:center;padding:2.6rem 1rem;color:var(--muted);border:1px dashed var(--line2);font-size:.88rem;font-weight:300}
.ra-empty b{display:block;font-family:var(--serif);font-size:1.5rem;color:var(--text);font-weight:400;margin-bottom:.2rem}
.ra-ownerset{display:flex;align-items:center;gap:.9rem}
.ra-ownerset img{width:60px;height:60px;object-fit:cover}
.ra-note{color:var(--muted);font-size:.84rem;font-weight:300}

/* Botón flotante de WhatsApp */
.ra-float{position:fixed;right:22px;bottom:22px;z-index:998;display:flex;align-items:center;gap:0;height:50px;padding:0 15px;border-radius:999px;background:var(--text);color:var(--bg)!important;text-decoration:none!important;box-shadow:0 12px 30px -12px var(--shadow);transition:gap .45s var(--ease),background-color .35s var(--ease);animation:fade 1s var(--ease) 1s both}
.ra-float svg{width:20px;height:20px;flex-shrink:0}
.ra-float span{max-width:0;overflow:hidden;white-space:nowrap;font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;font-weight:500;transition:max-width .45s var(--ease)}
.ra-float:hover{gap:.6rem;background:var(--accent);color:var(--accent-ink)!important}
.ra-float:hover span{max-width:160px}

/* Pie de página */
.ra-foot{margin:3.5rem -100vw 0;padding:2.6rem 100vw 1.2rem;background:var(--bg2);border-top:1px solid var(--line)}
.ra-foot-grid{display:grid;grid-template-columns:1.3fr 1fr 1fr;gap:2rem;max-width:1160px;margin:0 auto}
.ra-foot .ra-logo{justify-content:flex-start}
.ra-foot p{color:var(--muted)!important;font-size:.84rem;font-weight:300;margin-top:.8rem;max-width:34ch}
.ra-foot h5{font-family:var(--sans)!important;font-size:.64rem!important;letter-spacing:.22em;text-transform:uppercase;color:var(--accent)!important;font-weight:500!important;margin:0 0 .7rem!important;padding:0!important}
.ra-foot a.l{display:flex;align-items:center;gap:.5rem;color:var(--text)!important;text-decoration:none!important;font-size:.86rem;padding:.25rem 0;transition:color .3s var(--ease)}
.ra-foot a.l svg{width:14px;height:14px;color:var(--accent)}
.ra-foot a.l:hover{color:var(--accent)!important}
.ra-foot .li{font-size:.86rem;color:var(--text);padding:.25rem 0;font-weight:300}
.ra-copy{max-width:1160px;margin:2rem auto 0;padding-top:1rem;border-top:1px solid var(--line);text-align:center;font-size:.68rem;letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}

@keyframes fade{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}
@keyframes inR{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:none}}
@keyframes inL{from{opacity:0;transform:translateX(-20px)}to{opacity:1;transform:none}}
@keyframes draw{to{stroke-dashoffset:0}}
@keyframes curtain{0%{clip-path:inset(0 0 0 0)}100%{clip-path:inset(100% 0 0 0)}}
@keyframes sweep{0%{transform:translateY(0);opacity:1}92%{opacity:1}100%{transform:translateY(100vh);opacity:0}}

/* Celular */
@media (max-width:760px){
 html{font-size:14px}
 .block-container,[data-testid="stMainBlockContainer"]{padding:0 .8rem 1.5rem!important}
 .st-key-hdr [data-testid="stColumn"]:nth-child(2){flex:1 1 auto!important;width:auto!important}
 .st-key-hdr [data-testid="stColumn"]:not(:nth-child(2)){flex:0 0 auto!important;width:auto!important}
 .ra-hdr-note{display:none}
 .ra-logo-svg{width:38px;height:38px}
 .ra-word b{font-size:.92rem;letter-spacing:.12em;white-space:nowrap}
 .ra-word span{letter-spacing:.42em}
 .ra-intro{grid-template-columns:1fr;gap:1.6rem;padding:1.6rem 0}
 .ra-owner{display:grid;grid-template-columns:96px minmax(0,1fr);column-gap:1rem;align-items:start}
 .ra-owner-body{display:contents}
 .ra-sq{width:96px;height:96px;grid-row:1/4;grid-column:1}
 .ra-kicker,.ra-owner-name,.ra-owner-tag{grid-column:2}
 .ra-owner-name{font-size:1.6rem}
 .ra-owner-tag{margin-bottom:0}
 .ra-stack{grid-column:1/-1;max-width:none;margin-top:1.1rem;min-width:0}
 .ra-manifest h2{font-size:1.7rem!important}
 .ra-promises{grid-template-columns:1fr 1fr 1fr}
 [class*="st-key-grid_"]{gap:1.4rem!important}
 [class*="st-key-grid_"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:1.4rem .6rem!important}
 [class*="st-key-grid_"] [data-testid="stColumn"]{flex:1 1 calc(50% - .3rem)!important;min-width:calc(50% - .3rem)!important;width:calc(50% - .3rem)!important}
 .ra-specs{grid-template-columns:1fr 1fr}
 .ra-steps{grid-template-columns:1fr}
 .ra-step{border-right:none;border-bottom:1px solid var(--line)}
 .ra-step:last-child{border-bottom:none}
 .ra-prof .k{margin-left:0}
 .ra-podium{grid-template-columns:1fr}
 .ra-foot-grid{grid-template-columns:1fr;gap:1.4rem}
 .ra-float{right:14px;bottom:14px}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""


def inject_css():
    v = THEMES[ss.theme]
    root = ":root{" + "".join(f"--{k}:{val};" for k, val in v.items()) + "}"
    html(f"<style>{root}{CSS}</style>")
    old = ss.pop("_curtain", None)
    if old:  # cortina con el color del tema anterior que se levanta, con una línea de luz
        n = uuid.uuid4().hex[:6]
        html(f'<div class="ra-curtain" data-n="{n}" style="background:{THEMES[old]["bg"]}"></div>'
             f'<div class="ra-curtain-line" data-n="{n}" style="background:{v["accent"]}"></div>')


# ══════════════════════════════════════════════════════════════════════════
# 8 · COMPONENTES
# ══════════════════════════════════════════════════════════════════════════
def scroll_top():
    code = ("<script>(function(){const d=window.parent.document;"
            "['[data-testid=\"stMain\"]','section.main','[data-testid=\"stAppViewContainer\"]']"
            ".forEach(s=>{const e=d.querySelector(s);if(e&&e.scrollTo)e.scrollTo({top:0,behavior:'smooth'})});"
            f"window.parent.scrollTo({{top:0,behavior:'smooth'}});}})();/*{uuid.uuid4().hex}*/</script>")
    with st.container(key="scrolltop"):
        if hasattr(st, "iframe"):
            st.iframe(code, height=1)
        else:
            import streamlit.components.v1 as components
            components.html(code, height=0)


def logo_html() -> str:
    return (f'<div class="ra-logo">{LOGO}<div class="ra-word"><b>RISSOS ANGHELL</b>'
            '<span>STORE</span></div></div>')


def render_header(db, view):
    html('<div class="ra-announce">Entregas coordinadas en <b>Santiago</b> · '
         'Consultas por WhatsApp, Instagram o correo</div>')
    with st.container(key="hdr"):
        left, mid, right = st.columns([1, 1.6, 1], vertical_alignment="center")
        with left:
            if view == "home":
                html(f'<div class="ra-hdr-note">{esc(OWNER["city"])}</div>')
            elif st.button("Tienda", key="nav_shop", icon=":material/arrow_back:"):
                go("home")
        mid.markdown(logo_html(), unsafe_allow_html=True)
        with right:
            r1, r2 = st.columns([1, 1.5], vertical_alignment="center", gap="small")
            r1.button("Tema", key="theme_sw", on_click=_toggle_theme,
                      help="Tema oscuro" if ss.theme == "light" else "Tema claro")
            with r2:
                u = current_user(db)
                if u:
                    if st.button(u["name"].split()[0], key="nav_acc", icon=":material/person:",
                                 use_container_width=True):
                        go("profile")
                elif ss.role == "admin":
                    if st.button("Panel", key="nav_acc", icon=":material/admin_panel_settings:",
                                 use_container_width=True):
                        go("admin")
                elif st.button("Ingresar", key="nav_acc", icon=":material/person:", use_container_width=True):
                    go("login")


def contact_stack_html() -> str:
    mail = mailto("Contacto – Rissos Anghell Store", "Hola Benjamín,\n\n")
    wa = wa_link("Hola Benjamín, te escribo desde Rissos Anghell Store.")
    rows = [("wa", wa, "whatsapp", "WhatsApp", OWNER["whatsapp_display"], True),
            ("ig", IG_LINK, "instagram", "Instagram", "@" + OWNER["instagram"], True),
            ("ml", mail, "mail", "Correo electrónico", OWNER["email"], False)]
    return '<div class="ra-stack">' + "".join(
        f'<a class="ra-ct" href="{href}"{" target=_blank rel=noopener" if blank else ""}>'
        f'<span class="ic">{ICON[ic]}</span><span class="tx"><b>{lb}</b><span>{esc(val)}</span></span>'
        f'<span class="go">{ICON["arrow"]}</span></a>'
        for _, href, ic, lb, val, blank in rows) + "</div>"


def render_intro():
    html('<section class="ra-intro">'
         '<div class="ra-owner">'
         f'<div class="ra-sq"><img src="{owner_photo()}" alt="{esc(OWNER["name"])}"/></div>'
         '<div class="ra-owner-body"><div class="ra-kicker">Tienda de</div>'
         f'<div class="ra-owner-name">{esc(OWNER["name"])}</div>'
         f'<div class="ra-owner-tag">{esc(OWNER["tagline"])}</div>{contact_stack_html()}</div></div>'
         '<div class="ra-manifest"><h2>Piezas elegidas con calma, <em>revisadas una por una.</em></h2>'
         '<p>Perfumes, ropa y artículos de colección. Cada publicación muestra su talla, origen y estado '
         'reales, para que sepas exactamente lo que recibes.</p>'
         '<div class="ra-promises">'
         f'<div>{ICON["check"]}Originales<small>Estado real en cada ficha</small></div>'
         f'<div>{ICON["truck"]}Entrega coordinada<small>En Santiago</small></div>'
         f'<div>{ICON["chat"]}Respuesta rápida<small>Por tu canal favorito</small></div>'
         '</div></div></section>')


def section(kicker: str, title: str, sub: str = "", left: bool = False):
    html(f'<div class="ra-sec{" ra-left" if left else ""}">'
         + (f'<div class="k">{kicker}</div>' if kicker else "")
         + f'<div class="t">{title}</div>' + (f'<div class="s">{sub}</div>' if sub else "")
         + ("" if left else '<div class="ra-orn"><i></i></div>') + "</div>")


def empty(title: str, text: str):
    html(f'<div class="ra-empty"><b>{esc(title)}</b>{esc(text)}</div>')


def chips_html(p, with_brand=False) -> str:
    out = ""
    if p.get("size"):
        out += f'<span class="chip size">{esc(size_label(p))}</span>'
    if p.get("made_in"):
        out += f'<span class="chip">{ICON["globe"]}Made in {esc(p["made_in"])}</span>'
    if with_brand and p.get("condition"):
        out += f'<span class="chip">{esc(p["condition"])}</span>'
    return out


def card_image_html(p, idx: int, d: str, big: bool = False) -> str:
    imgs = p.get("images") or ["demo:bag:0"]
    sold = p["status"] != "Disponible"
    badge = f'<span class="ra-badge out">{esc(p["status"])}</span>' if sold else ""
    dots = "".join(f'<i class="{"on" if i == idx else ""}"></i>' for i in range(len(imgs))) if len(imgs) > 1 else ""
    quick = "" if big else '<div class="ra-quick">Ver detalle</div>'
    return (f'<div class="ra-img{" sold" if sold else ""}"><img class="{d}" src="{img_src(imgs[idx], thumb=not big)}" '
            f'alt="{esc(p["name"])}"/>{badge}<div class="ra-dots">{dots}</div>{quick}</div>')


def _step(prefix: str, pid: str, n: int, delta: int):
    k = f"{prefix}idx_{pid}"
    ss[k] = (ss.get(k, 0) + delta) % n
    ss[f"{prefix}dir_{pid}"] = "l" if delta < 0 else "r"


def carousel_arrows(prefix: str, ckey: str, pid: str, n: int):
    with st.container(key=ckey):
        a, b = st.columns(2)
        a.button("", key=f"btnp_{ckey}", icon=":material/chevron_left:", on_click=_step, args=(prefix, pid, n, -1))
        b.button("", key=f"btnn_{ckey}", icon=":material/chevron_right:", on_click=_step, args=(prefix, pid, n, 1))


@st.fragment
def product_card(p, scope: str = "h"):
    """Tarjeta aislada: cambiar foto solo recarga esta tarjeta (sin lag)."""
    pid = p["id"]
    imgs = p.get("images") or ["demo:bag:0"]
    n = len(imgs)
    idx = ss.get(f"idx_{pid}", 0) % n
    with st.container(key=f"card_{scope}_{pid}"):
        html(card_image_html(p, idx, ss.get(f"dir_{pid}", "r")))
        if n > 1:
            carousel_arrows("", f"arw_{scope}_{pid}", pid, n)
        html(f'<div class="ra-info"><div class="ra-brand">{esc(p.get("brand") or p.get("category"))}</div>'
             f'<div class="ra-name" title="{esc(p["name"])}">{esc(p["name"])}</div>'
             f'<div class="ra-chips">{chips_html(p)}</div><div class="ra-price">{money_html(p["price"])}</div></div>')
        if st.button("Ver detalle", key=f"view_{scope}_{pid}", use_container_width=True):
            ss.view = "product"
            st.query_params.clear()
            st.query_params["producto"] = pid
            st.rerun()


def product_grid(items, scope="h", cols_n=4):
    html("<style>" + "".join(f".st-key-card_{scope}_{p['id']}{{animation-delay:{min(i, 11) * .06:.2f}s}}"
                             for i, p in enumerate(items)) + "</style>")
    with st.container(key=f"grid_{scope}"):
        for start in range(0, len(items), cols_n):
            cols = st.columns(cols_n, gap="medium")
            for j, p in enumerate(items[start:start + cols_n]):
                with cols[j]:
                    product_card(p, scope)


# ══════════════════════════════════════════════════════════════════════════
# 9 · VISTAS DE LA TIENDA
# ══════════════════════════════════════════════════════════════════════════
def render_home(db):
    render_intro()
    section("Catálogo", "La colección", "Toca cualquier pieza para ver sus fotos, medidas y origen.")

    present = [c for c in CATEGORIES if any(p["category"] == c for p in db["products"])]
    cat = st.pills("Categoría", ["Todo"] + present, default="Todo",
                   label_visibility="collapsed", key="cat_pills") or "Todo"
    f1, f2, f3 = st.columns([2.4, 1.2, 1], vertical_alignment="center")
    q = f1.text_input("Buscar", placeholder="Buscar por nombre, marca o talla", key="search",
                      label_visibility="collapsed", icon=":material/search:")
    sort = f2.selectbox("Ordenar", SORTS, key="sort", label_visibility="collapsed")
    only = f3.toggle("Solo disponibles", key="only_avail")

    items = db["products"]
    if cat != "Todo":
        items = [p for p in items if p["category"] == cat]
    if only:
        items = [p for p in items if p["status"] == "Disponible"]
    if q:
        ql = q.lower().strip()
        items = [p for p in items if ql in " ".join(str(p.get(k, "")) for k in
                                                     ("name", "brand", "size", "made_in", "category", "short")).lower()]
    if sort == "Precio: menor a mayor":
        items = sorted(items, key=lambda p: p["price"])
    elif sort == "Precio: mayor a menor":
        items = sorted(items, key=lambda p: -p["price"])
    elif sort == "Más recientes":
        items = sorted(items, key=lambda p: p.get("created", ""), reverse=True)
    else:
        items = sorted(items, key=lambda p: p["status"] != "Disponible")

    html(f'<div class="ra-count">{len(items)} {"pieza" if len(items) == 1 else "piezas"}</div>')
    if items:
        product_grid(items, "h")
    else:
        empty("Sin resultados", "Prueba otra categoría o borra la búsqueda.")

    section("Así de simple", "Cómo comprar")
    html('<div class="ra-steps">'
         '<div class="ra-step"><div class="n">01</div><b>Elige tu pieza</b>'
         '<span>Revisa fotos, talla y origen en la ficha de cada artículo.</span></div>'
         '<div class="ra-step"><div class="n">02</div><b>Consulta el stock</b>'
         '<span>El botón Consultar arma el correo con el producto y su link. Solo envíalo.</span></div>'
         '<div class="ra-step"><div class="n">03</div><b>Coordinamos la entrega</b>'
         '<span>Acordamos punto y horario en Santiago. Pagas al recibir o por transferencia.</span></div>'
         '</div>')


@st.fragment
def gallery(p):
    pid = p["id"]
    imgs = p.get("images") or ["demo:bag:0"]
    n = len(imgs)
    idx = ss.get(f"gidx_{pid}", 0) % n
    html(card_image_html(p, idx, ss.get(f"gdir_{pid}", "r"), big=True))
    if n > 1:
        carousel_arrows("g", f"garw_{pid}", pid, n)
        html('<div class="ra-thumbs">' + "".join(
            f'<img class="{"on" if i == idx else ""}" src="{img_src(e, thumb=True)}"/>' for i, e in enumerate(imgs))
             + "</div>")


def render_product(db, pid):
    p = get_product(db, pid)
    if not p:
        st.write("")
        empty("Esta pieza ya no está publicada", "Puede que se haya vendido. Revisa la colección.")
        st.write("")
        if st.button("Ver la colección", type="primary"):
            go("home")
        return
    html(f'<div class="ra-crumb">Tienda / {esc(p["category"])} / <b>{esc(p["name"])}</b></div>')
    left, right = st.columns([1, 1.05], gap="large")
    with left:
        gallery(p)
    with right:
        sold = p["status"] != "Disponible"
        subject, body = consult_message(db, p)
        sl = size_label(p)
        wa_txt = (f"Hola Benjamín, quiero consultar el stock de: {p['name']}" + (f" ({sl})" if sl else "")
                  + f" – {money(p['price'])}\n{product_link(db, p['id'])}")
        specs = [("ruler", "Talla" if p.get("category") in SIZED else "Medida", p.get("size") or "No aplica"),
                 ("globe", "Made in", p.get("made_in") or "—"), ("tag", "Marca", p.get("brand") or "—"),
                 ("spark", "Condición", p.get("condition") or "—"), ("box", "Categoría", p.get("category")),
                 ("calendar", "Publicado", fmt_date(p.get("created")))]
        desc = esc(p.get("description"))
        det = "".join(f"<li>{esc(x)}</li>" for x in (p.get("details") or []) if str(x).strip())
        html('<div class="ra-d">'
             f'<div class="ra-d-brand">{esc(p.get("brand") or p.get("category"))}</div>'
             f'<div class="ra-d-name">{esc(p["name"])}</div>'
             f'<div class="ra-d-price"><b>{money_html(p["price"])}</b>'
             f'<span class="ra-pill {"out" if sold else "ok"}">{esc(p["status"])}</span></div>'
             f'<div class="ra-chips">{chips_html(p, with_brand=True)}</div>'
             f'<div class="ra-d-short">{esc(p.get("short"))}</div>'
             f'<a class="ra-cta" href="{mailto(subject, body)}">{ICON["mail"]}'
             f'{"Consultar disponibilidad" if sold else "Consultar"}</a>'
             '<div class="ra-cta-row">'
             f'<a class="ra-cta ghost" href="{wa_link(wa_txt)}" target="_blank" rel="noopener">{ICON["whatsapp"]}WhatsApp</a>'
             f'<a class="ra-cta ghost" href="{gmail_link(subject, body)}" target="_blank" rel="noopener">{ICON["mail"]}Gmail</a>'
             '</div><div class="ra-specs">'
             + "".join(f"<div><small>{ICON[i]}{esc(k)}</small><span>{esc(v)}</span></div>" for i, k, v in specs)
             + '</div><div class="ra-desc">'
             + (f"<h4>Descripción</h4><p>{desc}</p>" if desc else "")
             + (f"<h4 style='margin-top:1.1rem!important'>Detalles</h4><ul>{det}</ul>" if det else "")
             + "</div></div>")
        st.caption("Link directo de esta pieza")
        st.code(product_link(db, p["id"]), language=None)

    related = [x for x in db["products"] if x["id"] != p["id"] and x["category"] == p["category"]]
    related += [x for x in db["products"] if x["id"] != p["id"] and x not in related]
    related = sorted(related, key=lambda x: x["status"] != "Disponible")[:4]
    if related:
        section("Sigue mirando", "También te puede gustar")
        product_grid(related, "r")


# ══════════════════════════════════════════════════════════════════════════
# 10 · CUENTAS DE USUARIO
# ══════════════════════════════════════════════════════════════════════════
def avatar_picker(prefix: str, default: str | None = None):
    names = list(AVATAR_COLORS)
    key = f"{prefix}_color"
    if key not in ss:
        ss[key] = default if default in names else random.choice(names)
    name = st.radio("Color del avatar", names, horizontal=True, key=key)
    html(f'<div class="ra-avprev"><img src="{avatar_svg(AVATAR_COLORS[name])}"/><span>Vista previa</span></div>')
    return name


def opt_field(label: str, key: str, placeholder: str, current: str = ""):
    """Campo opcional con Agregar / No agregar."""
    if st.radio(label, ["No agregar", "Agregar"], horizontal=True, key=f"{key}_opt",
                index=1 if current else 0) == "Agregar":
        return st.text_input(label, value=current, key=key, placeholder=placeholder,
                             label_visibility="collapsed").strip()
    return ""


def render_login(db):
    _, mid, _ = st.columns([1, 1.45, 1])
    with mid, st.container(key="authbox"):
        html(f'<div class="ra-auth">{LOGO}<h3>Tu cuenta</h3>'
             '<p>Regístrate y tus compras quedarán guardadas en tu perfil.</p></div>')
        tab_user, tab_admin = st.tabs(["Usuario", "Administrador"])
        with tab_user:
            mode = st.segmented_control("Modo", ["Iniciar sesión", "Crear cuenta"], default="Iniciar sesión",
                                        key="auth_mode", label_visibility="collapsed") or "Iniciar sesión"
            if mode == "Iniciar sesión":
                phone = st.text_input("Teléfono", placeholder="+56 9 1234 5678", key="li_phone")
                pw = st.text_input("Contraseña", type="password", key="li_pw")
                if st.button("Iniciar sesión", type="primary", use_container_width=True, key="li_btn"):
                    u = find_user_by_phone(db, phone)
                    if u and check_pw(pw, u.get("pw")):
                        ss.role, ss.user_id = "user", u["id"]
                        flash(f"Hola de nuevo, {u['name'].split()[0]}", ":material/waving_hand:")
                        go("home")
                    st.error("El teléfono o la contraseña no coinciden.")
            else:
                register_form(db)
        with tab_admin:
            apw = st.text_input("Contraseña de administrador", type="password", key="adm_pw")
            if st.button("Entrar al panel", type="primary", use_container_width=True, key="adm_btn"):
                if check_admin(db, apw):
                    ss.role, ss.user_id = "admin", None
                    flash("Sesión de administrador iniciada", ":material/admin_panel_settings:")
                    go("admin")
                st.error("Contraseña incorrecta.")


def register_form(db):
    name = st.text_input("Nombre *", key="rg_name", placeholder="Ej: Pepito Pérez")
    phone = st.text_input("Teléfono *", key="rg_phone", placeholder="+56 9 1234 5678")
    c1, c2 = st.columns(2)
    pw = c1.text_input("Contraseña *", type="password", key="rg_pw", placeholder="Mínimo 4 caracteres")
    pw2 = c2.text_input("Repetir contraseña *", type="password", key="rg_pw2")
    email = opt_field("Correo electrónico (opcional)", "rg_email", "tu@correo.com")
    location = opt_field("Ubicación (opcional)", "rg_loc", "Ej: Maipú, Santiago")
    ph = st.radio("Foto de perfil", ["No, usar avatar", "Sí, subir foto"], horizontal=True, key="rg_ph_opt")
    photo, color = None, None
    if ph.startswith("Sí"):
        photo = st.file_uploader("Foto", type=["jpg", "jpeg", "png", "webp"], key="rg_photo",
                                 label_visibility="collapsed")
    else:
        color = avatar_picker("rg")
    if st.button("Crear cuenta", type="primary", use_container_width=True, key="rg_btn"):
        n = norm_phone(phone)
        existing = find_user_by_phone(db, phone)
        errors = [m for ok, m in [
            (name.strip(), "Escribe tu nombre."),
            (len(n) >= 8, "Escribe un teléfono válido."),
            (len(pw) >= 4, "La contraseña debe tener al menos 4 caracteres."),
            (pw == pw2, "Las contraseñas no coinciden."),
            (not email or re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email), "El correo no tiene un formato válido."),
            (not (existing and existing.get("pw")), "Ya existe una cuenta con ese teléfono. Inicia sesión."),
        ] if not ok]
        if errors:
            for e in errors:
                st.error(e)
            return
        data = dict(name=name.strip(), phone=n, phone_display=phone.strip(), email=email, location=location,
                    pw=hash_pw(pw), photo=save_upload(photo, 600) if photo else None,
                    avatar_color=AVATAR_COLORS.get(color or "Rojo"))
        if existing:
            existing.update(data)
            uid = existing["id"]
        else:
            uid = new_id()
            db["users"].append(dict(id=uid, gender="Prefiero no decirlo", gender_custom="", created=now_iso(), **data))
        save_db(db)
        ss.role, ss.user_id = "user", uid
        flash(f"Cuenta creada. Bienvenido, {name.split()[0]}", ":material/celebration:")
        go("profile")


def profile_header(db, u):
    c, units, total = user_stats(db, u["id"])
    gender = u.get("gender_custom") if u.get("gender") == "Personalizado" and u.get("gender_custom") else u.get("gender")
    bits = [("phone", u.get("phone_display") or u["phone"]), ("mail", u.get("email")), ("pin", u.get("location")),
            ("gender", gender), ("calendar", f"Desde {fmt_date(u.get('created'))}")]
    html(f'<div class="ra-prof"><img src="{user_avatar(u)}"/><div><div class="n">{esc(u["name"])}</div>'
         f'<div class="d">{"".join(f"<span>{ICON[i]}{esc(v)}</span>" for i, v in bits if v)}</div></div>'
         f'<div class="k"><div><b>{c}</b><small>compras</small></div><div><b>{units}</b><small>unidades</small></div>'
         f'<div><b>{money_html(total)}</b><small>total</small></div></div></div>')


def purchases_list(db, purchases, admin=False):
    if not purchases:
        empty("Sin compras registradas", "Regístralas en la pestaña Registrar venta." if admin
              else "Cuando Benjamín registre tu compra, aparecerá aquí.")
        return
    for pu in purchases:
        prod = get_product(db, pu.get("product_id"))
        thumb = img_src((prod.get("images") or [""])[0], thumb=True) if prod else demo_svg("bag", 0)
        meta = f"{fmt_date(pu.get('date'))} · {pu.get('qty', 1)} u."
        meta += f" · Talla {esc(pu['size'])}" if pu.get("size") else ""
        meta += f" · {esc(pu['note'])}" if pu.get("note") else ""
        row = (f'<div class="ra-row"><img src="{thumb}"/><div class="m"><b>{esc(pu["product_name"])}</b>'
               f'<small>{meta}</small></div><div class="v">{money_html(pu.get("total"))}</div></div>')
        if not admin:
            html(row)
            continue
        a, b = st.columns([10, 1], vertical_alignment="center")
        a.markdown(row, unsafe_allow_html=True)
        if b.button("", key=f"delpu_{pu['id']}", icon=":material/delete:", help="Quitar esta compra"):
            db["purchases"] = [x for x in db["purchases"] if x["id"] != pu["id"]]
            save_db(db)
            flash("Compra eliminada", ":material/delete:")
            st.rerun()


def render_profile(db):
    u = current_user(db)
    if not u:
        go("login")
    profile_header(db, u)
    t1, t2 = st.tabs(["Mis compras", "Mis datos"])
    with t1:
        purchases_list(db, user_purchases(db, u["id"]))
    with t2:
        c1, c2 = st.columns(2)
        name = c1.text_input("Nombre", value=u["name"], key="pf_name")
        c2.text_input("Teléfono", value=u.get("phone_display") or u["phone"], disabled=True,
                      help="Para cambiarlo, escríbele a Benjamín.")
        email = opt_field("Correo electrónico", "pf_email", "tu@correo.com", u.get("email", ""))
        location = opt_field("Ubicación", "pf_loc", "Ej: Maipú, Santiago", u.get("location", ""))
        g = u.get("gender") if u.get("gender") in GENDERS else "Prefiero no decirlo"
        gender = st.radio("Género", GENDERS, index=GENDERS.index(g), horizontal=True, key="pf_gender")
        gcustom = st.text_input("¿Cómo te identificas?", value=u.get("gender_custom", ""),
                                key="pf_gcustom") if gender == "Personalizado" else ""
        ph = st.radio("Foto de perfil", ["Mantener", "Subir foto nueva", "Usar avatar"], horizontal=True, key="pf_ph")
        new_photo, color = None, None
        if ph == "Subir foto nueva":
            new_photo = st.file_uploader("Foto", type=["jpg", "jpeg", "png", "webp"], key="pf_photo",
                                         label_visibility="collapsed")
        elif ph == "Usar avatar":
            color = avatar_picker("pf", next((k for k, v in AVATAR_COLORS.items() if v == u.get("avatar_color")), None))
        with st.expander("Cambiar contraseña"):
            npw = st.text_input("Nueva contraseña", type="password", key="pf_npw")
            npw2 = st.text_input("Repetir nueva contraseña", type="password", key="pf_npw2")
        b1, b2 = st.columns(2)
        if b1.button("Guardar cambios", type="primary", use_container_width=True, key="pf_save"):
            if not name.strip():
                st.error("El nombre no puede quedar vacío.")
            elif npw and (len(npw) < 4 or npw != npw2):
                st.error("La nueva contraseña debe tener 4+ caracteres y coincidir.")
            else:
                u.update(name=name.strip(), email=email, location=location, gender=gender, gender_custom=gcustom.strip())
                if new_photo:
                    delete_image(u.get("photo"))
                    u["photo"] = save_upload(new_photo, 600)
                elif color:
                    delete_image(u.get("photo"))
                    u.update(photo=None, avatar_color=AVATAR_COLORS[color])
                if npw:
                    u["pw"] = hash_pw(npw)
                save_db(db)
                flash("Cambios guardados")
                st.rerun()
        if b2.button("Cerrar sesión", use_container_width=True, key="pf_out"):
            logout()


# ══════════════════════════════════════════════════════════════════════════
# 11 · PANEL DE ADMINISTRACIÓN
# ══════════════════════════════════════════════════════════════════════════
def _set_status(pid):
    db = load_db()
    p = get_product(db, pid)
    if p:
        p["status"] = ss[f"status_{pid}"]
        save_db(db)
        ss["_flash"] = (f"{p['name']}: {p['status']}", ":material/sell:")


def product_form_fields(prefix, p=None):
    p = p or {}
    c1, c2 = st.columns([2, 1])
    name = c1.text_input("Nombre *", value=p.get("name", ""), key=f"{prefix}_name")
    category = c2.selectbox("Categoría", CATEGORIES, key=f"{prefix}_cat",
                            index=CATEGORIES.index(p["category"]) if p.get("category") in CATEGORIES else 0)
    c3, c4, c5 = st.columns(3)
    price = c3.number_input("Precio (CLP)", min_value=0, step=500, value=int(p.get("price", 0)), key=f"{prefix}_price")
    size = c4.text_input("Talla o medida", value=p.get("size", ""), placeholder="L, 42, 100 ml…", key=f"{prefix}_size")
    mi = p.get("made_in", "China")
    made = c5.selectbox("Made in", MADE_IN, key=f"{prefix}_made",
                        index=MADE_IN.index(mi) if mi in MADE_IN else len(MADE_IN) - 1)
    made_o = st.text_input("País (si elegiste Otro)", value="" if mi in MADE_IN else mi, key=f"{prefix}_made_o")
    c6, c7, c8 = st.columns(3)
    brand = c6.text_input("Marca", value=p.get("brand", ""), key=f"{prefix}_brand")
    cond = c7.selectbox("Condición", CONDITIONS, key=f"{prefix}_cond",
                        index=CONDITIONS.index(p["condition"]) if p.get("condition") in CONDITIONS else 0)
    status = c8.selectbox("Estado", STATUSES, key=f"{prefix}_status",
                          index=STATUSES.index(p["status"]) if p.get("status") in STATUSES else 0)
    short = st.text_input("Descripción corta", value=p.get("short", ""), key=f"{prefix}_short")
    desc = st.text_area("Descripción completa", value=p.get("description", ""), key=f"{prefix}_desc", height=90)
    det = st.text_area("Detalles (uno por línea)", value="\n".join(p.get("details") or []), key=f"{prefix}_det", height=90)
    return dict(name=name.strip(), category=category, price=int(price), size=size.strip(),
                made_in=(made_o.strip() or "Otro") if made == "Otro" else made, brand=brand.strip(),
                condition=cond, status=status, short=short.strip(), description=desc.strip(),
                details=[x.strip() for x in det.splitlines() if x.strip()])


def admin_products(db):
    with st.expander("Publicar una pieza nueva", icon=":material/add:"):
        with st.form("add_prod", clear_on_submit=True, border=False):
            data = product_form_fields("np")
            imgs = st.file_uploader("Fotos (la primera será la portada)", type=["jpg", "jpeg", "png", "webp"],
                                    accept_multiple_files=True, key="np_imgs")
            ok = st.form_submit_button("Publicar", type="primary", use_container_width=True)
        if ok:
            if not data["name"]:
                st.error("La pieza necesita un nombre.")
            else:
                data.update(id=new_id(), created=now_iso(),
                            images=[save_upload(f) for f in (imgs or [])] or ["demo:bag:0"])
                db["products"].insert(0, data)
                save_db(db)
                flash(f"Publicado: {data['name']}")
                st.rerun()

    if not db["products"]:
        empty("Catálogo vacío", "Publica tu primera pieza arriba.")
    for p in db["products"]:
        pid = p["id"]
        with st.container(border=True):
            c0, c1, c2, c3 = st.columns([.6, 3.4, 1.6, 1.3], vertical_alignment="center")
            c0.markdown(f'<div class="ra-row flat"><img src="{img_src((p.get("images") or [""])[0], thumb=True)}"/></div>',
                        unsafe_allow_html=True)
            c1.markdown(f'<div class="ra-row flat"><div class="m"><b>{esc(p["name"])}</b><small>{money_html(p["price"])}'
                        f' · {esc(p["category"])}{" · " + esc(size_label(p)) if p.get("size") else ""}'
                        f' · {len(p.get("images") or [])} fotos</small></div></div>', unsafe_allow_html=True)
            ss[f"status_{pid}"] = p["status"]
            c2.selectbox("Estado", STATUSES, key=f"status_{pid}", on_change=_set_status, args=(pid,),
                         label_visibility="collapsed")
            with c3:
                b1, b2 = st.columns(2)
                if b1.button("", key=f"see_{pid}", icon=":material/visibility:", help="Ver en la tienda",
                             use_container_width=True):
                    go("product", pid)
                if b2.button("", key=f"del_{pid}", icon=":material/delete:", help="Eliminar",
                             use_container_width=True):
                    ss.confirm_del = pid
            if ss.get("confirm_del") == pid:
                st.warning(f"¿Eliminar «{p['name']}»? Las compras ya registradas se mantienen.")
                y, n = st.columns(2)
                if y.button("Sí, eliminar", key=f"yes_{pid}", type="primary", use_container_width=True):
                    for e in p.get("images") or []:
                        delete_image(e)
                    db["products"] = [x for x in db["products"] if x["id"] != pid]
                    save_db(db)
                    ss.confirm_del = None
                    flash("Pieza eliminada", ":material/delete:")
                    st.rerun()
                if n.button("Cancelar", key=f"no_{pid}", use_container_width=True):
                    ss.confirm_del = None
                    st.rerun()
            with st.expander("Editar", icon=":material/edit:"):
                imgs = p.get("images") or []
                if imgs:
                    html('<div class="ra-thumbs">' + "".join(
                        f'<img class="on" src="{img_src(e, thumb=True)}" title="Foto {i + 1}"/>'
                        for i, e in enumerate(imgs)) + "</div>")
                with st.form(f"edit_{pid}", border=False):
                    data = product_form_fields(f"ed_{pid}", p)
                    rm = st.multiselect("Fotos a quitar", list(range(len(imgs))), key=f"ed_rm_{pid}",
                                        format_func=lambda i: f"Foto {i + 1}")
                    cover = st.selectbox("Portada", list(range(len(imgs))) or [0], key=f"ed_cv_{pid}",
                                         format_func=lambda i: f"Foto {i + 1}")
                    add = st.file_uploader("Agregar fotos", type=["jpg", "jpeg", "png", "webp"],
                                           accept_multiple_files=True, key=f"ed_add_{pid}")
                    saved = st.form_submit_button("Guardar cambios", type="primary", use_container_width=True)
                if saved:
                    if not data["name"]:
                        st.error("La pieza necesita un nombre.")
                    else:
                        keep = [e for i, e in enumerate(imgs) if i not in rm]
                        if imgs and cover not in rm and imgs[cover] in keep:
                            keep.remove(imgs[cover])
                            keep.insert(0, imgs[cover])
                        for i in rm:
                            delete_image(imgs[i])
                        keep += [save_upload(f) for f in (add or [])]
                        p.update(data, images=keep or ["demo:bag:0"])
                        save_db(db)
                        flash("Pieza actualizada")
                        st.rerun()


def admin_sales(db):
    if not db["users"]:
        empty("Todavía no hay clientes", "Cuando alguien cree su cuenta, o lo agregues en Clientes, podrás registrar sus compras aquí.")
        return
    if not db["products"]:
        st.info("Publica al menos una pieza para registrar ventas.")
        return
    html('<p class="ra-note">Ej: Pepito compró la Polera roja y ya se la entregaste. Queda guardado en su perfil.</p>')
    users = sorted(db["users"], key=lambda u: u["name"].lower())
    c1, c2 = st.columns(2)
    uid = c1.selectbox("Cliente", [u["id"] for u in users], key="sale_user",
                       format_func=lambda i: (lambda u: f"{u['name']} · {u.get('phone_display') or u['phone']}")(get_user(db, i)))
    pid = c2.selectbox("Pieza", [p["id"] for p in db["products"]], key="sale_prod",
                       format_func=lambda i: (lambda p: f"{p['name']} · {money(p['price'])}"
                                              + ("" if p["status"] == "Disponible" else f" · {p['status']}"))(get_product(db, i)))
    p = get_product(db, pid)
    c3, c4, c5 = st.columns(3)
    qty = c3.number_input("Cantidad", min_value=1, step=1, value=1, key="sale_qty")
    price = c4.number_input("Precio unitario", min_value=0, step=500, value=int(p["price"]), key=f"sale_price_{pid}")
    d = c5.date_input("Fecha de entrega", value=date.today(), key="sale_date", format="DD/MM/YYYY")
    note = st.text_input("Nota (opcional)", placeholder="Ej: entregado en metro Los Héroes", key="sale_note")
    mark = st.checkbox("Marcar la pieza como Agotado", value=True, key="sale_mark")
    if st.button("Registrar venta", type="primary", use_container_width=True, key="sale_btn"):
        db["purchases"].append(dict(id=new_id(), user_id=uid, product_id=pid, product_name=p["name"],
                                    size=p.get("size", ""), qty=int(qty), unit_price=int(price),
                                    total=int(qty) * int(price), date=d.isoformat(), note=note.strip(),
                                    created=now_iso()))
        if mark:
            p["status"] = "Agotado"
        save_db(db)
        flash(f"Venta registrada a {get_user(db, uid)['name']}", ":material/receipt_long:")
        st.rerun()

    recent = sorted(db["purchases"], key=lambda x: x.get("created", ""), reverse=True)[:8]
    if recent:
        section("", "Últimas ventas", left=True)
        rows = "".join(f"<tr><td>{fmt_date(x['date'])}</td><td>{esc((get_user(db, x['user_id']) or {}).get('name', '—'))}</td>"
                       f"<td>{esc(x['product_name'])}</td><td>{x['qty']}</td><td>{money_html(x['total'])}</td></tr>"
                       for x in recent)
        html('<div class="ra-table-wrap"><table class="ra-table"><thead><tr><th>Fecha</th><th>Cliente</th>'
             f'<th>Pieza</th><th>Cant.</th><th>Total</th></tr></thead><tbody>{rows}</tbody></table></div>')


def admin_clients(db):
    stats = []
    for u in db["users"]:
        c, units, total = user_stats(db, u["id"])
        stats.append((u, c, units, total, (user_purchases(db, u["id"]) or [{}])[0].get("date", "")))
    stats.sort(key=lambda x: (x[3], x[1]), reverse=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Clientes", len(db["users"]))
    m2.metric("Ventas", len(db["purchases"]))
    m3.metric("Total vendido", money(sum(int(x.get("total", 0)) for x in db["purchases"])))

    with st.expander("Agregar cliente manualmente", icon=":material/person_add:"):
        with st.form("add_client", clear_on_submit=True, border=False):
            a, b = st.columns(2)
            cn, cp = a.text_input("Nombre *"), b.text_input("Teléfono *")
            c, d = st.columns(2)
            ce, cl = c.text_input("Correo (opcional)"), d.text_input("Ubicación (opcional)")
            ok = st.form_submit_button("Agregar cliente", type="primary")
        if ok:
            if not cn.strip() or len(norm_phone(cp)) < 8:
                st.error("Escribe nombre y un teléfono válido.")
            elif find_user_by_phone(db, cp):
                st.error("Ya existe un cliente con ese teléfono.")
            else:
                db["users"].append(dict(id=new_id(), name=cn.strip(), phone=norm_phone(cp), phone_display=cp.strip(),
                                        email=ce.strip(), location=cl.strip(), gender="Prefiero no decirlo",
                                        gender_custom="", photo=None, pw=None, created=now_iso(),
                                        avatar_color=random.choice(list(AVATAR_COLORS.values()))))
                save_db(db)
                flash("Cliente agregado", ":material/person_add:")
                st.rerun()

    if not stats:
        empty("Aún no hay clientes", "Comparte la tienda para que se registren.")
        return

    top = [s for s in stats if s[3] > 0][:3]
    if top:
        section("", "Quién te compra más", left=True)
        html('<div class="ra-podium">' + "".join(
            f'<div class="ra-pod{" first" if i == 0 else ""}"><div class="p">{i + 1}</div>'
            f'<img src="{user_avatar(u)}"/><div><b>{esc(u["name"])}</b><small>{c} compras · {money_html(t)}</small></div></div>'
            for i, (u, c, _, t, _) in enumerate(top)) + "</div>")

    rows = "".join(
        f"<tr><td>{i}</td><td><img src='{user_avatar(u)}'/>{esc(u['name'])}</td><td>{esc(u.get('phone_display') or u['phone'])}</td>"
        f"<td>{esc(u.get('email') or '—')}</td><td>{esc(u.get('location') or '—')}</td><td>{c}</td><td>{units}</td>"
        f"<td><b>{money_html(total)}</b></td><td>{fmt_date(last) if last else '—'}</td></tr>"
        for i, (u, c, units, total, last) in enumerate(stats, 1))
    html('<div class="ra-table-wrap"><table class="ra-table"><thead><tr><th>#</th><th>Cliente</th><th>Teléfono</th>'
         '<th>Correo</th><th>Ubicación</th><th>Compras</th><th>Unid.</th><th>Total</th><th>Última</th></tr></thead>'
         f'<tbody>{rows}</tbody></table></div>')

    section("", "Perfil del cliente", left=True)
    uid = st.selectbox("Cliente", [s[0]["id"] for s in stats], key="cl_pick",
                       format_func=lambda i: get_user(db, i)["name"], label_visibility="collapsed")
    u = get_user(db, uid)
    profile_header(db, u)
    if not u.get("pw"):
        st.caption("Agregado manualmente: si se registra con este teléfono, tomará esta cuenta y su historial.")
    purchases_list(db, user_purchases(db, uid), admin=True)
    st.write("")
    if st.button("Eliminar cliente", key=f"delu_{uid}", icon=":material/person_remove:"):
        ss.confirm_user = uid
    if ss.get("confirm_user") == uid:
        st.warning(f"Se eliminará la cuenta de {u['name']} y su historial de compras.")
        y, n = st.columns(2)
        if y.button("Sí, eliminar", type="primary", key=f"delu_y_{uid}", use_container_width=True):
            delete_image(u.get("photo"))
            db["users"] = [x for x in db["users"] if x["id"] != uid]
            db["purchases"] = [x for x in db["purchases"] if x["user_id"] != uid]
            save_db(db)
            ss.confirm_user = None
            flash("Cliente eliminado", ":material/delete:")
            st.rerun()
        if n.button("Cancelar", key=f"delu_n_{uid}", use_container_width=True):
            ss.confirm_user = None
            st.rerun()


def admin_settings(db):
    found = find_owner_photo()
    html(f'<div class="ra-ownerset"><img src="{owner_photo()}"/><div class="ra-note">'
         + (f"Foto cargada desde <b>{esc(found.relative_to(BASE_DIR))}</b>." if found else
            "No se encontró <b>benja.jpeg</b>. Súbela a la raíz del repositorio y aparecerá sola.")
         + "</div></div>")
    st.divider()
    section("", "Link de la tienda", "Se usa en los correos de consulta. Si publicas la app, pega aquí su dirección.", left=True)
    bu = st.text_input("Dirección pública", value=db["settings"].get("base_url", ""), key="set_base",
                       placeholder=app_base_url(db), label_visibility="collapsed")
    if st.button("Guardar link", key="set_base_btn"):
        db["settings"]["base_url"] = bu.strip()
        save_db(db)
        flash("Link guardado", ":material/link:")
        st.rerun()
    st.divider()
    section("", "Contraseña de administrador", left=True)
    a, b, c = st.columns(3)
    cur = a.text_input("Actual", type="password", key="set_cur")
    new = b.text_input("Nueva", type="password", key="set_new")
    new2 = c.text_input("Repetir nueva", type="password", key="set_new2")
    if st.button("Cambiar contraseña", key="set_pw_btn"):
        if not check_admin(db, cur):
            st.error("La contraseña actual no es correcta.")
        elif len(new) < 6 or new != new2:
            st.error("La nueva contraseña debe tener 6+ caracteres y coincidir.")
        else:
            db["settings"]["admin_pw"] = hash_pw(new)
            save_db(db)
            flash("Contraseña actualizada", ":material/key:")
            st.rerun()
    st.divider()
    st.download_button("Descargar respaldo (JSON)", json.dumps(db, ensure_ascii=False, indent=2),
                       file_name=f"rissos_respaldo_{date.today().isoformat()}.json", mime="application/json")


def render_admin(db):
    if ss.role != "admin":
        go("login")
    h, o = st.columns([5, 1], vertical_alignment="bottom")
    with h:
        section("Administración", "Panel de la tienda", left=True)
    with o:
        if st.button("Salir", key="adm_out", icon=":material/logout:", use_container_width=True):
            logout()
    t1, t2, t3, t4 = st.tabs(["Piezas", "Registrar venta", "Clientes", "Ajustes"])
    with t1:
        admin_products(db)
    with t2:
        admin_sales(db)
    with t3:
        admin_clients(db)
    with t4:
        admin_settings(db)


# ══════════════════════════════════════════════════════════════════════════
# 12 · PIE DE PÁGINA Y BOTÓN FLOTANTE
# ══════════════════════════════════════════════════════════════════════════
def render_footer():
    html('<div class="ra-foot"><div class="ra-foot-grid">'
         f'<div>{logo_html()}<p>{esc(OWNER["tagline"])} Piezas revisadas y entregas coordinadas en Santiago.</p></div>'
         '<div><h5>Contacto</h5>'
         f'<a class="l" href="{wa_link()}" target="_blank" rel="noopener">{ICON["whatsapp"]}{OWNER["whatsapp_display"]}</a>'
         f'<a class="l" href="{IG_LINK}" target="_blank" rel="noopener">{ICON["instagram"]}@{OWNER["instagram"]}</a>'
         f'<a class="l" href="{mailto("Contacto – Rissos Anghell Store")}">{ICON["mail"]}{OWNER["email"]}</a></div>'
         '<div><h5>Información</h5>'
         f'<div class="li">{esc(OWNER["city"])}</div><div class="li">Entregas coordinadas</div>'
         '<div class="li">Pago al recibir o por transferencia</div></div>'
         f'</div><div class="ra-copy">{esc(COPYRIGHT)}</div></div>'
         f'<a class="ra-float" href="{wa_link("Hola Benjamín, te escribo desde Rissos Anghell Store.")}" '
         f'target="_blank" rel="noopener" aria-label="Escribir por WhatsApp">{ICON["whatsapp"]}<span>Escríbeme</span></a>')


# ══════════════════════════════════════════════════════════════════════════
# 13 · MAIN
# ══════════════════════════════════════════════════════════════════════════
def main():
    db = load_db()
    inject_css()
    if "_flash" in ss:
        msg, icon = ss.pop("_flash")
        st.toast(msg, icon=icon)

    pid = st.query_params.get("producto")
    view = "product" if pid else ("home" if ss.view == "product" else ss.view)

    render_header(db, view)
    {"product": lambda: render_product(db, pid), "login": lambda: render_login(db),
     "profile": lambda: render_profile(db), "admin": lambda: render_admin(db)}.get(view, lambda: render_home(db))()
    render_footer()

    nav_key = f"{view}:{pid or ''}"
    if ss.get("_last_nav") not in (None, nav_key):
        scroll_top()
    ss["_last_nav"] = nav_key


main()
