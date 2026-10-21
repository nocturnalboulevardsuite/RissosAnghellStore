# -*- coding: utf-8 -*-
"""
Rissos Anghell Store · Benjamín Espinoza
Ejecutar:  streamlit run app.py
Foto:      deja "benja.jpeg" en la raíz del repositorio (o en /assets).
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

st.set_page_config(page_title="Rissos Anghell Store", page_icon=":material/storefront:",
                   layout="wide", initial_sidebar_state="collapsed")

# ════════════════════════════════════════════════════════════════════════
# 1. CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
IMG_DIR = DATA_DIR / "images"
ASSETS_DIR = BASE_DIR / "assets"
DB_PATH = DATA_DIR / "db.json"
for _d in (DATA_DIR, IMG_DIR):
    _d.mkdir(parents=True, exist_ok=True)

OWNER = {
    "name": "Benjamín Espinoza",
    "tagline": "Compra y venta de artículos, ropa y más",
    "photo_names": ("benja.jpeg", "benja.jpg", "Benja.jpeg", "Benja.jpg", "benja.png", "benja.webp"),
    "whatsapp": "56936992950",
    "whatsapp_display": "+56 9 3699 2950",
    "instagram": "rissos._.anghell",
    "email": "nocturnalboulevardsuite@gmail.com",
}
DEFAULT_ADMIN_PASSWORD = "anghell2026"

CATEGORIES = ["Ropa", "Calzado", "Accesorios", "Perfumes", "Figuras", "Tecnología", "Otros"]
SIZED = ("Ropa", "Calzado", "Accesorios")
STATUSES = ["Disponible", "Agotado", "Fuera de stock"]
CONDITIONS = ["Nuevo", "Nuevo sin etiqueta", "Usado, como nuevo", "Usado"]
GENDERS = ["Masculino", "Femenino", "No Binario", "Prefiero no decirlo", "Personalizado"]
MADE_IN = ["China", "Taiwán", "EE.UU.", "Vietnam", "Bangladesh", "India", "Indonesia", "Camboya",
           "Tailandia", "Turquía", "Pakistán", "México", "Brasil", "Chile", "Perú", "Italia",
           "Francia", "España", "Portugal", "Alemania", "Reino Unido", "Japón", "Corea del Sur", "Otro"]
AVATAR_COLORS = {"Rojo": "#C8364B", "Blanco": "#F2F3F5", "Negro": "#16181D", "Azul": "#2F5BD3",
                 "Verde": "#2E8F63", "Morado": "#6E4BC4", "Naranjo": "#E07226", "Dorado": "#B9933F",
                 "Rosado": "#D9668F", "Gris": "#7D8292"}

THEMES = {
    "light": {"bg": "#F5F6F8", "surface": "#FFFFFF", "surface2": "#EEF0F3", "text": "#11141C",
              "muted": "#6A7080", "faint": "#9AA0AE", "border": "rgba(17,20,28,.08)",
              "border2": "rgba(17,20,28,.14)", "accent": "#8E1F33", "accent-ink": "#FFFFFF",
              "accent-soft": "rgba(142,31,51,.10)", "glow": "rgba(142,31,51,.22)",
              "shadow": "rgba(17,20,28,.10)", "shadow2": "rgba(17,20,28,.18)",
              "nav": "rgba(245,246,248,.78)", "chip": "rgba(17,20,28,.045)", "ok": "#1F9D61"},
    "dark": {"bg": "#0B0E15", "surface": "#12161F", "surface2": "#191E29", "text": "#ECEDF1",
             "muted": "#8F95A3", "faint": "#5F6573", "border": "rgba(236,237,241,.08)",
             "border2": "rgba(236,237,241,.16)", "accent": "#E06A80", "accent-ink": "#0B0E15",
             "accent-soft": "rgba(224,106,128,.12)", "glow": "rgba(224,106,128,.28)",
             "shadow": "rgba(0,0,0,.45)", "shadow2": "rgba(0,0,0,.65)",
             "nav": "rgba(11,14,21,.74)", "chip": "rgba(236,237,241,.06)", "ok": "#3DD68C"},
}

# Íconos dibujados (SVG lineal, estilo uniforme)
_SV = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">'
ICON = {
    "whatsapp": '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M17.47 14.38c-.3-.15-1.76-.87-2.03-.97-.27-.1-.47-.15-.67.15-.2.3-.77.97-.94 1.16-.17.2-.35.22-.64.08-.3-.15-1.26-.46-2.39-1.48-.88-.79-1.48-1.76-1.65-2.06-.17-.3-.02-.46.13-.6.13-.14.3-.35.45-.52.15-.17.2-.3.3-.5.1-.2.05-.37-.03-.52-.07-.15-.67-1.61-.92-2.2-.24-.58-.49-.5-.67-.51h-.57c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48 0 1.46 1.07 2.88 1.21 3.07.15.2 2.1 3.2 5.08 4.49.71.31 1.26.49 1.7.63.71.22 1.36.19 1.87.12.57-.09 1.76-.72 2-1.41.25-.7.25-1.29.18-1.41-.08-.13-.28-.2-.57-.35zM12.05 21.79h-.01a9.87 9.87 0 0 1-5.03-1.38l-.36-.21-3.74.98 1-3.65-.24-.37a9.86 9.86 0 0 1-1.51-5.26c0-5.45 4.44-9.88 9.89-9.88 2.64 0 5.12 1.03 6.99 2.9a9.83 9.83 0 0 1 2.89 6.99c0 5.45-4.44 9.88-9.88 9.88zm8.41-18.3A11.82 11.82 0 0 0 12.05 0C5.5 0 .16 5.34.16 11.89c0 2.1.55 4.14 1.59 5.95L.06 24l6.3-1.65a11.88 11.88 0 0 0 5.69 1.45c6.55 0 11.89-5.34 11.89-11.89 0-3.18-1.24-6.17-3.48-8.42z"/></svg>',
    "instagram": _SV + '<rect x="2.5" y="2.5" width="19" height="19" rx="5.5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.6" cy="6.4" r=".6" fill="currentColor"/></svg>',
    "mail": _SV + '<rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/><path d="m3 7 9 6 9-6"/></svg>',
    "phone": _SV + '<path d="M21 16.5v2.6a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 3.1 3.3 2 2 0 0 1 5.1 1h2.6a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8.8 8.6a16 16 0 0 0 6 6l1.1-1.1a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>',
    "pin": _SV + '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>',
    "user": _SV + '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/></svg>',
    "calendar": _SV + '<rect x="3" y="4.5" width="18" height="17" rx="2.5"/><path d="M3 9.5h18M8 2.5v4M16 2.5v4"/></svg>',
    "globe": _SV + '<circle cx="12" cy="12" r="9.5"/><path d="M2.5 12h19M12 2.5c2.6 2.8 3.8 6 3.8 9.5s-1.2 6.7-3.8 9.5c-2.6-2.8-3.8-6-3.8-9.5s1.2-6.7 3.8-9.5z"/></svg>',
    "ruler": _SV + '<path d="M3 17 17 3l4 4L7 21z"/><path d="m7 13 2 2M10 10l2 2M13 7l2 2"/></svg>',
    "tag": _SV + '<path d="M20.6 13.4 13.4 20.6a2 2 0 0 1-2.8 0L3 13V3h10l7.6 7.6a2 2 0 0 1 0 2.8z"/><circle cx="7.5" cy="7.5" r="1.3"/></svg>',
    "spark": _SV + '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/></svg>',
    "arrow": _SV + '<path d="M7 17 17 7M8 7h9v9"/></svg>',
    "gender": _SV + '<circle cx="10" cy="14" r="5.5"/><path d="M14 10l6-6M15 4h5v5"/></svg>',
    "bag": _SV + '<path d="M5 8h14l-1 13H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/></svg>',
}

# ════════════════════════════════════════════════════════════════════════
# 2. UTILIDADES
# ════════════════════════════════════════════════════════════════════════
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


# ════════════════════════════════════════════════════════════════════════
# 3. IMÁGENES
# ════════════════════════════════════════════════════════════════════════
# Ilustraciones lineales para las fotos de muestra (sin emojis)
ILLUS = {
    "tshirt": '<path d="M300 330 L365 292 C380 322 420 322 435 292 L500 330 L565 425 L512 455 L490 425 L490 712 L310 712 L310 425 L288 455 L235 425 Z"/><path d="M365 292 C380 340 420 340 435 292"/><path d="M340 640 H460" opacity=".5"/>',
    "jeans": '<path d="M318 290 H482 L506 712 H424 L400 440 L376 712 H294 Z"/><path d="M318 330 H482"/><path d="M400 330 V420"/><path d="M332 332 C336 368 358 380 380 382"/><path d="M468 332 C464 368 442 380 420 382"/>',
    "perfume": '<rect x="352" y="292" width="96" height="70" rx="12"/><rect x="378" y="362" width="44" height="46"/><rect x="300" y="408" width="200" height="304" rx="34"/><rect x="345" y="505" width="110" height="96" rx="8"/><path d="M330 450 C330 440 340 432 350 432" opacity=".55"/>',
    "cap": '<path d="M255 560 C255 420 320 372 400 372 C480 372 545 420 545 560 Z"/><path d="M255 560 C330 590 470 590 545 560 C600 575 620 600 590 615 C520 640 330 640 255 600 Z"/><path d="M400 372 C380 420 372 500 372 572"/><circle cx="400" cy="368" r="10"/>',
    "figure": '<ellipse cx="400" cy="705" rx="140" ry="26"/><circle cx="400" cy="372" r="54"/><path d="M366 334 L344 296 M434 334 L456 296"/><path d="M346 440 C346 428 454 428 454 440 L470 600 L430 600 L420 690 L380 690 L370 600 L330 600 Z"/><path d="M346 452 L292 540 M454 452 L508 540"/>',
    "monitor": '<rect x="236" y="320" width="328" height="226" rx="18"/><rect x="262" y="344" width="276" height="178" rx="6"/><path d="M380 546 L370 640 H430 L420 546"/><path d="M322 650 H478"/><path d="M290 470 L340 420 L380 455 L430 395 L510 470" opacity=".55"/>',
    "bag": '<path d="M290 420 H510 L530 712 H270 Z"/><path d="M345 420 V380 C345 330 455 330 455 380 V420"/>',
}
PALETTES = [("#E9ECF2", "#D3D9E4", "#1B2233"), ("#F1E6E8", "#DEC6CB", "#5A1626"),
            ("#1B2233", "#2C3650", "#E9ECF2"), ("#E4EDE9", "#C9D9D2", "#1F3B32"),
            ("#ECE7F3", "#D4CBE3", "#3A2A5A"), ("#5A1626", "#2A0B12", "#F1E6E8")]


@st.cache_data(show_spinner=False, max_entries=200)
def demo_svg(kind: str, idx: int) -> str:
    a, b, fg = PALETTES[idx % len(PALETTES)]
    tilt = (-6, 0, 5, -3, 4, -5)[idx % 6]
    scale = (1, .9, 1.06, .95, 1.02, .92)[idx % 6]
    body = ILLUS.get(kind, ILLUS["bag"])
    return b64svg(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/>'
        f'<stop offset="1" stop-color="{b}"/></linearGradient></defs>'
        '<rect width="800" height="1000" fill="url(#g)"/>'
        f'<circle cx="400" cy="500" r="300" fill="{fg}" fill-opacity=".05"/>'
        f'<g transform="translate(400 500) rotate({tilt}) scale({scale}) translate(-400 -500)">'
        '<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -14;0 0" '
        'dur="6s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
        f'<g fill="{fg}" fill-opacity=".06" stroke="{fg}" stroke-width="7" stroke-linecap="round" '
        f'stroke-linejoin="round">{body}</g></g></g>'
        f'<text x="400" y="925" font-size="22" letter-spacing="5" text-anchor="middle" fill="{fg}" '
        'fill-opacity=".45" font-family="Helvetica,Arial,sans-serif">foto de muestra</text></svg>')


@st.cache_data(show_spinner=False, max_entries=600)
def _file_uri(path: str, mtime: float, max_side: int | None = None) -> str:
    p = Path(path)
    if max_side:
        img = ImageOps.exif_transpose(Image.open(p)).convert("RGB")
        img.thumbnail((max_side, max_side))
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=86, optimize=True)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    mime = {"png": "image/png", "webp": "image/webp"}.get(p.suffix.lower().lstrip("."), "image/jpeg")
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def img_src(entry: str, thumb: bool = False) -> str:
    if not entry:
        return demo_svg("bag", 0)
    if entry.startswith("demo:"):
        _, kind, idx = (entry.split(":") + ["0"])[:3]
        return demo_svg(kind, int(idx))
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
    img.save(IMG_DIR / f"{stem}_t.jpg", "JPEG", quality=82, optimize=True)
    return f"images/{stem}.jpg"


def delete_image(entry: str | None):
    if entry and not entry.startswith("demo:"):
        p = DATA_DIR / entry
        for f in (p, p.with_name(p.stem + "_t.jpg")):
            try:
                f.unlink(missing_ok=True)
            except Exception:
                pass


@st.cache_data(show_spinner=False, max_entries=50)
def avatar_svg(color: str) -> str:
    c = color.lstrip("#")
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    fg = "#1B1F2A" if (r * 299 + g * 587 + b * 114) / 1000 > 170 else "#FFFFFF"
    return b64svg(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><clipPath id="c">'
        '<circle cx="50" cy="50" r="50"/></clipPath></defs><g clip-path="url(#c)">'
        f'<rect width="100" height="100" fill="{color}"/><circle cx="50" cy="39" r="17" fill="{fg}" fill-opacity=".9"/>'
        f'<path d="M14 100c0-22 16-36 36-36s36 14 36 36z" fill="{fg}" fill-opacity=".9"/></g></svg>')


def user_avatar(u) -> str:
    return img_src(u["photo"], thumb=True) if u.get("photo") else avatar_svg(u.get("avatar_color") or "#C8364B")


def find_owner_photo() -> Path | None:
    for folder in (BASE_DIR, ASSETS_DIR):
        for name in OWNER["photo_names"]:
            if (folder / name).exists():
                return folder / name
    return None


def owner_photo() -> str:
    p = find_owner_photo()
    if p:
        return _file_uri(str(p), p.stat().st_mtime, 360)  # se reduce para que cargue rápido
    return b64svg(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" fill="#8E1F33"/>'
        '<text x="50" y="62" font-size="34" text-anchor="middle" fill="#fff" font-family="Georgia,serif" '
        'font-style="italic">BE</text></svg>')


# ════════════════════════════════════════════════════════════════════════
# 4. BASE DE DATOS (JSON)
# ════════════════════════════════════════════════════════════════════════
def seed_db() -> dict:
    t = now_iso()
    rows = [
        ("Polera roja", "Ropa", 12990, "L", "China", "Rissos Basics", "Nuevo", "Disponible",
         "Algodón peinado, corte regular y color que no se lava.",
         "Polera de algodón peinado de gramaje medio, suave al tacto y con buena caída. El rojo es intenso y se mantiene lavado tras lavado.",
         ["100% algodón", "Corte regular fit", "Cuello redondo reforzado", "Lavar en frío"], "tshirt", [1, 0, 3]),
        ("Pantalón Jean negro", "Ropa", 24990, "42", "Bangladesh", "Denim Co.", "Usado, como nuevo", "Disponible",
         "Jean negro de corte recto, usado dos veces.",
         "Jean negro de mezclilla firme con un toque de elasticidad. Corte recto que funciona con zapatillas o botines. Sin desgaste visible.",
         ["98% algodón, 2% elastano", "Corte recto", "5 bolsillos", "Tiro medio"], "jeans", [2, 0, 4]),
        ("Dior Sauvage Parfum 150ml", "Perfumes", 129990, "", "Francia", "Dior", "Nuevo", "Disponible",
         "Perfume original, sellado, 150 ml.",
         "Dior Sauvage en su versión Parfum: más profunda y amaderada que el EDT, con notas de bergamota, sándalo y vainilla. Caja sellada.",
         ["Contenido: 150 ml", "Concentración: Parfum", "Caja sellada", "Original"], "perfume", [0, 5, 4]),
        ("Gorra F1", "Accesorios", 19990, "Ajustable", "Vietnam", "Formula 1", "Nuevo", "Agotado",
         "Gorra de seis paneles con bordado frontal.",
         "Gorra de seis paneles con logo bordado y cierre ajustable trasero. Visera curva y forro interior transpirable.",
         ["Talla única ajustable", "Logo bordado", "Cierre de velcro", "Visera curva"], "cap", [1, 2]),
        ("Figura de Freezer", "Figuras", 34990, "", "China", "Banpresto", "Nuevo", "Disponible",
         "Figura de colección de Dragon Ball, en su caja.",
         "Figura de Freezer en su forma final, con detalles pintados y base incluida. Ideal para colección; caja en buen estado.",
         ["Altura aprox.: 18 cm", "Material: PVC", "Base incluida", "Caja original"], "figure", [4, 2, 0]),
        ("Monitor 144Hz", "Tecnología", 159990, "", "Taiwán", "Genérico 24\"", "Usado, como nuevo", "Disponible",
         "24 pulgadas, Full HD, 144 Hz y 1 ms.",
         "Monitor gamer de 24 pulgadas con panel de 144 Hz, ideal para juegos competitivos. Sin píxeles muertos, con cables y caja.",
         ["24\" Full HD 1920×1080", "144 Hz, 1 ms", "HDMI y DisplayPort", "Incluye cables"], "monitor", [2, 0, 3]),
    ]
    prods = []
    for (name, cat, price, size, made, brand, cond, status, short, desc, det, kind, pals) in rows:
        prods.append(dict(id=new_id(), name=name, category=cat, price=price, size=size, made_in=made,
                          brand=brand, condition=cond, status=status, short=short, description=desc,
                          details=det, images=[f"demo:{kind}:{i}" for i in pals], created=t))
    return {"products": prods, "users": [], "purchases": [], "settings": {}}


def load_db() -> dict:
    if not DB_PATH.exists():
        save_db(seed_db())
    with open(DB_PATH, encoding="utf-8") as f:
        db = json.load(f)
    for k, v in (("products", []), ("users", []), ("purchases", []), ("settings", {})):
        db.setdefault(k, v)
    # migración: fotos de muestra antiguas con emoji pasan a ilustración
    for p in db["products"]:
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


# ════════════════════════════════════════════════════════════════════════
# 5. LINKS (correo, WhatsApp, Instagram, producto)
# ════════════════════════════════════════════════════════════════════════
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
    lines = ["Hola Benjamín,", "", "Quiero consultar el stock de este producto:", "",
             f"• Producto: {p['name']}"]
    if sl:
        lines.append(f"• {sl if p.get('category') in SIZED else 'Medida: ' + p['size']}")
    lines += [f"• Precio: {money(p['price'])}", f"• Link: {product_link(db, p['id'])}", ""]
    u = current_user(db)
    if u:
        lines += [f"Mi nombre: {u['name']}", f"Mi teléfono: {u.get('phone_display') or u['phone']}", ""]
    lines.append("¡Gracias!")
    return subject, "\n".join(lines)


# ════════════════════════════════════════════════════════════════════════
# 6. SESIÓN Y NAVEGACIÓN
# ════════════════════════════════════════════════════════════════════════
ss = st.session_state
ss.setdefault("theme", "light")
ss.setdefault("role", None)          # None | "user" | "admin"
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


# ════════════════════════════════════════════════════════════════════════
# 7. ESTILOS
# ════════════════════════════════════════════════════════════════════════
CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Instrument+Sans:wght@400;500;600;700&display=swap');
:root{--ease:cubic-bezier(.22,1,.36,1);--serif:'Instrument Serif',Georgia,serif;--sans:'Instrument Sans',system-ui,-apple-system,'Segoe UI',sans-serif;}
html{font-size:15px}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--bg)!important;color:var(--text)!important;font-family:var(--sans)}
.stApp{transition:background-color .6s var(--ease),color .6s var(--ease)}
.stApp *{transition-property:background-color,border-color,color,box-shadow,opacity;transition-duration:.35s;transition-timing-function:var(--ease)}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer,[data-testid="stStatusWidget"],[data-testid="stSidebarCollapsedControl"],[data-testid="stAppDeployButton"]{display:none!important}
.block-container,[data-testid="stMainBlockContainer"]{padding:.4rem 1.2rem 2rem!important;max-width:1120px!important}
.stApp h1,.stApp h2,.stApp h3{font-family:var(--serif)!important;color:var(--text)!important;font-weight:400!important}
.stApp [data-testid="stMarkdownContainer"] p,.stApp [data-testid="stMarkdownContainer"] li{color:var(--text);font-size:.95rem}
[data-testid="stWidgetLabel"] p{color:var(--muted)!important;font-size:.8rem!important;font-weight:600!important}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:var(--muted)!important;font-size:.8rem!important}
::selection{background:var(--accent);color:var(--accent-ink)}
::-webkit-scrollbar{width:8px;height:8px}::-webkit-scrollbar-thumb{background:var(--border2);border-radius:8px}
:focus-visible{outline:2px solid var(--accent)!important;outline-offset:2px}
[data-testid="stVerticalBlock"]{gap:.75rem}

/* Inputs */
.stApp input,.stApp textarea{color:var(--text)!important;-webkit-text-fill-color:var(--text)!important;caret-color:var(--accent);font-size:.92rem!important}
.stApp input::placeholder,.stApp textarea::placeholder{color:var(--faint)!important;-webkit-text-fill-color:var(--faint)!important}
[data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="base-input"],[data-baseweb="select"]>div,[data-testid$="RootElement"]{background:var(--surface)!important;border:1px solid var(--border2)!important;border-radius:10px!important}
[data-testid$="RootElement"]:focus-within,[data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within,[data-baseweb="select"]>div:focus-within{border-color:var(--accent)!important;box-shadow:0 0 0 3px var(--accent-soft)!important}
[data-baseweb="select"] *{color:var(--text)!important}
[data-baseweb="select"] svg{fill:var(--muted)!important}
[data-baseweb="popover"] ul,[data-baseweb="popover"] [data-baseweb="menu"]{background:var(--surface)!important;border:1px solid var(--border);border-radius:12px}
[data-baseweb="popover"] li{color:var(--text)!important;background:transparent!important}
[data-baseweb="popover"] li:hover,[data-baseweb="popover"] li[aria-selected="true"]{background:var(--chip)!important}
[data-testid="stNumberInput"] button{background:var(--surface2)!important;color:var(--text)!important;border-color:var(--border)!important}
[data-testid="stRadio"] label p,[data-testid="stCheckbox"] label p,[data-testid="stToggle"] label p{color:var(--text)!important;font-weight:500!important;font-size:.88rem!important}
[data-testid="stFileUploaderDropzone"]{background:var(--surface2)!important;border:1px dashed var(--border2)!important;border-radius:12px!important}
[data-testid="stFileUploaderDropzone"] *{color:var(--muted)!important}
[data-testid="stFileUploaderFile"] *{color:var(--text)!important}
[data-baseweb="calendar"],[data-baseweb="calendar"] *{background-color:var(--surface)!important;color:var(--text)!important}
[data-testid="stTooltipContent"]{background:var(--text)!important;color:var(--bg)!important}

/* Botones */
.stButton button,.stFormSubmitButton button,.stDownloadButton button{background:var(--surface)!important;color:var(--text)!important;border:1px solid var(--border2)!important;border-radius:10px!important;font-weight:600!important;font-size:.88rem!important;min-height:2.35rem;padding:.3rem .9rem!important;transition:all .35s var(--ease)!important}
.stButton button p,.stFormSubmitButton button p,.stDownloadButton button p{color:inherit!important;font-weight:600!important;font-size:.88rem!important}
.stButton button:hover,.stFormSubmitButton button:hover,.stDownloadButton button:hover{border-color:var(--text)!important;transform:translateY(-1px);box-shadow:0 8px 20px -12px var(--shadow2)!important}
.stButton button:active{transform:scale(.97)}
.stApp button[kind="primary"],.stApp button[kind="primaryFormSubmit"],.stApp [data-testid^="stBaseButton-primary"]{background:var(--text)!important;color:var(--bg)!important;border-color:var(--text)!important}
.stApp button[kind="primary"]:hover,.stApp button[kind="primaryFormSubmit"]:hover,.stApp [data-testid^="stBaseButton-primary"]:hover{background:var(--accent)!important;border-color:var(--accent)!important;color:var(--accent-ink)!important;box-shadow:0 12px 26px -12px var(--glow)!important}
[data-testid="stButtonGroup"] button[role="radio"]{border-radius:999px!important;background:transparent!important;border:1px solid var(--border2)!important;color:var(--muted)!important;padding:.2rem .85rem!important;min-height:2rem!important;font-size:.84rem!important}
[data-testid="stButtonGroup"] button[role="radio"] p{color:inherit!important;font-size:.84rem!important}
[data-testid="stButtonGroup"] button[role="radio"]:hover{color:var(--text)!important;border-color:var(--text)!important}
[data-testid="stButtonGroup"] button[aria-checked="true"]{background:var(--text)!important;color:var(--bg)!important;border-color:var(--text)!important}

/* Tabs, expander, contenedores */
.stTabs [data-baseweb="tab-list"]{gap:.2rem;border-bottom:1px solid var(--border);background:transparent}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;padding:.5rem .75rem}
.stTabs [data-baseweb="tab"] p{color:inherit!important;font-weight:600!important;font-size:.88rem!important}
.stTabs [aria-selected="true"]{color:var(--text)!important}
.stTabs [data-baseweb="tab-highlight"]{background:var(--accent)!important;height:2px}
.stTabs [data-baseweb="tab-border"]{display:none}
[data-testid="stExpander"] details{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:12px!important}
[data-testid="stExpander"] summary,[data-testid="stExpander"] summary p,[data-testid="stExpander"] summary span{color:var(--text)!important;font-weight:600;font-size:.9rem}
[data-testid="stVerticalBlockBorderWrapper"],[data-testid="stForm"]{border-color:var(--border)!important;border-radius:14px!important;background:var(--surface)}
[data-testid="stMetric"]{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:12px 16px}
[data-testid="stMetricValue"]{color:var(--text)!important;font-family:var(--serif);font-size:1.9rem!important}
[data-testid="stMetricLabel"] p{color:var(--muted)!important}
[data-testid="stCode"] pre{background:var(--surface2)!important;border-radius:10px!important;border:1px solid var(--border)}
[data-testid="stCode"] code{color:var(--text)!important;white-space:pre-wrap!important;word-break:break-all;font-size:.8rem!important}
[data-testid="stAlert"]{border-radius:12px!important}
hr{border-color:var(--border)!important;margin:1.2rem 0!important}
.st-key-scrolltop{position:absolute!important;height:0!important;overflow:hidden;visibility:hidden;pointer-events:none}

/* Navbar */
.st-key-navbar{position:sticky;top:.5rem;z-index:999;background:var(--nav);backdrop-filter:blur(16px) saturate(1.6);-webkit-backdrop-filter:blur(16px) saturate(1.6);border:1px solid var(--border);border-radius:14px;padding:.4rem .45rem .4rem .9rem;margin:.5rem 0 1.2rem;box-shadow:0 10px 30px -22px var(--shadow2)}
.st-key-navbar [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:.4rem!important;align-items:center}
.st-key-navbar [data-testid="stColumn"]{min-width:0!important}
.st-key-navbar .stButton button{min-height:2.1rem;border-color:var(--border)!important}
.ra-brand{display:flex;align-items:baseline;gap:.5rem;white-space:nowrap}
.ra-brand b{font-family:var(--serif);font-weight:400;font-size:1.35rem;color:var(--text);letter-spacing:-.01em}
.ra-brand b i{color:var(--accent)}
.ra-brand span{font-size:.72rem;color:var(--muted);font-weight:600;letter-spacing:.08em}

/* Contacto */
.ra-contact{display:flex;align-items:center;gap:1rem;flex-wrap:wrap;background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:.9rem 1rem;margin-bottom:2rem;position:relative;overflow:hidden;animation:fadeIn .8s var(--ease) both}
.ra-contact::before{content:"";position:absolute;inset:0;background:radial-gradient(600px 120px at 0% 0%,var(--accent-soft),transparent 70%);pointer-events:none}
.ra-ph{position:relative;width:58px;height:58px;flex-shrink:0;border-radius:50%;padding:2px;background:conic-gradient(from var(--a,0deg),var(--accent),transparent 40%,var(--accent) 75%,transparent);animation:spin 7s linear infinite}
.ra-ph img{width:100%;height:100%;border-radius:50%;object-fit:cover;border:2px solid var(--surface);display:block}
@property --a{syntax:'<angle>';inherits:false;initial-value:0deg}
.ra-who{position:relative;flex:1;min-width:170px}
.ra-who .n{font-family:var(--serif);font-size:1.45rem;line-height:1.05;color:var(--text)}
.ra-who .t{font-size:.84rem;color:var(--muted);margin-top:.15rem}
.ra-links{position:relative;display:flex;gap:.45rem}
.ra-lk{--c:var(--text);display:inline-flex;align-items:center;gap:.45rem;padding:.48rem .8rem;border-radius:10px;border:1px solid var(--border2);background:var(--surface);color:var(--text)!important;text-decoration:none!important;font-size:.84rem;font-weight:600;transition:all .4s var(--ease)!important;white-space:nowrap}
.ra-lk svg{width:16px;height:16px;flex-shrink:0;transition:transform .5s var(--ease)}
.ra-lk:hover{border-color:var(--c);color:var(--c)!important;transform:translateY(-2px);box-shadow:0 10px 22px -14px var(--c)}
.ra-lk:hover svg{transform:rotate(-10deg) scale(1.12)}
.ra-lk.wa{--c:#1EA952}.ra-lk.ig{--c:#D62976}.ra-lk.ml{--c:var(--accent)}

/* Encabezados de sección */
.ra-head{display:flex;align-items:baseline;justify-content:space-between;gap:1rem;margin:.2rem 0 .1rem}
.ra-head .t{font-family:var(--serif);font-size:2rem;line-height:1;color:var(--text)}
.ra-head .t i{color:var(--accent)}
.ra-head .c{font-size:.8rem;color:var(--muted);font-weight:600}
.ra-sub{color:var(--muted);font-size:.86rem;margin:.25rem 0 .2rem}

/* Tarjetas de producto */
[class*="st-key-card_"]{position:relative;background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:8px 8px 12px;gap:.4rem!important;cursor:pointer;transition:transform .55s var(--ease),box-shadow .55s var(--ease),border-color .4s!important;animation:rise .8s var(--ease) both}
@supports (animation-timeline:view()){[class*="st-key-card_"]{animation:rise linear both;animation-timeline:view();animation-range:entry 0% cover 22%}}
[class*="st-key-card_"]:hover{transform:translateY(-4px);box-shadow:0 22px 40px -26px var(--shadow2);border-color:var(--border2)}
[class*="st-key-card_"]:hover .ra-img img{transform:scale(1.045)}
[class*="st-key-card_"]:hover .ra-hint{opacity:1;transform:none}
[class*="st-key-card_"]:has(button:focus-visible){outline:2px solid var(--accent);outline-offset:2px}
[class*="st-key-view_"]{position:absolute!important;inset:0;z-index:2;margin:0!important}
[class*="st-key-view_"] div,[class*="st-key-view_"] button{width:100%!important;height:100%!important}
[class*="st-key-view_"] button{opacity:0!important;cursor:pointer}
.ra-img{position:relative;aspect-ratio:4/5;border-radius:11px;overflow:hidden;background:var(--surface2)}
.ra-img.big{border-radius:16px}
.ra-img img{width:100%;height:100%;object-fit:cover;display:block;transition:transform 1s var(--ease),filter .6s!important}
.ra-img img.r{animation:inR .55s var(--ease)}
.ra-img img.l{animation:inL .55s var(--ease)}
.ra-img.sold img{filter:grayscale(1) contrast(.9) brightness(.92)}
.ra-tl{position:absolute;top:8px;left:8px;display:flex;gap:4px}
.ra-badge{background:rgba(255,255,255,.88);color:#11141C;backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);font-size:.68rem;font-weight:700;padding:4px 8px;border-radius:999px;display:inline-flex;align-items:center;gap:5px}
.ra-badge.ok::before{content:"";width:6px;height:6px;border-radius:50%;background:#1F9D61;animation:pulse 2.4s infinite}
.ra-badge.out{background:#11141C;color:#fff}
.ra-hint{position:absolute;right:8px;top:8px;width:28px;height:28px;border-radius:50%;background:rgba(255,255,255,.9);color:#11141C;display:grid;place-items:center;opacity:0;transform:translate(-4px,4px);transition:all .45s var(--ease)!important}
.ra-hint svg{width:14px;height:14px}
.ra-dots{position:absolute;bottom:10px;left:50%;transform:translateX(-50%);display:flex;gap:4px}
.ra-dots i{width:5px;height:5px;border-radius:9px;background:rgba(255,255,255,.55);transition:all .45s var(--ease)!important}
.ra-dots i.on{width:16px;background:#fff}
.ra-info{padding:0 4px}
.ra-cat{font-size:.72rem;color:var(--muted);font-weight:600}
.ra-name{font-weight:600;font-size:.95rem;line-height:1.25;color:var(--text);margin:.1rem 0 .35rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ra-chips{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:.45rem}
.chip{display:inline-flex;align-items:center;gap:4px;font-size:.7rem;padding:3px 8px;border-radius:6px;background:var(--chip);color:var(--muted);font-weight:600;white-space:nowrap}
.chip svg{width:11px;height:11px}
.chip.size{background:var(--text);color:var(--bg)}
.ra-price{font-weight:700;font-size:1rem;color:var(--text)}

/* Flechas del carrusel sobre la foto */
[class*="st-key-arw_"],[class*="st-key-garw_"]{position:relative;z-index:3;margin-top:-3.1rem!important;padding:0 .55rem;pointer-events:none}
[class*="st-key-garw_"]{margin-top:-3.9rem!important;padding:0 .9rem}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;justify-content:space-between!important}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) [data-testid="stColumn"]{width:auto!important;flex:0 0 auto!important;min-width:0!important}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) button{pointer-events:auto;width:30px!important;height:30px!important;min-height:30px!important;padding:0!important;border-radius:50%!important;background:rgba(255,255,255,.9)!important;color:#11141C!important;border:none!important;box-shadow:0 6px 16px -8px rgba(0,0,0,.35)!important;opacity:0;transform:scale(.85)}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) button p,:is([class*="st-key-arw_"],[class*="st-key-garw_"]) button span{color:#11141C!important}
[class*="st-key-garw_"] button{width:40px!important;height:40px!important;min-height:40px!important;opacity:1;transform:none}
[class*="st-key-card_"]:hover [class*="st-key-arw_"] button{opacity:1;transform:none}
:is([class*="st-key-arw_"],[class*="st-key-garw_"]) button:hover{background:#fff!important;transform:scale(1.1)!important}
@media (hover:none){[class*="st-key-arw_"] button{opacity:1;transform:none}}

/* Detalle */
.ra-thumbs{display:flex;gap:6px;margin-top:.6rem;overflow-x:auto}
.ra-thumbs img{width:52px;height:64px;object-fit:cover;border-radius:8px;opacity:.4;border:1.5px solid transparent;flex-shrink:0;transition:all .4s var(--ease)!important}
.ra-thumbs img.on{opacity:1;border-color:var(--text)}
.ra-d{animation:rise .7s .05s var(--ease) both}
.ra-d-cat{font-size:.8rem;color:var(--accent);font-weight:700}
.ra-d-name{font-family:var(--serif);font-size:clamp(2rem,3.6vw,2.7rem);line-height:1.02;color:var(--text);margin:.25rem 0 .6rem;letter-spacing:-.01em}
.ra-d-price{display:flex;align-items:center;gap:.7rem;margin-bottom:.8rem}
.ra-d-price b{font-size:1.45rem;font-weight:700;color:var(--text)}
.ra-pill{font-size:.74rem;font-weight:700;padding:4px 10px;border-radius:999px;display:inline-flex;align-items:center;gap:6px}
.ra-pill.ok{background:color-mix(in srgb,var(--ok) 13%,transparent);color:var(--ok)}
.ra-pill.ok::before{content:"";width:6px;height:6px;border-radius:50%;background:var(--ok);animation:pulse 2.4s infinite}
.ra-pill.out{background:var(--chip);color:var(--muted)}
.ra-d-short{color:var(--muted);font-size:.92rem;line-height:1.6;margin:.5rem 0 1.1rem;max-width:52ch}
.ra-cta{position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;gap:.5rem;width:100%;padding:.8rem 1rem;border-radius:11px;background:var(--text);color:var(--bg)!important;font-weight:600;font-size:.92rem;text-decoration:none!important;transition:all .45s var(--ease)!important}
.ra-cta svg{width:17px;height:17px}
.ra-cta::after{content:"";position:absolute;inset:0;background:linear-gradient(105deg,transparent 35%,rgba(255,255,255,.28) 50%,transparent 65%);transform:translateX(-120%);transition:transform .9s var(--ease)}
.ra-cta:hover{background:var(--accent);color:var(--accent-ink)!important;transform:translateY(-2px);box-shadow:0 14px 28px -14px var(--glow)}
.ra-cta:hover::after{transform:translateX(120%)}
.ra-cta-row{display:grid;grid-template-columns:1fr 1fr;gap:.45rem;margin-top:.45rem}
.ra-cta.ghost{background:transparent;color:var(--text)!important;border:1px solid var(--border2);font-size:.85rem;padding:.62rem .8rem}
.ra-cta.ghost:hover{background:transparent;border-color:var(--text);color:var(--text)!important;box-shadow:none}
.ra-specs{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1px;background:var(--border);border:1px solid var(--border);border-radius:12px;overflow:hidden;margin:1.2rem 0}
.ra-specs div{background:var(--surface);padding:.65rem .8rem}
.ra-specs small{display:flex;align-items:center;gap:4px;color:var(--muted);font-size:.7rem;font-weight:600;margin-bottom:2px}
.ra-specs small svg{width:11px;height:11px}
.ra-specs span{color:var(--text);font-weight:600;font-size:.86rem}
.ra-desc h4{font-family:var(--sans)!important;font-size:.8rem!important;font-weight:700!important;color:var(--muted)!important;margin:.4rem 0 .35rem!important;padding:0!important}
.ra-desc p{color:var(--text)!important;opacity:.85;line-height:1.7;font-size:.92rem;max-width:62ch}
.ra-desc ul{list-style:none;padding:0;margin:.2rem 0 0}
.ra-desc li{padding:.4rem 0;border-bottom:1px solid var(--border);color:var(--text)!important;font-size:.88rem;display:flex;gap:.6rem}
.ra-desc li::before{content:"";width:5px;height:5px;margin-top:.5rem;border-radius:50%;background:var(--accent);flex-shrink:0}

/* Perfiles, listas y tablas */
.ra-prof{display:flex;gap:1rem;align-items:center;flex-wrap:wrap;background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:1rem 1.1rem;margin-bottom:1rem;animation:rise .6s var(--ease) both}
.ra-prof>img{width:64px;height:64px;border-radius:50%;object-fit:cover;box-shadow:0 0 0 3px var(--surface),0 0 0 4px var(--border2)}
.ra-prof .n{font-family:var(--serif);font-size:1.6rem;line-height:1.05;color:var(--text)}
.ra-prof .d{color:var(--muted);font-size:.8rem;margin-top:.3rem;display:flex;gap:.8rem;flex-wrap:wrap}
.ra-prof .d span{display:inline-flex;align-items:center;gap:4px}
.ra-prof .d svg{width:13px;height:13px}
.ra-prof .k{display:flex;gap:1.4rem;margin-left:auto}
.ra-prof .k div{text-align:right}
.ra-prof .k b{display:block;font-family:var(--serif);font-size:1.4rem;color:var(--text);font-weight:400}
.ra-prof .k small{color:var(--muted);font-size:.74rem}
.ra-row{display:flex;align-items:center;gap:.75rem;padding:.55rem;border:1px solid var(--border);border-radius:12px;background:var(--surface)}
.ra-row img{width:42px;height:50px;object-fit:cover;border-radius:8px;flex-shrink:0}
.ra-row .m{flex:1;min-width:0}
.ra-row .m b{display:block;color:var(--text);font-weight:600;font-size:.9rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ra-row .m small{color:var(--muted);font-size:.76rem}
.ra-row .v{font-weight:700;color:var(--text);font-size:.9rem;white-space:nowrap}
.ra-row.flat{border:none;padding:0;background:none}
.ra-table-wrap{overflow-x:auto;border:1px solid var(--border);border-radius:14px;background:var(--surface)}
.ra-table{width:100%;border-collapse:collapse;font-size:.84rem}
.ra-table th{text-align:left;color:var(--muted);font-weight:600;font-size:.74rem;padding:.6rem .8rem;border-bottom:1px solid var(--border);white-space:nowrap}
.ra-table td{padding:.55rem .8rem;border-bottom:1px solid var(--border);color:var(--text);white-space:nowrap}
.ra-table tr:last-child td{border-bottom:none}
.ra-table tbody tr:hover td{background:var(--chip)}
.ra-table img{width:24px;height:24px;border-radius:50%;vertical-align:middle;margin-right:6px;object-fit:cover}
.ra-podium{display:grid;grid-template-columns:repeat(3,1fr);gap:.6rem;margin:.4rem 0 1rem}
.ra-pod{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:.9rem;display:flex;align-items:center;gap:.7rem;animation:rise .6s var(--ease) both}
.ra-pod.first{border-color:var(--accent);box-shadow:0 12px 28px -20px var(--glow)}
.ra-pod img{width:42px;height:42px;border-radius:50%;object-fit:cover}
.ra-pod .p{font-family:var(--serif);font-size:1.6rem;color:var(--accent);width:1.2rem}
.ra-pod b{display:block;color:var(--text);font-size:.9rem}
.ra-pod small{color:var(--muted);font-size:.76rem}
.st-key-authbox{background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:1.4rem 1.4rem 1.2rem;animation:rise .6s var(--ease) both;box-shadow:0 30px 60px -45px var(--shadow2)}
.ra-auth-h{font-family:var(--serif);font-size:2rem;color:var(--text);line-height:1;text-align:center}
.ra-auth-s{color:var(--muted);text-align:center;font-size:.86rem;margin:.35rem 0 .6rem}
.ra-avprev{display:flex;align-items:center;gap:.6rem;margin:-.2rem 0 .3rem}
.ra-avprev img{width:40px;height:40px;border-radius:50%;box-shadow:0 0 0 1px var(--border2)}
.ra-avprev span{color:var(--muted);font-size:.8rem}
.ra-empty{text-align:center;padding:2.6rem 1rem;color:var(--muted);border:1px dashed var(--border2);border-radius:16px;font-size:.88rem}
.ra-empty b{display:block;font-family:var(--serif);font-size:1.4rem;color:var(--text);font-weight:400;margin-bottom:.2rem}
.ra-owner{display:flex;align-items:center;gap:.8rem}
.ra-owner img{width:56px;height:56px;border-radius:50%;object-fit:cover}

/* Footer */
.ra-foot{margin-top:3rem;padding:1.2rem 0 .4rem;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;gap:1rem;flex-wrap:wrap;color:var(--muted);font-size:.8rem}
.ra-foot .b{font-family:var(--serif);font-size:1.1rem;color:var(--text)}
.ra-foot nav{display:flex;gap:.4rem}
.ra-foot a{width:32px;height:32px;border-radius:50%;display:grid;place-items:center;border:1px solid var(--border2);color:var(--text)!important;transition:all .35s var(--ease)!important}
.ra-foot a svg{width:15px;height:15px}
.ra-foot a:hover{background:var(--text);color:var(--bg)!important;transform:translateY(-2px)}

/* Transición del cambio de tema: revelado circular */
.ra-wipe{position:fixed;inset:0;z-index:99999;pointer-events:none;clip-path:circle(145% at calc(100% - 7.5rem) 2.6rem);animation:wipe .9s cubic-bezier(.65,0,.35,1) forwards}
@keyframes wipe{0%{clip-path:circle(145% at calc(100% - 7.5rem) 2.6rem);opacity:1}92%{opacity:1}100%{clip-path:circle(0% at calc(100% - 7.5rem) 2.6rem);opacity:0}}

@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}
@keyframes fadeIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}
@keyframes inR{from{opacity:0;transform:translateX(28px)}to{opacity:1;transform:none}}
@keyframes inL{from{opacity:0;transform:translateX(-28px)}to{opacity:1;transform:none}}
@keyframes spin{to{--a:360deg}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(31,157,97,.45)}60%{box-shadow:0 0 0 6px rgba(31,157,97,0)}}

/* Móvil */
@media (max-width:640px){
 html{font-size:14px}
 .block-container,[data-testid="stMainBlockContainer"]{padding:.3rem .7rem 2rem!important}
 .ra-brand span{display:none}
 .st-key-navbar [data-testid="stColumn"]:first-child{flex:1 1 auto!important;width:auto!important}
 .st-key-navbar [data-testid="stColumn"]:not(:first-child){flex:0 0 auto!important;width:auto!important}
 .ra-contact{gap:.75rem}
 .ra-links{width:100%}
 .ra-lk{flex:1;justify-content:center;padding:.5rem .4rem;font-size:.78rem}
 [class*="st-key-grid_"] [data-testid="stHorizontalBlock"]{flex-wrap:wrap!important;gap:.6rem!important}
 [class*="st-key-grid_"] [data-testid="stColumn"]{flex:1 1 calc(50% - .3rem)!important;min-width:calc(50% - .3rem)!important;width:calc(50% - .3rem)!important}
 .ra-specs{grid-template-columns:1fr 1fr}
 .ra-cta-row{grid-template-columns:1fr 1fr}
 .ra-prof .k{margin-left:0}
 .ra-podium{grid-template-columns:1fr}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""


def inject_css():
    v = THEMES[ss.theme]
    root = ":root{" + "".join(f"--{k}:{val};" for k, val in v.items()) + "}"
    html(f"<style>{root}{CSS}</style>")
    wipe = ss.pop("_wipe", None)
    if wipe:  # capa con el color del tema anterior que se abre en círculo
        html(f'<div class="ra-wipe" style="background:{THEMES[wipe]["bg"]}" data-n="{uuid.uuid4().hex[:6]}"></div>')


# ════════════════════════════════════════════════════════════════════════
# 8. COMPONENTES
# ════════════════════════════════════════════════════════════════════════
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


def _toggle_theme():
    ss["_wipe"] = ss.theme
    ss.theme = "dark" if ss.theme == "light" else "light"


def render_navbar(db, view):
    with st.container(key="navbar"):
        c_brand, c_shop, c_theme, c_acc = st.columns([6, 1.1, .5, 1.25], vertical_alignment="center")
        c_brand.markdown('<div class="ra-brand"><b>Rissos <i>Anghell</i></b><span>STORE</span></div>',
                         unsafe_allow_html=True)
        with c_shop:
            if view != "home" and st.button("Tienda", key="nav_shop", icon=":material/storefront:",
                                            use_container_width=True):
                go("home")
        with c_theme:
            st.button("", key="nav_theme", on_click=_toggle_theme, use_container_width=True,
                      icon=":material/dark_mode:" if ss.theme == "light" else ":material/light_mode:",
                      help="Tema oscuro" if ss.theme == "light" else "Tema claro")
        with c_acc:
            u = current_user(db)
            if u:
                if st.button(u["name"].split()[0], key="nav_acc", icon=":material/account_circle:",
                             use_container_width=True):
                    go("profile")
            elif ss.role == "admin":
                if st.button("Panel", key="nav_acc", icon=":material/admin_panel_settings:",
                             use_container_width=True):
                    go("admin")
            elif st.button("Ingresar", key="nav_acc", icon=":material/person:", use_container_width=True):
                go("login")


def render_contact():
    mail = mailto("Contacto – Rissos Anghell Store", "Hola Benjamín,\n\n")
    wa = wa_link("Hola Benjamín, te escribo desde Rissos Anghell Store.")
    html(
        '<section class="ra-contact">'
        f'<div class="ra-ph"><img src="{owner_photo()}" alt="{esc(OWNER["name"])}"/></div>'
        f'<div class="ra-who"><div class="n">{esc(OWNER["name"])}</div><div class="t">{esc(OWNER["tagline"])}</div></div>'
        '<div class="ra-links">'
        f'<a class="ra-lk wa" href="{wa}" target="_blank" rel="noopener" title="{OWNER["whatsapp_display"]}">{ICON["whatsapp"]}<span>WhatsApp</span></a>'
        f'<a class="ra-lk ig" href="{IG_LINK}" target="_blank" rel="noopener" title="@{OWNER["instagram"]}">{ICON["instagram"]}<span>Instagram</span></a>'
        f'<a class="ra-lk ml" href="{mail}" title="{OWNER["email"]}">{ICON["mail"]}<span>Correo</span></a>'
        '</div></section>')


def card_image_html(p, idx: int, d: str, big: bool = False) -> str:
    imgs = p.get("images") or ["demo:bag:0"]
    sold = p["status"] != "Disponible"
    badge = (f'<span class="ra-badge out">{esc(p["status"])}</span>' if sold
             else '<span class="ra-badge ok">Disponible</span>')
    dots = "".join(f'<i class="{"on" if i == idx else ""}"></i>' for i in range(len(imgs))) if len(imgs) > 1 else ""
    hint = "" if big else f'<span class="ra-hint">{ICON["arrow"]}</span>'
    return (f'<div class="ra-img{" big" if big else ""}{" sold" if sold else ""}">'
            f'<img class="{d}" src="{img_src(imgs[idx], thumb=not big)}" alt="{esc(p["name"])}" loading="lazy"/>'
            f'<div class="ra-tl">{badge}</div>{hint}<div class="ra-dots">{dots}</div></div>')


def chips_html(p, with_brand=False) -> str:
    out = ""
    if p.get("size"):
        out += f'<span class="chip size">{esc(size_label(p))}</span>'
    if p.get("made_in"):
        out += f'<span class="chip">{ICON["globe"]}Made in {esc(p["made_in"])}</span>'
    if with_brand and p.get("brand"):
        out += f'<span class="chip">{ICON["tag"]}{esc(p["brand"])}</span>'
    return out


def _step(prefix: str, pid: str, n: int, delta: int):
    k = f"{prefix}idx_{pid}"
    ss[k] = (ss.get(k, 0) + delta) % n
    ss[f"{prefix}dir_{pid}"] = "l" if delta < 0 else "r"


def carousel_arrows(prefix: str, key: str, pid: str, n: int):
    with st.container(key=f"{key}_{pid}" if prefix == "g" else key):
        a, b = st.columns(2)
        a.button("", key=f"btnp_{key}_{pid}", icon=":material/chevron_left:", on_click=_step, args=(prefix, pid, n, -1))
        b.button("", key=f"btnn_{key}_{pid}", icon=":material/chevron_right:", on_click=_step, args=(prefix, pid, n, 1))


@st.fragment
def product_card(p, scope: str = "h"):
    pid = p["id"]
    imgs = p.get("images") or ["demo:bag:0"]
    n = len(imgs)
    idx = ss.get(f"idx_{pid}", 0) % n
    with st.container(key=f"card_{scope}_{pid}"):
        html(card_image_html(p, idx, ss.get(f"dir_{pid}", "r")))
        if n > 1:
            carousel_arrows("", f"arw_{scope}_{pid}", pid, n)
        html(f'<div class="ra-info"><div class="ra-cat">{esc(p.get("category"))}</div>'
             f'<div class="ra-name" title="{esc(p["name"])}">{esc(p["name"])}</div>'
             f'<div class="ra-chips">{chips_html(p)}</div>'
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


def empty(title: str, text: str):
    html(f'<div class="ra-empty"><b>{esc(title)}</b>{esc(text)}</div>')


def section(title_html: str, right: str = "", sub: str = ""):
    html(f'<div class="ra-head"><div class="t">{title_html}</div><div class="c">{right}</div></div>'
         + (f'<div class="ra-sub">{sub}</div>' if sub else ""))


# ════════════════════════════════════════════════════════════════════════
# 9. VISTAS PÚBLICAS
# ════════════════════════════════════════════════════════════════════════
def render_home(db):
    render_contact()
    avail = sum(1 for p in db["products"] if p["status"] == "Disponible")
    section("Catálogo", f"{avail} disponibles de {len(db['products'])}")

    present = [c for c in CATEGORIES if any(p["category"] == c for p in db["products"])]
    f1, f2 = st.columns([3, 1], vertical_alignment="center")
    with f1:
        cat = st.pills("Categoría", ["Todo"] + present, default="Todo",
                       label_visibility="collapsed", key="cat_pills") or "Todo"
    with f2:
        only = st.toggle("Solo disponibles", key="only_avail")
    q = st.text_input("Buscar", placeholder="Buscar por nombre, marca o talla",
                      label_visibility="collapsed", key="search", icon=":material/search:")

    items = db["products"]
    if cat != "Todo":
        items = [p for p in items if p["category"] == cat]
    if only:
        items = [p for p in items if p["status"] == "Disponible"]
    if q:
        ql = q.lower().strip()
        items = [p for p in items if ql in " ".join(str(p.get(k, "")) for k in
                                                     ("name", "brand", "size", "made_in", "category", "short")).lower()]
    items = sorted(items, key=lambda p: p["status"] != "Disponible")
    if items:
        product_grid(items, "h")
    else:
        empty("Sin resultados", "Prueba otra categoría o borra la búsqueda.")


@st.fragment
def gallery(p):
    pid = p["id"]
    imgs = p.get("images") or ["demo:bag:0"]
    n = len(imgs)
    idx = ss.get(f"gidx_{pid}", 0) % n
    html(card_image_html(p, idx, ss.get(f"gdir_{pid}", "r"), big=True))
    if n > 1:
        carousel_arrows("g", "garw", pid, n)
        html('<div class="ra-thumbs">' + "".join(
            f'<img class="{"on" if i == idx else ""}" src="{img_src(e, thumb=True)}"/>' for i, e in enumerate(imgs))
             + "</div>")


def render_product(db, pid):
    p = get_product(db, pid)
    if not p:
        empty("Este artículo ya no está publicado", "Puede que se haya vendido. Revisa el catálogo.")
        st.write("")
        if st.button("Ver catálogo", type="primary", icon=":material/storefront:"):
            go("home")
        return
    if st.button("Volver", key="back_top", icon=":material/arrow_back:"):
        go("home")

    left, right = st.columns([1, 1.05], gap="large")
    with left:
        gallery(p)
    with right:
        sold = p["status"] != "Disponible"
        pill = f'<span class="ra-pill {"out" if sold else "ok"}">{esc(p["status"])}</span>'
        subject, body = consult_message(db, p)
        sl = size_label(p)
        wa_txt = (f"Hola Benjamín, quiero consultar el stock de: {p['name']}" + (f" ({sl})" if sl else "")
                  + f" – {money(p['price'])}\n{product_link(db, p['id'])}")
        specs = [("ruler", "Talla" if p.get("category") in SIZED else "Medida", p.get("size") or "No aplica"),
                 ("globe", "Made in", p.get("made_in") or "—"), ("tag", "Marca", p.get("brand") or "—"),
                 ("spark", "Condición", p.get("condition") or "—"), ("bag", "Categoría", p.get("category")),
                 ("calendar", "Publicado", fmt_date(p.get("created")))]
        desc = esc(p.get("description"))
        det = "".join(f"<li>{esc(x)}</li>" for x in (p.get("details") or []) if str(x).strip())
        html(
            '<div class="ra-d">'
            f'<div class="ra-d-cat">{esc(p.get("category"))}</div>'
            f'<div class="ra-d-name">{esc(p["name"])}</div>'
            f'<div class="ra-d-price"><b>{money_html(p["price"])}</b>{pill}</div>'
            f'<div class="ra-chips">{chips_html(p, with_brand=True)}</div>'
            f'<div class="ra-d-short">{esc(p.get("short"))}</div>'
            f'<a class="ra-cta" href="{mailto(subject, body)}">{ICON["mail"]}'
            f'{"Consultar disponibilidad" if sold else "Consultar"}</a>'
            '<div class="ra-cta-row">'
            f'<a class="ra-cta ghost" href="{wa_link(wa_txt)}" target="_blank" rel="noopener">{ICON["whatsapp"]}WhatsApp</a>'
            f'<a class="ra-cta ghost" href="{gmail_link(subject, body)}" target="_blank" rel="noopener">{ICON["mail"]}Gmail</a>'
            '</div>'
            '<div class="ra-specs">' + "".join(
                f"<div><small>{ICON[i]}{esc(k)}</small><span>{esc(v)}</span></div>" for i, k, v in specs) + "</div>"
            '<div class="ra-desc">'
            + (f"<h4>Descripción</h4><p>{desc}</p>" if desc else "")
            + (f"<h4 style='margin-top:1rem!important'>Detalles</h4><ul>{det}</ul>" if det else "")
            + "</div></div>")
        st.caption("Link directo del artículo")
        st.code(product_link(db, p["id"]), language=None)

    related = [x for x in db["products"] if x["id"] != p["id"] and x["category"] == p["category"]]
    related += [x for x in db["products"] if x["id"] != p["id"] and x not in related]
    related = sorted(related, key=lambda x: x["status"] != "Disponible")[:4]
    if related:
        st.write("")
        section("También te puede <i>gustar</i>")
        product_grid(related, "r")


# ════════════════════════════════════════════════════════════════════════
# 10. CUENTAS
# ════════════════════════════════════════════════════════════════════════
def avatar_picker(prefix: str, default: str | None = None):
    names = list(AVATAR_COLORS)
    key = f"{prefix}_color"
    if key not in ss:
        ss[key] = default if default in names else random.choice(names)
    name = st.radio("Color del avatar", names, horizontal=True, key=key)
    html(f'<div class="ra-avprev"><img src="{avatar_svg(AVATAR_COLORS[name])}"/><span>Vista previa</span></div>')
    return name


def opt_field(label: str, key: str, placeholder: str, current: str = ""):
    """Campo opcional con selector Agregar / No agregar."""
    choice = st.radio(label, ["No agregar", "Agregar"], horizontal=True, key=f"{key}_opt",
                      index=1 if current else 0)
    if choice == "Agregar":
        return st.text_input(label, value=current, key=key, placeholder=placeholder,
                             label_visibility="collapsed").strip()
    return ""


def render_login(db):
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid, st.container(key="authbox"):
        html('<div class="ra-auth-h">Tu cuenta</div>'
             '<div class="ra-auth-s">Regístrate y tus compras quedarán guardadas en tu perfil.</div>')
        tab_user, tab_admin = st.tabs([":material/person: Usuario", ":material/admin_panel_settings: Administrador"])
        with tab_user:
            mode = st.segmented_control("Modo", ["Iniciar sesión", "Crear cuenta"], default="Iniciar sesión",
                                        key="auth_mode", label_visibility="collapsed") or "Iniciar sesión"
            if mode == "Iniciar sesión":
                phone = st.text_input("Teléfono", placeholder="+56 9 1234 5678", key="li_phone",
                                      icon=":material/call:")
                pw = st.text_input("Contraseña", type="password", key="li_pw", icon=":material/lock:")
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
            apw = st.text_input("Contraseña de administrador", type="password", key="adm_pw",
                                icon=":material/key:")
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
        if existing:  # cliente creado antes por el admin: toma esa cuenta y sus compras
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
    bits = [("phone", u.get("phone_display") or u["phone"]), ("mail", u.get("email")),
            ("pin", u.get("location")), ("gender", gender), ("calendar", f"Desde {fmt_date(u.get('created'))}")]
    meta = "".join(f"<span>{ICON[i]}{esc(v)}</span>" for i, v in bits if v)
    html(f'<div class="ra-prof"><img src="{user_avatar(u)}"/><div><div class="n">{esc(u["name"])}</div>'
         f'<div class="d">{meta}</div></div><div class="k"><div><b>{c}</b><small>compras</small></div>'
         f'<div><b>{units}</b><small>unidades</small></div><div><b>{money_html(total)}</b><small>total</small></div>'
         '</div></div>')


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
    t1, t2 = st.tabs([":material/receipt_long: Mis compras", ":material/manage_accounts: Mis datos"])
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
            cur = next((k for k, v in AVATAR_COLORS.items() if v == u.get("avatar_color")), None)
            color = avatar_picker("pf", cur)
        with st.expander("Cambiar contraseña", icon=":material/lock:"):
            npw = st.text_input("Nueva contraseña", type="password", key="pf_npw")
            npw2 = st.text_input("Repetir nueva contraseña", type="password", key="pf_npw2")
        b1, b2 = st.columns(2)
        if b1.button("Guardar cambios", type="primary", use_container_width=True, key="pf_save",
                     icon=":material/save:"):
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
        if b2.button("Cerrar sesión", use_container_width=True, key="pf_out", icon=":material/logout:"):
            logout()


# ════════════════════════════════════════════════════════════════════════
# 11. ADMINISTRACIÓN
# ════════════════════════════════════════════════════════════════════════
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
    size = c4.text_input("Talla o medida", value=p.get("size", ""), placeholder="L, 42, Única…", key=f"{prefix}_size")
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
    with st.expander("Publicar producto nuevo", icon=":material/add_circle:"):
        with st.form("add_prod", clear_on_submit=True, border=False):
            data = product_form_fields("np")
            imgs = st.file_uploader("Fotos (la primera será la portada)", type=["jpg", "jpeg", "png", "webp"],
                                    accept_multiple_files=True, key="np_imgs")
            ok = st.form_submit_button("Publicar", type="primary", use_container_width=True)
        if ok:
            if not data["name"]:
                st.error("El producto necesita un nombre.")
            else:
                data.update(id=new_id(), created=now_iso(),
                            images=[save_upload(f) for f in (imgs or [])] or ["demo:bag:0"])
                db["products"].insert(0, data)
                save_db(db)
                flash(f"Publicado: {data['name']}")
                st.rerun()

    if not db["products"]:
        empty("Catálogo vacío", "Publica tu primer producto arriba.")
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
                    flash("Producto eliminado", ":material/delete:")
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
                        st.error("El producto necesita un nombre.")
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
                        flash("Producto actualizado")
                        st.rerun()


def admin_sales(db):
    if not db["users"]:
        empty("Todavía no hay clientes", "Cuando alguien cree su cuenta, o lo agregues en Clientes, podrás registrar sus compras aquí.")
        return
    if not db["products"]:
        st.info("Publica al menos un producto para registrar ventas.")
        return
    html('<div class="ra-sub">Ej: Pepito compró la Polera roja y ya se la entregaste. Queda guardado en su perfil.</div>')
    users = sorted(db["users"], key=lambda u: u["name"].lower())
    c1, c2 = st.columns(2)
    uid = c1.selectbox("Cliente", [u["id"] for u in users], key="sale_user",
                       format_func=lambda i: (lambda u: f"{u['name']} · {u.get('phone_display') or u['phone']}")(get_user(db, i)))
    pid = c2.selectbox("Producto", [p["id"] for p in db["products"]], key="sale_prod",
                       format_func=lambda i: (lambda p: f"{p['name']} · {money(p['price'])}"
                                              + ("" if p["status"] == "Disponible" else f" · {p['status']}"))(get_product(db, i)))
    p = get_product(db, pid)
    c3, c4, c5 = st.columns(3)
    qty = c3.number_input("Cantidad", min_value=1, step=1, value=1, key="sale_qty")
    price = c4.number_input("Precio unitario", min_value=0, step=500, value=int(p["price"]), key=f"sale_price_{pid}")
    d = c5.date_input("Fecha de entrega", value=date.today(), key="sale_date", format="DD/MM/YYYY")
    note = st.text_input("Nota (opcional)", placeholder="Ej: entregado en metro Los Héroes", key="sale_note")
    mark = st.checkbox("Marcar el producto como Agotado", value=True, key="sale_mark")
    if st.button("Registrar venta", type="primary", use_container_width=True, key="sale_btn",
                 icon=":material/receipt_long:"):
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
        section("Últimas ventas")
        rows = "".join(f"<tr><td>{fmt_date(x['date'])}</td><td>{esc((get_user(db, x['user_id']) or {}).get('name', '—'))}</td>"
                       f"<td>{esc(x['product_name'])}</td><td>{x['qty']}</td><td>{money_html(x['total'])}</td></tr>"
                       for x in recent)
        html('<div class="ra-table-wrap"><table class="ra-table"><thead><tr><th>Fecha</th><th>Cliente</th>'
             f'<th>Producto</th><th>Cant.</th><th>Total</th></tr></thead><tbody>{rows}</tbody></table></div>')


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
        section("Quién te compra <i>más</i>")
        html('<div class="ra-podium">' + "".join(
            f'<div class="ra-pod{" first" if i == 0 else ""}" style="animation-delay:{i * .08}s"><div class="p">{i + 1}</div>'
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

    st.write("")
    section("Perfil del cliente")
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
    html(f'<div class="ra-owner"><img src="{owner_photo()}"/><div class="ra-sub" style="margin:0">'
         + (f"Foto cargada desde <b>{esc(found.relative_to(BASE_DIR))}</b>." if found else
            "No se encontró <b>benja.jpeg</b>. Súbela a la raíz del repositorio de GitHub y se mostrará sola.")
         + "</div></div>")
    st.divider()
    section("Link de la tienda", sub="Se usa en los correos de consulta. Si publicas la app, pega aquí su dirección.")
    bu = st.text_input("Dirección pública", value=db["settings"].get("base_url", ""), key="set_base",
                       placeholder=app_base_url(db), label_visibility="collapsed")
    if st.button("Guardar link", key="set_base_btn", icon=":material/link:"):
        db["settings"]["base_url"] = bu.strip()
        save_db(db)
        flash("Link guardado", ":material/link:")
        st.rerun()
    st.divider()
    section("Contraseña de administrador")
    a, b, c = st.columns(3)
    cur = a.text_input("Actual", type="password", key="set_cur")
    new = b.text_input("Nueva", type="password", key="set_new")
    new2 = c.text_input("Repetir nueva", type="password", key="set_new2")
    if st.button("Cambiar contraseña", key="set_pw_btn", icon=":material/key:"):
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
                       file_name=f"rissos_respaldo_{date.today().isoformat()}.json", mime="application/json",
                       icon=":material/download:")


def render_admin(db):
    if ss.role != "admin":
        go("login")
    h, o = st.columns([5, 1], vertical_alignment="bottom")
    with h:
        section("Panel de <i>administración</i>")
    with o:
        if st.button("Salir", key="adm_out", icon=":material/logout:", use_container_width=True):
            logout()
    t1, t2, t3, t4 = st.tabs([":material/inventory_2: Productos", ":material/receipt_long: Registrar venta",
                              ":material/group: Clientes", ":material/settings: Ajustes"])
    with t1:
        admin_products(db)
    with t2:
        admin_sales(db)
    with t3:
        admin_clients(db)
    with t4:
        admin_settings(db)


def render_footer():
    html(f'<footer class="ra-foot"><div><div class="b">Rissos Anghell Store</div>'
         f'© {date.today().year} Benjamín Espinoza · Santiago, Chile</div><nav>'
         f'<a href="{wa_link()}" target="_blank" rel="noopener" title="WhatsApp">{ICON["whatsapp"]}</a>'
         f'<a href="{IG_LINK}" target="_blank" rel="noopener" title="Instagram">{ICON["instagram"]}</a>'
         f'<a href="{mailto("Contacto – Rissos Anghell Store")}" title="Correo">{ICON["mail"]}</a></nav></footer>')


# ════════════════════════════════════════════════════════════════════════
# 12. MAIN
# ════════════════════════════════════════════════════════════════════════
def main():
    db = load_db()
    inject_css()
    if "_flash" in ss:
        msg, icon = ss.pop("_flash")
        st.toast(msg, icon=icon)

    pid = st.query_params.get("producto")
    view = "product" if pid else ("home" if ss.view == "product" else ss.view)

    render_navbar(db, view)
    {"product": lambda: render_product(db, pid), "login": lambda: render_login(db),
     "profile": lambda: render_profile(db), "admin": lambda: render_admin(db)}.get(view, lambda: render_home(db))()
    render_footer()

    nav_key = f"{view}:{pid or ''}"
    if ss.get("_last_nav") not in (None, nav_key):
        scroll_top()
    ss["_last_nav"] = nav_key


main()
