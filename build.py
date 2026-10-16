#!/usr/bin/env python3
"""Gera o site Pão Diário em Família a partir de mensagens.json e da pasta conteudo/.

Uso: python3 build.py
Gera: index.html, mensagens/, livros/, links/, sobre/, 404.html, sitemap.xml, robots.txt, feed.xml
e uma imagem de compartilhamento (og.png) para cada mensagem.
Para trocar de endereço (domínio próprio), edite apenas conteudo/site.json.
"""
import json, os, html, shutil, datetime
from zoneinfo import ZoneInfo
from email.utils import format_datetime

RAIZ = os.path.dirname(os.path.abspath(__file__))
def ler(p):
    with open(os.path.join(RAIZ, p), encoding="utf-8") as f: return json.load(f)
def gravar(p, txt):
    p = os.path.join(RAIZ, p); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(txt)

SITE = ler("conteudo/site.json")
URL, BASE, NOME = SITE["url"].rstrip("/"), SITE["base"].rstrip("/"), SITE["nome"]
FUSO = ZoneInfo(SITE.get("fuso", "America/Sao_Paulo"))
HOJE = datetime.datetime.now(FUSO).date().isoformat()
e = lambda s: html.escape(str(s or ""), quote=True)
ASSET_V = str(int(os.path.getmtime(os.path.join(RAIZ, "assets/style.css")))) if os.path.exists(os.path.join(RAIZ, "assets/style.css")) else "1"

MESES = ["janeiro","fevereiro","março","abril","maio","junho","julho","agosto","setembro","outubro","novembro","dezembro"]
MESES_C = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
DIAS = ["segunda-feira","terça-feira","quarta-feira","quinta-feira","sexta-feira","sábado","domingo"]
def d(s): return datetime.date.fromisoformat(s)
def data_longa(s): x = d(s); return f"{DIAS[x.weekday()].capitalize()}, {x.day} de {MESES[x.month-1]} de {x.year}"
def data_curta(s): x = d(s); return f"{x.day:02d} {MESES_C[x.month-1]} {x.year}"

msgs = sorted([m for m in ler("mensagens.json") if m.get("data") and m["data"] <= HOJE], key=lambda m: m["data"], reverse=True)
destaques, livros, links = ler("conteudo/destaques.json"), ler("conteudo/livros.json"), ler("conteudo/links.json")

def p(path=""): return f"{BASE}/{path}"
def abs_(path=""): return f"{URL}/{path}"
def msg_path(m): return f"mensagens/{m['data']}/"

ICONE = '<svg viewBox="0 0 32 32" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><path d="M4 22h24" stroke-linecap="round"/><path d="M9 22a7 7 0 0 1 14 0"/><path d="M16 8v3M8.2 11.2l2 2M23.8 11.2l-2 2M5 16.5h2.5M27 16.5h-2.5" stroke-linecap="round"/></svg>'
MENU = [("", "Início"), ("mensagens/", "Mensagens"), ("livros/", "Livros"), ("links/", "Links úteis"), ("sobre/", "Sobre")]

def layout(path, titulo, descricao, corpo, *, atual="", og_tipo="website", og_img=None, jsonld=None, faixa="", folha=True):
    titulo_full = NOME if titulo == NOME else f"{titulo} · {NOME}"
    og_img = og_img or abs_("assets/og.png")
    nav = "".join(f'<li><a href="{p(h)}"{" aria-current=\"page\"" if h == atual else ""}>{e(t)}</a></li>' for h, t in MENU)
    foot = "".join(f'<a href="{p(h)}">{e(t)}</a>' for h, t in MENU[1:])
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(titulo_full)}</title>
<meta name="description" content="{e(descricao)}">
<link rel="canonical" href="{abs_(path)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:site_name" content="{e(NOME)}">
<meta property="og:locale" content="pt_BR">
<meta property="og:type" content="{og_tipo}">
<meta property="og:title" content="{e(titulo)}">
<meta property="og:description" content="{e(descricao)}">
<meta property="og:url" content="{abs_(path)}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#eef1f4" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#141a23" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{p('assets/icone.svg')}" type="image/svg+xml">
<link rel="alternate" type="application/rss+xml" title="{e(NOME)}" href="{abs_('feed.xml')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,500;0,600;1,500&family=Nunito+Sans:opsz,wght@6..12,400;6..12,600;6..12,700&display=swap">
<link rel="stylesheet" href="{p('assets/style.css')}?v={ASSET_V}">
{ld}
</head>
<body>
<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<header class="topbar gutter">
  <div class="topbar-inner">
    <a class="brand" href="{p()}">{ICONE}<span>{e(NOME)}</span></a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="menu">Menu</button>
    <nav class="nav" id="menu" aria-label="Principal"><ul>{nav}</ul></nav>
  </div>
