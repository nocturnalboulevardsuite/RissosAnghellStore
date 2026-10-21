# -*- coding: utf-8 -*-
"""
Rissos Anghell Store — tienda personal de Benjamín Espinoza
Ejecutar:  streamlit run app.py
"""
import base64
import hashlib
import html as htmllib
import json
import random
import re
import secrets
import uuid
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps

st.set_page_config(
    page_title="Rissos Anghell Store",
    page_icon="🖤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ════════════════════════════════════════════════════════════════════
#  CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════════
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
IMG_DIR = DATA_DIR / "images"
ASSETS_DIR = BASE_DIR / "assets"
DB_PATH = DATA_DIR / "db.json"
for _d in (DATA_DIR, IMG_DIR, ASSETS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

STORE_NAME = "Rissos Anghell Store"
OWNER = {
    "name": "Benjamín Espinoza",
    "tagline": "Compra y venta de artículos, ropa y mucho más.",
    "whatsapp": "56936992950",
    "whatsapp_display": "+56 9 3699 2950",
    "instagram": "rissos._.anghell",
    "email": "nocturnalboulevardsuite@gmail.com",
}
DEFAULT_ADMIN_PASSWORD = "anghell2026"  # cámbiala en Admin › Ajustes

CATEGORIES = ["Ropa", "Calzado", "Accesorios", "Perfumes", "Figuras", "Tecnología", "Otros"]
SIZED_CATEGORIES = ("Ropa", "Calzado", "Accesorios")
STATUSES = ["Disponible", "Agotado", "Fuera de stock"]
CONDITIONS = ["Nuevo", "Nuevo sin etiqueta", "Usado, como nuevo", "Usado"]
GENDERS = ["Masculino", "Femenino", "No Binario", "Prefiero no decirlo", "Personalizado"]
FLAGS = {
    "China": "🇨🇳", "Taiwán": "🇹🇼", "EE.UU.": "🇺🇸", "Vietnam": "🇻🇳", "Bangladesh": "🇧🇩",
    "India": "🇮🇳", "Indonesia": "🇮🇩", "Camboya": "🇰🇭", "Tailandia": "🇹🇭", "Turquía": "🇹🇷",
    "Pakistán": "🇵🇰", "México": "🇲🇽", "Brasil": "🇧🇷", "Chile": "🇨🇱", "Perú": "🇵🇪",
    "Italia": "🇮🇹", "Francia": "🇫🇷", "España": "🇪🇸", "Portugal": "🇵🇹", "Alemania": "🇩🇪",
    "Reino Unido": "🇬🇧", "Japón": "🇯🇵", "Corea del Sur": "🇰🇷",
}
MADE_IN_OPTIONS = list(FLAGS.keys()) + ["Otro"]
AVATAR_COLORS = {
    "Rojo": "#D32F45", "Blanco": "#F4F4F6", "Negro": "#151515", "Azul": "#2557D6",
    "Verde": "#2E9E6A", "Morado": "#7A4FD0", "Naranjo": "#EF7A1A", "Dorado": "#C9A24A",
    "Rosado": "#E86A9A", "Gris": "#7E8494",
}

# Paleta "boulevard nocturno": tinta de noche + granate + plata lunar
THEMES = {
    "dark": {
        "bg": "#0D1220", "surface": "#141B2D", "surface2": "#1B2338",
        "text": "#ECEAF2", "muted": "#8E94A8", "border": "rgba(236,234,242,.09)",
        "accent": "#D4566E", "accent-ink": "#ffffff", "accent-soft": "rgba(212,86,110,.45)",
        "glow": "rgba(212,86,110,.35)", "shadow": "rgba(0,0,0,.65)",
        "nav": "rgba(13,18,32,.74)", "blob1": "rgba(212,86,110,.20)",
        "blob2": "rgba(92,116,196,.24)", "chip": "rgba(236,234,242,.06)",
        "silver": "#B9C0D4",
    },
    "light": {
        "bg": "#EEF0F4", "surface": "#FFFFFF", "surface2": "#E6E9EF",
        "text": "#121726", "muted": "#5E6478", "border": "rgba(18,23,38,.09)",
        "accent": "#9E2238", "accent-ink": "#ffffff", "accent-soft": "rgba(158,34,56,.40)",
        "glow": "rgba(158,34,56,.28)", "shadow": "rgba(18,23,38,.22)",
        "nav": "rgba(238,240,244,.78)", "blob1": "rgba(158,34,56,.12)",
        "blob2": "rgba(60,84,150,.14)", "chip": "rgba(18,23,38,.045)",
        "silver": "#5E6478",
    },
}

# ════════════════════════════════════════════════════════════════════
#  UTILIDADES
# ════════════════════════════════════════════════════════════════════
def esc(s) -> str:
    return htmllib.escape(str(s or ""))


def html(s: str):
    st.markdown(s, unsafe_allow_html=True)


def money(n) -> str:
    return "$" + f"{int(n or 0):,}".replace(",", ".")


def money_html(n) -> str:
    # &#36; evita que Streamlit interprete el $ como fórmula
    return "&#36;" + f"{int(n or 0):,}".replace(",", ".")


def norm_phone(s: str) -> str:
    d = re.sub(r"\D", "", s or "")
    if len(d) == 9 and d.startswith("9"):
        d = "56" + d
    return d


def new_id() -> str:
    return uuid.uuid4().hex[:8]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def fmt_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%d/%m/%Y")
    except Exception:
        return iso or ""


def flag(country: str) -> str:
    return FLAGS.get(country, "🌐")


def size_label(p) -> str:
    s = (p.get("size") or "").strip()
    if not s:
        return ""
    return f"Talla {s}" if p.get("category") in SIZED_CATEGORIES else s


def hash_pw(pw: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(8)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 120_000).hex()
    return f"{salt}${h}"


def check_pw(pw: str, stored: str | None) -> bool:
    if not stored or "$" not in stored:
        return False
    salt = stored.split("$", 1)[0]
    return secrets.compare_digest(hash_pw(pw, salt), stored)


# ════════════════════════════════════════════════════════════════════
#  IMÁGENES
# ════════════════════════════════════════════════════════════════════
PALETTES = [("#141B2D", "#2A3556"), ("#5B1626", "#1A0A10"), ("#E9ECF2", "#B8BFCE"),
            ("#2B1F3D", "#0F0B18"), ("#1D3A4A", "#0B1820"), ("#8C6A3A", "#2E220F")]


def demo_svg(emoji: str, idx: int) -> str:
    a, b = PALETTES[idx % len(PALETTES)]
    rot = (-10, 0, 9, -4, 6, -7)[idx % 6]
    scale = (1, 0.82, 1.12, 0.92, 1.05, 0.88)[idx % 6]
    light = idx % len(PALETTES) == 2
    fg = "#121726" if light else "#ffffff"
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 1000">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{a}"/>'
        f'<stop offset="1" stop-color="{b}"/></linearGradient>'
        '<radialGradient id="r" cx=".5" cy=".44" r=".46"><stop offset="0" stop-color="#fff" stop-opacity=".22"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>'
        '<rect width="800" height="1000" fill="url(#g)"/><circle cx="400" cy="450" r="340" fill="url(#r)"/>'
        f'<g transform="translate(400 470) rotate({rot}) scale({scale})">'
        f'<text x="0" y="90" font-size="270" text-anchor="middle">{emoji}</text></g>'
        f'<text x="400" y="910" font-size="26" letter-spacing="6" text-anchor="middle" fill="{fg}" '
        'fill-opacity=".5" font-family="Georgia,serif">foto de muestra</text></svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


@st.cache_data(show_spinner=False, max_entries=500)
def _file_uri(path: str, mtime: float) -> str:
    p = Path(path)
    mime = {"png": "image/png", "webp": "image/webp", "gif": "image/gif"}.get(
        p.suffix.lower().lstrip("."), "image/jpeg")
    return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()


def img_src(entry: str) -> str:
    if not entry:
        return demo_svg("🖤", 0)
    if entry.startswith("demo:"):
        parts = entry.split(":")
        return demo_svg(parts[1], int(parts[2]) if len(parts) > 2 else 0)
    p = DATA_DIR / entry
    if p.exists():
        return _file_uri(str(p), p.stat().st_mtime)
    return demo_svg("🖤", 0)


def save_upload(uploaded, max_side: int = 1400) -> str:
    img = Image.open(uploaded)
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    else:
        img = img.convert("RGB")
    img.thumbnail((max_side, max_side))
    name = f"{uuid.uuid4().hex}.jpg"
    img.save(IMG_DIR / name, "JPEG", quality=86, optimize=True)
    return f"images/{name}"


def delete_image(entry: str):
    if entry and not entry.startswith("demo:"):
        try:
            (DATA_DIR / entry).unlink(missing_ok=True)
        except Exception:
            pass


def avatar_svg(color: str) -> str:
    c = color.lstrip("#")
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    fg = "#1b1f2a" if (r * 299 + g * 587 + b * 114) / 1000 > 170 else "#ffffff"
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
        '<defs><clipPath id="c"><circle cx="50" cy="50" r="50"/></clipPath></defs>'
        f'<g clip-path="url(#c)"><rect width="100" height="100" fill="{color}"/>'
        f'<circle cx="50" cy="39" r="17" fill="{fg}" fill-opacity=".92"/>'
        f'<path d="M14 100c0-22 16-36 36-36s36 14 36 36z" fill="{fg}" fill-opacity=".92"/></g></svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def user_avatar(u) -> str:
    if u.get("photo"):
        return img_src(u["photo"])
    return avatar_svg(u.get("avatar_color") or AVATAR_COLORS["Rojo"])


def owner_photo(db) -> str:
    sp = db["settings"].get("owner_photo")
    if sp and (DATA_DIR / sp).exists():
        return img_src(sp)
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = ASSETS_DIR / f"benjamin.{ext}"
        if p.exists():
            return _file_uri(str(p), p.stat().st_mtime)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 520">'
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5B1626"/>'
        '<stop offset="1" stop-color="#141B2D"/></linearGradient></defs>'
        '<rect width="400" height="520" fill="url(#g)"/>'
        '<text x="200" y="300" font-size="150" text-anchor="middle" fill="#fff" fill-opacity=".9" '
        'font-family="Georgia,serif" font-style="italic">BE</text></svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


# ════════════════════════════════════════════════════════════════════
#  BASE DE DATOS (JSON local)
# ════════════════════════════════════════════════════════════════════
def seed_db() -> dict:
    t = now_iso()
    prods = [
        dict(name="Polera roja", category="Ropa", price=12990, size="L", made_in="China",
             brand="Rissos Basics", condition="Nuevo", status="Disponible",
             short="Algodón peinado, corte regular y color que no se lava.",
             description="Polera de algodón peinado de gramaje medio, suave al tacto y con buena caída. "
                         "El rojo es intenso y se mantiene lavado tras lavado.",
             details=["100% algodón", "Corte regular fit", "Cuello redondo reforzado", "Lavar en frío"],
             images=["demo:👕:1", "demo:👕:0", "demo:👕:2"]),
        dict(name="Pantalón Jean negro", category="Ropa", price=24990, size="42", made_in="Bangladesh",
             brand="Denim Co.", condition="Usado, como nuevo", status="Disponible",
             short="Jean negro de corte recto, usado dos veces.",
             description="Jean negro de mezclilla firme con un toque de elasticidad. Corte recto que "
                         "funciona con zapatillas o botines. Sin desgaste visible.",
             details=["98% algodón, 2% elastano", "Corte recto", "5 bolsillos", "Tiro medio"],
             images=["demo:👖:0", "demo:👖:3", "demo:👖:4"]),
        dict(name="Dior Sauvage Parfum 150ml", category="Perfumes", price=129990, size="",
             made_in="Francia", brand="Dior", condition="Nuevo", status="Disponible",
             short="Perfume original, sellado, 150 ml.",
             description="Dior Sauvage en su versión Parfum: más profunda y amaderada que el EDT, con "
                         "notas de bergamota, sándalo y vainilla. Caja sellada.",
             details=["Contenido: 150 ml", "Concentración: Parfum", "Caja sellada", "Original"],
             images=["demo:🧴:3", "demo:🧴:5", "demo:🧴:2"]),
        dict(name="Gorra F1", category="Accesorios", price=19990, size="Ajustable", made_in="Vietnam",
             brand="Formula 1", condition="Nuevo", status="Agotado",
             short="Gorra de seis paneles con bordado frontal.",
             description="Gorra de seis paneles con logo bordado y cierre ajustable trasero. "
                         "Visera curva y forro interior transpirable.",
             details=["Talla única ajustable", "Logo bordado", "Cierre de velcro", "Visera curva"],
             images=["demo:🧢:1", "demo:🧢:0"]),
        dict(name="Figura de Freezer", category="Figuras", price=34990, size="", made_in="China",
             brand="Banpresto", condition="Nuevo", status="Disponible",
             short="Figura de colección de Dragon Ball, en su caja.",
             description="Figura de Freezer en su forma final, con detalles pintados a mano y base "
                         "incluida. Ideal para colección; caja en buen estado.",
             details=["Altura aprox.: 18 cm", "Material: PVC", "Base incluida", "Caja original"],
             images=["demo:👽:3", "demo:👽:4", "demo:👽:1"]),
        dict(name="Monitor 144Hz", category="Tecnología", price=159990, size="", made_in="Taiwán",
             brand="Genérico 24\"", condition="Usado, como nuevo", status="Disponible",
             short="24 pulgadas, Full HD, 144 Hz y 1 ms.",
             description="Monitor gamer de 24 pulgadas con panel de 144 Hz, ideal para juegos "
                         "competitivos. Sin píxeles muertos, con cables y caja.",
             details=["24\" Full HD 1920×1080", "144 Hz, 1 ms", "HDMI y DisplayPort", "Incluye cables"],
             images=["demo:🖥️:4", "demo:🖥️:0", "demo:🖥️:2"]),
    ]
    for p in prods:
        p["id"] = new_id()
        p["created"] = t
    return {"products": prods, "users": [], "purchases": [], "settings": {}}


def load_db() -> dict:
    if not DB_PATH.exists():
        save_db(seed_db())
    with open(DB_PATH, encoding="utf-8") as f:
        db = json.load(f)
    for k, v in (("products", []), ("users", []), ("purchases", []), ("settings", {})):
        db.setdefault(k, v)
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
    ps = [p for p in db["purchases"] if p["user_id"] == uid]
    return sorted(ps, key=lambda x: x.get("date", ""), reverse=True)


def user_stats(db, uid):
    ps = user_purchases(db, uid)
    return len(ps), sum(int(p.get("qty", 1)) for p in ps), sum(int(p.get("total", 0)) for p in ps)


def check_admin(db, pw: str) -> bool:
    stored = db["settings"].get("admin_pw")
    if stored:
        return check_pw(pw, stored)
    try:
        expected = st.secrets.get("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)
    except Exception:
        expected = DEFAULT_ADMIN_PASSWORD
    return secrets.compare_digest(pw, expected)


# ════════════════════════════════════════════════════════════════════
#  LINKS (correo, WhatsApp, producto)
# ════════════════════════════════════════════════════════════════════
def app_base_url(db) -> str:
    s = (db["settings"].get("base_url") or "").strip()
    if s:
        return s.rstrip("/")
    try:
        u = getattr(st.context, "url", None)
        if u:
            return u.split("?")[0].rstrip("/")
    except Exception:
        pass
    try:
        host = st.context.headers.get("host")
        if host:
            scheme = "http" if host.startswith(("localhost", "127.", "0.0.0.0")) else "https"
            return f"{scheme}://{host}"
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


def consult_message(db, p):
    subject = f"Consulta de Stock – {p['name']}" + (f" ({size_label(p)})" if p.get("size") else "")
    lines = [
        "Hola Benjamín 👋",
        "",
        "Quiero consultar el stock de este producto:",
        "",
        f"• Producto: {p['name']}",
    ]
    if p.get("size"):
        lines.append(f"• {size_label(p) if p.get('category') in SIZED_CATEGORIES else 'Medida: ' + p['size']}")
    lines += [f"• Precio: {money(p['price'])}", f"• Link: {product_link(db, p['id'])}", ""]
    u = current_user(db)
    if u:
        lines += [f"Mi nombre: {u['name']}", f"Mi teléfono: {u.get('phone_display') or u.get('phone')}", ""]
    lines.append("¡Gracias!")
    return subject, "\n".join(lines)


# ════════════════════════════════════════════════════════════════════
#  ESTADO DE SESIÓN Y NAVEGACIÓN
# ════════════════════════════════════════════════════════════════════
ss = st.session_state
ss.setdefault("theme", "dark")
ss.setdefault("role", None)        # None | "user" | "admin"
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


def flash(msg: str, icon: str = "✨"):
    ss["_flash"] = (msg, icon)


def logout():
    ss.role = None
    ss.user_id = None
    flash("Cerraste sesión", "👋")
    go("home")


# ════════════════════════════════════════════════════════════════════
#  ESTILOS
# ════════════════════════════════════════════════════════════════════
CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,opsz,wght@0,6..96,400..800;1,6..96,400..800&family=Manrope:wght@300;400;500;600;700;800&display=swap');
:root{--ease:cubic-bezier(.22,1,.36,1);--serif:'Bodoni Moda',Didot,'Times New Roman',serif;--sans:'Manrope',system-ui,-apple-system,'Segoe UI',sans-serif;}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--bg)!important;color:var(--text)!important;font-family:var(--sans);}
.stApp{transition:background-color .7s var(--ease),color .7s var(--ease);}
.stApp *{transition-property:background-color,border-color,color,box-shadow,transform,opacity,filter;transition-duration:.45s;transition-timing-function:var(--ease);}
[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer,[data-testid="stStatusWidget"],[data-testid="stSidebarCollapsedControl"],[data-testid="stAppDeployButton"]{display:none!important;}
.block-container,[data-testid="stMainBlockContainer"]{padding-top:.5rem!important;padding-bottom:2rem!important;max-width:1240px!important;}
.stApp h1,.stApp h2,.stApp h3,.stApp h4{font-family:var(--serif)!important;color:var(--text)!important;}
.stApp [data-testid="stMarkdownContainer"] p,.stApp [data-testid="stMarkdownContainer"] li{color:var(--text);}
[data-testid="stWidgetLabel"] p,[data-testid="stWidgetLabel"] label{color:var(--muted)!important;font-size:.84rem!important;font-weight:600!important;}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] p{color:var(--muted)!important;}
::selection{background:var(--accent);color:var(--accent-ink);}
::-webkit-scrollbar{width:10px;height:10px}::-webkit-scrollbar-thumb{background:var(--surface2);border-radius:10px;border:2px solid var(--bg)}
:focus-visible{outline:2px solid var(--accent)!important;outline-offset:2px;}

/* Inputs */
.stApp input,.stApp textarea{color:var(--text)!important;-webkit-text-fill-color:var(--text)!important;caret-color:var(--accent);}
.stApp input::placeholder,.stApp textarea::placeholder{color:var(--muted)!important;-webkit-text-fill-color:var(--muted)!important;opacity:.8}
[data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="base-input"],[data-baseweb="select"]>div,[data-testid$="RootElement"]{background:var(--surface2)!important;border-color:var(--border)!important;border-radius:14px!important;}
[data-testid$="RootElement"]:focus-within,[data-baseweb="input"]:focus-within,[data-baseweb="textarea"]:focus-within,[data-baseweb="select"]>div:focus-within{border-color:var(--accent)!important;box-shadow:0 0 0 3px var(--glow)!important;}
[data-baseweb="select"] *{color:var(--text)!important;}
[data-baseweb="select"] svg{fill:var(--muted)!important}
[data-baseweb="popover"] [data-baseweb="menu"],[data-baseweb="popover"] ul{background:var(--surface)!important;border:1px solid var(--border);border-radius:14px;}
[data-baseweb="popover"] li{color:var(--text)!important;background:transparent!important}
[data-baseweb="popover"] li:hover,[data-baseweb="popover"] li[aria-selected="true"]{background:var(--chip)!important}
[data-testid="stNumberInput"] button{background:var(--surface2)!important;color:var(--text)!important;border-color:var(--border)!important}
[data-testid="stRadio"] label p,[data-testid="stCheckbox"] label p,[data-testid="stToggle"] label p{color:var(--text)!important;font-weight:500!important;}
[data-testid="stFileUploaderDropzone"]{background:var(--surface2)!important;border:1px dashed var(--accent-soft)!important;border-radius:16px!important;}
[data-testid="stFileUploaderDropzone"] *{color:var(--muted)!important}
[data-testid="stFileUploaderFile"] *{color:var(--text)!important}
[data-testid="stDateInput"] input{background:transparent!important}
[data-baseweb="calendar"]{background:var(--surface)!important}
[data-baseweb="calendar"] *{color:var(--text)!important}

/* Botones */
.stButton button,.stFormSubmitButton button,.stDownloadButton button,[data-testid="stPopover"] button,[data-testid="stPopoverButton"]{
 background:var(--surface)!important;color:var(--text)!important;border:1px solid var(--border)!important;border-radius:999px!important;
 font-weight:650!important;min-height:2.6rem;transition:all .45s var(--ease)!important;}
.stButton button p,.stFormSubmitButton button p,.stDownloadButton button p,[data-testid="stPopover"] button p{color:inherit!important;font-weight:650!important}
.stButton button:hover,.stFormSubmitButton button:hover,.stDownloadButton button:hover,[data-testid="stPopover"] button:hover,[data-testid="stPopoverButton"]:hover{
 border-color:var(--accent)!important;color:var(--accent)!important;transform:translateY(-2px);box-shadow:0 14px 30px -16px var(--glow)!important;}
.stButton button:active{transform:translateY(0) scale(.97)}
.stApp button[kind="primary"],.stApp button[kind="primaryFormSubmit"],.stApp [data-testid^="stBaseButton-primary"]{
 background:var(--accent)!important;color:var(--accent-ink)!important;border-color:transparent!important;}
.stApp button[kind="primary"]:hover,.stApp button[kind="primaryFormSubmit"]:hover,.stApp [data-testid^="stBaseButton-primary"]:hover{color:var(--accent-ink)!important;filter:brightness(1.08);box-shadow:0 18px 36px -14px var(--glow)!important;}
[data-testid="stPopoverBody"],div[data-baseweb="popover"]>div{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:20px!important;box-shadow:0 30px 60px -30px var(--shadow)!important;}
[data-testid="stButtonGroup"] button[role="radio"]{border-radius:999px!important;background:var(--surface)!important;border:1px solid var(--border)!important;color:var(--text)!important;padding:.35rem 1rem!important}
[data-testid="stButtonGroup"] button p{color:inherit!important}
[data-testid="stButtonGroup"] button[aria-checked="true"],[data-testid="stButtonGroup"] button[kind="pillsActive"]{background:var(--text)!important;color:var(--bg)!important;border-color:var(--text)!important}

/* Tabs, expander, contenedores */
.stTabs [data-baseweb="tab-list"]{gap:.4rem;border-bottom:1px solid var(--border);background:transparent}
.stTabs [data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;padding:.6rem .9rem}
.stTabs [data-baseweb="tab"] p{color:inherit!important;font-weight:650!important}
.stTabs [aria-selected="true"]{color:var(--text)!important}
.stTabs [data-baseweb="tab-highlight"]{background:var(--accent)!important;height:2px}
.stTabs [data-baseweb="tab-border"]{display:none}
[data-testid="stExpander"] details{background:var(--surface)!important;border:1px solid var(--border)!important;border-radius:18px!important;}
[data-testid="stExpander"] summary,[data-testid="stExpander"] summary p{color:var(--text)!important;font-weight:650}
[data-testid="stExpander"] summary:hover p{color:var(--accent)!important}
[data-testid="stVerticalBlockBorderWrapper"]{border-color:var(--border)!important;border-radius:20px!important}
[data-testid="stForm"]{border:1px solid var(--border)!important;border-radius:20px!important;background:var(--surface)}
[data-testid="stMetric"]{background:var(--surface);border:1px solid var(--border);border-radius:18px;padding:16px 18px}
[data-testid="stMetricValue"]{color:var(--text)!important;font-family:var(--serif);}
[data-testid="stMetricLabel"] p{color:var(--muted)!important}
[data-testid="stCode"] pre,.stCode pre{background:var(--surface2)!important;border-radius:14px!important;border:1px solid var(--border)}
[data-testid="stCode"] code{color:var(--text)!important;white-space:pre-wrap!important;word-break:break-all}
[data-testid="stAlert"]{border-radius:16px!important}
hr{border-color:var(--border)!important}
.st-key-scrolltop{position:absolute!important;height:0!important;overflow:hidden;visibility:hidden;pointer-events:none}

/* Navbar */
.st-key-navbar{position:sticky;top:0;z-index:999;background:var(--nav);backdrop-filter:blur(18px) saturate(1.5);-webkit-backdrop-filter:blur(18px) saturate(1.5);
 border:1px solid var(--border);border-radius:999px;padding:.45rem .55rem .45rem 1rem;margin:.4rem 0 1.4rem;}
.st-key-navbar [data-testid="stHorizontalBlock"]{flex-wrap:nowrap!important;gap:.5rem!important}
.st-key-navbar [data-testid="stColumn"]{min-width:0!important}
.ra-brand{display:flex;align-items:center;gap:.7rem;white-space:nowrap}
.ra-mono{width:40px;height:40px;border-radius:50%;display:grid;place-items:center;background:var(--text);color:var(--bg);font-family:var(--serif);font-style:italic;font-weight:700;font-size:1.05rem;flex-shrink:0}
.ra-brand-name{font-family:var(--serif);font-size:1.32rem;font-weight:600;line-height:1;color:var(--text)}
.ra-brand-name i{font-weight:400;color:var(--accent)}
.ra-brand-sub{font-size:.72rem;color:var(--muted);margin-top:2px}

/* Hero */
.ra-hero{position:relative;overflow:hidden;border-radius:36px;border:1px solid var(--border);background:var(--surface);padding:clamp(26px,5vw,60px);margin:0 0 3rem;}
.ra-blob{position:absolute;border-radius:50%;filter:blur(70px);pointer-events:none;animation:float 16s ease-in-out infinite}
.ra-blob.b1{width:460px;height:460px;background:var(--blob1);top:-170px;right:-90px}
.ra-blob.b2{width:400px;height:400px;background:var(--blob2);bottom:-190px;left:-120px;animation-delay:-7s}
.ra-hero-inner{position:relative;display:flex;gap:clamp(26px,5vw,64px);align-items:center;flex-wrap:wrap}
.ra-arch{position:relative;width:clamp(170px,22vw,250px);aspect-ratio:3/4;flex-shrink:0;animation:archIn 1.3s var(--ease) both}
.ra-arch::before{content:"";position:absolute;inset:-10px;border-radius:999px 999px 30px 30px;border:1px solid var(--accent-soft);}
.ra-arch img{position:relative;width:100%;height:100%;object-fit:cover;border-radius:999px 999px 24px 24px;box-shadow:0 40px 70px -35px var(--shadow)}
.ra-hero-text{flex:1;min-width:260px}
.ra-hello{color:var(--accent);font-weight:700;font-size:.95rem;animation:rise .9s .25s var(--ease) both}
.ra-hero-name{font-family:var(--serif);font-style:italic;font-weight:500;font-size:clamp(2.7rem,6.4vw,5.2rem);line-height:.95;letter-spacing:-.02em;color:var(--text);margin:.3rem 0 .9rem;animation:rise 1s .35s var(--ease) both}
.ra-hero-tag{color:var(--muted);font-size:1.08rem;max-width:46ch;line-height:1.6;margin-bottom:1.6rem;animation:rise 1s .45s var(--ease) both}
.ra-contacts{display:flex;flex-wrap:wrap;gap:10px;animation:rise 1s .55s var(--ease) both}
.ra-cbtn{--c:var(--accent);display:inline-flex;align-items:center;gap:12px;padding:8px 20px 8px 8px;border-radius:999px;background:var(--chip);border:1px solid var(--border);color:var(--text)!important;text-decoration:none!important;transition:all .5s var(--ease)!important}
.ra-cbtn .ic{width:40px;height:40px;border-radius:50%;display:grid;place-items:center;background:var(--surface);color:var(--text);transition:all .5s var(--ease)}
.ra-cbtn svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.ra-cbtn .lb{display:flex;flex-direction:column;line-height:1.2}
.ra-cbtn .lb b{font-size:.9rem;font-weight:700;color:var(--text)}
.ra-cbtn .lb small{font-size:.76rem;color:var(--muted)}
.ra-cbtn:hover{transform:translateY(-3px);border-color:var(--c);box-shadow:0 20px 40px -20px var(--c)}
.ra-cbtn:hover .ic{background:var(--c);color:#fff;transform:rotate(-8deg) scale(1.06)}
.ra-cbtn.wa{--c:#25D366}.ra-cbtn.ig{--c:#E1306C}.ra-cbtn.ml{--c:var(--accent)}
.ra-stats{display:flex;gap:1.6rem;margin-top:1.6rem;color:var(--muted);font-size:.88rem;animation:rise 1s .65s var(--ease) both}
.ra-stats b{color:var(--text);font-family:var(--serif);font-size:1.4rem;font-weight:600;margin-right:.3rem}

/* Secciones */
.ra-sec{margin:.4rem 0 1rem}
.ra-sec .t{font-family:var(--serif);font-size:clamp(2rem,4vw,3rem);font-weight:500;line-height:1;color:var(--text)}
.ra-sec .t i{color:var(--accent)}
.ra-sec .s{color:var(--muted);margin-top:.4rem}

/* Tarjetas */
[class*="st-key-card_"]{background:var(--surface);border:1px solid var(--border);border-radius:26px;padding:12px 12px 14px;gap:.55rem!important;animation:rise .9s var(--ease) both;}
[class*="st-key-card_"]:hover{transform:translateY(-6px);border-color:var(--accent-soft);box-shadow:0 34px 60px -34px var(--shadow)}
[class*="st-key-card_"]:hover .ra-img img{transform:scale(1.05)}
.ra-img{position:relative;aspect-ratio:4/5;border-radius:18px;overflow:hidden;background:var(--surface2)}
.ra-img.big{border-radius:28px}
.ra-img img{width:100%;height:100%;object-fit:cover;display:block;transition:transform 1.2s var(--ease),filter .6s!important}
.ra-img img.r{animation:inR .65s var(--ease)}
.ra-img img.l{animation:inL .65s var(--ease)}
.ra-img.sold img{filter:grayscale(.9) brightness(.75)}
.ra-tl{position:absolute;top:12px;left:12px;display:flex;gap:6px;flex-wrap:wrap}
.ra-badge{backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);background:rgba(13,18,32,.55);color:#fff;font-size:.72rem;padding:6px 11px;border-radius:999px;font-weight:700;display:inline-flex;align-items:center;gap:6px}
.ra-badge.ok::before{content:"";width:7px;height:7px;border-radius:50%;background:#3ddc84;box-shadow:0 0 0 3px rgba(61,220,132,.25);animation:pulse 2.2s infinite}
.ra-badge.out{background:rgba(158,34,56,.9)}
.ra-dots{position:absolute;bottom:12px;left:50%;transform:translateX(-50%);display:flex;gap:6px}
.ra-dots i{width:6px;height:6px;border-radius:99px;background:rgba(255,255,255,.5);transition:all .5s var(--ease)}
.ra-dots i.on{width:22px;background:#fff}
.ra-info{padding:2px 4px}
.ra-cat{font-size:.78rem;color:var(--muted);font-weight:600}
.ra-name{font-family:var(--serif);font-size:1.45rem;font-weight:500;line-height:1.12;color:var(--text);margin:.15rem 0 .3rem}
.ra-short{color:var(--muted);font-size:.86rem;line-height:1.45;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:2.5em}
.ra-chips{display:flex;flex-wrap:wrap;gap:6px;margin:.6rem 0 .5rem}
.chip{font-size:.76rem;padding:5px 11px;border-radius:999px;background:var(--chip);border:1px solid var(--border);color:var(--text);font-weight:600;white-space:nowrap}
.chip.size{background:var(--text);color:var(--bg);border-color:var(--text);font-weight:800}
.ra-price{font-weight:800;font-size:1.18rem;color:var(--text);letter-spacing:.01em}
.ra-count{text-align:center;color:var(--muted);font-size:.8rem;font-weight:600}
[class*="prev_"] button,[class*="next_"] button{width:42px!important;height:42px!important;min-height:42px!important;padding:0!important;border-radius:50%!important;font-size:1.3rem!important}
[class*="next_"] [data-testid="stButton"]{display:flex;justify-content:flex-end;width:100%}
[class*="st-key-view_"] button{border-color:var(--accent-soft)!important}

/* Detalle */
.ra-thumbs{display:flex;gap:8px;margin-top:10px;overflow-x:auto;padding-bottom:4px}
.ra-thumbs img{width:62px;height:76px;object-fit:cover;border-radius:12px;opacity:.45;border:2px solid transparent;flex-shrink:0}
.ra-thumbs img.on{opacity:1;border-color:var(--accent)}
.ra-d{animation:rise .9s .1s var(--ease) both}
.ra-d-cat{color:var(--accent);font-weight:700;font-size:.9rem}
.ra-d-name{font-family:var(--serif);font-weight:500;font-size:clamp(2.3rem,4.6vw,3.6rem);line-height:1;letter-spacing:-.01em;color:var(--text);margin:.35rem 0 .8rem}
.ra-d-price{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin-bottom:.9rem}
.ra-d-price b{font-size:1.9rem;font-weight:800;color:var(--text)}
.ra-pill{font-size:.8rem;font-weight:700;padding:6px 12px;border-radius:999px;display:inline-flex;align-items:center;gap:7px}
.ra-pill.ok{background:rgba(61,220,132,.13);color:#2fbf72}
.ra-pill.ok::before{content:"";width:7px;height:7px;border-radius:50%;background:#3ddc84;animation:pulse 2.2s infinite}
.ra-pill.out{background:var(--chip);color:var(--accent);border:1px solid var(--accent-soft)}
.ra-d-short{color:var(--muted);font-size:1.02rem;line-height:1.6;margin:.4rem 0 1.3rem;max-width:52ch}
.ra-cta{position:relative;overflow:hidden;display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:16px 20px;border-radius:999px;background:var(--accent);color:var(--accent-ink)!important;font-weight:800;font-size:1rem;text-decoration:none!important;transition:all .5s var(--ease)!important;box-shadow:0 20px 40px -22px var(--glow)}
.ra-cta::after{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 30%,rgba(255,255,255,.35) 50%,transparent 70%);transform:translateX(-120%);transition:transform .9s var(--ease)}
.ra-cta:hover{transform:translateY(-3px);box-shadow:0 26px 50px -20px var(--glow)}
.ra-cta:hover::after{transform:translateX(120%)}
.ra-cta svg{width:19px;height:19px;stroke:currentColor;fill:none;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.ra-cta-row{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px}
.ra-cta.ghost{background:transparent;color:var(--text)!important;border:1px solid var(--border);box-shadow:none;font-weight:700;font-size:.92rem;padding:13px 16px}
.ra-cta.ghost:hover{border-color:var(--accent);color:var(--accent)!important}
.ra-specs{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--border);border:1px solid var(--border);border-radius:20px;overflow:hidden;margin:1.5rem 0}
.ra-specs div{background:var(--surface);padding:14px 16px}
.ra-specs small{display:block;color:var(--muted);font-size:.76rem;font-weight:600;margin-bottom:3px}
.ra-specs span{color:var(--text);font-weight:700}
.ra-desc h4{font-family:var(--serif)!important;font-size:1.45rem!important;font-weight:500!important;margin:.2rem 0 .5rem!important;color:var(--text)!important}
.ra-desc p{color:var(--muted)!important;line-height:1.75;max-width:62ch}
.ra-desc ul{list-style:none;padding:0;margin:.6rem 0 0}
.ra-desc li{padding:.55rem 0;border-bottom:1px solid var(--border);color:var(--text)!important;display:flex;gap:.7rem}
.ra-desc li::before{content:"";width:6px;height:6px;margin-top:.55rem;border-radius:50%;background:var(--accent);flex-shrink:0}

/* Listas, perfiles, tablas */
.ra-row{display:flex;align-items:center;gap:14px;padding:12px;border:1px solid var(--border);border-radius:18px;background:var(--surface)}
.ra-row img{width:54px;height:64px;object-fit:cover;border-radius:12px;flex-shrink:0}
.ra-row .m{flex:1;min-width:0}
.ra-row .m b{display:block;color:var(--text);font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.ra-row .m small{color:var(--muted)}
.ra-row .v{font-weight:800;color:var(--text);white-space:nowrap}
.ra-prof{display:flex;gap:22px;align-items:center;flex-wrap:wrap;background:var(--surface);border:1px solid var(--border);border-radius:28px;padding:22px 24px;margin-bottom:1.2rem;animation:rise .8s var(--ease) both}
.ra-prof img{width:96px;height:96px;border-radius:50%;object-fit:cover;box-shadow:0 0 0 4px var(--surface),0 0 0 5px var(--accent-soft)}
.ra-prof .n{font-family:var(--serif);font-size:2rem;font-weight:500;color:var(--text);line-height:1.05}
.ra-prof .d{color:var(--muted);font-size:.9rem;margin-top:.35rem;display:flex;gap:.9rem;flex-wrap:wrap}
.ra-prof .k{display:flex;gap:1.6rem;margin-left:auto}
.ra-prof .k div{text-align:right}.ra-prof .k b{display:block;font-family:var(--serif);font-size:1.6rem;color:var(--text);font-weight:600}
.ra-prof .k small{color:var(--muted)}
.ra-table-wrap{overflow-x:auto;border:1px solid var(--border);border-radius:20px;background:var(--surface)}
.ra-table{width:100%;border-collapse:collapse;font-size:.9rem}
.ra-table th{text-align:left;color:var(--muted);font-weight:700;padding:12px 14px;border-bottom:1px solid var(--border);white-space:nowrap}
.ra-table td{padding:11px 14px;border-bottom:1px solid var(--border);color:var(--text);white-space:nowrap}
.ra-table tr:last-child td{border-bottom:none}
.ra-table tr:hover td{background:var(--chip)}
.ra-table img{width:30px;height:30px;border-radius:50%;vertical-align:middle;margin-right:8px;object-fit:cover}
.ra-podium{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:.4rem 0 1rem}
.ra-pod{background:var(--surface);border:1px solid var(--border);border-radius:24px;padding:18px;text-align:center;animation:rise .8s var(--ease) both}
.ra-pod.first{border-color:var(--accent-soft);box-shadow:0 24px 50px -30px var(--glow)}
.ra-pod img{width:64px;height:64px;border-radius:50%;object-fit:cover;margin-bottom:8px}
.ra-pod .p{font-family:var(--serif);font-style:italic;color:var(--accent);font-size:1.1rem}
.ra-pod b{display:block;color:var(--text);font-size:1.02rem}
.ra-pod small{color:var(--muted)}
.ra-mini{display:flex;align-items:center;gap:10px;padding:4px 2px 10px}
.ra-mini img{width:42px;height:42px;border-radius:50%;object-fit:cover}
.ra-mini b{color:var(--text);display:block}.ra-mini small{color:var(--muted)}
.ra-auth-h{font-family:var(--serif);font-size:2.4rem;font-weight:500;color:var(--text);line-height:1;margin:.4rem 0 .3rem;text-align:center}
.ra-auth-s{color:var(--muted);text-align:center;margin-bottom:1rem}
.st-key-authbox{background:var(--surface);border:1px solid var(--border);border-radius:30px;padding:26px 26px 22px;animation:rise .8s var(--ease) both}
.ra-avprev{display:flex;align-items:center;gap:12px;margin:.2rem 0 .6rem}
.ra-avprev img{width:56px;height:56px;border-radius:50%;box-shadow:0 0 0 1px var(--border)}
.ra-avprev span{color:var(--muted);font-size:.86rem}
.ra-empty{text-align:center;padding:3.5rem 1rem;color:var(--muted);border:1px dashed var(--border);border-radius:26px}
.ra-empty b{display:block;font-family:var(--serif);font-size:1.6rem;color:var(--text);font-weight:500;margin-bottom:.3rem}

/* Footer */
.ra-foot{margin-top:4rem;padding:2rem 0 1rem;border-top:1px solid var(--border);display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;color:var(--muted);font-size:.88rem}
.ra-foot a{color:var(--text)!important;text-decoration:none!important;margin-left:1.1rem;font-weight:600}
.ra-foot a:hover{color:var(--accent)!important}
.ra-foot .b{font-family:var(--serif);font-size:1.2rem;color:var(--text)}

@keyframes rise{from{opacity:0;transform:translateY(22px)}to{opacity:1;transform:none}}
@keyframes archIn{from{opacity:0;transform:translateY(30px) scale(.96);clip-path:inset(100% 0 0 0 round 999px 999px 24px 24px)}to{opacity:1;transform:none;clip-path:inset(0 0 0 0 round 999px 999px 24px 24px)}}
@keyframes inR{from{opacity:0;transform:translateX(36px) scale(1.03)}to{opacity:1;transform:none}}
@keyframes inL{from{opacity:0;transform:translateX(-36px) scale(1.03)}to{opacity:1;transform:none}}
@keyframes float{0%,100%{transform:translate(0,0)}50%{transform:translate(30px,24px)}}
@keyframes pulse{0%,100%{box-shadow:0 0 0 0 rgba(61,220,132,.45)}60%{box-shadow:0 0 0 7px rgba(61,220,132,0)}}

@media (max-width:640px){
 .ra-brand-sub{display:none}.ra-brand-name{font-size:1.05rem}.ra-mono{width:34px;height:34px;font-size:.9rem}
 .st-key-navbar{padding-left:.6rem;border-radius:26px}
 .st-key-navbar [data-testid="stColumn"]:first-child{flex:1 1 auto!important;width:auto!important}
 .st-key-navbar [data-testid="stColumn"]:not(:first-child){flex:0 0 auto!important;width:auto!important}
 .st-key-navbar [data-testid="stColumn"]:not(:first-child) button{padding:0 .85rem!important;min-width:44px}
 .ra-hero{border-radius:26px}.ra-hero-inner{justify-content:center;text-align:center}
 .ra-contacts,.ra-stats{justify-content:center}
 .ra-cta-row{grid-template-columns:1fr}
 .ra-prof .k{margin-left:0}
 .ra-podium{grid-template-columns:1fr}
 .ra-foot a{margin:0 1rem 0 0}
}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
"""


def inject_css():
    v = THEMES[ss.theme]
    root = ":root{" + "".join(f"--{k}:{val};" for k, val in v.items()) + "}"
    html(f"<style>{root}{CSS}</style>")


ICONS = {
    "wa": '<svg viewBox="0 0 24 24"><path d="M7.9 20A9 9 0 1 0 4 16.1L2 22Z"/><path d="M9 10.5c.5 1.6 2 3.1 3.6 3.6l1.2-1.2 2 .9c-.2 1.2-1.1 1.9-2.3 1.9-3.2-.3-6-3.1-6.3-6.3 0-1.2.7-2.1 1.9-2.3l.9 2z"/></svg>',
    "ig": '<svg viewBox="0 0 24 24"><rect width="20" height="20" x="2" y="2" rx="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/></svg>',
    "ml": '<svg viewBox="0 0 24 24"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>',
}


# ════════════════════════════════════════════════════════════════════
#  COMPONENTES
# ════════════════════════════════════════════════════════════════════
def scroll_top():
    code = ("<script>(function(){const d=window.parent.document;"
            "['[data-testid=\"stMain\"]','section.main','[data-testid=\"stAppViewContainer\"]']"
            ".forEach(s=>{const e=d.querySelector(s);if(e&&e.scrollTo)e.scrollTo({top:0,behavior:'smooth'})});"
            f"window.parent.scrollTo({{top:0,behavior:'smooth'}});}})();/*{uuid.uuid4().hex}*/</script>")
    with st.container(key="scrolltop"):
        if hasattr(st, "iframe"):
            st.iframe(code, height=1)
        else:
            components.html(code, height=0)


def render_navbar(db, view):
    with st.container(key="navbar"):
        c_brand, c_shop, c_theme, c_acc = st.columns([5, 1.25, 0.62, 1.7], vertical_alignment="center")
        with c_brand:
            html('<div class="ra-brand"><div class="ra-mono">RA</div><div>'
                 '<div class="ra-brand-name">Rissos <i>Anghell</i></div>'
                 '<div class="ra-brand-sub">Store de Benjamín Espinoza</div></div></div>')
        with c_shop:
            if view != "home" and st.button("Tienda", key="nav_shop", use_container_width=True):
                go("home")
        with c_theme:
            icon = "☀️" if ss.theme == "dark" else "🌙"
            if st.button(icon, key="nav_theme", help="Cambiar a tema claro u oscuro",
                         use_container_width=True):
                ss.theme = "light" if ss.theme == "dark" else "dark"
                st.rerun()
        with c_acc:
            u = current_user(db)
            if u:
                if st.button(f"👤 {u['name'].split()[0]}", key="nav_acc", use_container_width=True,
                             help="Ver tu perfil y tus compras"):
                    go("profile")
            elif ss.role == "admin":
                if st.button("🛡️ Panel", key="nav_acc", use_container_width=True, help="Panel de administración"):
                    go("admin")
            else:
                if st.button("👤 Ingresar", key="nav_acc", use_container_width=True,
                             help="Inicia sesión como usuario o administrador"):
                    go("login")


def render_hero(db):
    total = len(db["products"])
    avail = sum(1 for p in db["products"] if p["status"] == "Disponible")
    mail = mailto("Contacto – Rissos Anghell Store",
                  "Hola Benjamín 👋\n\nTe escribo desde Rissos Anghell Store.\n\n")
    wa = wa_link("Hola Benjamín 👋 Te escribo desde Rissos Anghell Store.")
    ig = f"https://www.instagram.com/{OWNER['instagram']}/"
    html(
        '<section class="ra-hero"><div class="ra-blob b1"></div><div class="ra-blob b2"></div>'
        '<div class="ra-hero-inner">'
        f'<div class="ra-arch"><img src="{owner_photo(db)}" alt="{esc(OWNER["name"])}"/></div>'
        '<div class="ra-hero-text">'
        '<div class="ra-hello">Hola, soy</div>'
        f'<div class="ra-hero-name">{esc(OWNER["name"])}</div>'
        '<div class="ra-hero-tag">Compra y venta de artículos, ropa y lo que vaya apareciendo. '
        'Todo revisado y con fotos reales. Escríbeme por donde te acomode.</div>'
        '<div class="ra-contacts">'
        f'<a class="ra-cbtn wa" href="{wa}" target="_blank" rel="noopener"><span class="ic">{ICONS["wa"]}</span>'
        f'<span class="lb"><b>WhatsApp</b><small>{OWNER["whatsapp_display"]}</small></span></a>'
        f'<a class="ra-cbtn ig" href="{ig}" target="_blank" rel="noopener"><span class="ic">{ICONS["ig"]}</span>'
        f'<span class="lb"><b>Instagram</b><small>@{OWNER["instagram"]}</small></span></a>'
        f'<a class="ra-cbtn ml" href="{mail}"><span class="ic">{ICONS["ml"]}</span>'
        f'<span class="lb"><b>Correo</b><small>{OWNER["email"]}</small></span></a>'
        '</div>'
        f'<div class="ra-stats"><span><b>{total}</b>artículos</span><span><b>{avail}</b>disponibles</span></div>'
        '</div></div></section>'
    )


def card_image_html(p, idx: int, d: str, big: bool = False) -> str:
    imgs = p.get("images") or ["demo:🖤:0"]
    sold = p["status"] != "Disponible"
    badge = (f'<span class="ra-badge out">{esc(p["status"])}</span>' if sold
             else '<span class="ra-badge ok">Disponible</span>')
    if p.get("made_in") and not big:
        badge += f'<span class="ra-badge">{flag(p["made_in"])} {esc(p["made_in"])}</span>'
    dots = "".join(f'<i class="{"on" if i == idx else ""}"></i>' for i in range(len(imgs))) if len(imgs) > 1 else ""
    return (f'<div class="ra-img{" big" if big else ""}{" sold" if sold else ""}">'
            f'<img class="{d}" src="{img_src(imgs[idx])}" alt="{esc(p["name"])}"/>'
            f'<div class="ra-tl">{badge}</div><div class="ra-dots">{dots}</div></div>')


def card_info_html(p) -> str:
    chips = ""
    if p.get("size"):
        chips += f'<span class="chip size">{esc(size_label(p))}</span>'
    if p.get("made_in"):
        chips += f'<span class="chip">Made in {esc(p["made_in"])}</span>'
    if p.get("condition"):
        chips += f'<span class="chip">{esc(p["condition"])}</span>'
    return (f'<div class="ra-info"><div class="ra-cat">{esc(p.get("category"))}</div>'
            f'<div class="ra-name">{esc(p["name"])}</div>'
            f'<div class="ra-short">{esc(p.get("short"))}</div>'
            f'<div class="ra-chips">{chips}</div>'
            f'<div class="ra-price">{money_html(p["price"])}</div></div>')


def _step(prefix: str, pid: str, n: int, delta: int):
    k = f"{prefix}idx_{pid}"
    ss[k] = (ss.get(k, 0) + delta) % n
    ss[f"{prefix}dir_{pid}"] = "l" if delta < 0 else "r"


@st.fragment
def product_card(p, scope: str = "h"):
    pid = p["id"]
    imgs = p.get("images") or ["demo:🖤:0"]
    n = len(imgs)
    idx = ss.get(f"idx_{pid}", 0) % n
    d = ss.get(f"dir_{pid}", "r")
    with st.container(key=f"card_{scope}_{pid}"):
        html(card_image_html(p, idx, d))
        if n > 1:
            a, b, c = st.columns([1, 2, 1], vertical_alignment="center")
            a.button("‹", key=f"prev_{scope}_{pid}", on_click=_step, args=("", pid, n, -1),
                     help="Foto anterior")
            b.markdown(f'<div class="ra-count">{idx + 1} / {n}</div>', unsafe_allow_html=True)
            c.button("›", key=f"next_{scope}_{pid}", on_click=_step, args=("", pid, n, 1),
                     help="Foto siguiente")
        html(card_info_html(p))
        if st.button("Ver detalle", key=f"view_{scope}_{pid}", use_container_width=True):
            ss.view = "product"
            st.query_params.clear()
            st.query_params["producto"] = pid
            st.rerun()


def product_grid(items, scope="h", cols_n=3):
    delays = "".join(f".st-key-card_{scope}_{p['id']}{{animation-delay:{min(i, 9) * 0.07:.2f}s}}"
                     for i, p in enumerate(items))
    html(f"<style>{delays}</style>")
    for start in range(0, len(items), cols_n):
        cols = st.columns(cols_n, gap="medium")
        for j, p in enumerate(items[start:start + cols_n]):
            with cols[j]:
                product_card(p, scope)


# ════════════════════════════════════════════════════════════════════
#  VISTAS
# ════════════════════════════════════════════════════════════════════
def render_home(db):
    render_hero(db)
    html('<div class="ra-sec"><div class="t">El <i>catálogo</i></div>'
         '<div class="s">Toca un artículo para ver todas sus fotos, medidas y detalles.</div></div>')

    present = [c for c in CATEGORIES if any(p["category"] == c for p in db["products"])]
    f1, f2 = st.columns([2.2, 1], vertical_alignment="center")
    with f1:
        q = st.text_input("Buscar", placeholder="Busca por nombre, marca o talla…",
                          label_visibility="collapsed", key="search")
    with f2:
        only = st.toggle("Solo disponibles", key="only_avail")
    cat = st.pills("Categoría", ["Todo"] + present, default="Todo",
                   label_visibility="collapsed", key="cat_pills") or "Todo"

    items = db["products"]
    if cat != "Todo":
        items = [p for p in items if p["category"] == cat]
    if only:
        items = [p for p in items if p["status"] == "Disponible"]
    if q:
        ql = q.lower().strip()
        items = [p for p in items if ql in " ".join(
            str(p.get(k, "")) for k in ("name", "brand", "size", "made_in", "category", "short")).lower()]
    items = sorted(items, key=lambda p: p["status"] != "Disponible")  # disponibles primero

    st.write("")
    if not items:
        html('<div class="ra-empty"><b>No hay artículos con ese filtro</b>'
             'Prueba otra categoría o borra la búsqueda.</div>')
    else:
        product_grid(items, "h")


@st.fragment
def gallery(p):
    pid = p["id"]
    imgs = p.get("images") or ["demo:🖤:0"]
    n = len(imgs)
    idx = ss.get(f"gidx_{pid}", 0) % n
    d = ss.get(f"gdir_{pid}", "r")
    html(card_image_html(p, idx, d, big=True))
    if n > 1:
        a, b, c = st.columns([1, 3, 1], vertical_alignment="center")
        a.button("‹", key=f"gprev_{pid}", on_click=_step, args=("g", pid, n, -1), help="Foto anterior")
        b.markdown(f'<div class="ra-count">Foto {idx + 1} de {n}</div>', unsafe_allow_html=True)
        c.button("›", key=f"gnext_{pid}", on_click=_step, args=("g", pid, n, 1), help="Foto siguiente")
        thumbs = "".join(f'<img class="{"on" if i == idx else ""}" src="{img_src(e)}"/>' for i, e in enumerate(imgs))
        html(f'<div class="ra-thumbs">{thumbs}</div>')


def render_product(db, pid):
    p = get_product(db, pid)
    if not p:
        html('<div class="ra-empty"><b>Este artículo ya no está publicado</b>'
             'Puede que se haya vendido. Revisa el catálogo para ver lo disponible.</div>')
        st.write("")
        if st.button("Ver el catálogo", type="primary"):
            go("home")
        return

    if st.button("‹ Volver al catálogo", key="back_top"):
        go("home")
    st.write("")
    left, right = st.columns([1.05, 1], gap="large")
    with left:
        gallery(p)
    with right:
        sold = p["status"] != "Disponible"
        pill = (f'<span class="ra-pill out">{esc(p["status"])}</span>' if sold
                else '<span class="ra-pill ok">Disponible</span>')
        chips = ""
        if p.get("size"):
            chips += f'<span class="chip size">{esc(size_label(p))}</span>'
        if p.get("made_in"):
            chips += f'<span class="chip">{flag(p["made_in"])} Made in {esc(p["made_in"])}</span>'
        if p.get("brand"):
            chips += f'<span class="chip">{esc(p["brand"])}</span>'
        subject, body = consult_message(db, p)
        wa_txt = (f"Hola Benjamín 👋 Quiero consultar el stock de: {p['name']}"
                  + (f" ({size_label(p)})" if p.get("size") else "")
                  + f" – {money(p['price'])}\n{product_link(db, p['id'])}")
        cta_label = "Consultar disponibilidad" if sold else "Consultar"
        specs = [("Categoría", p.get("category")), ("Talla" if p.get("category") in SIZED_CATEGORIES else "Medida",
                  p.get("size") or "No aplica"),
                 ("Made in", f'{flag(p.get("made_in"))} {p.get("made_in") or "—"}'),
                 ("Marca", p.get("brand") or "—"), ("Condición", p.get("condition") or "—"),
                 ("Publicado", fmt_date(p.get("created")))]
        specs_html = "".join(f"<div><small>{esc(k)}</small><span>{esc(v)}</span></div>" for k, v in specs)
        html(
            '<div class="ra-d">'
            f'<div class="ra-d-cat">{esc(p.get("category"))}</div>'
            f'<div class="ra-d-name">{esc(p["name"])}</div>'
            f'<div class="ra-d-price"><b>{money_html(p["price"])}</b>{pill}</div>'
            f'<div class="ra-chips">{chips}</div>'
            f'<div class="ra-d-short">{esc(p.get("short"))}</div>'
            f'<a class="ra-cta" href="{mailto(subject, body)}">{ICONS["ml"]}{cta_label}</a>'
            '<div class="ra-cta-row">'
            f'<a class="ra-cta ghost" href="{wa_link(wa_txt)}" target="_blank" rel="noopener">{ICONS["wa"]}Por WhatsApp</a>'
            f'<a class="ra-cta ghost" href="{gmail_link(subject, body)}" target="_blank" rel="noopener">{ICONS["ml"]}Abrir en Gmail</a>'
            '</div>'
            f'<div class="ra-specs">{specs_html}</div>'
            '</div>'
        )
        desc = esc(p.get("description"))
        det = "".join(f"<li>{esc(x)}</li>" for x in (p.get("details") or []) if str(x).strip())
        if desc or det:
            html('<div class="ra-desc">'
                 + (f"<h4>Descripción</h4><p>{desc}</p>" if desc else "")
                 + (f"<h4 style='margin-top:1.2rem!important'>Detalles</h4><ul>{det}</ul>" if det else "")
                 + "</div>")
        st.write("")
        st.caption("Link directo de este artículo (cópialo para compartirlo)")
        st.code(product_link(db, p["id"]), language=None)

    related = [x for x in db["products"] if x["id"] != p["id"] and x["category"] == p["category"]]
    if len(related) < 3:
        related += [x for x in db["products"] if x["id"] != p["id"] and x not in related]
    related = sorted(related[:6], key=lambda x: x["status"] != "Disponible")[:3]
    if related:
        st.write("")
        html('<div class="ra-sec" style="margin-top:3rem"><div class="t">También te puede <i>gustar</i></div></div>')
        product_grid(related, "r")


# ─────────────────────────── Autenticación ───────────────────────────
def avatar_picker(prefix: str, default: str | None = None):
    names = list(AVATAR_COLORS)
    key = f"{prefix}_color"
    if key not in ss:
        ss[key] = default if default in names else random.choice(names)
    color_name = st.radio("Color de tu avatar", names, horizontal=True, key=key)
    html(f'<div class="ra-avprev"><img src="{avatar_svg(AVATAR_COLORS[color_name])}"/>'
         f'<span>Así se verá tu icono</span></div>')
    return color_name


def render_login(db):
    _, mid, _ = st.columns([1, 1.7, 1])
    with mid:
        with st.container(key="authbox"):
            html('<div class="ra-auth-h">Tu <i>cuenta</i></div>'
                 '<div class="ra-auth-s">Regístrate para que tus compras queden guardadas en tu perfil.</div>')
            tab_user, tab_admin = st.tabs(["👤 Usuario", "🛡️ Administrador"])

            with tab_user:
                mode = st.radio("¿Qué quieres hacer?", ["Iniciar sesión", "Crear cuenta"],
                                horizontal=True, key="auth_mode", label_visibility="collapsed")
                if mode == "Iniciar sesión":
                    phone = st.text_input("Número de teléfono", placeholder="+56 9 1234 5678", key="li_phone")
                    pw = st.text_input("Contraseña", type="password", key="li_pw")
                    if st.button("Iniciar sesión", type="primary", use_container_width=True, key="li_btn"):
                        u = find_user_by_phone(db, phone)
                        if u and check_pw(pw, u.get("pw")):
                            ss.role, ss.user_id = "user", u["id"]
                            flash(f"Hola de nuevo, {u['name'].split()[0]}", "👋")
                            go("home")
                        else:
                            st.error("El teléfono o la contraseña no coinciden. Revisa e inténtalo otra vez.")
                else:
                    register_form(db)

            with tab_admin:
                apw = st.text_input("Contraseña de administrador", type="password", key="adm_pw")
                if st.button("Entrar al panel", type="primary", use_container_width=True, key="adm_btn"):
                    if check_admin(db, apw):
                        ss.role, ss.user_id = "admin", None
                        flash("Sesión de administrador iniciada", "🛡️")
                        go("admin")
                    else:
                        st.error("Contraseña incorrecta.")


def register_form(db):
    name = st.text_input("Nombre *", key="rg_name", placeholder="Ej: Pepito Pérez")
    phone = st.text_input("Número de teléfono *", key="rg_phone", placeholder="+56 9 1234 5678")
    c1, c2 = st.columns(2)
    pw = c1.text_input("Crea una contraseña *", type="password", key="rg_pw", help="Mínimo 4 caracteres")
    pw2 = c2.text_input("Repite la contraseña *", type="password", key="rg_pw2")

    em_opt = st.radio("Correo electrónico (opcional)", ["No agregar", "Agregar"], horizontal=True, key="rg_em_opt")
    email = st.text_input("Correo", key="rg_email", placeholder="tu@correo.com",
                          label_visibility="collapsed") if em_opt == "Agregar" else ""
    loc_opt = st.radio("Ubicación (opcional)", ["No agregar", "Agregar"], horizontal=True, key="rg_loc_opt")
    location = st.text_input("Ubicación", key="rg_loc", placeholder="Ej: Maipú, Santiago",
                             label_visibility="collapsed") if loc_opt == "Agregar" else ""
    ph_opt = st.radio("Foto de perfil", ["No, usar un avatar", "Sí, subir una foto"], horizontal=True, key="rg_ph_opt")
    photo, color_name = None, None
    if ph_opt.startswith("Sí"):
        photo = st.file_uploader("Sube tu foto", type=["jpg", "jpeg", "png", "webp"], key="rg_photo")
    else:
        color_name = avatar_picker("rg")

    if st.button("Crear cuenta", type="primary", use_container_width=True, key="rg_btn"):
        errors = []
        n = norm_phone(phone)
        if not name.strip():
            errors.append("Escribe tu nombre.")
        if len(n) < 8:
            errors.append("Escribe un número de teléfono válido.")
        if len(pw) < 4:
            errors.append("La contraseña debe tener al menos 4 caracteres.")
        if pw != pw2:
            errors.append("Las contraseñas no coinciden.")
        if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()):
            errors.append("El correo no tiene un formato válido.")
        existing = find_user_by_phone(db, phone)
        if existing and existing.get("pw"):
            errors.append("Ya existe una cuenta con ese teléfono. Inicia sesión.")
        if errors:
            for e in errors:
                st.error(e)
            return
        data = dict(name=name.strip(), phone=n, phone_display=phone.strip(), email=email.strip(),
                    location=location.strip(), pw=hash_pw(pw))
        data["photo"] = save_upload(photo, 600) if photo else None
        data["avatar_color"] = AVATAR_COLORS.get(color_name or "Rojo")
        if existing:  # cuenta creada antes por el admin: se reclama
            existing.update(data)
            uid = existing["id"]
        else:
            uid = new_id()
            db["users"].append(dict(id=uid, gender="Prefiero no decirlo", gender_custom="",
                                    created=now_iso(), **data))
        save_db(db)
        ss.role, ss.user_id = "user", uid
        flash(f"Cuenta creada. Bienvenido, {name.split()[0]}", "🎉")
        go("profile")


# ─────────────────────────── Perfiles ───────────────────────────
def profile_header(db, u):
    c, units, total = user_stats(db, u["id"])
    gender = u.get("gender_custom") if u.get("gender") == "Personalizado" and u.get("gender_custom") else u.get("gender")
    bits = [f"📞 {esc(u.get('phone_display') or u['phone'])}"]
    if u.get("email"):
        bits.append(f"✉️ {esc(u['email'])}")
    if u.get("location"):
        bits.append(f"📍 {esc(u['location'])}")
    if gender:
        bits.append(f"◐ {esc(gender)}")
    bits.append(f"Desde {fmt_date(u.get('created'))}")
    html(f'<div class="ra-prof"><img src="{user_avatar(u)}"/><div><div class="n">{esc(u["name"])}</div>'
         f'<div class="d">{"".join(f"<span>{b}</span>" for b in bits)}</div></div>'
         f'<div class="k"><div><b>{c}</b><small>compras</small></div><div><b>{units}</b><small>unidades</small></div>'
         f'<div><b>{money_html(total)}</b><small>total</small></div></div></div>')


def purchases_list(db, purchases, admin=False):
    if not purchases:
        html('<div class="ra-empty"><b>Aún no hay compras registradas</b>'
             + ("Regístralas desde la pestaña Registrar venta." if admin
                else "Cuando Benjamín registre tu compra, aparecerá aquí.") + '</div>')
        return
    for pu in purchases:
        prod = get_product(db, pu.get("product_id"))
        thumb = img_src((prod.get("images") or [""])[0]) if prod else demo_svg("🛍️", 0)
        meta = f"{fmt_date(pu.get('date'))} · {pu.get('qty', 1)} u."
        if pu.get("size"):
            meta += f" · Talla {esc(pu['size'])}"
        if pu.get("note"):
            meta += f" · {esc(pu['note'])}"
        row = (f'<div class="ra-row"><img src="{thumb}"/><div class="m"><b>{esc(pu["product_name"])}</b>'
               f'<small>{meta}</small></div><div class="v">{money_html(pu.get("total"))}</div></div>')
        if admin:
            a, b = st.columns([8, 1.3], vertical_alignment="center")
            a.markdown(row, unsafe_allow_html=True)
            if b.button("Quitar", key=f"delpu_{pu['id']}", help="Eliminar este registro de compra"):
                db["purchases"] = [x for x in db["purchases"] if x["id"] != pu["id"]]
                save_db(db)
                flash("Compra eliminada", "🗑️")
                st.rerun()
        else:
            html(row)
            st.write("")


def render_profile(db):
    u = current_user(db)
    if not u:
        go("login")
    profile_header(db, u)
    t1, t2 = st.tabs(["Mis compras", "Mis datos"])
    with t1:
        purchases_list(db, user_purchases(db, u["id"]))
    with t2:
        name = st.text_input("Nombre", value=u["name"], key="pf_name")
        st.text_input("Teléfono", value=u.get("phone_display") or u["phone"], disabled=True,
                      help="Para cambiar tu teléfono, escríbele a Benjamín.")
        em_opt = st.radio("Correo electrónico", ["No agregar", "Agregar"], horizontal=True,
                          index=1 if u.get("email") else 0, key="pf_em_opt")
        email = st.text_input("Correo", value=u.get("email", ""), key="pf_email",
                              label_visibility="collapsed") if em_opt == "Agregar" else ""
        loc_opt = st.radio("Ubicación", ["No agregar", "Agregar"], horizontal=True,
                           index=1 if u.get("location") else 0, key="pf_loc_opt")
        location = st.text_input("Ubicación", value=u.get("location", ""), key="pf_loc",
                                 label_visibility="collapsed") if loc_opt == "Agregar" else ""
        g = u.get("gender") if u.get("gender") in GENDERS else "Prefiero no decirlo"
        gender = st.radio("Género", GENDERS, index=GENDERS.index(g), horizontal=True, key="pf_gender")
        gender_custom = st.text_input("¿Cómo te identificas?", value=u.get("gender_custom", ""),
                                      key="pf_gcustom") if gender == "Personalizado" else ""
        ph_opt = st.radio("Foto de perfil", ["Mantener la actual", "Subir una foto nueva", "Usar un avatar"],
                          horizontal=True, key="pf_ph")
        new_photo, color_name = None, None
        if ph_opt == "Subir una foto nueva":
            new_photo = st.file_uploader("Sube tu foto", type=["jpg", "jpeg", "png", "webp"], key="pf_photo")
        elif ph_opt == "Usar un avatar":
            cur = next((k for k, v in AVATAR_COLORS.items() if v == u.get("avatar_color")), None)
            color_name = avatar_picker("pf", cur)
        with st.expander("Cambiar contraseña"):
            npw = st.text_input("Nueva contraseña", type="password", key="pf_npw")
            npw2 = st.text_input("Repite la nueva contraseña", type="password", key="pf_npw2")

        c1, c2 = st.columns(2)
        if c1.button("Guardar cambios", type="primary", use_container_width=True, key="pf_save"):
            if not name.strip():
                st.error("El nombre no puede quedar vacío.")
                return
            if npw and (len(npw) < 4 or npw != npw2):
                st.error("La nueva contraseña debe tener 4+ caracteres y coincidir en ambos campos.")
                return
            u.update(name=name.strip(), email=email.strip(), location=location.strip(),
                     gender=gender, gender_custom=gender_custom.strip())
            if new_photo:
                delete_image(u.get("photo"))
                u["photo"] = save_upload(new_photo, 600)
            elif color_name:
                delete_image(u.get("photo"))
                u["photo"] = None
                u["avatar_color"] = AVATAR_COLORS[color_name]
            if npw:
                u["pw"] = hash_pw(npw)
            save_db(db)
            flash("Cambios guardados", "✅")
            st.rerun()
        if c2.button("Cerrar sesión", use_container_width=True, key="pf_out"):
            logout()


# ─────────────────────────── Administración ───────────────────────────
def _set_status(pid):
    db = load_db()
    p = get_product(db, pid)
    if p:
        p["status"] = ss[f"status_{pid}"]
        save_db(db)
        ss["_flash"] = (f"{p['name']}: {p['status']}", "🏷️")


def product_form_fields(prefix, p=None):
    p = p or {}
    c1, c2 = st.columns([2, 1])
    name = c1.text_input("Nombre del producto *", value=p.get("name", ""), key=f"{prefix}_name")
    category = c2.selectbox("Categoría", CATEGORIES,
                            index=CATEGORIES.index(p["category"]) if p.get("category") in CATEGORIES else 0,
                            key=f"{prefix}_cat")
    c3, c4, c5 = st.columns(3)
    price = c3.number_input("Precio (CLP)", min_value=0, step=500, value=int(p.get("price", 0)), key=f"{prefix}_price")
    size = c4.text_input("Talla o medida", value=p.get("size", ""), placeholder="L, 42, Única… (vacío si no aplica)",
                         key=f"{prefix}_size")
    mi = p.get("made_in", "China")
    made_sel = c5.selectbox("Made in", MADE_IN_OPTIONS,
                            index=MADE_IN_OPTIONS.index(mi) if mi in MADE_IN_OPTIONS else len(MADE_IN_OPTIONS) - 1,
                            key=f"{prefix}_made")
    made_other = st.text_input("País (si elegiste Otro)", value="" if mi in MADE_IN_OPTIONS else mi,
                               key=f"{prefix}_made_o")
    c6, c7, c8 = st.columns(3)
    brand = c6.text_input("Marca", value=p.get("brand", ""), key=f"{prefix}_brand")
    condition = c7.selectbox("Condición", CONDITIONS,
                             index=CONDITIONS.index(p["condition"]) if p.get("condition") in CONDITIONS else 0,
                             key=f"{prefix}_cond")
    status = c8.selectbox("Estado", STATUSES,
                          index=STATUSES.index(p["status"]) if p.get("status") in STATUSES else 0,
                          key=f"{prefix}_status")
    short = st.text_input("Descripción corta (se ve en la tarjeta)", value=p.get("short", ""), key=f"{prefix}_short")
    desc = st.text_area("Descripción completa", value=p.get("description", ""), key=f"{prefix}_desc")
    details = st.text_area("Detalles (uno por línea)", value="\n".join(p.get("details") or []), key=f"{prefix}_det")
    return dict(name=name.strip(), category=category, price=int(price), size=size.strip(),
                made_in=(made_other.strip() or "Otro") if made_sel == "Otro" else made_sel,
                brand=brand.strip(), condition=condition, status=status, short=short.strip(),
                description=desc.strip(), details=[x.strip() for x in details.splitlines() if x.strip()])


def admin_products(db):
    with st.expander("➕ Publicar un producto nuevo"):
        with st.form("add_prod", clear_on_submit=True):
            data = product_form_fields("np")
            imgs = st.file_uploader("Fotos (puedes subir varias; la primera será la portada)",
                                    type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key="np_imgs")
            ok = st.form_submit_button("Publicar producto", type="primary", use_container_width=True)
        if ok:
            if not data["name"]:
                st.error("El producto necesita un nombre.")
            else:
                data["images"] = [save_upload(f) for f in (imgs or [])] or ["demo:🛍️:0"]
                data["id"], data["created"] = new_id(), now_iso()
                db["products"].insert(0, data)
                save_db(db)
                flash(f"Publicado: {data['name']}", "✅")
                st.rerun()

    st.write("")
    if not db["products"]:
        html('<div class="ra-empty"><b>Tu catálogo está vacío</b>Publica tu primer producto arriba.</div>')
    for p in db["products"]:
        pid = p["id"]
        with st.container(border=True):
            c0, c1, c2, c3 = st.columns([0.9, 3.2, 1.7, 1.6], vertical_alignment="center")
            c0.markdown(f'<div class="ra-row" style="border:none;padding:0;background:none">'
                        f'<img src="{img_src((p.get("images") or [""])[0])}"/></div>', unsafe_allow_html=True)
            c1.markdown(f'<div class="ra-row" style="border:none;padding:0;background:none"><div class="m">'
                        f'<b>{esc(p["name"])}</b><small>{money_html(p["price"])} · {esc(p["category"])}'
                        f'{" · " + esc(size_label(p)) if p.get("size") else ""} · {len(p.get("images") or [])} fotos'
                        f'</small></div></div>', unsafe_allow_html=True)
            ss[f"status_{pid}"] = p["status"]
            c2.selectbox("Estado", STATUSES, key=f"status_{pid}", on_change=_set_status, args=(pid,),
                         label_visibility="collapsed")
            with c3:
                b1, b2 = st.columns(2)
                if b1.button("Ver", key=f"see_{pid}", use_container_width=True):
                    go("product", pid)
                if b2.button("🗑️", key=f"del_{pid}", help="Eliminar producto", use_container_width=True):
                    ss.confirm_del = pid
            if ss.get("confirm_del") == pid:
                st.warning(f"¿Eliminar «{p['name']}» del catálogo? Las compras ya registradas se mantienen.")
                y, n = st.columns(2)
                if y.button("Sí, eliminar", key=f"yes_{pid}", type="primary", use_container_width=True):
                    for e in p.get("images") or []:
                        delete_image(e)
                    db["products"] = [x for x in db["products"] if x["id"] != pid]
                    save_db(db)
                    ss.confirm_del = None
                    flash("Producto eliminado", "🗑️")
                    st.rerun()
                if n.button("Cancelar", key=f"no_{pid}", use_container_width=True):
                    ss.confirm_del = None
                    st.rerun()
            with st.expander("Editar producto"):
                with st.form(f"edit_{pid}"):
                    data = product_form_fields(f"ed_{pid}", p)
                    imgs = p.get("images") or []
                    remove = st.multiselect("Fotos a quitar", list(range(len(imgs))),
                                            format_func=lambda i: f"Foto {i + 1}", key=f"ed_rm_{pid}")
                    cover = st.selectbox("Foto de portada", list(range(len(imgs))) or [0],
                                         format_func=lambda i: f"Foto {i + 1}", key=f"ed_cover_{pid}")
                    add = st.file_uploader("Agregar fotos", type=["jpg", "jpeg", "png", "webp"],
                                           accept_multiple_files=True, key=f"ed_add_{pid}")
                    saved = st.form_submit_button("Guardar cambios", type="primary", use_container_width=True)
                if imgs:
                    thumbs = "".join(f'<img class="on" src="{img_src(e)}" title="Foto {i + 1}"/>'
                                     for i, e in enumerate(imgs))
                    html(f'<div class="ra-thumbs">{thumbs}</div>')
                if saved:
                    if not data["name"]:
                        st.error("El producto necesita un nombre.")
                    else:
                        keep = [e for i, e in enumerate(imgs) if i not in remove]
                        if imgs and cover not in remove and cover < len(imgs):
                            keep.remove(imgs[cover])
                            keep.insert(0, imgs[cover])
                        for i in remove:
                            delete_image(imgs[i])
                        keep += [save_upload(f) for f in (add or [])]
                        p.update(data)
                        p["images"] = keep or ["demo:🛍️:0"]
                        save_db(db)
                        flash("Producto actualizado", "✅")
                        st.rerun()


def admin_sales(db):
    if not db["users"]:
        html('<div class="ra-empty"><b>Todavía no hay clientes</b>'
             'Cuando alguien cree su cuenta (o la agregues en Clientes), podrás registrar sus compras aquí.</div>')
        return
    if not db["products"]:
        st.info("Publica al menos un producto para registrar ventas.")
        return
    html('<div class="ra-sec"><div class="t" style="font-size:2rem">Registrar una <i>venta</i></div>'
         '<div class="s">Ej: Pepito compró la Polera roja y ya se la entregaste. Queda guardado en su perfil.</div></div>')
    users = sorted(db["users"], key=lambda u: u["name"].lower())
    prods = db["products"]
    c1, c2 = st.columns(2)
    uid = c1.selectbox("Cliente", [u["id"] for u in users], key="sale_user",
                       format_func=lambda i: f"{get_user(db, i)['name']} · {get_user(db, i).get('phone_display') or get_user(db, i)['phone']}")
    pid = c2.selectbox("Producto", [p["id"] for p in prods], key="sale_prod",
                       format_func=lambda i: f"{get_product(db, i)['name']} · {money(get_product(db, i)['price'])}"
                                             f"{' · ' + get_product(db, i)['status'] if get_product(db, i)['status'] != 'Disponible' else ''}")
    p = get_product(db, pid)
    c3, c4, c5 = st.columns(3)
    qty = c3.number_input("Cantidad", min_value=1, step=1, value=1, key="sale_qty")
    price = c4.number_input("Precio unitario (CLP)", min_value=0, step=500, value=int(p["price"]), key=f"sale_price_{pid}")
    d = c5.date_input("Fecha de entrega", value=date.today(), key="sale_date", format="DD/MM/YYYY")
    note = st.text_input("Nota (opcional)", placeholder="Ej: entregado en metro Los Héroes", key="sale_note")
    mark = st.checkbox("Marcar el producto como Agotado", value=True, key="sale_mark")
    if st.button("Registrar venta", type="primary", use_container_width=True, key="sale_btn"):
        db["purchases"].append(dict(
            id=new_id(), user_id=uid, product_id=pid, product_name=p["name"], size=p.get("size", ""),
            qty=int(qty), unit_price=int(price), total=int(qty) * int(price),
            date=d.isoformat(), note=note.strip(), created=now_iso()))
        if mark:
            p["status"] = "Agotado"
        save_db(db)
        flash(f"Venta registrada a {get_user(db, uid)['name']}", "🧾")
        st.rerun()

    recent = sorted(db["purchases"], key=lambda x: x.get("created", ""), reverse=True)[:8]
    if recent:
        st.write("")
        html('<div class="ra-sec"><div class="t" style="font-size:1.6rem">Últimas ventas</div></div>')
        rows = "".join(
            f"<tr><td>{fmt_date(x['date'])}</td><td>{esc((get_user(db, x['user_id']) or {}).get('name', 'Cliente eliminado'))}</td>"
            f"<td>{esc(x['product_name'])}</td><td>{x['qty']}</td><td>{money_html(x['total'])}</td></tr>" for x in recent)
        html(f'<div class="ra-table-wrap"><table class="ra-table"><tr><th>Fecha</th><th>Cliente</th>'
             f'<th>Producto</th><th>Cant.</th><th>Total</th></tr>{rows}</table></div>')


def admin_clients(db):
    stats = []
    for u in db["users"]:
        c, units, total = user_stats(db, u["id"])
        last = (user_purchases(db, u["id"]) or [{}])[0].get("date", "")
        stats.append((u, c, units, total, last))
    stats.sort(key=lambda x: (x[3], x[1]), reverse=True)

    m1, m2, m3 = st.columns(3)
    m1.metric("Clientes", len(db["users"]))
    m2.metric("Ventas registradas", len(db["purchases"]))
    m3.metric("Total vendido", money(sum(int(x.get("total", 0)) for x in db["purchases"])))

    with st.expander("➕ Agregar un cliente manualmente (si compró sin crear cuenta)"):
        with st.form("add_client", clear_on_submit=True):
            a, b = st.columns(2)
            cn = a.text_input("Nombre *")
            cp = b.text_input("Teléfono *")
            c, d = st.columns(2)
            ce = c.text_input("Correo (opcional)")
            cl = d.text_input("Ubicación (opcional)")
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
                flash("Cliente agregado. Si luego se registra con ese teléfono, verá sus compras.", "👤")
                st.rerun()

    if not stats:
        html('<div class="ra-empty"><b>Aún no hay clientes</b>Comparte la tienda para que se registren.</div>')
        return

    top = [s for s in stats if s[3] > 0][:3]
    if top:
        html('<div class="ra-sec" style="margin-top:1.2rem"><div class="t" style="font-size:1.8rem">Quién te compra <i>más</i></div></div>')
        pods = ""
        for i, (u, c, units, total, _) in enumerate(top):
            pods += (f'<div class="ra-pod{" first" if i == 0 else ""}" style="animation-delay:{i * .1}s">'
                     f'<div class="p">{["Primer lugar", "Segundo lugar", "Tercer lugar"][i]}</div>'
                     f'<img src="{user_avatar(u)}"/><b>{esc(u["name"])}</b>'
                     f'<small>{c} compras · {money_html(total)}</small></div>')
        html(f'<div class="ra-podium">{pods}</div>')

    rows = ""
    for i, (u, c, units, total, last) in enumerate(stats, 1):
        rows += (f"<tr><td>{i}</td><td><img src='{user_avatar(u)}'/>{esc(u['name'])}</td>"
                 f"<td>{esc(u.get('phone_display') or u['phone'])}</td><td>{esc(u.get('email') or '—')}</td>"
                 f"<td>{esc(u.get('location') or '—')}</td><td>{c}</td><td>{units}</td>"
                 f"<td><b>{money_html(total)}</b></td><td>{fmt_date(last) if last else '—'}</td></tr>")
    html('<div class="ra-table-wrap"><table class="ra-table"><tr><th>#</th><th>Cliente</th><th>Teléfono</th>'
         '<th>Correo</th><th>Ubicación</th><th>Compras</th><th>Unid.</th><th>Total</th><th>Última</th></tr>'
         f'{rows}</table></div>')

    st.write("")
    html('<div class="ra-sec" style="margin-top:1rem"><div class="t" style="font-size:1.8rem">Perfil del <i>cliente</i></div></div>')
    uid = st.selectbox("Elige un cliente", [s[0]["id"] for s in stats], key="cl_pick",
                       format_func=lambda i: get_user(db, i)["name"])
    u = get_user(db, uid)
    profile_header(db, u)
    if not u.get("pw"):
        st.caption("Este cliente fue agregado manualmente. Si se registra con el mismo teléfono, tomará esta cuenta.")
    purchases_list(db, user_purchases(db, uid), admin=True)
    st.write("")
    if st.button("Eliminar cuenta de este cliente", key=f"delu_{uid}"):
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
            flash("Cliente eliminado", "🗑️")
            st.rerun()
        if n.button("Cancelar", key=f"delu_n_{uid}", use_container_width=True):
            ss.confirm_user = None
            st.rerun()


def admin_settings(db):
    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        html(f'<div class="ra-arch" style="width:170px"><img src="{owner_photo(db)}"/></div>')
    with c2:
        html('<div class="ra-sec"><div class="t" style="font-size:1.7rem">Tu foto</div>'
             '<div class="s">Es la que aparece al inicio de la tienda. Una vertical se ve mejor.</div></div>')
        ph = st.file_uploader("Foto de Benjamín", type=["jpg", "jpeg", "png", "webp"], key="own_photo")
        a, b = st.columns(2)
        if a.button("Guardar foto", type="primary", use_container_width=True, disabled=ph is None):
            delete_image(db["settings"].get("owner_photo"))
            db["settings"]["owner_photo"] = save_upload(ph, 1000)
            save_db(db)
            flash("Foto actualizada", "📸")
            st.rerun()
        if b.button("Quitar foto", use_container_width=True, disabled=not db["settings"].get("owner_photo")):
            delete_image(db["settings"].pop("owner_photo", None))
            save_db(db)
            st.rerun()

    st.divider()
    html('<div class="ra-sec"><div class="t" style="font-size:1.7rem">Link de la tienda</div>'
         '<div class="s">Se usa en los correos de consulta. Déjalo vacío para detectarlo solo; '
         'si publicas la app, pega aquí su dirección (ej: https://rissos-anghell.streamlit.app).</div></div>')
    bu = st.text_input("Dirección pública", value=db["settings"].get("base_url", ""), key="set_base",
                       placeholder=app_base_url(db))
    if st.button("Guardar link", key="set_base_btn"):
        db["settings"]["base_url"] = bu.strip()
        save_db(db)
        flash("Link guardado", "🔗")
        st.rerun()

    st.divider()
    html('<div class="ra-sec"><div class="t" style="font-size:1.7rem">Contraseña de administrador</div></div>')
    a, b, c = st.columns(3)
    cur = a.text_input("Actual", type="password", key="set_cur")
    new = b.text_input("Nueva", type="password", key="set_new")
    new2 = c.text_input("Repite la nueva", type="password", key="set_new2")
    if st.button("Cambiar contraseña", key="set_pw_btn"):
        if not check_admin(db, cur):
            st.error("La contraseña actual no es correcta.")
        elif len(new) < 6 or new != new2:
            st.error("La nueva contraseña debe tener 6+ caracteres y coincidir.")
        else:
            db["settings"]["admin_pw"] = hash_pw(new)
            save_db(db)
            flash("Contraseña actualizada", "🔐")
            st.rerun()

    st.divider()
    st.download_button("Descargar respaldo de datos (JSON)", json.dumps(db, ensure_ascii=False, indent=2),
                       file_name=f"rissos_respaldo_{date.today().isoformat()}.json", mime="application/json")


def render_admin(db):
    if ss.role != "admin":
        go("login")
    h, o = st.columns([5, 1.2], vertical_alignment="bottom")
    with h:
        html('<div class="ra-sec"><div class="t">Panel de <i>administración</i></div>'
             '<div class="s">Productos, ventas y clientes en un solo lugar.</div></div>')
    with o:
        if st.button("Cerrar sesión", key="adm_out", use_container_width=True):
            logout()
    t1, t2, t3, t4 = st.tabs(["🛍️ Productos", "🧾 Registrar venta", "👥 Clientes", "⚙️ Ajustes"])
    with t1:
        admin_products(db)
    with t2:
        admin_sales(db)
    with t3:
        admin_clients(db)
    with t4:
        admin_settings(db)


def render_footer():
    mail = mailto("Contacto – Rissos Anghell Store")
    html(f'<div class="ra-foot"><div><div class="b">Rissos Anghell Store</div>'
         f'© {date.today().year} Benjamín Espinoza · Santiago, Chile</div>'
         f'<div><a href="{wa_link()}" target="_blank" rel="noopener">WhatsApp</a>'
         f'<a href="https://www.instagram.com/{OWNER["instagram"]}/" target="_blank" rel="noopener">Instagram</a>'
         f'<a href="{mail}">Correo</a></div></div>')


# ════════════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════════════
def main():
    db = load_db()
    inject_css()
    if "_flash" in ss:
        msg, icon = ss.pop("_flash")
        st.toast(msg, icon=icon)

    pid = st.query_params.get("producto")
    view = "product" if pid else ss.view
    if view == "product" and not pid:
        view = "home"

    render_navbar(db, view)

    if view == "product":
        render_product(db, pid)
    elif view == "login":
        render_login(db)
    elif view == "profile":
        render_profile(db)
    elif view == "admin":
        render_admin(db)
    else:
        render_home(db)

    render_footer()

    nav_key = f"{view}:{pid or ''}"
    if ss.get("_last_nav") not in (None, nav_key):
        scroll_top()
    ss["_last_nav"] = nav_key


main()
