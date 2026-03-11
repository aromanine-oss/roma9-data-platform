"""
sprint_parser.py
Lê o sprint_preview.md aprovado e extrai as issues para criar no GitHub.
"""

import re
from pathlib import Path


def parse_sprint_preview(filepath: str = "sprint_preview.md") -> list[dict]:
    """
    Lê o sprint_preview.md e extrai as issues selecionadas para a sprint.

    Procura pela seção '### Issues Selecionadas' e extrai cada item numerado.

    Returns:
        Lista de dicts com 'title', 'body' e 'priority'
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")

    content = path.read_text(encoding="utf-8")

    # Localiza a seção de issues selecionadas
    # Estratégia 1: procura seção ### com título relacionado a issues/sprint
    section_match = re.search(
        r"###[^\n]*(?:issues|tarefas|tasks|sprint)[^\n]*\n(.*?)(?=\n###|\n##|\Z)",
        content,
        re.DOTALL | re.IGNORECASE
    )

    # Estratégia 2: fallback — pega o bloco que contém a primeira lista numerada
    if not section_match:
        section_match = re.search(
            r"###[^\n]*\n(.*?1\..*?)(?=\n###|\n##|\Z)",
            content,
            re.DOTALL
        )

    if not section_match:
        raise ValueError(
            "Nenhuma lista numerada encontrada no sprint_preview.md.\n"
            "O arquivo precisa ter issues no formato: '1. **Título** *(Must Have)*'"
        )

    section = section_match.group(1)

    # Extrai cada issue numerada: "1. **Título** *(prioridade)*"
    issue_blocks = re.split(r"\n(?=\d+\.\s)", section.strip())

    issues = []
    for block in issue_blocks:
        block = block.strip()
        if not block:
            continue

        # Extrai título (negrito ou texto simples)
        title_match = re.match(r"\d+\.\s+\*\*(.+?)\*\*", block) or \
                      re.match(r"\d+\.\s+(.+?)(?:\s+\*|$)", block)
        if not title_match:
            continue

        title = title_match.group(1).strip()

        # Extrai prioridade
        priority_match = re.search(r"\*(Must Have|Should Have|Could Have)\*", block)
        priority = priority_match.group(1) if priority_match else "Should Have"

        # Extrai sub-itens como corpo da issue
        sub_items = re.findall(r"^\s+-\s+(.+)$", block, re.MULTILINE)
        body = "\n".join(f"- {item}" for item in sub_items) if sub_items else ""

        issues.append({
            "title": title,
            "body": body,
            "priority": priority,
        })

    if not issues:
        raise ValueError(
            "Nenhuma issue encontrada no sprint_preview.md.\n"
            "Verifique se as issues estão no formato: '1. **Título** *(Must Have)*'"
        )

    return issues


def get_sprint_title(filepath: str = "sprint_preview.md") -> str:
    """Extrai o título da sprint do sprint_preview.md."""
    path = Path(filepath)
    content = path.read_text(encoding="utf-8")

    # Procura por "# Sprint N" ou "## Sprint N"
    match = re.search(r"#+ Sprint (\d+)", content)
    if match:
        return f"Sprint {match.group(1)}"

    return "Sprint"