</header>
{faixa}
<main id="conteudo" class="gutter"><div class="col{' sheet' if folha else ''}">
{corpo}
</div></main>
<footer class="site gutter"><div class="col">
  <span>Leituras conforme a Liturgia Diária da Igreja no Brasil; demais textos bíblicos segundo a Bíblia Ave&#8209;Maria.</span>
  <nav aria-label="Rodapé">{foot}<a href="{p('feed.xml')}">RSS</a></nav>
</div></footer>
<script src="{p('assets/site.js')}?v={ASSET_V}" defer></script>
</body>
</html>
"""

def share_text(m):
    return f"{m['titulo']}\n\n“{m['versiculo']}” ({m['referencia']})\n\n{abs_(msg_path(m))}"

CORES_LIT = {"verde": "#3f7d4e", "roxo": "#6b3f8f", "branco": "#d9d2c3", "vermelho": "#b3322e", "rosa": "#d98aa6", "preto": "#2a2a2a", "dourado": "#c9a13a"}
def liturgia_html(m):
    if not m.get("liturgia"): return ""
    cor = str(m.get("cor", "")).strip().lower()
    dot = f'<span class="lit-dot" style="background:{CORES_LIT[cor]}" title="Cor litúrgica: {e(cor)}"></span>' if cor in CORES_LIT else ""
    return f'<span class="liturgia">{dot}{e(m["liturgia"])}</span>'

def bloco_dia(m, *, titulo_link=True, h="h2"):
    tag = "Hoje" if m["data"] == HOJE else (m.get("tema") or "Mensagem")
    t = f'<a href="{p(msg_path(m))}">{e(m["titulo"])}</a>' if titulo_link else e(m["titulo"])
    refl = "".join(f"<p>{e(x.strip())}</p>" for x in str(m.get("reflexao","")).split("\n\n") if x.strip())
    perg = f'<div class="pergunta"><p class="label">Para conversar em família</p><p>{e(m["pergunta"])}</p></div>' if m.get("pergunta") else ""
    orac = f'<div class="oracao"><p class="label">Oração</p><p>{e(m["oracao"])}</p></div>' if m.get("oracao") else ""
    wa = "https://wa.me/?text=" + __import__("urllib.parse").parse.quote(share_text(m))
    return f"""<article class="day">
  <div class="day-head"><div class="day-when"><time class="date" datetime="{m['data']}">{data_longa(m['data'])}</time>{liturgia_html(m)}</div><span class="tag">{e(tag)}</span></div>
  <{h} class="day-title">{t}</{h}>
  <blockquote>“{e(m['versiculo'])}”<cite>{e(m['referencia'])}{(' · ' + e(m['fonte'])) if m.get('fonte') else ''}</cite></blockquote>
  <div class="reflexao"><p class="label">Reflexão</p>{refl}</div>
  {perg}
  {orac}
  <div class="actions"><a class="btn" href="{e(wa)}" target="_blank" rel="noopener">Enviar pelo WhatsApp</a><button class="btn" type="button" data-copy="{e(share_text(m))}">Copiar mensagem</button></div>
</article>"""

def lista(ms):
    if not ms: return ""
    itens = "".join(f'<li><a href="{p(msg_path(m))}"><span class="d">{data_curta(m["data"])}</span><span class="t">{e(m["titulo"])}<span class="r">{e(m["referencia"])}</span></span></a></li>' for m in ms)
    return f'<ul class="list">{itens}</ul>'

def faixa_slides():
    sl = "".join(f'<figure class="slide{" on" if i == 0 else ""}"><p>“{e(x["texto"])}”</p><cite>{e(x["referencia"])}</cite></figure>' for i, x in enumerate(destaques))
    return f"""<section class="band gutter" aria-roledescription="carrossel" aria-label="Passagens bíblicas" data-slides>
  <div class="slides">
    <span class="eyebrow">Palavras para guardar no coração</span>
    <div class="slide-track">{sl}</div>
    <div class="slide-ctrl">
      <button class="arrow" type="button" data-prev aria-label="Passagem anterior"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 3 5 8l5 5"/></svg></button>
      <div class="dots"></div>
      <button class="arrow" type="button" data-next aria-label="Próxima passagem"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2"><path d="m6 3 5 5-5 5"/></svg></button>
    </div>
    <p class="sr-only" aria-live="polite"></p>
  </div>
