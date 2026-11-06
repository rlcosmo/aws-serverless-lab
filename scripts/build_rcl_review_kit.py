"""Reutiliza o renderizador CosmoTech para evidências reais RCL, sem simular telas."""

from __future__ import annotations

import base64
import json

from build_cosmotech_visual_kit import (
    CYAN,
    MUTED,
    NAVY,
    ORANGE,
    ROOT,
    Renderer,
    architecture,
    box,
    canary,
    chip,
    line,
    slide1,
    slide2,
    start,
    text,
    wrap,
)


def latest(e, application):
    return max(
        (c for c in e["changes"] if c["application"] == application),
        key=lambda c: int(c["gmud_id"][3:]),
    )


def delivery(e):
    worker = latest(e, "orders-worker")
    api = latest(e, "orders-api")
    o = start(
        1600,
        1040,
        "GMUD corporativa",
        "O mesmo RCL em toda a entrega.",
        "Identificador persistente e atômico; IDs nativos GLPI/Kestra e GMUDs históricas preservados.",
    )
    for x, title, body, status in [
        (60, "CI + Trivy", "Fonte testada, versão real e digest imutável.", "ATIVO"),
        (
            450,
            "GLPI + RCL",
            worker["gmud_id"]
            + " · GLPI"
            + str(worker["glpi_id"])
            + ". Retry sem duplicação.",
            "ATIVO",
        ),
        (840, "Kestra", "Label gmud_id. Política protegida por criticidade.", "ATIVO"),
        (
            1230,
            "Portal + SNS",
            api["gmud_id"] + "/API: decisão humana autenticada.",
            "HUMANO",
        ),
    ]:
        o += box(x, 345, 310, 190, title, body, status=status)
    for x in [370, 760, 1150]:
        o += line(x, 440, x + 80, 440)
    for x, title, body, status in [
        (
            60,
            "GitOps assinado",
            "Publisher exclusivo; RCL no commit e na evidência.",
            "ATIVO",
        ),
        (
            450,
            "Argo + Canary",
            "Worker:1→2 consumidores. Promoção e drenagem reais.",
            "ATIVO",
        ),
        (
            840,
            "Observação12h",
            "Sucesso técnico inicia12h. Encerramento sem antecipação.",
            "ATIVO",
        ),
        (
            1230,
            "Encerramento",
            "Sucesso exige12h limpas. Rollback nunca conta nos cinco sucessos.",
            "ISOLADO",
        ),
    ]:
        o += box(x, 640, 310, 195, title, body, status=status)
    for x in [370, 760, 1150]:
        o += line(x, 735, x + 80, 735)
    o += (
        line(1385, 535, 1385, 580)
        + line(1385, 580, 215, 580)
        + line(215, 580, 215, 640)
    )
    o += text(
        65,
        925,
        "Portal moderno em pt-BR. Autenticação, CSRF, auditoria e assinatura preservados.",
        23,
        MUTED,
    )
    return o + "</svg>"


def slide3(e):
    o = start(
        1080,
        1350,
        "Identidade corporativa",
        "Uma GMUD. Um RCL.",
        "Sequência global persistente; números não são reutilizados após cancelamento.",
        page="03/06",
    )
    first = next(c for c in e["changes"] if c["gmud_id"] == "RCL000005")
    for y, c in zip(
        [335, 600, 865], [first, latest(e, "orders-api"), latest(e, "orders-worker")]
    ):
        status = {
            "OBSERVING": "OBSERVAÇÃO",
            "HUMAN_REVIEW": "HUMANO",
            "ROLLED_BACK": "REVERTIDA",
        }.get(c["phase"], "EM TESTE")
        app = "API" if c["application"] == "orders-api" else "Worker"
        mode = (
            "humana autenticada"
            if c["human_decision_exists"]
            else "humana pendente" if c["phase"] == "HUMAN_REVIEW" else "automática pela política"
        )
        body = (
            "GLPI"
            + str(c["glpi_id"])
            + ". Aprovação "
            + mode
            + ". Estado real: "
            + c["phase"]
            + "."
        )
        o += box(
            60,
            y,
            960,
            225,
            c["gmud_id"] + " · " + app + " " + c["version"],
            body,
            status=status,
        )
    o += text(
        65, 1190, "IDs GLPI/Kestra imutáveis. Histórico anterior preservado.", 22, MUTED
    )
    return o + "</svg>"


def slide4(e):
    o = start(
        1080,
        1350,
        "Aprovação e experiência",
        "Clareza sem perder controle.",
        "Portal real implementado e verificado por HTTPS autenticado. Este slide não é uma captura de tela.",
        page="04/06",
    )
    for i, (title, body) in enumerate(
        [
            (
                "Aplicação + versão + RCL",
                "Identidade visível no portal, no GLPI, no Kestra e nas notificações.",
            ),
            (
                "Cards e timeline em português",
                "Dez etapas reais, início, fim, duração e evidências expansíveis.",
            ),
            (
                "Acompanhamento CD + Canary",
                "release_pipeline por GMUD; scheduler técnico separado. Links Kestra/Argo e selo Canary no topo.",
            ),
            (
                "Identidade e decisões visíveis",
                "laboratorio com acesso operacional. Página reaberta informa quem aprovou. Histórico disponível durante falha do GLPI.",
            ),
        ]
    ):
        o += box(60, 340 + i * 210, 960, 180, title, body, status="ATIVO")
    o += chip(65, 1210, "AUTENTICAÇÃO • CSRF • AUDITORIA PRESERVADOS", CYAN)
    return o + "</svg>"


