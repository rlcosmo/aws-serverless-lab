"""Build native SVG/PNG/PDF publication artifacts from sanitized evidence.

Uses existing system librsvg/cairo through ctypes. No package/tool installation,
AI-created screenshots or external rendering service is used.
"""

from __future__ import annotations

import argparse
import base64
import ctypes as C
import ctypes.util
import html
import json
import struct
import textwrap
from pathlib import Path

NAVY = "#081525"
CARD = "#10243b"
CYAN = "#39d5e8"
ORANGE = "#ff9b35"
WHITE = "#f4f8ff"
MUTED = "#a6bbd0"
GRAY = "#6d849c"
BLUE = "#488cff"
ROOT = Path(__file__).resolve().parents[1] / "docs/linkedin-showcase"


def esc(value):
    return html.escape(str(value), quote=True)


def text(x, y, value, size=28, color=WHITE, weight=400):
    return f'<text x="{x}" y="{y}" font-family="DejaVu Sans,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{esc(value)}</text>'


def wrap(x, y, value, width=50, size=25, color=MUTED, line=38):
    return "".join(
        text(x, y + i * line, s, size, color)
        for i, s in enumerate(textwrap.wrap(value, width))
    )


def rect(x, y, w, h, fill=CARD, stroke=None, dash=False, r=20):
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'
        + (
            f' stroke="{stroke}" stroke-width="2"'
            + (' stroke-dasharray="9 7"' if dash else "")
            if stroke
            else ""
        )
        + "/>"
    )


def line(x1, y1, x2, y2, color=CYAN, dash=False):
    return (
        f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="3"'
        + (' stroke-dasharray="10 8"' if dash else "")
        + ' marker-end="url(#arrow)"/>'
    )


def chip(x, y, label, color=CYAN):
    w = max(100, len(label) * 11 + 30)
    return rect(x, y, w, 32, NAVY, color, r=10) + text(
        x + 13, y + 23, label, 15, color, 700
    )


def icon(x, y, name, size=58):
    p = ROOT / "assets/aws" / (name + ".svg")
    if not p.exists():
        return ""
    data = base64.b64encode(p.read_bytes()).decode()
    return f'<image x="{x}" y="{y}" width="{size}" height="{size}" href="data:image/svg+xml;base64,{data}"/>'


def start(w, h, kicker, title, subtitle="", page=None):
    body = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 1L9 5L0 9" fill="none" stroke="{CYAN}" stroke-width="1.5"/></marker></defs>