</section>"""

ORG = {"@type": "Organization", "name": NOME, "url": abs_()}
def ld_site():
    return {"@context": "https://schema.org", "@type": "WebSite", "name": NOME, "url": abs_(), "inLanguage": "pt-BR", "description": SITE["descricao"]}
def ld_artigo(m):
    return {"@context": "https://schema.org", "@type": "Article", "headline": m["titulo"], "description": desc_msg(m),
            "datePublished": f"{m['data']}T06:00:00-03:00", "dateModified": f"{m['data']}T06:00:00-03:00", "inLanguage": "pt-BR",
            "mainEntityOfPage": abs_(msg_path(m)), "image": abs_(msg_path(m) + "og.png"), "author": ORG, "publisher": ORG,
            "about": m.get("tema"), "citation": m["referencia"]}
def ld_trilha(itens):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": abs_(u)} for i, (n, u) in enumerate(itens)]}
def desc_msg(m):
    t = f"{m['referencia']}: {m['versiculo']}"
    return t if len(t) <= 155 else t[:152].rsplit(" ", 1)[0] + "…"

# ---------- imagens de compartilhamento ----------
def og_image(dest, titulo, verso, ref):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return False
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), "#1f2a3a"); dr = ImageDraw.Draw(img)
    F = "/usr/share/fonts/truetype/dejavu/"
    def font(n, s):
        try: return ImageFont.truetype(F + n, s)
        except Exception: return ImageFont.load_default()
    # nascer do sol
    cx, cy = 1040, 590
    dr.ellipse((cx - 150, cy - 150, cx + 150, cy + 150), outline="#b4742a", width=6)
    dr.rectangle((0, cy, W, H), fill="#1f2a3a"); dr.line((0, cy, W, cy), fill="#b4742a", width=6)
    for a, b in [((cx, cy - 210), (cx, cy - 175)), ((cx - 150, cy - 150), (cx - 128, cy - 128)), ((cx + 150, cy - 150), (cx + 128, cy - 128))]:
        dr.line((a, b), fill="#b4742a", width=6)
    dr.text((80, 70), NOME.upper(), font=font("DejaVuSans-Bold.ttf", 26), fill="#e0a35a")
    def wrap(txt, f, maxw):
        linhas, cur = [], ""
        for w in txt.split():
            t = (cur + " " + w).strip()
            if dr.textlength(t, font=f) <= maxw: cur = t
            else: linhas.append(cur); cur = w
        if cur: linhas.append(cur)
        return linhas
    y = 130
    if titulo:
        ft = font("DejaVuSerif-Bold.ttf", 54)
        for l in wrap(titulo, ft, 900)[:2]: dr.text((80, y), l, font=ft, fill="#f4efe6"); y += 66
        y += 18
    size = 34
    while size > 22:
        fv = font("DejaVuSerif-Italic.ttf", size); ls = wrap(f"“{verso}”", fv, 860)
        if y + len(ls) * size * 1.35 < 480: break
        size -= 2
    if len(ls) * size * 1.35 + y >= 480:
        ls = ls[: int((480 - y) // (size * 1.35))]; ls[-1] = ls[-1].rstrip(".,;:”") + "…"
    for l in ls: dr.text((80, y), l, font=fv, fill="#e6e1d7"); y += int(size * 1.35)
    dr.text((80, 512), ref, font=font("DejaVuSans-Bold.ttf", 26), fill="#b9c1cc")
    os.makedirs(os.path.dirname(dest), exist_ok=True); img.save(dest, optimize=True)
    return True

# ---------- páginas ----------
def limpar_gerados():
    pasta = os.path.join(RAIZ, "mensagens")
    if os.path.isdir(pasta): shutil.rmtree(pasta)

def main():
    limpar_gerados()
    og_image(os.path.join(RAIZ, "assets/og.png"), NOME, destaques[0]["texto"], destaques[0]["referencia"])

    # Início
    if msgs:
        hoje = msgs[0]
        corpo = f"""<div class="page-head"><span class="eyebrow">{'Mensagem de hoje' if hoje['data'] == HOJE else 'Mensagem mais recente'}</span><h1 class="sr-only">{e(NOME)}: mensagem bíblica diária para ler em família</h1></div>
{bloco_dia(hoje, h='h2')}
<section><h2 class="sec">Mensagens anteriores</h2>{lista(msgs[1:8]) or '<p class="note">As próximas mensagens aparecem aqui todos os dias às 6h.</p>'}<a class="more" href="{p('mensagens/')}">Ver todas as mensagens</a></section>"""
    else:
        corpo = '<div class="page-head"><h1>A primeira mensagem chega amanhã às 6h</h1></div>'
    gravar("index.html", layout("", NOME, SITE["descricao"], corpo, atual="", jsonld=[ld_site()], faixa=faixa_slides(), folha=False))

    # Uma página por mensagem
    for i, m in enumerate(msgs):
        mais_nova = msgs[i - 1] if i > 0 else None
        mais_antiga = msgs[i + 1] if i + 1 < len(msgs) else None
        pager = '<nav class="pager" aria-label="Outras mensagens">'
        if mais_antiga: pager += f'<a href="{p(msg_path(mais_antiga))}" rel="prev"><small>Anterior</small><span>{e(mais_antiga["titulo"])}</span></a>'
        if mais_nova: pager += f'<a href="{p(msg_path(mais_nova))}" rel="next"><small>Próxima</small><span>{e(mais_nova["titulo"])}</span></a>'
        pager += "</nav>"
        corpo = f"""<div class="page-head"><a class="eyebrow" href="{p('mensagens/')}" style="text-decoration:none">Mensagens</a></div>
{bloco_dia(m, titulo_link=False, h='h1')}
{pager}"""
        tem_og = og_image(os.path.join(RAIZ, msg_path(m), "og.png"), m["titulo"], m["versiculo"], m["referencia"])
        gravar(msg_path(m) + "index.html", layout(msg_path(m), f"{m['titulo']} ({m['referencia']})", desc_msg(m), corpo,
               atual="mensagens/", og_tipo="article", og_img=abs_(msg_path(m) + "og.png") if tem_og else None, folha=False,
               jsonld=[ld_artigo(m), ld_trilha([("Início", ""), ("Mensagens", "mensagens/"), (m["titulo"], msg_path(m))])]))

    # Arquivo
    corpo = f"""<div class="page-head"><span class="eyebrow">Arquivo</span><h1>Todas as mensagens</h1><p class="lead">Cada dia, uma passagem da Bíblia com reflexão e oração para a família. Toque em uma mensagem para ler.</p></div>
{lista(msgs) or '<p class="note">A primeira mensagem chega amanhã às 6h.</p>'}"""
    gravar("mensagens/index.html", layout("mensagens/", "Todas as mensagens", "Arquivo completo das mensagens bíblicas diárias para ler em família, com versículo, reflexão e oração.", corpo, atual="mensagens/",
           jsonld=[ld_trilha([("Início", ""), ("Mensagens", "mensagens/")])]))

    # Livros
    grupos = ""
    n = 0
    for gi, g in enumerate(livros):
        cards = ""
        for b in g["itens"]:
            cards += f'<article class="book"><div class="book-txt"><h3>{e(b["titulo"])}</h3><span class="by">{e(b["autor"])}</span><p>{e(b["nota"])}</p></div></article>'
            n += 1
        grupos += f'<section class="group"><h2 class="sec">{e(g["grupo"])}</h2><div class="books">{cards}</div></section>'
    corpo = f"""<div class="page-head"><span class="eyebrow">Leitura recomendada</span><h1>Livros para crescer na fé</h1><p class="lead">Obras de referência e clássicos cristãos para ler sozinho, a dois ou em família. Indicações sem patrocínio.</p></div>
{grupos}"""
    livros_ld = {"@context": "https://schema.org", "@type": "ItemList", "name": "Livros cristãos recomendados", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "item": {"@type": "Book", "name": b["titulo"], "author": {"@type": "Person", "name": b["autor"]}}}
        for i, b in enumerate(b for g in livros for b in g["itens"])]}
    gravar("livros/index.html", layout("livros/", "Livros cristãos recomendados", "Indicações de livros cristãos de referência: clássicos da fé, teologia, família, casamento e leituras para crianças.", corpo, atual="livros/", jsonld=[livros_ld]))

    # Links
    grupos = ""
    from urllib.parse import urlparse
    for g in links:
        itens = "".join(f'<a class="link" href="{e(l["url"])}" target="_blank" rel="noopener"><span class="host">{e(urlparse(l["url"]).netloc.replace("www.",""))}</span><strong>{e(l["nome"])}</strong><p>{e(l["nota"])}</p></a>' for l in g["itens"])
        grupos += f'<section class="group"><h2 class="sec">{e(g["grupo"])}</h2><div class="links">{itens}</div></section>'
    corpo = f"""<div class="page-head"><span class="eyebrow">Para ir além</span><h1>Links úteis</h1><p class="lead">Sites e aplicativos confiáveis para ler, ouvir e estudar a Bíblia. Os links abrem em uma nova aba.</p></div>
{grupos}"""
    gravar("links/index.html", layout("links/", "Links úteis para ler e estudar a Bíblia", "Sites e aplicativos confiáveis para ler, ouvir e estudar a Bíblia em português.", corpo, atual="links/"))

    # Sobre
    corpo = f"""<div class="page-head"><span class="eyebrow">Sobre</span><h1>Sobre o {e(NOME)}</h1></div>
