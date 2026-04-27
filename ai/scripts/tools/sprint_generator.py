"""
sprint_generator.py
Envia o contexto do repositório ao Claude e gera o sprint_preview.md.
"""

import os
import anthropic
from pathlib import Path


def load_system_prompt() -> str:
    """Carrega o prompt de sistema do arquivo po_system.md."""
    prompt_path = Path(__file__).parent.parent / "prompts" / "po_system.md"
    return prompt_path.read_text(encoding="utf-8")


def generate_sprint_preview(context_text: str, sprint_number: int = None) -> str:
    """
    Envia o contexto ao Claude e retorna o conteúdo do sprint_preview.md.

    Args:
        context_text: Contexto formatado do repositório (saída do context_builder)
        sprint_number: Número da sprint (opcional, para nomear corretamente)

    Returns:
        Conteúdo do sprint_preview.md como string
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    sprint_hint = ""
    if sprint_number:
        sprint_hint = f"\n\nEsta será a **Sprint {sprint_number}**. Nomeie a sprint corretamente no documento."

    user_message = f"""Analise o repositório abaixo e gere o sprint_preview.md com o backlog priorizado e a próxima sprint.

{context_text}
{sprint_hint}"""

    print("🧠 Claude está analisando o repositório...")

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system=load_system_prompt(),
        messages=[
            {"role": "user", "content": user_message}
        ]
    )

    return message.content[0].text


def save_sprint_preview(content: str, output_path: str = "sprint_preview.md") -> str:
    """
    Salva o conteúdo gerado no arquivo sprint_preview.md.

    Args:
        content: Conteúdo gerado pelo Claude
        output_path: Caminho do arquivo de saída

    Returns:
        Caminho absoluto do arquivo salvo
    """
    path = Path(output_path)
    path.write_text(content, encoding="utf-8")
    return str(path.resolve())