<rect width="{w}" height="{h}" fill="{NAVY}"/>
<path d="M{w - 350} 0H{w}V350" fill="none" stroke="{CARD}" stroke-width="120"/>
<rect x="0" y="0" width="{w}" height="8" fill="{ORANGE}"/>
'''
    body += text(55, 62, "COSMOTECH", 25, WHITE, 700) + text(
        55, 85, "SOLUTIONS", 13, CYAN, 700
    )
    body += text(55, 144, kicker.upper(), 17, ORANGE, 700) + text(
        55, 205, title, 46 if w == 1080 else 48, WHITE, 700
    )
    if subtitle:
        body += wrap(55, 246, subtitle, 72 if w == 1080 else 100, 21, MUTED, line=31)
    body += f'<path d="M55 {h - 66}H{w - 55}" stroke="{CARD}" stroke-width="2"/>'
    body += text(55, h - 31, "LABORATÓRIO PESSOAL  /  AWS • SRE • GITOPS", 15, MUTED)
    if page:
        body += text(w - 95, h - 31, page, 18, CYAN, 700)
    return body


def box(x, y, w, h, title, body="", status="ATIVO", aws=None):
    color = (
        CYAN
        if status == "ATIVO"
        else ORANGE
        if status in {"ISOLADO", "HUMANO"}
        else GRAY
    )
    out = rect(x, y, w, h, stroke=color, dash=status == "PLANEJADO")
    offset = 82 if aws else 22
    if aws:
        out += icon(x + 18, y + 20, aws, 50)
    out += text(x + offset, y + 46, title, 25, WHITE, 700)
    if body:
        size = 21
        while (
            size > 15
            and len(textwrap.wrap(body, max(18, int((w - 44) / (size * 0.5)))))
            * size
            * 1.4
            > h - 125
        ):
            size -= 1
        out += wrap(
            x + 22,
            y + 90,
            body,
            max(18, int((w - 44) / (size * 0.5))),
            size,
            MUTED,
            line=size * 1.4,
        )
    out += chip(x + 20, y + h - 48, status, color)
    return out


def architecture():
    out = start(
        1600,
        1020,
        "Arquitetura AWS",
        "Pedidos assíncronos. Controles explícitos.",
        "Componentes existentes e extensão de entrega, com estados distintos. Sem alegação de alta disponibilidade.",
    )
    out += rect(50, 295, 1500, 570, stroke=BLUE, r=25) + text(
        80, 334, "AWS  /  us-east-1  /  REDE PRIVADA EM DUAS ZONAS", 19, CYAN, 700
    )
    out += box(
        85, 380, 290, 175, "HTTPS + ALB", "TLS e proteção WAF existentes.", aws="elb"
    )
    out += box(
        430,
        380,
        290,
        175,
        "Orders API",
        "EKS. Release crítica exige humano.",
        aws="eks",
    )
    out += box(
        775,
        380,
        290,
        175,
        "Amazon SQS",
        "Fila e DLQ. Entrega ao menos uma vez.",
        aws="sqs",
    )
    out += box(
        1120,
        380,
        290,
        175,
        "Orders Worker",
        "Consumidor atual ativo no EKS.",
        aws="eks",
    )
    out += (
        line(375, 465, 430, 465) + line(720, 465, 775, 465) + line(1065, 465, 1120, 465)
    )
    out += box(
        1120, 635, 290, 175, "DynamoDB", "Persistência e idempotência.", aws="dynamodb"
    ) + line(1265, 555, 1265, 635)
    out += box(
        85,
        635,
        390,
        175,
        "GLPI + Kestra",
        "GMUD e gate determinístico. Aprovação autenticada.",
        status="HUMANO",
    )
    out += box(
        530,
        635,
        450,
        175,
        "Observabilidade",
        "Prometheus, Grafana, traces e logs. CloudWatch para dados AWS.",
        aws="cloudwatch",
    )
    out += line(475, 720, 530, 720)
    out += text(
        65,
        916,
        "Ativo = componente observado • Humano = promoção aguardando decisão • Canary ainda não validado no EKS.",
        21,
        MUTED,
    )
    return out + "</svg>"


def delivery():
    out = start(
        1600,
        1040,
        "Entrega e governança",
        "Uma release. Uma GMUD. Um gate.",
        "Integração verificada até a aprovação. Publicação de aplicação e janela real de observação permanecem pendentes.",
    )
    entries = [
        (
            65,
            330,
            325,
            180,
            "CI + Trivy",
            "Testes e scan obrigatórios. Imagem por digest.",
            "ATIVO",
            "ecr",
        ),
        (
            455,
            330,
            325,
            180,
            "GLPI Change",
            "Commit, digest, ambiente, planos e execução Kestra.",
            "ATIVO",
            None,
        ),
        (
            845,
            330,
            325,
            180,
            "Kestra",
            "Política protegida por criticidade e histórico.",
            "ATIVO",
            None,
        ),
        (
            1235,
            330,
            300,
            180,
            "Portal + SNS",
            "Humano autenticado quando exigido.",
            "HUMANO",
            None,
        ),
    ]
    for args in entries:
        out += box(*args[:6], status=args[6], aws=args[7])
    for a, b in [(390, 455), (780, 845), (1170, 1235)]:
        out += line(a, 420, b, 420)
    out += box(
        65,
        640,
        365,
        190,
        "Publisher GitOps",
        "Autoridade GPG exclusiva e proteção contra replay.",
        status="ATIVO",
    )
    out += box(
        500,
        640,
        325,
        190,
        "Argo CD",
        "Chave exigida no destino. Signatário alternativo recusado.",
        status="ATIVO",
    )
    out += box(
        895,
        640,
        325,
        190,
        "Validação + Review",
        "Health e métricas. GMUD em observação por 12h.",
        status="PLANEJADO",
    )
    out += box(
        1290,
        640,
        245,
        190,
        "Encerramento",
        "Somente após 12h limpas, sem rollback.",
        status="ISOLADO",
    )
    out += (
        line(1385, 510, 1385, 575)
        + line(1385, 575, 245, 575)
        + line(245, 575, 245, 640)
    )
    out += (
        line(430, 735, 500, 735) + line(825, 735, 895, 735) + line(1220, 735, 1290, 735)
    )
    out += chip(65, 900, "BEDROCK OPCIONAL / DESABILITADO", GRAY)
    out += text(
        65,
        957,
        "Agendamento Kestra persistente instalado. Lógica de encerramento/rollback testada isoladamente.",
        20,
        MUTED,
    )
    return out + "</svg>"


def canary():
    out = start(
        1600,
        1030,
        "Canary exclusivo do Worker",
        "SQS distribui consumo. Métricas decidem.",
        "Desenho e componentes testados isoladamente. Progressão e rollback EKS ainda não demonstrados.",
    )
    out += box(
        60,
        385,
        300,
        200,
        "SQS + DLQ",
        "Mesma fila. Sem pesos HTTP ou promessa de percentuais.",
        aws="sqs",
    )
    out += box(
        490, 320, 380, 185, "Worker stable", "Consumidor atual preservado.", aws="eks"
    )
    out += box(
        490,
        600,
        380,
        185,
        "Worker canary",
        "Candidata: 1 → 2 consumidores. Lease expira para drain.",
        status="PLANEJADO",
        aws="eks",
    )
    out += line(360, 460, 490, 412) + line(360, 515, 490, 690, dash=True)
    out += box(
        1000,
        320,
        500,
        185,
        "Métricas por versão",
        "Amostras mínimas, p95, falhas, retries, idade da fila e DLQ.",
        status="ISOLADO",
        aws="cloudwatch",
    )
    out += box(
        1000,
        600,
        500,
        185,
        "Rollback com drenagem",
        "Parar novos polls → inflight zero → restaurar versão conhecida.",
        status="ISOLADO",
    )
    out += (
        line(870, 412, 1000, 412)
        + line(870, 690, 950, 690, dash=True)
        + line(950, 690, 950, 505, dash=True)
    )
    out += line(1250, 505, 1250, 600, dash=True)
    out += text(
        65,
        875,
        "RESPONSÁVEL AUTENTICADO: solicitação até 12h após validação; versão substituída exige análise humana.",
        21,
        MUTED,
    )
    out += text(
        65,
        920,
        "Após o prazo: nova GMUD. Rollback nunca conta como sucesso no histórico das cinco mudanças.",
        21,
        MUTED,
    )
    return out + "</svg>"


def slide1(e):
    o = start(
        1080,
        1350,
        "Cloud engineering na prática",
        "AWS com rastreabilidade.",
        "Um laboratório CosmoTech Solutions para aprofundar a prática em AWS.",
        page="01/06",
    )
    o += text(60, 380, "Da experiência em", 41, WHITE, 700) + text(
        60, 440, "Azure / AKS ao lab AWS.", 44, CYAN, 700
    )
    o += wrap(
        60,
        520,
        "Arquitetura, automação, troubleshooting, segurança, observabilidade e práticas SRE.",
        47,
        29,
        line=46,
    )
    for x, title, desc, aws in [
        (60, "EKS", "Aplicações", "eks"),
        (390, "SQS", "Processamento", "sqs"),
        (720, "DynamoDB", "Persistência", "dynamodb"),
    ]:
        o += box(x, 700, 300, 210, title, desc, aws=aws)
    o += chip(60, 990, "ESTADO ATUAL / INTEGRAÇÃO EM VALIDAÇÃO", ORANGE)
    o += wrap(
        60,
        1080,
        "Componentes ativos, testes isolados e etapas pendentes apresentados sem confundir os resultados.",
        52,
        24,
        line=38,
    )
    return o + "</svg>"


def slide2(e):
    o = start(
        1080,
        1350,
        "Arquitetura",
        "Do pedido à persistência.",
        "Serviços existentes, fronteiras claras e processamento assíncrono.",
        page="02/06",
    )
    o += box(60, 340, 420, 180, "Orders API", "Entrada HTTPS no EKS.", aws="eks")
    o += box(
        600, 340, 420, 180, "Amazon SQS", "Fila principal e DLQ.", aws="sqs"
    ) + line(480, 430, 600, 430)
    o += box(
        600, 630, 420, 180, "Orders Worker", "Consumo atual ativo.", aws="eks"
    ) + line(810, 520, 810, 630)
    o += box(
        60, 630, 420, 180, "DynamoDB", "Persistência de pedidos.", aws="dynamodb"
    ) + line(600, 720, 480, 720)
    o += rect(60, 920, 960, 235, stroke=BLUE) + text(
        85, 969, "Operação e confiabilidade", 29, WHITE, 700
    )
    o += wrap(
        85,
        1020,
        "Idempotência • retries limitados • métricas e traces • menor privilégio • digest imutável.",
        58,
        25,
        line=40,
    )
    return o + "</svg>"


def slide3(e):
    o = start(
        1080,
        1350,
        "GMUD no GLPI",
        "Aprovação por criticidade.",
        "Configuração protegida: CI e IA não reclassificam as aplicações.",
        page="03/06",
    )
    for y, title, desc, status in [
        (
            330,
            "CRÍTICA / Orders API",
            "Sempre exige aprovação humana autenticada.",
            "HUMANO",
        ),
        (
            600,
            "NÃO CRÍTICA / Worker",
            "Automática com todos os controles. Bootstrap inicial em revisão.",
            "ISOLADO",
        ),
        (
            870,
            "CRÍTICA CUSTOMIZADA",
            "Cinco últimas GMUDs válidas e bem-sucedidas. Sem histórico: humano.",
            "ISOLADO",
        ),
    ]:
        o += box(60, y, 960, 225, title, desc, status=status)
    o += text(
        65,
        1190,
        "Aberta, simulada, cancelada, falha ou rollback não comprova cinco sucessos.",
        18,
        MUTED,
    )
    return o + "</svg>"


def slide4(e):
    o = start(
        1080,
        1350,
        "Entrega controlada",
        "Kestra como gate único.",
        "Releases propostas por CI; autorização e evidências verificadas no servidor.",
        page="04/06",
    )
    steps = [
        ("CI + Trivy + ECR", "Testes e scan aprovados; referência por digest."),
        ("GLPI + Kestra", "GMUD única e decisão determinística."),
        ("Portal humano + SNS", "Aprovação vinculada à release quando exigida."),
        ("GitOps + Argo CD", "Publisher assinado; outra chave recusada no destino."),
    ]
    for i, (title, desc) in enumerate(steps):
        y = 325 + i * 205
        o += rect(60, y, 960, 160, stroke=CYAN if i != 2 else ORANGE)
        o += text(86, y + 51, f"0{i + 1}", 28, ORANGE, 700) + text(
            158, y + 51, title, 29, WHITE, 700
        )
        o += wrap(158, y + 97, desc, 48, 23, line=34)
        if i < 3:
            o += line(540, y + 160, 540, y + 205)
    o += chip(60, 1195, "DEPLOY DE APLICAÇÃO AINDA PENDENTE", ORANGE)
    return o + "</svg>"


def slide5(e):
    o = start(
        1080,
        1350,
        "Canary Worker",
        "Medir antes de avançar.",
        "Estratégia preparada para consumidores SQS. Não é roteamento HTTP.",
        page="05/06",
    )
    o += box(
        60,
        325,
        960,
        170,
        "Fila SQS compartilhada",
        "Distribuição efetiva depende dos consumidores e é medida.",
        aws="sqs",
    )
    o += line(300, 495, 300, 575) + line(780, 495, 780, 575, dash=True)
    o += box(60, 575, 450, 220, "Stable", "Versão atual preservada.", aws="eks")
    o += box(
        570,
        575,
        450,
        220,
        "Canary 1 → 2",
        "Lease e consumo controlado.",
        status="PLANEJADO",
        aws="eks",
    )
    o += rect(60, 880, 960, 280, stroke=ORANGE, dash=True) + text(
        85, 929, "Métricas → progressão ou drenagem", 29, WHITE, 700
    )
    o += wrap(
        85,
        982,
        "p95, amostras por versão, falhas, retries e DLQ. Antes de retirar a candidata: inflight igual a zero.",
        57,
        25,
        line=42,
    )
    o += chip(85, 1095, "TESTES ISOLADOS / EKS AINDA PENDENTE", ORANGE)
    return o + "</svg>"


def slide6(e):
    o = start(
        1080,
        1350,
        "Auditoria e SRE",
        "Resultados que deixam provas.",
        "Nenhuma simulação é apresentada como integração concluída.",
        page="06/06",
    )
    facts = [
        ("SEGURANÇA", "Trivy bloqueou imagens; pacotes corrigidos e CIs aprovados."),
        (
            "GITOPS",
            "Argo recusou signatário alternativo, sem sync da aplicação de teste.",
        ),
        (
            "OBSERVABILIDADE",
            "Endpoints oficiais EKS conectados; alertas preservados e targets up.",
        ),
        (
            "JANELA DE 12H",
            "Agendamento persistente ativo; janela real ainda não iniciada.",
        ),
    ]
    for i, (title, desc) in enumerate(facts):
        y = 330 + i * 180
        o += text(65, y, title, 19, ORANGE, 700) + wrap(
            65, y + 42, desc, 59, 26, WHITE, line=40
        )
    o += rect(60, 1080, 960, 125, stroke=CYAN) + text(
        85,
        1127,
        "Arquitetura • Automação • Engenharia de confiabilidade",
        25,
        WHITE,
        700,
    )
    o += text(
        85,
        1170,
        "Experiência prática em AWS, com limites e evidências documentados.",
        21,
        MUTED,
    )
    return o + "</svg>"


class Rect(C.Structure):
    _fields_ = [
        ("x", C.c_double),
        ("y", C.c_double),
        ("width", C.c_double),
        ("height", C.c_double),
    ]


class Renderer:
    def __init__(self):
        self.c = C.CDLL(ctypes.util.find_library("cairo"))
        self.r = C.CDLL(ctypes.util.find_library("rsvg-2"))
        self.g = C.CDLL(ctypes.util.find_library("gobject-2.0"))
        self.bind(
            self.c,
            "cairo_image_surface_create",
            [C.c_int, C.c_int, C.c_int],
            C.c_void_p,
        )
        self.bind(self.c, "cairo_create", [C.c_void_p], C.c_void_p)
        self.bind(
            self.c, "cairo_surface_write_to_png", [C.c_void_p, C.c_char_p], C.c_int
        )
        self.bind(
            self.c,
            "cairo_pdf_surface_create",
            [C.c_char_p, C.c_double, C.c_double],
            C.c_void_p,
        )
        for name in [
            "cairo_show_page",
            "cairo_destroy",
            "cairo_surface_destroy",
            "cairo_surface_finish",
        ]:
            self.bind(self.c, name, [C.c_void_p], None)
        self.bind(
            self.r,
            "rsvg_handle_new_from_data",
            [C.c_char_p, C.c_size_t, C.POINTER(C.c_void_p)],
            C.c_void_p,
        )
        self.bind(
            self.r,
            "rsvg_handle_render_document",
            [C.c_void_p, C.c_void_p, C.POINTER(Rect), C.POINTER(C.c_void_p)],
            C.c_int,
        )
        self.bind(self.g, "g_object_unref", [C.c_void_p], None)

    @staticmethod
    def bind(lib, name, args, ret):
        function = getattr(lib, name)
        function.argtypes = args
        function.restype = ret

    def draw(self, svg, context, w, h):
        data = svg.encode()
        error = C.c_void_p()
        handle = self.r.rsvg_handle_new_from_data(data, len(data), C.byref(error))
        if not handle:
            raise RuntimeError("Invalid SVG document")
        try:
            if not self.r.rsvg_handle_render_document(
                handle, context, C.byref(Rect(0, 0, w, h)), C.byref(error)
            ):
                raise RuntimeError("SVG rendering failed")
        finally:
            self.g.g_object_unref(handle)

    def png(self, svg, path, w, h):
        surface = self.c.cairo_image_surface_create(0, w, h)
        context = self.c.cairo_create(surface)
        try:
            self.draw(svg, context, w, h)
            if self.c.cairo_surface_write_to_png(surface, str(path).encode()):
                raise RuntimeError("PNG export failed")
        finally:
            self.c.cairo_destroy(context)
            self.c.cairo_surface_destroy(surface)

    def pdf(self, svgs, path):
        surface = self.c.cairo_pdf_surface_create(str(path).encode(), 540, 675)
        context = self.c.cairo_create(surface)
        try:
            for svg in svgs:
                self.draw(svg, context, 540, 675)
                self.c.cairo_show_page(context)
            self.c.cairo_surface_finish(surface)
        finally:
            self.c.cairo_destroy(context)
            self.c.cairo_surface_destroy(surface)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    evidence = json.loads(args.evidence.read_text())
    if (
        evidence.get("bedrock_enabled") is not False
        or evidence.get("canary_integrated") is not False
        or evidence.get("real_window_started") is not False
        or evidence.get("foreign_signer_rejected") is not True
        or evidence.get("control_plane_targets_up") is not True
        or evidence.get("gmud_pending_human", 0) < 1
        or not all(
            evidence.get("ci_passed", {}).get(k) is True for k in ["api", "worker"]
        )
    ):
        raise ValueError(
            "This editorial revision does not match the verified evidence; update it before export"
        )
    renderer = Renderer()
    for name, svg in [
        ("aws-architecture", architecture()),
        ("cicd-gmud-gitops", delivery()),
        ("worker-canary", canary()),
    ]:
        p = ROOT / "assets" / name
        p.with_suffix(".svg").write_text(svg)
        renderer.png(
            svg,
            p.with_suffix(".png"),
            1600,
            1020
            if name == "aws-architecture"
            else 1040
            if name == "cicd-gmud-gitops"
            else 1030,
        )
    svgs = []
    for i, function in enumerate([slide1, slide2, slide3, slide4, slide5, slide6], 1):
        svg = function(evidence)
        svgs.append(svg)
        p = ROOT / "carousel" / f"{i:02d}-cosmotech"
        p.with_suffix(".svg").write_text(svg)
        renderer.png(svg, p.with_suffix(".png"), 1080, 1350)
        assert struct.unpack(">II", p.with_suffix(".png").read_bytes()[16:24]) == (
            1080,
            1350,
        )
    renderer.pdf(svgs, ROOT / "carousel/cosmotech-carousel-review.pdf")
    overview = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="900"><rect width="1080" height="900" fill="'
        + NAVY
        + '"/>'
    )
    for i in range(6):
        png = base64.b64encode(
            (ROOT / "carousel" / f"{i + 1:02d}-cosmotech.png").read_bytes()
        ).decode()
        overview += f'<image x="{i % 3 * 360}" y="{i // 3 * 450}" width="360" height="450" href="data:image/png;base64,{png}"/>'
    renderer.png(overview + "</svg>", ROOT / "carousel/contact-sheet.png", 1080, 900)
    for name, title in [
        ("grafana", "Dashboard e métricas por versão"),
        ("kestra", "Execução Kestra e aprovação"),
        ("glpi", "GMUD nativa GLPI"),
        ("argocd", "Assinatura e sync Argo CD"),
    ]:
        svg = start(1080, 750, "Placeholder de captura", title)
        svg += rect(60, 330, 960, 245, stroke=GRAY, dash=True) + text(
            90, 397, "CAPTURA REAL PENDENTE", 34, ORANGE, 700
        )
        svg += wrap(
            90,
            455,
            "Este espaço não contém uma interface, dashboard ou resultado simulado. Substituir somente por captura real sanitizada.",
            55,
            24,
            line=37,
        )
        svg += "</svg>"
        p = ROOT / "screenshots" / (name + "-placeholder.svg")
        p.write_text(svg)
        renderer.png(svg, p.with_suffix(".png"), 1080, 750)
    print(
        "Exported 3 diagrams, 6 carousel pages, 6-page PDF, contact sheet and 4 explicit capture placeholders."
    )


if __name__ == "__main__":
    main()
