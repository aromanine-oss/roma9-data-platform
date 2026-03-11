"""
agent.py
Entry point do Agente PO.

Uso:
    # Gera o sprint_preview.md para revisão
    python agent.py --repo usuario/repositorio

    # Após editar o sprint_preview.md, envia ao GitHub
    python agent.py --repo usuario/repositorio --push

    # Debug: mostra contexto completo no terminal
    python agent.py --repo usuario/repositorio --debug
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from tools.context_builder import build_context, format_context_for_prompt
from tools.sprint_generator import generate_sprint_preview, save_sprint_preview
from tools.sprint_parser import parse_sprint_preview, get_sprint_title
from tools.github_writer import GitHubWriter
from tools.sprint_parser import parse_sprint_preview, get_sprint_title
from tools.github_writer import GitHubWriter

# Busca o .env subindo até 3 níveis acima do agent.py (cobre raiz do repo)
_here = Path(__file__).resolve().parent
_env_path = next(
    (p / ".env" for p in [_here, _here.parent, _here.parent.parent] if (p / ".env").exists()),
    None
)
load_dotenv(dotenv_path=_env_path)

PREVIEW_FILE = "sprint_preview.md"


def validate_env():
    """Valida que as variáveis de ambiente necessárias estão presentes."""
    missing = []
    if not os.getenv("GITHUB_TOKEN"):
        missing.append("GITHUB_TOKEN")
    if not os.getenv("ANTHROPIC_API_KEY"):
        missing.append("ANTHROPIC_API_KEY")
    if missing:
        print(f"❌ Variáveis de ambiente faltando: {', '.join(missing)}")
        print("   Configure seu arquivo .env (veja .env.example)")
        sys.exit(1)


def detect_sprint_number(context: dict) -> int:
    """Infere o número da próxima sprint com base nas sprints anteriores."""
    if not context["sprints"]:
        return 1
    return len(context["sprints"]) + 1


def main():
    parser = argparse.ArgumentParser(description="Agente PO — Geração de sprints")
    parser.add_argument("--repo", required=True, help="Repositório no formato usuario/repo")
    parser.add_argument("--push", action="store_true", help="Envia o sprint_preview.md aprovado ao GitHub (Fase 3)")
    parser.add_argument("--debug", action="store_true", help="Mostra o contexto completo no terminal")
    parser.add_argument("--sprint", type=int, default=None, help="Força o número da sprint (ex: --sprint 7)")
    parser.add_argument("--output", default="context_debug.json", help="Salva contexto em JSON (debug)")
    args = parser.parse_args()

    validate_env()

    print(f"\n🤖 Agente PO iniciado")
    print(f"📦 Repositório: {args.repo}")
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print("-" * 50)

    # ── Fase 1: Leitura ──────────────────────────────────────────────────────
    try:
        context = build_context(repo_full_name=args.repo)
    except PermissionError as e:
        print(f"❌ Erro de permissão: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Erro ao ler repositório: {e}")
        sys.exit(1)

    print("\n✅ Leitura concluída!\n")

    # ── Diagnóstico resumido ──────────────────────────────────────────────────
    print("📊 Diagnóstico do repositório:")
    print(f"   - README encontrado:       {'✅' if context['readme'] else '❌'}")
    print(f"   - Stack identificada:      {', '.join(context['stack']) if context['stack'] else 'não detectada'}")
    print(f"   - Commits recentes:        {len(context['recent_commits'])}")
    print(f"   - Issues abertas:          {len(context['open_issues'])}")
    print(f"   - Issues fechadas:         {len(context['closed_issues'])}")
    print(f"   - Sprints anteriores:      {len(context['sprints'])}")

    # ── Contexto formatado ────────────────────────────────────────────────────
    prompt_context = format_context_for_prompt(context)

    if args.debug:
        print("\n" + "=" * 50)
        print("CONTEXTO FORMATADO PARA O CLAUDE:")
        print("=" * 50)
        print(prompt_context)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(context, f, ensure_ascii=False, indent=2, default=str)
        print(f"\n💾 Contexto salvo em: {args.output}")

    # ── Fase 3: Push (se --push) ──────────────────────────────────────────────
    if args.push:
        print("\n📤 Modo push ativado — lendo sprint_preview.md aprovado...")

        try:
            issues = parse_sprint_preview(PREVIEW_FILE)
            sprint_title = get_sprint_title(PREVIEW_FILE)
        except (FileNotFoundError, ValueError) as e:
            print(f"❌ Erro ao ler sprint_preview.md: {e}")
            sys.exit(1)

        print(f"📋 {len(issues)} issues encontradas para a {sprint_title}")
        print()

        writer = GitHubWriter(token=os.getenv("GITHUB_TOKEN"), repo_full_name=args.repo)

        try:
            project_id, project_name = writer.get_project_id()
            print(f"📁 Projeto encontrado: {project_name}")
        except RuntimeError as e:
            print(f"❌ {e}")
            sys.exit(1)

        field_id, option_id = writer.get_status_field(project_id)

        created = []
        for i, issue in enumerate(issues, 1):
            print(f"   [{i}/{len(issues)}] Criando: {issue['title']}...", end=" ", flush=True)
            try:
                result = writer.create_issue(
                    title=issue["title"],
                    body=issue["body"],
                    labels=["sprint"],
                )
                item_id = writer.add_issue_to_project(project_id, result["node_id"])
                if field_id and option_id:
                    writer.set_item_status(project_id, item_id, field_id, option_id)
                print(f"✅ #{result['number']}")
                created.append(result)
            except Exception as e:
                print(f"❌ Erro: {e}")

        print()
        print(f"✅ {len(created)} issues criadas com sucesso na {sprint_title}!")
        print()
        for r in created:
            print(f"   #{r['number']} → {r['url']}")
        return

    # ── Fase 2: Geração do sprint_preview.md ─────────────────────────────────
    print()
    sprint_number = args.sprint if args.sprint else detect_sprint_number(context)
    source = "informado manualmente" if args.sprint else "detectado automaticamente"
    print(f"🔢 Sprint {sprint_number} ({source})")
    print()

    try:
        preview_content = generate_sprint_preview(
            context_text=prompt_context,
            sprint_number=sprint_number
        )
    except Exception as e:
        print(f"❌ Erro ao chamar a API do Claude: {e}")
        sys.exit(1)

    saved_path = save_sprint_preview(preview_content, PREVIEW_FILE)

    print(f"\n✅ sprint_preview.md gerado com sucesso!")
    print(f"📄 Arquivo: {saved_path}")
    print()
    print("─" * 50)
    print("📋 PRÓXIMOS PASSOS:")
    print(f"   1. Abra e revise o arquivo: {PREVIEW_FILE}")
    print("   2. Edite à vontade (adicione, remova ou reordene issues)")
    print("   3. Quando aprovar, rode:")
    print(f"      python agent.py --repo {args.repo} --push")
    print("─" * 50)


if __name__ == "__main__":
    main()