<div class="prose">
<p>O {e(NOME)} publica, todos os dias às 6h (horário de Brasília), uma mensagem curta para ser lida em família: um versículo da Bíblia, uma reflexão simples, uma pergunta para conversar juntos e uma oração.</p>
<p>A ideia é ajudar pais, filhos, avós e netos a começar o dia com a Palavra de Deus, à mesa do café ou a caminho da escola. As mensagens podem ser enviadas pelo WhatsApp com um toque.</p>
<p>É um projeto católico. O versículo de cada dia é tirado das leituras da missa daquele dia, conforme a Liturgia Diária da Igreja no Brasil; os demais textos bíblicos seguem a Bíblia Ave-Maria. As reflexões e orações são preparadas com a ajuda de inteligência artificial, em sintonia com o ensinamento da Igreja, e revisadas pelo responsável pelo site.</p>
<p>Para receber as mensagens num leitor de notícias, use o <a href="{p('feed.xml')}">feed RSS</a>.</p>
</div>"""
    gravar("sobre/index.html", layout("sobre/", "Sobre", "Conheça o Pão Diário em Família: mensagens bíblicas diárias com versículo, reflexão, pergunta e oração para a família.", corpo, atual="sobre/"))

    # 404
    corpo = f'<div class="page-head"><span class="eyebrow">Página não encontrada</span><h1>Esta página não existe</h1><p class="lead">O endereço pode ter mudado. <a href="{p()}">Volte para a mensagem de hoje</a> ou veja <a href="{p("mensagens/")}">todas as mensagens</a>.</p></div>'
    gravar("404.html", layout("404.html", "Página não encontrada", "Página não encontrada.", corpo).replace('<meta name="robots" content="index,follow,max-image-preview:large">', '<meta name="robots" content="noindex">'))

    # sitemap, robots, feed
    ult = msgs[0]["data"] if msgs else HOJE
    urls = [("", ult, "daily", "1.0"), ("mensagens/", ult, "daily", "0.8"), ("livros/", None, "monthly", "0.6"), ("links/", None, "monthly", "0.5"), ("sobre/", None, "yearly", "0.4")]
    urls += [(msg_path(m), m["data"], "yearly", "0.7") for m in msgs]
    sm = "".join(f"<url><loc>{abs_(u)}</loc>{f'<lastmod>{lm}</lastmod>' if lm else ''}<changefreq>{cf}</changefreq><priority>{pr}</priority></url>" for u, lm, cf, pr in urls)
    gravar("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>\n')
    gravar("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {abs_('sitemap.xml')}\n")
    def rfc(dt): return format_datetime(datetime.datetime.fromisoformat(dt + "T06:00:00").replace(tzinfo=FUSO))
    itens = "".join(f"<item><title>{e(m['titulo'])} ({e(m['referencia'])})</title><link>{abs_(msg_path(m))}</link><guid>{abs_(msg_path(m))}</guid><pubDate>{rfc(m['data'])}</pubDate><description>{e(chr(8220) + m['versiculo'] + chr(8221) + ' ' + m['referencia'] + ' — ' + str(m.get('reflexao','')).split(chr(10))[0])}</description></item>" for m in msgs[:30])
    gravar("feed.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>{e(NOME)}</title><link>{abs_()}</link><atom:link href="{abs_("feed.xml")}" rel="self" type="application/rss+xml"/><description>{e(SITE["descricao"])}</description><language>pt-br</language>{itens}</channel></rss>\n')

    print(f"Site gerado: {len(msgs)} mensagem(ns) publicada(s), hoje = {HOJE}.")

if __name__ == "__main__":
    main()
