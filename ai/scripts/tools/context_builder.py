"""
context_builder.py
Monta o contexto completo do repositório para o agente PO.
"""

import os
from tools.github_reader import GitHubReader


def build_context(repo_full_name: str) -> dict:
    token = os.getenv("GITHUB_TOKEN")
    reader = GitHubReader(token=token, repo_full_name=repo_full_name)

    print("📖 Lendo README...")
    readme = reader.get_readme()

    print("🗂️  Lendo estrutura de pastas...")
    structure = reader.get_repo_structure()

    print("🔧 Identificando stack...")
    stack = reader.get_stack_hints()

    print("📝 Lendo commits recentes...")
    commits = reader.get_recent_commits(limit=20)

    print("🐛 Lendo issues abertas...")
    open_issues = reader.get_open_issues()

    print("✅ Lendo issues fechadas (sprint anterior)...")
    closed_issues = reader.get_closed_issues(limit=20)

    print("🗓️  Lendo sprints anteriores...")
    try:
        sprints = reader.get_sprints()
    except Exception:
        print("   ⚠️  Sprints não disponíveis (verifique permissão 'project' no token)")
        sprints = []

    print("🎯 Lendo escopo da sprint atual...")
    try:
        sprint_scope = reader.get_current_sprint_scope()
    except Exception:
        print("   ⚠️  Escopo da sprint não disponível")
        sprint_scope = None

    return {
        "repo": repo_full_name,
        "sprint_scope": sprint_scope,
        "readme": readme,
        "structure": structure,
        "stack": stack,
        "recent_commits": commits,
        "open_issues": open_issues,
        "closed_issues": closed_issues,
        "sprints": sprints,
    }


def format_context_for_prompt(context: dict) -> str:
    parts = []

    parts.append(f"# Repositório: {context['repo']}\n")

    # Escopo da sprint vem primeiro — é a fonte primária de verdade
    scope = context.get("sprint_scope")
    if scope and scope.get("description"):
        parts.append(
            f"## 🎯 Escopo da Sprint Atual: {scope['title']}\n"
            f"{scope['description']}"
        )
    elif scope and scope.get("short_description"):
        parts.append(
            f"## 🎯 Escopo da Sprint Atual: {scope['title']}\n"
            f"{scope['short_description']}"
        )

    if context["readme"]:
        parts.append("## README\n" + context["readme"][:3000])

    parts.append("## Estrutura do Projeto\n```\n" + context["structure"] + "\n```")

    if context["stack"]:
        parts.append("## Stack Identificada\n" + "\n".join(f"- {s}" for s in context["stack"]))

    if context["recent_commits"]:
        parts.append("## Commits Recentes")
        for c in context["recent_commits"]:
            parts.append(f"- [{c['sha'][:7]}] {c['message']} ({c['date']})")

    if context["open_issues"]:
        parts.append("## Issues Abertas (Backlog atual)")
        for i in context["open_issues"]:
            parts.append(f"- #{i['number']} {i['title']} [labels: {', '.join(i['labels'])}]")
    else:
        parts.append("## Issues Abertas\nNenhuma issue aberta no momento.")

    if context["closed_issues"]:
        parts.append("## Issues Recentemente Fechadas (últimas sprints)")
        for i in context["closed_issues"]:
            parts.append(f"- #{i['number']} {i['title']} (fechada em {i['closed_at']})")

    if context["sprints"]:
        parts.append("## Sprints Anteriores")
        for sprint in context["sprints"]:
            parts.append(f"\n### {sprint['title']}")
            for item in sprint["items"]:
                status = "✅" if item["status"] == "Done" else "🔄"
                parts.append(f"  {status} {item['title']}")

    return "\n\n".join(parts)