def slide5(e):
    c = latest(e, "orders-worker")
    stage = {
        "CANARY_1": "Canary com1 consumidor",
        "CANARY_2": "Canary com2 consumidores",
        "PROMOTING": "Promovendo candidata",
        "DRAIN_PROMOTED": "Drenagem final",
        "COMPLETE": "Progressão concluída",
        "ROLLED_BACK": "Revertido",
    }.get(c.get("canary_stage"), c["phase"])
    o = start(
        1080,
        1350,
        "Canary exclusivo Worker",
        "Medir. Avançar. Drenar.",
        "Dados sintéticos identificados percorrem API, SQS e DynamoDB reais.",
        page="05/06",
    )
    o += box(
        60,
        345,
        960,
        200,
        "RCL000005: rollback automático",
        "Backlog175s excedeu120s. Candidata drenada, stable restaurada e HPA recuperado.",
        status="ATIVO",
    )
    o += box(
        60,
        620,
        960,
        200,
        c["gmud_id"] + ": " + stage,
        "Worker "
        + c["version"]
        + ". Etapa real registrada; progressão exige amostras, p95, erros, fila e DLQ.",
        status="ATIVO",
    )
    o += box(
        60,
        895,
        960,
        200,
        "Limites explícitos",
        "Solicitação humana de rollback e encerramento real12h ainda pendentes.",
        status="ISOLADO",
    )
    o += text(
        65,
        1190,
        "Métricas ausentes bloqueiam. Nenhum valor vazio é apresentado como zero.",
        20,
        MUTED,
    )
    return o + "</svg>"


def slide6(e):
    o = start(
        1080,
        1350,
        "Engenharia com evidência",
        "Prática AWS, com rastreabilidade.",
        "Experiência recente em Azure/AKS; aprofundamento prático em AWS no laboratório.",
        page="06/06",
    )
    for y, title, body in [
        (
            355,
            "GOVERNANÇA",
            "RCL único, política protegida, portal autenticado e GMUD nativa.",
        ),
        (
            565,
            "SEGURANÇA",
            "Trivy obrigatório, GitOps assinado e signatário alternativo recusado.",
        ),
        (
            775,
            "OBSERVABILIDADE",
            "Métricas por versão e RCL. Falhas reais registradas, sem simular sucesso.",
        ),
        (
            985,
            "PRÓXIMAS PROVAS",
            "Observação12h sem encerramento antecipado; rollback responsável pós-promoção ainda pendente.",
        ),
    ]:
        o += text(65, y, title, 19, ORANGE, 700) + wrap(
            65, y + 48, body, 57, 26, line=40
        )
    return o + "</svg>"


def main():
    e = json.loads((ROOT / "assets/rcl-live-evidence.json").read_text())
    assert e["bedrock_enabled"] is False and e["real_window_completed"] is False
    assert {x["gmud_id"] for x in e["changes"]} >= {
        "RCL000001",
        "RCL000002",
        "RCL000003",
    }
    assert all(x["labels_match"] for x in e["changes"])
    r = Renderer()
    drawings = [
        (
            "aws-architecture",
            architecture().replace(
                "Ativo = componente observado • Humano = promoção aguardando decisão • Canary ainda não validado no EKS.",
                "Ativo = observado • Humano = aprovação exigida • Canary Worker validado;12h abertas.",
            ),
            1020,
        ),
        ("cicd-gmud-gitops", delivery(e), 1040),
        (
            "worker-canary",
            canary()
            .replace(
                "Desenho e componentes testados isoladamente. Progressão e rollback EKS ainda não demonstrados.",
                "RCL000005: rollback automático real. Nova release corretiva acompanhada por métricas.",
            )
            .replace("PLANEJADO", "EM TESTE")
            .replace("ISOLADO", "EM TESTE"),
            1030,
        ),
    ]
    for name, svg, h in drawings:
        (ROOT / "assets" / f"{name}.svg").write_text(svg)
        r.png(svg, ROOT / "assets" / f"{name}.png", 1600, h)
    slides = []
    for i, f in enumerate([slide1, slide2, slide3, slide4, slide5, slide6], 1):
        svg = f(e)
        slides.append(svg)
        p = ROOT / "carousel" / f"{i:02d}-cosmotech"
        p.with_suffix(".svg").write_text(svg)
        r.png(svg, p.with_suffix(".png"), 1080, 1350)
    r.pdf(slides, ROOT / "carousel/cosmotech-carousel-review.pdf")
    overview = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="900"><rect width="1080" height="900" fill="'
        + NAVY
        + '"/>'
    )
    for i in range(6):
        data = base64.b64encode(
            (ROOT / "carousel" / f"{i + 1:02d}-cosmotech.png").read_bytes()
        ).decode()
        overview += f'<image x="{i % 3 * 360}" y="{i // 3 * 450}" width="360" height="450" href="data:image/png;base64,{data}"/>'
    r.png(overview + "</svg>", ROOT / "carousel/contact-sheet.png", 1080, 900)
    print("Kit RCL exportado; diagramas e slides, sem capturas simuladas.")


if __name__ == "__main__":
    main()
