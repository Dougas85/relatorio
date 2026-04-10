"""
 — Relatório de Reestruturação Logística
============================================
Tela 1 · Editor: formulário + múltiplas imagens por seção
Tela 2 · Dashboard: KPIs + gráficos + botão download PDF
         (o relatório formatado só existe no PDF)
"""

import io, math, base64, datetime
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.platypus import Flowable

# ── CONFIG ────────────────────────────────────────────────────
st.set_page_config(
    page_title="DFS · Relatório 5W2H"
    page_icon="📦", layout="wide",
    initial_sidebar_state="collapsed",
)

SECOES = ["escopo", "problemas", "acoes", "conclusao"]

# ── ESTADO INICIAL ────────────────────────────────────────────
def init():
    if "tela" not in st.session_state:
        st.session_state.tela = "editor"
    if "form" not in st.session_state:
        st.session_state.form = {
            "unidade":     " ",
            "responsavel": " ",
            "data":        datetime.date.today().strftime("%d/%m/%Y"),
            "iep_atual":   ,
            "iep_meta":    ,
            "residuo":     ,
            "distritos":   ,
            "prazo":       ,
            "escopo": ,
            "problemas": ,
            "acoes": ,
            "conclusao": ,
            "imgs": {s: [] for s in SECOES},
            "w5h2": [
                {
                    "acao":     " ",
                    "what":     " ",
                    "why":      " ",
                    "where":    " ",
                    "who":      " ",
                    "when":     " ",
                    "how":      " ",
                    "howmuch":  " ",
                },
                {
                    "acao":     " ",
                    "what":     " ",
                    "why":      " ",
                    "where":    " ",
                    "who":      " ",
                    "when":     " ",
                    "how":      " ",
                    "howmuch":  " ",
                },
                {
                    "acao":     " ",
                    "what":     " ",
                    "why":      " ",
                    "where":    " ",
                    "who":      " ",
                    "when":     " ",
                    "how":      " ",
                    "howmuch":  " ",
                },
            ],
        }

init()
F = st.session_state.form

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

*, html, body, [class*="css"] { font-family:'IBM Plex Sans',sans-serif !important; }
.block-container { padding:1.5rem 3rem 3rem !important; max-width:1380px; }

