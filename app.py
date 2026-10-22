# -*- coding: utf-8 -*-
"""
RISSOS ANGHELL STORE · Benjamín Espinoza
───────────────────────────────────────────────
Ejecutar:  streamlit run app.py
Tu foto:   sube "benja.jpeg" a la raíz del repositorio (al lado de app.py) o a /assets.
Admin:     contraseña inicial "anghell2026" (cámbiala en Panel › Ajustes).
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

def _favicon() -> Image.Image:
    """Círculo negro con un carrito rojo al medio (dibujado a 4x y reducido = bordes suaves)."""
    from PIL import ImageDraw
    S = 256
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, S - 1, S - 1), fill=(11, 11, 11, 255))
    red, w = (255, 43, 62, 255), 15
    k = S / 48  # mismo dibujo que el logo (viewBox 48)
    P = lambda x, y: (x * k, y * k)
    d.line([P(10.5, 14), P(14.5, 14), P(18.4, 29.6), P(34, 29.6), P(37, 18.5), P(15.4, 18.5)],
           fill=red, width=w, joint="curve")
    for cx in (20.6, 31.6):
        x, y = P(cx, 36)
        d.ellipse((x - 13, y - 13, x + 13, y + 13), fill=red)
    for x, y in (P(10.5, 14),):
        d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=red)
    return im.resize((64, 64), Image.LANCZOS)


st.set_page_config(page_title="Rissos Anghell Store", page_icon=_favicon(),
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
        "tagline": "Compra y venta de artículos, ropa y más.",
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
AVATAR_COLORS = {"Rojo": "#C8102E", "Blanco": "#F2F2F2", "Negro": "#111111", "Azul": "#24489C",
                 "Verde": "#2F6B50", "Morado": "#5B3F8C", "Naranjo": "#D06A28", "Dorado": "#B08A3E",
                 "Rosado": "#C9708A", "Gris": "#7A7A7A"}


def _svg_url(svg: str) -> str:
    return 'url("data:image/svg+xml,' + quote(svg) + '")'


_SUN = _svg_url('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#B08A3E" '
                'stroke-width="2.2" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2'
                'M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>')
_MOON = _svg_url('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#FF2D4A">'
                 '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>')

# Claro: blanco · dorado · negro   |   Oscuro: negro · blanco · rojo neón mate
THEMES = {
    "light": {"bg": "#FFFFFF", "bg2": "#F6F4EF", "text": "#0B0B0B", "muted": "#6E6E6E", "faint": "#A9A9A9",
              "line": "rgba(11,11,11,.08)", "line2": "rgba(11,11,11,.2)", "accent": "#B08A3E",
              "accent-ink": "#FFFFFF", "accent-soft": "rgba(176,138,62,.14)", "glow": "none",
              "drop-glow": "none", "head": "rgba(255,255,255,.96)", "ok": "#3F7D4E",
              "sw-track": "#F1EBDD", "sw-knob": "#FFFFFF", "sw-x": "0px", "sw-icon": _SUN, "red": "#D7102C"},
    "dark": {"bg": "#050505", "bg2": "#0F0F0F", "text": "#F4F4F4", "muted": "#8C8C8C", "faint": "#565656",
             "line": "rgba(244,244,244,.08)", "line2": "rgba(244,244,244,.2)", "accent": "#FF2D4A",
             "accent-ink": "#FFFFFF", "accent-soft": "rgba(255,45,74,.14)",
             "glow": "0 0 24px rgba(255,45,74,.45)", "drop-glow": "drop-shadow(0 0 5px rgba(255,45,74,.75))",
             "head": "rgba(5,5,5,.94)", "ok": "#5FD07A",
             "sw-track": "#1E080C", "sw-knob": "#050505", "sw-x": "30px", "sw-icon": _MOON, "red": "#FF2D4A"},
}

# ── Íconos de marca, con sus colores reales ──────────────────────────────
WA_PATH = ("M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.16-.17.2-.35.22-.64.08"
           "-.3-.15-1.26-.46-2.39-1.48-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.17.2"
           "-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27"
           ".3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.88 1.21 3.07.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.7.63.71.22 1.36"
           ".19 1.87.12.57-.09 1.76-.72 2-1.41.25-.7.25-1.29.18-1.41-.08-.13-.28-.2-.57-.35zM12.05 21.79h-.01a9.87"
           " 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.86 9.86 0 0 1-1.51-5.26c0-5.45 4.44-9.88 9.89"
           "-9.88 2.64 0 5.12 1.03 6.99 2.9a9.83 9.83 0 0 1 2.89 6.99c0 5.45-4.44 9.88-9.88 9.88zm8.41-18.3A11.82"
           " 11.82 0 0 0 12.05 0C5.5 0 .16 5.34.16 11.89c0 2.1.55 4.14 1.59 5.95L.06 24l6.3-1.65a11.88 11.88 0 0 0"
           " 5.69 1.45c6.55 0 11.89-5.34 11.89-11.89 0-3.18-1.24-6.17-3.48-8.42z")
BRAND = {
    "whatsapp": f'<svg viewBox="0 0 24 24"><path fill="#25D366" d="{WA_PATH}"/></svg>',
    "whatsapp_white": f'<svg viewBox="0 0 24 24"><path fill="#FFFFFF" d="{WA_PATH}"/></svg>',
    "instagram": (
        '<svg viewBox="0 0 24 24"><defs><radialGradient id="rag" cx="28%" cy="105%" r="140%">'
        '<stop offset="0" stop-color="#FDF497"/><stop offset=".08" stop-color="#FDF497"/>'
        '<stop offset=".45" stop-color="#FD5949"/><stop offset=".62" stop-color="#D6249F"/>'
        '<stop offset=".92" stop-color="#285AEB"/></radialGradient></defs>'
        '<rect width="24" height="24" rx="6.5" fill="url(#rag)"/>'
        '<rect x="5.4" y="5.4" width="13.2" height="13.2" rx="4" fill="none" stroke="#fff" stroke-width="1.7"/>'
        '<circle cx="12" cy="12" r="3.15" fill="none" stroke="#fff" stroke-width="1.7"/>'
        '<circle cx="16.15" cy="7.85" r="1" fill="#fff"/></svg>'),
    "gmail": (
        '<svg viewBox="0 0 48 48"><path fill="#4CAF50" d="M45 16.2l-5 2.75-5 4.75V40h7c1.66 0 3-1.34 3-3V16.2z"/>'
        '<path fill="#1E88E5" d="M3 16.2l3.61 1.71L13 23.7V40H6c-1.66 0-3-1.34-3-3V16.2z"/>'
        '<path fill="#E53935" d="M35 11.2L24 19.45 13 11.2 12 17l1 6.7 11 8.25 11-8.25 1-6.7z"/>'
        '<path fill="#C62828" d="M3 12.3v3.9l10 7.5V11.2L9.88 8.86A4.3 4.3 0 0 0 7.3 8C4.92 8 3 9.92 3 12.3z"/>'
        '<path fill="#FBC02D" d="M45 12.3v3.9l-10 7.5V11.2l3.12-2.34A4.3 4.3 0 0 1 40.7 8c2.38 0 4.3 1.92 4.3 4.3z"/></svg>'),
}
_I = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" '
      'stroke-linecap="round" stroke-linejoin="round">')
ICON = {
    "arrow": _I + '<path d="M4 12h16M14 6l6 6-6 6"/></svg>',
    "phone": _I + '<path d="M21 16.5v2.6a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 3.1 3.3 2 2 0 0 1 5.1 1h2.6a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8.8 8.6a16 16 0 0 0 6 6l1.1-1.1a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    "mail": _I + '<rect x="3" y="5" width="18" height="14" rx="1.5"/><path d="m3.5 6.5 8.5 6 8.5-6"/></svg>',
    "pin": _I + '<path d="M19 10c0 5.5-7 11-7 11s-7-5.5-7-11a7 7 0 0 1 14 0z"/><circle cx="12" cy="10" r="2.5"/></svg>',
    "calendar": _I + '<rect x="3" y="4.5" width="18" height="16.5" rx="1.5"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/></svg>',
    "gender": _I + '<circle cx="10" cy="14" r="5"/><path d="M14 10l6-6M15 4h5v5"/></svg>',
}

# ── Logo: carrito rojo sobre fondo negro ─────────────────────────────────
LOGO = (
    '<svg class="ra-cart" viewBox="0 0 48 48" aria-label="Rissos Anghell Store">'
    '<rect width="48" height="48" rx="13" fill="#0B0B0B"/>'
    '<rect x=".5" y=".5" width="47" height="47" rx="12.5" fill="none" stroke="#FFFFFF" stroke-opacity=".10"/>'
    '<g class="ra-cart-g">'
    '<path d="M9 12.5h4l4.2 16.7a2.4 2.4 0 0 0 2.3 1.8h13.4a2.4 2.4 0 0 0 2.3-1.7L38.2 18H14.4" fill="none" '
    'stroke="#FF2B3E" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
    '<path d="M19.6 23.6h14.6" stroke="#FF2B3E" stroke-opacity=".5" stroke-width="2.2" stroke-linecap="round"/>'
    '<circle cx="20.4" cy="36.4" r="2.3" fill="#FF2B3E"/><circle cx="32.4" cy="36.4" r="2.3" fill="#FF2B3E"/>'
    '</g></svg>'
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


def meta_line(p) -> str:
    parts = [size_label(p), f"Made in {p['made_in']}" if p.get("made_in") else ""]
    return " · ".join(x for x in parts if x)


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
# 3 · IMÁGENES (en caché: la página no se pone lenta)
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
PALETTES = [("#F3F1EC", "#E6E1D8", "#1A1A1A"), ("#121212", "#050505", "#E9E2D3"),
            ("#EEE7DA", "#DDD1BC", "#8A6A2E"), ("#1C0B0F", "#0A0405", "#FF4D63"),
            ("#F7F7F7", "#E9E9E9", "#3A3A3A"), ("#D8D1C4", "#C5BBA9", "#2A2420")]


@st.cache_data(show_spinner=False, max_entries=300)
def demo_svg(kind: str, idx: int) -> str:
    a, b, fg = PALETTES[idx % len(PALETTES)]
    return b64svg(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1066">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{a}"/>'
        f'<stop offset="1" stop-color="{b}"/></linearGradient></defs><rect width="800" height="1066" fill="url(#g)"/>'
        f'<g fill="{fg}" fill-opacity=".05" stroke="{fg}" stroke-width="4.5" stroke-linecap="round" '
        f'stroke-linejoin="round" transform="translate(0 40)">{ILLUS.get(kind, ILLUS["bag"])}</g>'
        f'<text x="400" y="1000" font-size="18" letter-spacing="9" text-anchor="middle" fill="{fg}" '
        'fill-opacity=".45" font-family="Helvetica,Arial,sans-serif">FOTO DE MUESTRA</text></svg>')


@st.cache_data(show_spinner=False, max_entries=800)
def _file_uri(path: str, mtime: float, portrait: int = 0) -> str:
    p = Path(path)
    if portrait:  # retrato 4:5 recortado (foto de perfil)
        img = ImageOps.fit(ImageOps.exif_transpose(Image.open(p)).convert("RGB"), (portrait, int(portrait * 1.25)),
                           Image.LANCZOS, centering=(0.5, 0.3))
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
    img.thumbnail((560, 560))
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
    fg = "#111111" if (r * 299 + g * 587 + b * 114) / 1000 > 170 else "#FFFFFF"
    return b64svg(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><clipPath id="c"><circle cx="50" '
        f'cy="50" r="50"/></clipPath></defs><g clip-path="url(#c)"><rect width="100" height="100" fill="{color}"/>'
        f'<circle cx="50" cy="39" r="16" fill="{fg}" fill-opacity=".9"/>'
        f'<path d="M15 100c0-21 15-34 35-34s35 13 35 34z" fill="{fg}" fill-opacity=".9"/></g></svg>')


def user_avatar(u) -> str:
    return img_src(u["photo"], thumb=True) if u.get("photo") else avatar_svg(u.get("avatar_color") or "#C8102E")


def find_owner_photo() -> Path | None:
    for folder in (BASE_DIR, ASSETS_DIR):
        for name in OWNER["photo_names"]:
            if (folder / name).exists():
                return folder / name
    return None


def owner_photo() -> str:
    p = find_owner_photo()
    if p:
        return _file_uri(str(p), p.stat().st_mtime, 560)
    return b64svg('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 500"><rect width="400" height="500" '
                  'fill="#111"/><text x="200" y="285" font-size="110" text-anchor="middle" fill="#B08A3E" '
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
         ["100% algodón", "Corte regular fit", "Cuello redondo reforzado", "Lavar en frío"], "tshirt", [0, 3, 4]),
        ("Pantalón Jean negro", "Ropa", 24990, "42", "Bangladesh", "Denim Co.", "Usado, como nuevo", "Disponible",
         "Jean negro de corte recto, usado dos veces.",
         "Jean negro de mezclilla firme con un toque de elasticidad. Corte recto que funciona con zapatillas o botines. Sin desgaste visible.",
         ["98% algodón, 2% elastano", "Corte recto", "5 bolsillos", "Tiro medio"], "jeans", [1, 4, 5]),
        ("Figura de Freezer", "Figuras", 34990, "", "China", "Banpresto", "Nuevo", "Disponible",
         "Figura de colección de Dragon Ball, en su caja.",
         "Figura de Freezer en su forma final, con detalles pintados y base incluida. Ideal para colección; caja en buen estado.",
         ["Altura aprox.: 18 cm", "Material: PVC", "Base incluida", "Caja original"], "figure", [2, 1, 0]),
        ("Monitor 144Hz", "Tecnología", 159990, "", "Taiwán", "Genérico 24\"", "Usado, como nuevo", "Disponible",
         "24 pulgadas, Full HD, 144 Hz y 1 ms.",
         "Monitor gamer de 24 pulgadas con panel de 144 Hz, ideal para juegos competitivos. Sin píxeles muertos, con cables y caja.",
         ["24\" Full HD 1920×1080", "144 Hz, 1 ms", "HDMI y DisplayPort", "Incluye cables"], "monitor", [4, 1, 5]),
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
# 7 · ESTILOS — editorial, sin cajas; solo se anima transform/opacity
# ══════════════════════════════════════════════════════════════════════════
CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500;600;700&display=swap');
:root{--ease:cubic-bezier(.22,.8,.24,1);--sans:'Inter Tight','Helvetica Neue',Helvetica,Arial,sans-serif}
html{font-size:15px}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--bg)!important;color:var(--text)!important;font-family:var(--sans);-webkit-font-smoothing:antialiased}
.stApp,[data-testid="stMain"]{overflow-x:hidden!important}
[data-testid="stMain"]{scroll-behavior:smooth}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer,[data-testid="stStatusWidget"],[data-testid="stSidebarCollapsedControl"],[data-testid="stAppDeployButton"]{display:none!important}
.block-container,[data-testid="stMainBlockContainer"]{padding:.5rem 2.4rem 0!important;max-width:1240px!important}
[data-testid="stVerticalBlock"]{gap:.8rem}
.stApp [data-testid="stMarkdownContainer"] p,.stApp [data-testid="stMarkdownContainer"] li{color:var(--text);font-size:.92rem;font-weight:400}
[data-testid="stWidgetLabel"] p{color:var(--muted)!important;font-size:.72rem!important;font-weight:500!important;letter-spacing:.06em}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:var(--muted)!important;font-size:.76rem!important}
::selection{background:var(--accent);color:var(--accent-ink)}
::-webkit-scrollbar{width:7px;height:7px}::-webkit-scrollbar-thumb{background:var(--line2);border-radius:7px}
:focus-visible{outline:1.5px solid var(--accent)!important;outline-offset:3px}
.st-key-scrolltop{position:absolute!important;height:0!important;overflow:hidden;visibility:hidden;pointer-events:none}

/* Campos minimalistas */
.stApp input,.stApp textarea{color:var(--text)!important;-webkit-text-fill-color:var(--text)!important;caret-color:var(--accent);font-size:.92rem!important;font-family:var(--sans)!important}
.stApp input::placeholder,.stApp textarea::placeholder{color:var(--faint)!important;-webkit-text-fill-color:var(--faint)!important}
[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="select"]>div,[data-testid$="RootElement"],.react-aria-ComboBox [role="group"],[data-testid="stSelectbox"] [role="group"],[data-testid="stMultiSelect"] [role="group"]{background:transparent!important;border:none!important;border-bottom:1px solid var(--line2)!important;border-radius:0!important;box-shadow:none!important}
[data-baseweb="textarea"]{background:transparent!important;border:1px solid var(--line2)!important;border-radius:10px!important}
[data-testid$="RootElement"]:focus-within,[data-baseweb="input"]:focus-within,.react-aria-ComboBox [role="group"]:focus-within{border-bottom-color:var(--text)!important}
.react-aria-ComboBox button{color:var(--muted)!important;background:transparent!important}
[role="listbox"],.react-aria-Popover,.react-aria-ListBox,[data-baseweb="popover"] ul,[data-baseweb="popover"] [data-baseweb="menu"]{background:var(--bg)!important;border:1px solid var(--line2)!important;border-radius:10px!important}
[role="option"],[data-baseweb="popover"] li{color:var(--text)!important;background:transparent!important}
[role="option"][data-focused="true"],[role="option"][aria-selected="true"],[role="option"]:hover,[data-baseweb="popover"] li:hover{background:var(--bg2)!important}
[data-baseweb="select"] *{color:var(--text)!important}
[data-testid="stNumberInput"] button{background:transparent!important;color:var(--text)!important;border:none!important}
[data-testid="stRadio"] label p,[data-testid="stCheckbox"] label p,[data-testid="stToggle"] label p{color:var(--text)!important;font-weight:400!important;font-size:.88rem!important}
[data-testid="stFileUploaderDropzone"]{background:var(--bg2)!important;border:1px dashed var(--line2)!important;border-radius:12px!important}
[data-testid="stFileUploaderDropzone"] *{color:var(--muted)!important}
[data-testid="stFileUploaderFile"] *{color:var(--text)!important}
[data-baseweb="calendar"],[data-baseweb="calendar"] *{background-color:var(--bg)!important;color:var(--text)!important}

/* Botones */
.stButton button,.stFormSubmitButton button,.stDownloadButton button{background:transparent!important;color:var(--text)!important;border:1px solid var(--line2)!important;border-radius:999px!important;min-height:2.4rem;padding:.3rem 1.1rem!important;transition:transform .25s var(--ease),opacity .25s var(--ease)!important}
.stButton button p,.stFormSubmitButton button p,.stDownloadButton button p{color:inherit!important;font-family:var(--sans)!important;font-weight:500!important;font-size:.82rem!important}
.stButton button:hover,.stFormSubmitButton button:hover,.stDownloadButton button:hover{border-color:var(--text)!important}
.stButton button:active{transform:scale(.97)}
.stApp button[kind="primary"],.stApp button[kind="primaryFormSubmit"],.stApp [data-testid^="stBaseButton-primary"]{background:var(--text)!important;color:var(--bg)!important;border-color:var(--text)!important}
.stApp button[kind="primary"]:hover,.stApp [data-testid^="stBaseButton-primary"]:hover{opacity:.86}
[data-testid="stButtonGroup"] button[role="radio"]{border:1px solid transparent!important;border-radius:999px!important;background:transparent!important;color:var(--muted)!important;padding:.25rem .9rem!important;min-height:2rem!important}
[data-testid="stButtonGroup"] button[role="radio"] p{color:inherit!important;font-size:.82rem!important;font-weight:500!important}
[data-testid="stButtonGroup"] button[role="radio"]:hover{color:var(--text)!important}
[data-testid="stButtonGroup"] button[aria-checked="true"]{color:var(--bg)!important;background:var(--text)!important}

/* Pestañas, expanders, contenedores */
.stTabs [data-baseweb="tab-list"]{gap:1.6rem;border-bottom:1px solid var(--line);background:transparent}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;padding:.7rem 0}
.stTabs [data-baseweb="tab"] p{color:inherit!important;font-size:.84rem!important;font-weight:500!important}
.stTabs [aria-selected="true"]{color:var(--text)!important}
.stTabs [data-baseweb="tab-highlight"]{background:var(--text)!important;height:1.5px}
.stTabs [data-baseweb="tab-border"]{display:none}
[data-testid="stExpander"] details{background:transparent!important;border:none!important;border-bottom:1px solid var(--line)!important;border-radius:0!important}
[data-testid="stExpander"] summary{padding-left:0!important}
[data-testid="stExpander"] summary,[data-testid="stExpander"] summary p,[data-testid="stExpander"] summary span{color:var(--text)!important;font-size:.86rem;font-weight:500}
[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stForm"]{border:none!important;background:transparent!important;padding:0!important}
[data-testid="stMetric"]{border-top:1px solid var(--line);padding:.9rem 0}
[data-testid="stMetricValue"]{color:var(--text)!important;font-size:2rem!important;font-weight:500}
[data-testid="stMetricLabel"] p{color:var(--muted)!important;font-size:.76rem!important}
[data-testid="stCode"] pre{background:var(--bg2)!important;border-radius:10px!important;border:none}
[data-testid="stCode"] code{color:var(--text)!important;white-space:pre-wrap!important;word-break:break-all;font-size:.76rem!important}
[data-testid="stAlert"]{border-radius:10px!important}
hr{border-color:var(--line)!important;margin:1.4rem 0!important}

/* Cabecera */
.st-key-hdr{position:sticky;top:0;z-index:999;background:var(--bg);margin:0!important;padding:.6rem 0}
.st-key-hdr [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;align-items:center;gap:.6rem!important}
.st-key-hdr [data-testid="stColumn"]{min-width:0!important}
.st-key-hdr .stButton button{border:none!important;min-height:2.1rem;padding:.2rem .5rem!important}
.st-key-hdr .stButton button:hover{opacity:.7}
.ra-brand{display:flex;align-items:center;gap:.75rem;white-space:nowrap}
.ra-cart{width:40px;height:40px;flex-shrink:0;display:block}
.ra-cart-g{transform-box:fill-box;transform-origin:center;animation:cartIn .9s var(--ease) .1s backwards}
.ra-brand:hover .ra-cart-g{transform:translateX(2px);transition:transform .4s var(--ease)}
.ra-brand b{display:block;font-size:1.02rem;font-weight:600;letter-spacing:-.01em;color:var(--text);line-height:1.1}
.ra-brand span{display:block;font-size:.72rem;color:var(--muted);letter-spacing:.18em;text-transform:uppercase;margin-top:2px}
/* Switch de tema flotante (abajo a la derecha) */
.st-key-theme_sw{position:fixed!important;right:24px;bottom:24px;z-index:1000;width:auto!important}
.st-key-theme_sw::before{content:"";position:absolute;inset:-6px;border-radius:999px;border:1.5px solid var(--red);opacity:0;pointer-events:none}
.st-key-theme_sw button{position:relative;width:64px!important;min-width:64px!important;height:34px!important;min-height:34px!important;padding:0!important;border-radius:999px!important;background:var(--sw-track)!important;border:1px solid var(--line2)!important;overflow:hidden;box-shadow:0 8px 24px -10px rgba(0,0,0,.45)}
.st-key-theme_sw button:hover{border-color:var(--red)!important}
.st-key-theme_sw button p,.st-key-theme_sw button span{font-size:0!important;opacity:0}
.st-key-theme_sw button::before{content:"";position:absolute;top:50%;left:0;width:100%;height:3px;margin-top:-1.5px;border-radius:3px;opacity:0;pointer-events:none;background:linear-gradient(90deg,transparent,var(--red) 55%,transparent)}
.st-key-theme_sw button::after{content:"";position:absolute;top:4px;left:4px;width:24px;height:24px;border-radius:50%;background:var(--sw-icon) center/14px no-repeat,var(--sw-knob);box-shadow:0 1px 5px rgba(0,0,0,.3);transform:translateX(var(--sw-x));transition:transform .55s cubic-bezier(.68,-.35,.27,1.35)}
@keyframes dashR{0%{opacity:0;transform:translateX(-100%) scaleX(.4)}35%{opacity:1}100%{opacity:0;transform:translateX(100%) scaleX(1.2)}}
@keyframes dashL{0%{opacity:0;transform:translateX(100%) scaleX(.4)}35%{opacity:1}100%{opacity:0;transform:translateX(-100%) scaleX(1.2)}}
@keyframes ring{0%{opacity:.9;transform:scale(.92)}100%{opacity:0;transform:scale(1.35)}}
.ra-fade{position:fixed;inset:0;z-index:99998;pointer-events:none;animation:fadeOut .6s var(--ease) forwards}

/* Portada: foto + nombre + redes, a la izquierda y centrado en pantalla */
.ra-hero{min-height:calc(72vh - 64px);display:flex;align-items:center;padding:2rem 0}
.ra-me{display:flex;align-items:center;gap:2.4rem}
.ra-photo{width:212px;height:264px;flex-shrink:0;border-radius:22px;overflow:hidden;background:var(--bg2);animation:photoIn 1s var(--ease) backwards}
.ra-photo img{width:100%;height:100%;object-fit:cover;display:block}
.ra-info{min-width:0}
.ra-hello{font-size:.86rem;color:var(--red);font-weight:600;animation:rise .8s var(--ease) .15s backwards}
.ra-name{font-size:clamp(2.2rem,4.6vw,3.4rem);font-weight:600;letter-spacing:-.035em;line-height:1.02;color:var(--text);margin:.3rem 0 .5rem;animation:rise .8s var(--ease) .22s backwards}
.ra-tag{font-size:.95rem;color:var(--muted);margin-bottom:1.4rem;animation:rise .8s var(--ease) .3s backwards}
.ra-socials{display:flex;flex-direction:column;gap:.35rem;max-width:340px}
.ra-so{display:flex;align-items:center;gap:.8rem;padding:.55rem .2rem;color:var(--text)!important;text-decoration:none!important;border-radius:12px;animation:rise .8s var(--ease) backwards}
.ra-so:nth-child(1){animation-delay:.38s}.ra-so:nth-child(2){animation-delay:.46s}.ra-so:nth-child(3){animation-delay:.54s}
.ra-so svg{width:26px;height:26px;flex-shrink:0;display:block;transition:transform .35s var(--ease)}
.ra-so .tx{line-height:1.2;min-width:0}
.ra-so b{display:block;font-size:.88rem;font-weight:600;color:var(--text)}
.ra-so small{display:block;font-size:.8rem;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ra-so:hover svg{transform:scale(1.12)}
.ra-so:hover b{color:var(--accent)}

/* Mi colección */
.ra-sec{display:flex;align-items:baseline;justify-content:space-between;gap:1rem;padding-top:1.2rem;margin-bottom:.4rem}
.ra-sec .t{font-size:1.9rem;font-weight:600;letter-spacing:-.03em;line-height:1.1;color:var(--text)}
.ra-sec span{font-size:.82rem;color:var(--muted)}
.ra-anchor{position:relative;top:-80px;height:0}

/* Tarjetas: abiertas, alturas fijas, aparecen al hacer scroll */
[class*="st-key-grid_"]{gap:2.4rem!important}
[class*="st-key-card_"]{position:relative;gap:.65rem!important;animation:rise .7s var(--ease) backwards}
@supports (animation-timeline:view()){[class*="st-key-card_"]{animation:reveal linear backwards!important;animation-timeline:view()!important;animation-range:entry 0% entry 55%!important;animation-delay:0s!important}}
[class*="st-key-view_"]{position:absolute!important;inset:0;z-index:2;margin:0!important}
[class*="st-key-view_"] div,[class*="st-key-view_"] button{width:100%!important;height:100%!important}
[class*="st-key-view_"] button{opacity:0!important;cursor:pointer}
[class*="st-key-card_"]:has(button:focus-visible){outline:1.5px solid var(--accent);outline-offset:4px;border-radius:14px}
.ra-img{position:relative;aspect-ratio:3/4;overflow:hidden;background:var(--bg2);border-radius:14px;isolation:isolate}
.ra-img.big{border-radius:20px}
.ra-img img{width:100%;height:100%;object-fit:cover;display:block;transition:transform 1.1s var(--ease);backface-visibility:hidden}
.ra-img img.r{animation:inR .45s var(--ease)}
.ra-img img.l{animation:inL .45s var(--ease)}
[class*="st-key-card_"]:hover .ra-img img{transform:scale(1.04)}
.ra-img.sold img{filter:grayscale(1);opacity:.7}
.ra-tag2{position:absolute;top:10px;left:10px;font-size:.66rem;font-weight:600;color:var(--text);background:var(--bg);padding:4px 9px;border-radius:999px}
.ra-bars{position:absolute;left:12px;right:12px;bottom:10px;display:flex;gap:4px}
.ra-bars i{flex:1;height:2px;border-radius:2px;background:rgba(255,255,255,.4)}
.ra-bars i.on{background:rgba(255,255,255,.95)}
.ra-pinfo{padding:0 2px}
.ra-pname{font-size:.9rem;font-weight:500;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ra-pmeta{font-size:.78rem;color:var(--muted);margin:.15rem 0 .3rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;height:1.15em}
.ra-price{font-size:.9rem;font-weight:600;color:var(--text)}

/* Flechas del carrusel (superpuestas, no mueven nada) */
[class*="st-key-arw_"],[class*="st-key-garw_"]{position:relative;z-index:3;margin-top:-3.9rem!important;padding:0 .6rem;pointer-events:none;height:2.4rem}
[class*="st-key-garw_"]{margin-top:-4.4rem!important;padding:0 1rem;height:2.8rem}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;justify-content:space-between!important}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) [data-testid="stColumn"]{width:auto!important;flex:0 0 auto!important;min-width:0!important}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) button{pointer-events:auto;width:30px!important;height:30px!important;min-height:30px!important;padding:0!important;border-radius:50%!important;background:rgba(255,255,255,.92)!important;color:#0B0B0B!important;border:none!important;opacity:0;transition:opacity .3s var(--ease),transform .25s var(--ease)!important}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) button p,:is([class*="st-key-arw_"],[class*="st-key-garw_"]) button span{color:#0B0B0B!important}
[class*="st-key-card_"]:hover [class*="st-key-arw_"] button,[class*="st-key-garw_"] button{opacity:1}
[class*="st-key-garw_"] button{width:38px!important;height:38px!important;min-height:38px!important}
@media (hover:none){[class*="st-key-arw_"] button{opacity:1}}

/* Ficha de producto */
.ra-back{margin-top:1rem}
.ra-thumbs{display:flex;gap:6px;margin-top:.6rem;overflow-x:auto}
.ra-thumbs img{width:54px;height:72px;object-fit:cover;border-radius:8px;opacity:.4;flex-shrink:0;transition:opacity .3s var(--ease)}
.ra-thumbs img.on{opacity:1}
.ra-d{animation:rise .6s var(--ease) backwards;padding-top:.4rem}
.ra-d-brand{font-size:.8rem;color:var(--muted);font-weight:500}
.ra-d-name{font-size:clamp(1.9rem,3.4vw,2.6rem);font-weight:600;letter-spacing:-.03em;line-height:1.05;color:var(--text);margin:.3rem 0 .7rem}
.ra-d-price{display:flex;align-items:center;gap:1rem;margin-bottom:1rem}
.ra-d-price b{font-size:1.2rem;font-weight:600;color:var(--text)}
.ra-st{font-size:.76rem;font-weight:500;display:inline-flex;align-items:center;gap:6px;color:var(--muted)}
.ra-st.ok{color:var(--ok)}
.ra-st::before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor}
.ra-d-short{color:var(--muted);font-size:.95rem;line-height:1.7;margin:0 0 1.4rem;max-width:46ch}
.ra-buy{display:flex;align-items:center;justify-content:center;width:100%;padding:.95rem;border-radius:999px;background:var(--text);color:var(--bg)!important;font-size:.88rem;font-weight:600;text-decoration:none!important;transition:transform .25s var(--ease),opacity .25s var(--ease)}
.ra-buy:hover{opacity:.88}
.ra-buy:active{transform:scale(.98)}
.ra-buy-row{display:grid;grid-template-columns:1fr 1fr;gap:.5rem;margin-top:.5rem}
.ra-alt{display:flex;align-items:center;justify-content:center;gap:.55rem;padding:.75rem;border-radius:999px;border:1px solid var(--line2);color:var(--text)!important;text-decoration:none!important;font-size:.84rem;font-weight:500}
.ra-alt svg{width:18px;height:18px}
.ra-alt:hover{border-color:var(--text)}
.ra-dl{margin:1.6rem 0 1.2rem;border-top:1px solid var(--line)}
.ra-dl div{display:flex;justify-content:space-between;align-items:baseline;gap:1rem;padding:.65rem 0;border-bottom:1px solid var(--line);font-size:.88rem}
.ra-dl span:first-child{color:var(--muted)}
.ra-dl span:last-child{color:var(--text);text-align:right}
.ra-desc h4{font-family:var(--sans)!important;font-size:.82rem!important;font-weight:600!important;color:var(--text)!important;margin:1.2rem 0 .4rem!important;padding:0!important}
.ra-desc p{color:var(--muted)!important;line-height:1.8;font-size:.94rem;max-width:60ch}
.ra-desc ul{list-style:none;padding:0;margin:0}
.ra-desc li{padding:.25rem 0;font-size:.9rem;display:flex;gap:.7rem;color:var(--text)}
.ra-desc li::before{content:"";width:4px;height:4px;border-radius:50%;background:var(--accent);margin-top:.6rem;flex-shrink:0}

/* Perfiles, listas y tablas */
.ra-prof{display:flex;gap:1.2rem;align-items:center;flex-wrap:wrap;padding:1.6rem 0;border-bottom:1px solid var(--line);margin-bottom:1rem;animation:rise .6s var(--ease) backwards}
.ra-prof>img{width:72px;height:72px;border-radius:50%;object-fit:cover}
.ra-prof .n{font-size:1.8rem;font-weight:600;letter-spacing:-.03em;line-height:1.05;color:var(--text)}
.ra-prof .d{color:var(--muted);font-size:.8rem;margin-top:.4rem;display:flex;gap:1rem;flex-wrap:wrap}
.ra-prof .d span{display:inline-flex;align-items:center;gap:5px}
.ra-prof .d svg{width:13px;height:13px}
.ra-prof .k{display:flex;gap:2rem;margin-left:auto}
.ra-prof .k div{text-align:right}
.ra-prof .k b{display:block;font-size:1.5rem;font-weight:600;color:var(--text)}
.ra-prof .k small{color:var(--muted);font-size:.74rem}
.ra-row{display:flex;align-items:center;gap:1rem;padding:.7rem 0;border-bottom:1px solid var(--line)}
.ra-row img{width:44px;height:58px;object-fit:cover;border-radius:8px;flex-shrink:0}
.ra-row .m{flex:1;min-width:0}
.ra-row .m b{display:block;color:var(--text);font-weight:500;font-size:.9rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ra-row .m small{color:var(--muted);font-size:.78rem}
.ra-row .v{color:var(--text);font-size:.9rem;font-weight:600;white-space:nowrap}
.ra-row.flat{border:none;padding:0}
[class*="st-key-adm_"]{border-bottom:1px solid var(--line);padding:.3rem 0 .7rem}
.ra-table-wrap{overflow-x:auto}
.ra-table{width:100%;border-collapse:collapse;font-size:.86rem}
.ra-table th{text-align:left;color:var(--muted);font-weight:500;font-size:.74rem;padding:.7rem .6rem .7rem 0;border-bottom:1px solid var(--line2);white-space:nowrap}
.ra-table td{padding:.65rem .6rem .65rem 0;border-bottom:1px solid var(--line);color:var(--text);white-space:nowrap}
.ra-table img{width:24px;height:24px;border-radius:50%;vertical-align:middle;margin-right:8px;object-fit:cover}
.ra-podium{display:grid;grid-template-columns:repeat(3,1fr);gap:2rem;margin:.8rem 0 1.6rem}
.ra-pod{display:flex;align-items:center;gap:.9rem}
.ra-pod img{width:44px;height:44px;border-radius:50%;object-fit:cover}
.ra-pod .p{font-size:1.8rem;font-weight:600;color:var(--accent);line-height:1}
.ra-pod b{display:block;color:var(--text);font-size:.9rem;font-weight:600}
.ra-pod small{color:var(--muted);font-size:.78rem}
.ra-sub{font-size:1.2rem;font-weight:600;letter-spacing:-.02em;color:var(--text);margin:1rem 0 .3rem}
.st-key-authbox{padding:2.4rem 0 1rem;animation:rise .6s var(--ease) backwards}
.ra-auth{text-align:center;margin-bottom:.6rem}
.ra-auth .ra-cart{width:52px;height:52px;margin:0 auto}
.ra-auth h3{font-family:var(--sans)!important;font-size:1.9rem!important;font-weight:600!important;letter-spacing:-.03em;color:var(--text)!important;margin:.9rem 0 .2rem!important;padding:0!important}
.ra-auth p{color:var(--muted)!important;font-size:.88rem}
.ra-avprev{display:flex;align-items:center;gap:.7rem;margin:-.2rem 0 .3rem}
.ra-avprev img{width:40px;height:40px;border-radius:50%}
.ra-avprev span{color:var(--muted);font-size:.8rem}
.ra-empty{text-align:center;padding:3.4rem 1rem;color:var(--muted);font-size:.9rem}
.ra-empty b{display:block;font-size:1.3rem;color:var(--text);font-weight:600;margin-bottom:.3rem}
.ra-ownerset{display:flex;align-items:center;gap:1rem}
.ra-ownerset img{width:64px;height:80px;object-fit:cover;border-radius:12px}
.ra-note{color:var(--muted);font-size:.86rem}

/* Pie */
.ra-foot{display:flex;align-items:center;justify-content:center;gap:.7rem;margin-top:5rem;padding:1.6rem 0 1.8rem;border-top:1px solid var(--line);font-size:.78rem;color:var(--muted);text-align:center}
.ra-foot .ra-cart{width:22px;height:22px}

/* Animaciones (solo transform y opacity → 60 fps) */
@keyframes rise{from{opacity:0;transform:translate3d(0,14px,0)}to{opacity:1;transform:none}}
@keyframes reveal{from{opacity:0;transform:translate3d(0,28px,0)}to{opacity:1;transform:none}}
@keyframes photoIn{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:none}}
@keyframes cartIn{from{opacity:0;transform:translateX(-7px)}to{opacity:1;transform:none}}
@keyframes inR{from{opacity:.3;transform:translate3d(12px,0,0)}to{opacity:1;transform:none}}
@keyframes inL{from{opacity:.3;transform:translate3d(-12px,0,0)}to{opacity:1;transform:none}}
@keyframes fadeOut{from{opacity:1}to{opacity:0}}

/* Celular */
@media (max-width:760px){
 html{font-size:14px}
 .block-container,[data-testid="stMainBlockContainer"]{padding:.4rem 1rem 0!important}
 .st-key-hdr [data-testid="stColumn"]:first-child{flex:1 1 auto!important;width:auto!important}
 .st-key-hdr [data-testid="stColumn"]:not(:first-child){flex:0 0 auto!important;width:auto!important}
 .ra-brand span{display:none}
 .ra-cart{width:34px;height:34px}
 .ra-hero{min-height:auto;padding:2.2rem 0 1.6rem}
 .ra-me{display:grid;grid-template-columns:118px minmax(0,1fr);grid-template-rows:1fr auto auto auto 1fr;column-gap:1.1rem;row-gap:0;width:100%}
 .ra-photo{width:120px;height:150px;border-radius:16px;grid-row:1/6;grid-column:1}
 .ra-info{display:contents}
 .ra-hello{grid-column:2;grid-row:2}
 .ra-name{grid-column:2;grid-row:3;font-size:1.75rem;margin:.15rem 0 .3rem}
 .ra-tag{grid-column:2;grid-row:4;margin:0;font-size:.85rem}
 .ra-socials{grid-column:1/-1;max-width:none;margin-top:1.4rem;flex-direction:row;justify-content:space-between;gap:.4rem}
 .ra-so{flex:1;flex-direction:column;gap:.35rem;text-align:center;padding:.7rem .2rem;border:1px solid var(--line)}
 .ra-so small{display:none}
 .ra-sec .t{font-size:1.6rem}
 [class*="st-key-grid_"]{gap:1.8rem!important}
 [class*="st-key-grid_"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:1.8rem .7rem!important}
 [class*="st-key-grid_"] [data-testid="stColumn"]{flex:1 1 calc(50% - .35rem)!important;min-width:calc(50% - .35rem)!important;width:calc(50% - .35rem)!important}
 .ra-prof .k{margin-left:0}
 .ra-podium{grid-template-columns:1fr;gap:1rem}
 .ra-foot{flex-direction:column;gap:.5rem;margin-top:3.5rem;padding-bottom:5rem}
 .st-key-theme_sw{right:16px;bottom:16px}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""


def inject_css():
    v = THEMES[ss.theme]
    root = ":root{" + "".join(f"--{k}:{val};" for k, val in v.items()) + "}"
    html(f"<style>{root}{CSS}</style>")
    old = ss.pop("_curtain", None)
    if old:  # el tema anterior se desvanece + estela roja en el switch (solo transform/opacity → 60 fps)
        dash = "dashR" if ss.theme == "dark" else "dashL"
        html(f'<style>.st-key-theme_sw button::before{{animation:{dash} .6s cubic-bezier(.22,.8,.24,1)}}'
             '.st-key-theme_sw::before{animation:ring .7s cubic-bezier(.22,.8,.24,1)}</style>'
             f'<div class="ra-fade" data-n="{uuid.uuid4().hex[:6]}" style="background:{THEMES[old]["bg"]}"></div>')


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


def brand_html() -> str:
    return f'<div class="ra-brand">{LOGO}<div><b>Rissos Anghell</b><span>Store</span></div></div>'


def render_header(db, view):
    with st.container(key="hdr"):
        left, c_shop, c_acc = st.columns([4.6, 1.1, 1.3], vertical_alignment="center")
        left.markdown(brand_html(), unsafe_allow_html=True)
        with c_shop:
            if view != "home" and st.button("Tienda", key="nav_shop", icon=":material/west:"):
                go("home")
        with c_acc:
            u = current_user(db)
            if u:
                label, icon, target = u["name"].split()[0], ":material/person:", "profile"
            elif ss.role == "admin":
                label, icon, target = "Panel", ":material/tune:", "admin"
            else:
                label, icon, target = "Ingresar", ":material/person:", "login"
            if st.button(label, key="nav_acc", icon=icon, use_container_width=True):
                go(target)


def render_hero():
    mail = mailto("Contacto – Rissos Anghell Store", "Hola Benjamín,\n\n")
    wa = wa_link("Hola Benjamín, te escribo desde Rissos Anghell Store.")
    socials = [(wa, BRAND["whatsapp"], "WhatsApp", OWNER["whatsapp_display"], True),
               (IG_LINK, BRAND["instagram"], "Instagram", "@" + OWNER["instagram"], True),
               (mail, BRAND["gmail"], "Correo", OWNER["email"], False)]
    links = "".join(
        f'<a class="ra-so" href="{h}"{" target=_blank rel=noopener" if blank else ""}>{ic}'
        f'<span class="tx"><b>{lb}</b><small>{esc(val)}</small></span></a>'
        for h, ic, lb, val, blank in socials)
    html('<section class="ra-hero"><div class="ra-me">'
         f'<div class="ra-photo"><img src="{owner_photo()}" alt="{esc(OWNER["name"])}" decoding="async"/></div>'
         '<div class="ra-info"><div class="ra-hello">Hola, soy</div>'
         f'<div class="ra-name">{esc(OWNER["name"])}</div>'
         f'<div class="ra-tag">{esc(OWNER["tagline"])}</div>'
         f'<div class="ra-socials">{links}</div></div></div></section>')


def section(title: str, kicker: str = "", right: str = "", anchor: str = ""):
    title = re.sub(r"</?em>", "", title)
    html((f'<div class="ra-anchor" id="{anchor}"></div>' if anchor else "")
         + f'<div class="ra-sec"><div class="t">{title}</div><span>{right}</span></div>')


def empty(title: str, text: str):
    html(f'<div class="ra-empty"><b>{esc(title)}</b>{esc(text)}</div>')


def card_image_html(p, idx: int, d: str, big: bool = False) -> str:
    imgs = p.get("images") or ["demo:bag:0"]
    sold = p["status"] != "Disponible"
    tag = f'<span class="ra-tag2">{esc(p["status"])}</span>' if sold else ""
    bars = ('<div class="ra-bars">' + "".join(f'<i class="{"on" if i == idx else ""}"></i>' for i in range(len(imgs)))
            + "</div>") if len(imgs) > 1 else ""
    return (f'<div class="ra-img{" big" if big else ""}{" sold" if sold else ""}"><img class="{d}" '
            f'src="{img_src(imgs[idx], thumb=not big)}" alt="{esc(p["name"])}" decoding="async"/>{tag}{bars}</div>')


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
    """Tarjeta aislada: cambiar de foto solo recarga esta tarjeta."""
    pid = p["id"]
    imgs = p.get("images") or ["demo:bag:0"]
    n = len(imgs)
    idx = ss.get(f"idx_{pid}", 0) % n
    with st.container(key=f"card_{scope}_{pid}"):
        html(card_image_html(p, idx, ss.get(f"dir_{pid}", "r")))
        if n > 1:
            carousel_arrows("", f"arw_{scope}_{pid}", pid, n)
        html(f'<div class="ra-pinfo"><div class="ra-pname" title="{esc(p["name"])}">{esc(p["name"])}</div>'
             f'<div class="ra-pmeta">{esc(meta_line(p)) or "&nbsp;"}</div>'
             f'<div class="ra-price">{money_html(p["price"])}</div></div>')
        if st.button("Ver detalle", key=f"view_{scope}_{pid}", use_container_width=True):
            ss.view = "product"
            st.query_params.clear()
            st.query_params["producto"] = pid
            st.rerun()


def product_grid(items, scope="h", cols_n=4):
    html("<style>" + "".join(f".st-key-card_{scope}_{p['id']}{{animation-delay:{min(i, 11) * .05:.2f}s}}"
                             for i, p in enumerate(items)) + "</style>")
    with st.container(key=f"grid_{scope}"):
        for start in range(0, len(items), cols_n):
            cols = st.columns(cols_n, gap="small")
            for j, p in enumerate(items[start:start + cols_n]):
                with cols[j]:
                    product_card(p, scope)


# ══════════════════════════════════════════════════════════════════════════
# 9 · TIENDA
# ══════════════════════════════════════════════════════════════════════════
def render_home(db):
    render_hero()
    items = sorted(db["products"], key=lambda p: p["status"] != "Disponible")
    section("Mi colección", right=f"{len(items)} {'pieza' if len(items) == 1 else 'piezas'}", anchor="coleccion")
    present = [c for c in CATEGORIES if any(p["category"] == c for p in items)]
    if len(present) > 1:
        cat = st.pills("Categoría", ["Todo"] + present, default="Todo",
                       label_visibility="collapsed", key="cat_pills") or "Todo"
        if cat != "Todo":
            items = [p for p in items if p["category"] == cat]
    st.write("")
    if items:
        product_grid(items, "h")
    else:
        empty("Pronto habrá piezas nuevas", "Vuelve en unos días o escríbeme por WhatsApp.")


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
        empty("Esta pieza ya no está publicada", "Puede que se haya vendido. Revisa la colección.")
        if st.button("Ver la colección", type="primary"):
            go("home")
        return
    st.write("")
    left, right = st.columns([1.1, 1], gap="large")
    with left:
        gallery(p)
    with right:
        sold = p["status"] != "Disponible"
        subject, body = consult_message(db, p)
        sl = size_label(p)
        wa_txt = (f"Hola Benjamín, quiero consultar el stock de: {p['name']}" + (f" ({sl})" if sl else "")
                  + f" – {money(p['price'])}\n{product_link(db, p['id'])}")
        rows = [("Talla" if p.get("category") in SIZED else "Medida", p.get("size") or "No aplica"),
                ("Made in", p.get("made_in") or "—"), ("Marca", p.get("brand") or "—"),
                ("Condición", p.get("condition") or "—"), ("Categoría", p.get("category")),
                ("Publicado", fmt_date(p.get("created")))]
        desc = esc(p.get("description"))
        det = "".join(f"<li>{esc(x)}</li>" for x in (p.get("details") or []) if str(x).strip())
        html('<div class="ra-d">'
             f'<div class="ra-d-brand">{esc(p.get("brand") or p.get("category"))}</div>'
             f'<div class="ra-d-name">{esc(p["name"])}</div>'
             f'<div class="ra-d-price"><b>{money_html(p["price"])}</b>'
             f'<span class="ra-st{"" if sold else " ok"}">{esc(p["status"])}</span></div>'
             f'<div class="ra-d-short">{esc(p.get("short"))}</div>'
             f'<a class="ra-buy" href="{mailto(subject, body)}">{"Consultar disponibilidad" if sold else "Consultar"}</a>'
             '<div class="ra-buy-row">'
             f'<a class="ra-alt" href="{wa_link(wa_txt)}" target="_blank" rel="noopener">{BRAND["whatsapp"]}WhatsApp</a>'
             f'<a class="ra-alt" href="{gmail_link(subject, body)}" target="_blank" rel="noopener">{BRAND["gmail"]}Gmail</a>'
             '</div><div class="ra-dl">'
             + "".join(f"<div><span>{esc(k)}</span><span>{esc(v)}</span></div>" for k, v in rows)
             + '</div><div class="ra-desc">'
             + (f"<h4>Descripción</h4><p>{desc}</p>" if desc else "")
             + (f"<h4>Detalles</h4><ul>{det}</ul>" if det else "")
             + "</div></div>")
        st.caption("Link directo de esta pieza")
        st.code(product_link(db, p["id"]), language=None)

    related = [x for x in db["products"] if x["id"] != p["id"] and x["category"] == p["category"]]
    related += [x for x in db["products"] if x["id"] != p["id"] and x not in related]
    related = sorted(related, key=lambda x: x["status"] != "Disponible")[:4]
    if related:
        st.write("")
        st.write("")
        section("También te puede <em>gustar</em>", "Sigue mirando")
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
    _, mid, _ = st.columns([1, 1.3, 1])
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
                    flash("Sesión de administrador iniciada", ":material/tune:")
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
        if b.button("", key=f"delpu_{pu['id']}", icon=":material/close:", help="Quitar esta compra"):
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
        with st.container(key=f"adm_{pid}"):
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
            with st.expander("Editar"):
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
        st.write("")
        section("Últimas <em>ventas</em>")
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
        st.write("")
        section("Quién te compra <em>más</em>")
        html('<div class="ra-podium">' + "".join(
            f'<div class="ra-pod"><div class="p">{i + 1}</div><img src="{user_avatar(u)}"/>'
            f'<div><b>{esc(u["name"])}</b><small>{c} compras · {money_html(t)}</small></div></div>'
            for i, (u, c, _, t, _) in enumerate(top)) + "</div>")

    rows = "".join(
        f"<tr><td>{i}</td><td><img src='{user_avatar(u)}'/>{esc(u['name'])}</td><td>{esc(u.get('phone_display') or u['phone'])}</td>"
        f"<td>{esc(u.get('email') or '—')}</td><td>{esc(u.get('location') or '—')}</td><td>{c}</td><td>{units}</td>"
        f"<td>{money_html(total)}</td><td>{fmt_date(last) if last else '—'}</td></tr>"
        for i, (u, c, units, total, last) in enumerate(stats, 1))
    html('<div class="ra-table-wrap"><table class="ra-table"><thead><tr><th>#</th><th>Cliente</th><th>Teléfono</th>'
         '<th>Correo</th><th>Ubicación</th><th>Compras</th><th>Unid.</th><th>Total</th><th>Última</th></tr></thead>'
         f'<tbody>{rows}</tbody></table></div>')

    st.write("")
    section("Perfil del <em>cliente</em>")
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
    st.caption("Link público de la tienda (se usa en los correos de consulta)")
    bu = st.text_input("Dirección pública", value=db["settings"].get("base_url", ""), key="set_base",
                       placeholder=app_base_url(db), label_visibility="collapsed")
    if st.button("Guardar link", key="set_base_btn"):
        db["settings"]["base_url"] = bu.strip()
        save_db(db)
        flash("Link guardado", ":material/link:")
        st.rerun()
    st.divider()
    st.caption("Contraseña de administrador")
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
    st.write("")
    h, o = st.columns([5, 1], vertical_alignment="bottom")
    with h:
        section("Panel de <em>la tienda</em>", "Administración")
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
    html(f'<div class="ra-foot">{LOGO}<span>{esc(COPYRIGHT)}</span></div>')


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
    st.button("Tema", key="theme_sw", on_click=_toggle_theme,
              help="Cambiar a tema oscuro" if ss.theme == "light" else "Cambiar a tema claro")

    nav_key = f"{view}:{pid or ''}"
    if ss.get("_last_nav") not in (None, nav_key):
        scroll_top()
    ss["_last_nav"] = nav_key


main()