/* HERO */
.hero {
    background:linear-gradient(125deg,#0d1b2a 0%,#1b3a5c 60%,#0d2137 100%);
    border-radius:10px; padding:2rem 2.8rem; color:#f0e8d8;
    margin-bottom:2rem; position:relative; overflow:hidden;
}
.hero::after {
    content:''; position:absolute; right:-40px; top:-40px;
    width:220px; height:220px; border-radius:50%;
    background:rgba(201,168,76,.08);
}
.hero-tag {
    font-family:'IBM Plex Mono',monospace; font-size:.6rem;
    letter-spacing:.28em; text-transform:uppercase; color:#c9a84c; margin-bottom:.4rem;
}
.hero-h1  { font-size:1.75rem; font-weight:700; margin-bottom:.3rem; line-height:1.15; }
.hero-sub { font-size:.87rem; color:#7a9ab8; }
.hero-badge {
    display:inline-block; background:rgba(201,168,76,.18);
    color:#e8c96a; border:1px solid rgba(201,168,76,.35);
    border-radius:20px; padding:.2rem .75rem; font-size:.72rem;
    font-family:'IBM Plex Mono',monospace; margin-top:.7rem;
}

/* SECTION LABEL */
.slabel {
    font-family:'IBM Plex Mono',monospace; font-size:.65rem;
    letter-spacing:.18em; text-transform:uppercase;
    color:#f0e8d8; background:linear-gradient(90deg,#0d1b2a,#1b3a5c);
    padding:.5rem 1rem; border-left:3px solid #c9a84c;
    border-radius:3px; margin:1.6rem 0 .8rem;
}

/* KPI CARDS */
[data-testid="metric-container"] {
    background:#0d1b2a !important;
    border-left:3px solid #c9a84c !important;
    border-radius:6px !important;
    padding:1.1rem 1.2rem !important;
}
[data-testid="metric-container"] label {
    color:#5a7a9a !important; font-size:.68rem !important;
    font-family:'IBM Plex Mono',monospace !important;
    text-transform:uppercase; letter-spacing:.1em;
}
[data-testid="stMetricValue"] { color:#f0e8d8 !important; font-size:1.7rem !important; font-weight:700 !important; }
[data-testid="stMetricDelta"] { font-size:.74rem !important; }

/* BUTTONS */
.stButton>button {
    background:#0d1b2a !important; color:#f0e8d8 !important;
    border:1.5px solid #c9a84c !important; border-radius:4px !important;
    font-family:'IBM Plex Mono',monospace !important; font-size:.7rem !important;
    letter-spacing:.1em !important; text-transform:uppercase !important;
    padding:.6rem 1.6rem !important; font-weight:600 !important;
    transition:all .18s !important;
}
.stButton>button:hover { background:#c9a84c !important; color:#0d1b2a !important; }
.stDownloadButton>button {
    background:#c9a84c !important; color:#0d1b2a !important;
    border:none !important; border-radius:4px !important;
    font-family:'IBM Plex Mono',monospace !important; font-size:.75rem !important;
    letter-spacing:.1em !important; text-transform:uppercase !important;
    padding:.7rem 2rem !important; font-weight:700 !important;
    width:100% !important;
}
.stDownloadButton>button:hover { background:#e8c96a !important; }

/* PROG BARS */
.prog-row { display:flex; align-items:center; gap:.8rem; margin:.55rem 0; }
.prog-label { font-size:.82rem; width:190px; flex-shrink:0; color:#334; }
.prog-bar-bg { flex:1; background:#e8e4dc; border-radius:20px; height:10px; }
.prog-bar-fill { height:10px; border-radius:20px; }
.prog-pct { font-size:.75rem; font-family:'IBM Plex Mono',monospace; width:36px; text-align:right; color:#666; }

/* INPUTS */
.stTextInput input, .stTextArea textarea, .stNumberInput input {
    border:1px solid #ccc !important; border-radius:4px !important;
    font-family:'IBM Plex Sans',sans-serif !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color:#c9a84c !important;
    box-shadow:0 0 0 2px rgba(201,168,76,.18) !important;
}
hr { border-color:#e0dcd4 !important; }

/* INFO BOX no dashboard */
.info-box {
    background:#f5f9ff; border:1px solid #c8ddf5; border-radius:6px;
    padding:1rem 1.4rem; font-size:.88rem; color:#1a3a5c;
    display:flex; align-items:center; gap:.7rem; margin-bottom:1rem;
}
/* 5W2H TABLE */
.w5h2-wrap { overflow-x:auto; margin-top:.5rem; }
.w5h2-table {
    width:100%; border-collapse:collapse;
    font-family:'IBM Plex Sans',sans-serif; font-size:.82rem;
    box-shadow:0 2px 16px rgba(0,0,0,.08); border-radius:8px; overflow:hidden;
}
.w5h2-table thead tr { background:#0d1b2a; color:#f0e8d8; }
.w5h2-table thead th {
    padding:.65rem .9rem; text-align:left;
    font-family:'IBM Plex Mono',monospace; font-size:.6rem;
    letter-spacing:.14em; text-transform:uppercase; white-space:nowrap;
}
.w5h2-table thead th:first-child { border-left:3px solid #c9a84c; }
.w5h2-table tbody tr:nth-child(odd)  { background:#f8f7f4; }
.w5h2-table tbody tr:nth-child(even) { background:#ffffff; }
.w5h2-table tbody tr:hover { background:#eef4ff; transition:background .15s; }
.w5h2-table tbody td {
    padding:.6rem .9rem; vertical-align:top;
    border-bottom:1px solid #e8e4dc; color:#1a2a3a; line-height:1.5;
}
.w5h2-table tbody td:first-child {
    font-weight:700; color:#0d1b2a;
    border-left:3px solid #c9a84c; min-width:160px;
}
.pill  { display:inline-block; background:#0d1b2a; color:#f0e8d8;
         border-radius:10px; padding:.12rem .55rem; font-size:.66rem;
         font-family:'IBM Plex Mono',monospace; }
.pillg { display:inline-block; background:rgba(201,168,76,.18); color:#6b4a00;
         border:1px solid rgba(201,168,76,.5);
         border-radius:10px; padding:.12rem .55rem; font-size:.66rem;
         font-family:'IBM Plex Mono',monospace; }
</style>
""", unsafe_allow_html=True)


# ── PDF ───────────────────────────────────────────────────────
def gerar_pdf() -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer,
        HRFlowable, Table, TableStyle, Image as RLImage,
    )
    from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
    from PIL import Image as PILImage

    PAGE_W, _ = A4
    MARGIN    = 2.5 * cm
    TW        = PAGE_W - 2 * MARGIN

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN,  bottomMargin=MARGIN)

    azul    = colors.HexColor("#0d1b2a")
    azclaro = colors.HexColor("#dce8f5")
    cinza   = colors.HexColor("#555555")

    s_title = ParagraphStyle("T", fontName="Helvetica-Bold", fontSize=13,
        leading=18, alignment=TA_CENTER, textColor=azul, spaceAfter=8)
    s_key   = ParagraphStyle("K", fontName="Helvetica-Bold", fontSize=10,
        leading=14, textColor=azul)
    s_val   = ParagraphStyle("V", fontName="Helvetica", fontSize=10,
        leading=14, textColor=colors.HexColor("#222"))
    s_sec   = ParagraphStyle("S", fontName="Helvetica-Bold", fontSize=11,
        leading=14, textColor=azul, backColor=azclaro,
        spaceBefore=14, spaceAfter=6, leftIndent=4, rightIndent=4, borderPad=5)
    s_body  = ParagraphStyle("B", fontName="Times-Roman", fontSize=10.5,
        leading=18, alignment=TA_JUSTIFY,
        textColor=colors.HexColor("#111"),
        spaceAfter=5, firstLineIndent=28)        # ← RECUO REAL
    s_cap   = ParagraphStyle("C", fontName="Helvetica-Oblique", fontSize=8.5,
        leading=11, alignment=TA_CENTER, textColor=cinza, spaceAfter=6)
    s_foot  = ParagraphStyle("F", fontName="Helvetica", fontSize=8,
        leading=10, alignment=TA_CENTER, textColor=cinza)

    story = []
    story.append(Spacer(1, .3*cm))
    story.append(Paragraph("RELATÓRIO DE REESTRUTURAÇÃO E EFICIÊNCIA LOGÍSTICA", s_title))
    story.append(HRFlowable(width="100%", thickness=2, color=azul, spaceAfter=10))
    story.append(Spacer(1, .2*cm))

    meta_rows = [
        [Paragraph("<b>UNIDADE:</b>",     s_key), Paragraph(F["unidade"],     s_val)],
        [Paragraph("<b>RESPONSÁVEL:</b>", s_key), Paragraph(F["responsavel"], s_val)],
        [Paragraph("<b>DATA:</b>",        s_key), Paragraph(F["data"],        s_val)],
    ]
    t = Table(meta_rows, colWidths=[4*cm, TW-4*cm])
    t.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("BOTTOMPADDING", (0,0), (-1,-1),  3),
        ("TOPPADDING",    (0,0), (-1,-1),  2),
    ]))
    story.append(t)
    story.append(HRFlowable(width="100%", thickness=.5,
        color=colors.HexColor("#bbb"), spaceAfter=10))
    story.append(Spacer(1, .2*cm))

    def pdf_imgs(secao):
        for item in F["imgs"].get(secao, []):
            try:
                ib = io.BytesIO(item["bytes"])
                pil = PILImage.open(ib)
                ow, oh = pil.size
                scale  = min(TW / ow, (10*cm) / oh)
                ib.seek(0)
                img = RLImage(ib, width=ow*scale, height=oh*scale)
                img.hAlign = "CENTER"
                story.append(Spacer(1, .3*cm))
                story.append(img)
                story.append(Paragraph(item["nome"], s_cap))
                story.append(Spacer(1, .3*cm))
            except Exception as e:
                story.append(Paragraph(f"[Erro: {e}]", s_cap))

    TITULOS = {
        "escopo":    "1. Diagnóstico de Infraestrutura (Escopo)",
        "problemas": "2. Gargalos e Não-Conformidades (Problemas)",
        "acoes":     "3. Plano de Otimização (Ações)",
        "conclusao": "4. Conclusão e Projeção de Resultados",
    }
    for secao, titulo in TITULOS.items():
        story.append(Paragraph(titulo, s_sec))
        for p in F[secao].split("\n\n"):
            p = p.strip().replace("\n", " ")
            if p:
                story.append(Paragraph(p, s_body))
        pdf_imgs(secao)


    # 1. Definição de Cores
    C_AZUL      = colors.HexColor("#0d1b2a")
    C_AZUL_MED  = colors.HexColor("#1a2a3a")
    C_DOURADO   = colors.HexColor("#c9a84c")
    C_CREAM     = colors.HexColor("#f0e8d8")
    C_BG_CLARO  = colors.HexColor("#f4f2ef")
    C_PILL_BG   = colors.HexColor("#ece8df")
    C_PILL_TXT  = colors.HexColor("#6b5a3e")
    C_VERDE_BG  = colors.HexColor("#e8f4ec")
    C_VERDE_TXT = colors.HexColor("#2d6a4f")
    C_BORDA     = colors.HexColor("#d8d3cc")

    # 2. Definição de Estilos de Texto
    s_th = PS("TH5", fontName="Helvetica-Bold", fontSize=8, textColor=C_CREAM, leading=11)
    s_td = PS("TD5", fontName="Helvetica", fontSize=8.5, textColor=C_AZUL_MED, leading=12)
    s_td_bold = PS("TDB5", fontName="Helvetica-Bold", fontSize=8.5, textColor=C_AZUL, leading=12)

    # 3. Classe Badge com Auto-Ajuste (Para não invadir outras colunas)
    class Badge(Flowable):
        def __init__(self, text, bg=C_AZUL, fg=C_CREAM, width=None, height=20, radius=4, font="Helvetica-Bold", fontsize=7.5):
            super().__init__()
            self.text = text; self.bg = bg; self.fg = fg; self.max_w = width
            self.height = height; self.radius = radius; self.font = font; self.fontsize = fontsize

        def wrap(self, aW, aH):
            self.width = self.max_w if self.max_w else min(len(self.text) * self.fontsize * 0.62 + 14, aW)
            return self.width, self.height

        def draw(self):
            c = self.canv; c.saveState()
            curr_fs = self.fontsize
            tw = c.stringWidth(self.text, self.font, curr_fs)
            while tw > (self.width - 4) and curr_fs > 5:
                curr_fs -= 0.5
                tw = c.stringWidth(self.text, self.font, curr_fs)
            c.setFillColor(self.bg)
            c.roundRect(0, 0, self.width, self.height, self.radius, fill=1, stroke=0)
            c.setFillColor(self.fg); c.setFont(self.font, curr_fs)
            c.drawCentredString(self.width / 2, (self.height - curr_fs) / 2 + 1, self.text)
            c.restoreState()

    # 4. Helpers de Coluna
    HEADERS = ["AÇÃO","O QUÊ?","POR QUÊ?","ONDE?","QUEM?","QUANDO?","COMO?","QUANTO?"]
    col_ws = [TW*0.13, TW*0.15, TW*0.14, TW*0.09, TW*0.10, TW*0.08, TW*0.19, TW*0.12]

    def make_resp(texto):
        linhas_r = [l.strip() for l in texto.strip().split("\n") if l.strip()]
        if not linhas_r: return Paragraph("—", s_td)
        badge_w = col_ws[4] - 6 # Ajuste fino de margem
        badges = [[Badge(ln, width=badge_w)] for ln in linhas_r]
        t_resp = Table(badges, colWidths=[badge_w])
        t_resp.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
        return t_resp

    def make_prazo(texto):
        return Badge(texto or "—", bg=C_PILL_BG, fg=C_PILL_TXT, font="Helvetica-Bold", fontsize=8, height=19, radius=9, width=col_ws[5]-4)

    def make_custo(texto):
        if "sem" in (texto or "").lower():
            return Badge(texto, bg=C_VERDE_BG, fg=C_VERDE_TXT, font="Helvetica", fontsize=7.5, height=19, radius=9, width=col_ws[7]-4)
        return Paragraph(texto or "—", s_td)

    # 5. Execução da Tabela 5W2H
    linhas_5w = [r for r in F.get("w5h2", []) if any(r.get(k,"").strip() for k in ("what","why","who"))]
    
    if linhas_5w:
        story.append(Paragraph("5. Plano de Ação — 5W2H", s_sec))
        story.append(Spacer(1, .2*cm))

        table_data = [[Paragraph(h, s_th) for h in HEADERS]]
        for row in linhas_5w:
            acao_nm = row.get("acao","") or row.get("what","")[:30] or "—"
            table_data.append([
                Paragraph(f"<b>{acao_nm}</b>", s_td_bold),
                Paragraph(row.get("what", "—") or "—", s_td),
                Paragraph(row.get("why",  "—") or "—", s_td),
                Paragraph(row.get("where","—") or "—", s_td),
                make_resp(row.get("who",  "—") or "—"),
                make_prazo(row.get("when","—") or "—"),
                Paragraph(row.get("how",  "—") or "—", s_td),
                make_custo(row.get("howmuch","—") or "—"),
            ])

        tbl_5w = Table(table_data, colWidths=col_ws, repeatRows=1)
        tbl_5w.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), C_AZUL),
            ("LINEBELOW", (0, 0), (-1, 0), 1.5, C_DOURADO),
            ("GRID", (0, 0), (-1, -1), 0.4, C_BORDA),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (4, 1), (5, -1), "CENTER"),
            ("ALIGN", (7, 1), (7, -1), "CENTER"),
            *[("BACKGROUND", (0, r), (-1, r), C_BG_CLARO if r % 2 == 0 else colors.white) for r in range(1, len(table_data))],
        ]))
        story.append(tbl_5w)

    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=azul))
    story.append(Spacer(1, .3*cm))
    story.append(Paragraph(
        f"Documento gerado em {F['data']} · Sistema de Gestão de Reestruturação EUFT",
        s_foot))

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ── UPLOADER MÚLTIPLO POR SEÇÃO ───────────────────────────────
def uploader_imagens(secao: str, num: str):
    lista = F["imgs"].setdefault(secao, [])
    up = st.file_uploader(
        f"📎 Adicionar imagem(ns) — seção {num}",
        type=["png","jpg","jpeg"],
        accept_multiple_files=True,
        key=f"up_{secao}",
    )
    if up:
        existentes = {i["nome"] for i in lista}
        added = 0
        for f_up in up:
            if f_up.name not in existentes:
                lista.append({"bytes": f_up.read(), "nome": f_up.name})
                existentes.add(f_up.name)
                added += 1
        if added:
            st.rerun()

    if lista:
        st.caption(f"{len(lista)} imagem(ns) anexada(s) nesta seção")
        to_rm = []
        for idx, item in enumerate(lista):
            c1, c2, c3 = st.columns([1, 6, 1])
            c1.image(item["bytes"], width=72)
            c2.markdown(
                f"<div style='font-size:.8rem;color:#555;padding-top:.6rem;'>{item['nome']}</div>",
                unsafe_allow_html=True)
            c3.write("")
            if c3.button("✕", key=f"rm_{secao}_{idx}", help="Remover"):
                to_rm.append(idx)
        for i in reversed(to_rm):
            lista.pop(i)
        if to_rm:
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# TELA 1 — EDITOR
# ═══════════════════════════════════════════════════════════════
def tela_editor():
    st.markdown("""
    <div class="hero">
        <div class="hero-tag"> · Relatório de Reestruturação Logística</div>
        <div class="hero-h1">Editor do Plano Técnico</div>
        <div class="hero-sub">
            Preencha os campos e anexe imagens em cada seção.
            Clique em <strong style="color:#c9a84c">Gerar Relatório Técnico Final</strong> para abrir o Dashboard.
        </div>
        <div class="hero-badge">● Tela 1 de 2 — Formulário</div>
    </div>
    """, unsafe_allow_html=True)

    # 01 — Identificação
    st.markdown('<div class="slabel">01 — Identificação da Unidade</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    F["unidade"]     = c1.text_input("Unidade Operacional", value=F["unidade"],     key="f_uni")
    F["responsavel"] = c2.text_input("Responsável Técnico",  value=F["responsavel"], key="f_resp")
    F["data"]        = c3.text_input("Data",                 value=F["data"],        key="f_data")

    # 02 — Indicadores
    st.markdown('<div class="slabel">02 — Indicadores Operacionais</div>', unsafe_allow_html=True)
    k1,k2,k3,k4,k5 = st.columns(5)
    F["iep_atual"]  = k1.number_input("IEP Atual (%)",      0, 100,       value=int(F["iep_atual"]),  key="f_ia")
    F["iep_meta"]   = k2.number_input("IEP Meta (%)",       0, 100,       value=int(F["iep_meta"]),   key="f_im")
    F["residuo"]    = k3.number_input("Resíduo (objetos)",  0, 5_000_000, value=int(F["residuo"]),    step=1000, key="f_res")
    F["distritos"]  = k4.number_input("Distritos Críticos", 0, 100,       value=int(F["distritos"]),  key="f_dis")
    F["prazo"]      = k5.number_input("Prazo (dias)",        1, 365,       value=int(F["prazo"]),      key="f_prz")

    # 03–06 — Seções com texto + imagens
    CAMPOS = [
        ("03", "escopo",    "Diagnóstico de Infraestrutura (Escopo)",   150),
        ("04", "problemas", "Gargalos e Não-Conformidades (Problemas)", 200),
        ("05", "acoes",     "Plano de Otimização (Ações)",              220),
        ("06", "conclusao", "Conclusão e Projeção de Resultados",       130),
    ]
    for num, secao, titulo, h in CAMPOS:
        st.markdown(f'<div class="slabel">{num} — {titulo}</div>', unsafe_allow_html=True)
        F[secao] = st.text_area(
            "", value=F[secao], height=h, key=f"ta_{secao}",
            help="Separe parágrafos com linha em branco → recuo automático no PDF.")
        uploader_imagens(secao, num)
        st.markdown("<hr>", unsafe_allow_html=True)

    # ── 07 — 5W2H ───────────────────────────────────────────
    st.markdown('<div class="slabel">07 — Plano de Ação 5W2H</div>', unsafe_allow_html=True)
    st.caption("Cada linha é uma ação. Preencha os 7 campos. Use o botão ➕ para adicionar novas ações.")

    linhas = F.get("w5h2", [])

    # Cabeçalho visual da tabela — fundo branco, texto escuro, bem legível
    HEADERS_5W = [
        ("AÇÃO",      "Action",    "2"),
        ("O QUÊ?",    "What",      "3"),
        ("POR QUÊ?",  "Why",       "3"),
        ("ONDE?",     "Where",     "2"),
        ("QUEM?",     "Who",       "2"),
        ("QUANDO?",   "When",      "2"),
        ("COMO?",     "How",       "3"),
        ("QUANTO?",   "How Much",  "2"),
        ("",          "",          "1"),
    ]
    hdr_html = (
        '<div style="display:grid;grid-template-columns:2fr 3fr 3fr 2fr 2fr 2fr 3fr 2fr 1fr;'
        'gap:.5rem;background:#0d1b2a;border-radius:6px 6px 0 0;'
        'padding:.6rem 1rem;margin-bottom:.1rem;border-left:3px solid #c9a84c;">'
    )
    for pt, en, _ in HEADERS_5W:
        if pt:
            hdr_html += (
                '<div style="font-family:\'IBM Plex Mono\',monospace;">'
                '<span style="font-size:.75rem;font-weight:700;color:#f0e8d8;'
                'letter-spacing:.08em;text-transform:uppercase;display:block;">' + pt + '</span>'
                '<span style="font-size:.6rem;color:#c9a84c;letter-spacing:.06em;">' + en + '</span>'
                '</div>'
            )
        else:
            hdr_html += '<div></div>'
    hdr_html += '</div>'
    st.markdown(hdr_html, unsafe_allow_html=True)

    to_del = []
    for i, row in enumerate(linhas):
        cols = st.columns([2, 3, 3, 2, 2, 2, 3, 2, 1])
        row["acao"]    = cols[0].text_area("", value=row.get("acao",""),    height=80, key=f"w_acao_{i}",  label_visibility="collapsed")
        row["what"]    = cols[1].text_area("", value=row.get("what",""),    height=80, key=f"w_what_{i}",  label_visibility="collapsed")
        row["why"]     = cols[2].text_area("", value=row.get("why",""),     height=80, key=f"w_why_{i}",   label_visibility="collapsed")
        row["where"]   = cols[3].text_input("", value=row.get("where",""),             key=f"w_where_{i}", label_visibility="collapsed")
        row["who"]     = cols[4].text_input("", value=row.get("who",""),               key=f"w_who_{i}",   label_visibility="collapsed")
        row["when"]    = cols[5].text_input("", value=row.get("when",""),              key=f"w_when_{i}",  label_visibility="collapsed")
        row["how"]     = cols[6].text_area("", value=row.get("how",""),     height=80, key=f"w_how_{i}",   label_visibility="collapsed")
        row["howmuch"] = cols[7].text_input("", value=row.get("howmuch",""),           key=f"w_howm_{i}",  label_visibility="collapsed")
        cols[8].write("")
        cols[8].write("")
        if cols[8].button("🗑️", key=f"del_w_{i}", help="Remover ação"):
            to_del.append(i)

    for i in reversed(to_del):
        linhas.pop(i)
    if to_del:
        st.rerun()

    if st.button("➕  Adicionar ação ao 5W2H", key="add_w5h2"):
        linhas.append({"acao":"","what":"","why":"","where":"","who":"","when":"","how":"","howmuch":""})
        st.rerun()

    F["w5h2"] = linhas

    # Botão principal
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn = st.columns([3, 7])[0]
    with col_btn:
        if st.button("🚀  Gerar Relatório Técnico Final", key="btn_gerar"):
            st.session_state.tela = "dashboard"
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# TELA 2 — DASHBOARD EXECUTIVO
# ═══════════════════════════════════════════════════════════════
def tela_dashboard():
    ia    = int(F["iep_atual"])
    im    = int(F["iep_meta"])
    ganho = im - ia
    prazo = int(F["prazo"])

    # Hero
    st.markdown(f"""
    <div class="hero">
        <div class="hero-tag">EUFT · Dashboard Executivo de Reestruturação</div>
        <div class="hero-h1">{F['unidade']}</div>
        <div class="hero-sub">
            Responsável: {F['responsavel']} &nbsp;·&nbsp; Data: {F['data']}
            &nbsp;·&nbsp; Projeção:
            <strong style="color:#c9a84c">+{ganho}pp de IEP</strong> em {prazo} dias
        </div>
        <div class="hero-badge">● Tela 2 de 2 — Dashboard Executivo</div>
    </div>
    """, unsafe_allow_html=True)

    col_v, col_dl, _ = st.columns([2, 3, 7])
    with col_v:
        if st.button("← Voltar ao Editor", key="btn_voltar"):
            st.session_state.tela = "editor"
            st.rerun()
    with col_dl:
        pdf_bytes = gerar_pdf()
        nome_pdf  = f"relatorio_{F['unidade'].replace(' ','_')}_{datetime.date.today()}.pdf"
        st.download_button(
            "⬇️  Baixar Relatório PDF",
            data=pdf_bytes, file_name=nome_pdf,
            mime="application/pdf", key="dl_top",
        )

    st.divider()

    # ── KPIs ─────────────────────────────────────────────────
    st.markdown('<div class="slabel">Indicadores Operacionais</div>', unsafe_allow_html=True)
    c1,c2,c3,c4,c5 = st.columns(5)
    c1.metric("IEP Atual",            f"{ia}%",                f"−{100-ia}pp do ótimo")
    c2.metric("IEP Meta Pós-SD",      f"{im}%",                f"+{ganho}pp projetado")
    c3.metric("Resíduo Identificado", f"{int(F['residuo']):,}", "objetos pendentes")
    c4.metric("Distritos Críticos",   str(F["distritos"]),      "em reestruturação")
    c5.metric("Prazo de Execução",    f"{prazo} dias",          "meta operacional")

    st.divider()

    # ── GRÁFICOS LINHA 1: Gauge | Barras | Progresso ──────────
    st.markdown('<div class="slabel">Análise Visual de Impacto</div>', unsafe_allow_html=True)
    g1, g2, g3 = st.columns([2, 2, 3])

    # Gauge
    with g1:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=ia,
            delta={"reference": im, "valueformat": ".0f", "prefix": "Meta: "},
            title={"text":"IEP Atual vs Meta","font":{"size":14,"color":"#0d1b2a"}},
            gauge={
                "axis":    {"range":[0,100]},
                "bar":     {"color":"#0d1b2a"},
                "bgcolor": "white",
                "steps":   [
                    {"range":[0, 70],"color":"rgba(220,70,70,.18)"},
                    {"range":[70,90],"color":"rgba(201,168,76,.18)"},
                    {"range":[90,100],"color":"rgba(60,200,180,.18)"},
                ],
                "threshold":{"line":{"color":"#c9a84c","width":4},"thickness":.8,"value":im},
            },
            number={"suffix":"%","font":{"size":40,"color":"#0d1b2a"}},
        ))
        fig_g.update_layout(height=270, margin=dict(t=40,b=0,l=30,r=30),
            paper_bgcolor="rgba(0,0,0,0)", font={"family":"IBM Plex Sans"})
        st.plotly_chart(fig_g, use_container_width=True)

    # Barras antes/depois
    with g2:
        df_b = pd.DataFrame({
            "Cenário": ["Antes da\nReestruturação", f"Meta Pós-SD\n({prazo} dias)"],
            "IEP":     [ia, im],
            "Cor":     ["Antes","Depois"],
        })
        fig_b = px.bar(df_b, x="Cenário", y="IEP", color="Cor", text="IEP",
            color_discrete_map={"Antes":"#e05555","Depois":"#3dc8b0"},
            labels={"IEP":"IEP (%)"})
        fig_b.update_traces(texttemplate="%{text}%", textposition="outside", marker_line_width=0)
        fig_b.update_layout(height=270, showlegend=False,
            margin=dict(t=30,b=0,l=10,r=10),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font={"family":"IBM Plex Sans","color":"#0d1b2a"},
            yaxis=dict(range=[0,115], gridcolor="#eee", zeroline=False, title="IEP (%)"),
            xaxis=dict(gridcolor="rgba(0,0,0,0)"),
            title={"text":"Capacidade de Entrega","font":{"size":13}})
        st.plotly_chart(fig_b, use_container_width=True)

    # Progresso por ação (HTML puro, sem f-string para evitar render de código)
    with g3:
        acoes_prog = [
            ("Triagem Objetos Urgentes", 85, "#3dc8b0"),
            ("Implantação SDD",          40, "#e05555"),
            ("Redistribuição Distritos", 60, "#c9a84c"),
            ("Monitoramento IEP Diário", 90, "#3dc8b0"),
            ("Capacitação de Líderes",   30, "#e05555"),
        ]
        rows_html = ""
        for nome_a, pct, cor in acoes_prog:
            rows_html += (
                '<div class="prog-row">'
                '<span class="prog-label">' + nome_a + '</span>'
                '<div class="prog-bar-bg">'
                '<div class="prog-bar-fill" style="width:' + str(pct) + '%;background:' + cor + ';"></div>'
                '</div>'
                '<span class="prog-pct">' + str(pct) + '%</span>'
                '</div>'
            )
        st.markdown(
            '<div style="background:#fff;border-radius:8px;padding:1.2rem 1.5rem;'
            'border:1px solid #ddd;box-shadow:0 2px 12px rgba(0,0,0,.06);height:100%;">'
            '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:.65rem;'
            'letter-spacing:.15em;text-transform:uppercase;color:#0d1b2a;margin-bottom:1rem;">'
            'Progresso por Ação Estratégica'
            '</div>'
            + rows_html +
            '</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # ── CURVA DE EVOLUÇÃO ─────────────────────────────────────
    st.markdown('<div class="slabel">Curva de Evolução Projetada do IEP</div>', unsafe_allow_html=True)

    pts = sorted(set(list(range(0, prazo+1, max(1, prazo//40))) + [prazo]))
    def sig(t): return ia + (im-ia)/(1+math.exp(-(t/prazo-.5)*10))
    df_l = pd.DataFrame({"Dia": pts, "IEP (%)": [sig(t) for t in pts]})

    fig_l = px.area(df_l, x="Dia", y="IEP (%)")
    fig_l.update_traces(
        line=dict(color="#0d1b2a", width=2.5),
        fillcolor="rgba(13,27,42,.07)")
    fig_l.add_hline(y=im, line_dash="dash", line_color="#3dc8b0",
        annotation_text="Meta " + str(im) + "%", annotation_position="top right")
    fig_l.add_hline(y=90, line_dash="dot", line_color="#c9a84c",
        annotation_text="Limite 90%")
    fig_l.add_scatter(x=[prazo], y=[sig(prazo)], mode="markers",
        marker=dict(color="#c9a84c",size=12,line=dict(color="#0d1b2a",width=2)),
        showlegend=False)
    fig_l.update_layout(height=300, showlegend=False,
        margin=dict(t=20,b=20,l=10,r=20),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family":"IBM Plex Sans","color":"#0d1b2a"},
        yaxis=dict(range=[ia-5,im+5], gridcolor="#eee", zeroline=False, title="IEP (%)"),
        xaxis=dict(title="Dias desde o início", gridcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_l, use_container_width=True)

    st.divider()

    # ── 5W2H ─────────────────────────────────────────────────
    linhas_5w = F.get("w5h2", [])
    preenchidas = [r for r in linhas_5w if any(r.get(k,"").strip() for k in ("what","why","where","who","when","how","howmuch"))]

    st.markdown('<div class="slabel">Plano de Ação — 5W2H</div>', unsafe_allow_html=True)

    if not preenchidas:
        st.info("Nenhuma ação cadastrada no 5W2H. Volte ao Editor e preencha a seção 07.")
    else:
        COLS_5W = [
            ("O QUÊ?",   "what"),
            ("POR QUÊ?", "why"),
            ("ONDE?",    "where"),
            ("QUEM?",    "who"),
            ("QUANDO?",  "when"),
            ("COMO?",    "how"),
            ("QUANTO?",  "howmuch"),
        ]

        # Monta thead
        th_cells = '<th style="border-left:3px solid #c9a84c">AÇÃO</th>'
        for label, _ in COLS_5W:
            th_cells += "<th>" + label + "</th>"
        thead = "<thead><tr>" + th_cells + "</tr></thead>"

        # Monta tbody
        tbody_rows = ""
        for i, row in enumerate(preenchidas):
            # nome da ação = what ou fallback
            acao_nome = row.get("acao", "") or row.get("what", f"Ação {i+1}")[:40]
            row_html = (
                '<td style="border-left:3px solid #c9a84c;font-weight:700;">'
                + acao_nome + "</td>"
            )
            for _, key in COLS_5W:
                val = row.get(key, "") or "—"
                # destaque para who e when
                if key == "who":
                    val = '<span class="pill">' + val + "</span>"
                elif key == "when":
                    val = '<span class="pillg">' + val + "</span>"
                elif key == "howmuch":
                    val = '<span class="pillg">' + val + "</span>"
                row_html += "<td>" + val + "</td>"
            tbody_rows += "<tr>" + row_html + "</tr>"

        table_html = (
            '<div class="w5h2-wrap">'
            '<table class="w5h2-table">'
            + thead
            + "<tbody>" + tbody_rows + "</tbody>"
            + "</table></div>"
        )
        st.markdown(table_html, unsafe_allow_html=True)

    st.divider()

    # ── RESUMO TEXTUAL DAS SEÇÕES ────────────────────────────
    st.markdown('<div class="slabel">Resumo do Plano Técnico</div>', unsafe_allow_html=True)

    LABELS = {
        "escopo":    ("📋", "Diagnóstico de Infraestrutura"),
        "problemas": ("⚠️", "Gargalos Identificados"),
        "acoes":     ("✅", "Ações Estratégicas"),
        "conclusao": ("🎯", "Conclusão e Projeção"),
    }
    for secao, (icone, titulo_s) in LABELS.items():
        n_imgs = len(F["imgs"].get(secao, []))
        with st.expander(icone + "  " + titulo_s +
                         (f"  ·  {n_imgs} imagem(ns)" if n_imgs else ""), expanded=False):
            st.markdown(F[secao].replace("\n\n", "\n\n"))
            if n_imgs:
                cols = st.columns(min(n_imgs, 3))
                for idx, item in enumerate(F["imgs"][secao]):
                    cols[idx % 3].image(item["bytes"],
                        caption=item["nome"], use_column_width=True)

    st.divider()

    # ── DOWNLOAD FINAL ────────────────────────────────────────
    st.markdown('<div class="slabel">Exportar Relatório</div>', unsafe_allow_html=True)
    col_dl2, col_info, _ = st.columns([2, 4, 6])
    with col_dl2:
        st.download_button(
            "⬇️  Baixar Relatório PDF",
            data=pdf_bytes, file_name=nome_pdf,
            mime="application/pdf", key="dl_bottom",
        )
    with col_info:
        total_imgs = sum(len(v) for v in F["imgs"].values())
        st.markdown(
            '<div class="info-box">📄 O PDF inclui o relatório completo formatado com recuo nos '
            'parágrafos, cabeçalhos por seção'
            + (f' e {total_imgs} imagem(ns) inserida(s).' if total_imgs else '.')
            + '</div>',
            unsafe_allow_html=True)


# ── ROTEADOR ─────────────────────────────────────────────────
if st.session_state.tela == "editor":
    tela_editor()
else:
    tela_dashboard()
