"""
github_reader.py
Responsável por toda leitura do repositório via GitHub API.
"""

import base64
import requests


class GitHubReader:
    """
    Encapsula todas as chamadas de leitura à GitHub API.
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, repo_full_name: str):
        """
        Args:
            token: GitHub Personal Access Token
            repo_full_name: ex: "usuario/repositorio"
        """
        if not token:
            raise ValueError("GITHUB_TOKEN não encontrado. Verifique seu arquivo .env")

        self.repo = repo_full_name
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get(self, path: str, params: dict = None) -> dict | list:
        """Faz uma requisição GET autenticada à GitHub API."""
        url = f"{self.BASE_URL}{path}"
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 404:
            return None
        if response.status_code == 403:
            raise PermissionError("Token sem permissão para este recurso.")
        response.raise_for_status()
        return response.json()

    # -------------------------------------------------------------------------
    # README
    # -------------------------------------------------------------------------

    def get_readme(self) -> str | None:
        """Retorna o conteúdo do README.md em texto plano."""
        data = self._get(f"/repos/{self.repo}/readme")
        if not data:
            return None
        content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
        return content

    # -------------------------------------------------------------------------
    # ESTRUTURA DE PASTAS
    # -------------------------------------------------------------------------

    def get_repo_structure(self, max_depth: int = 3) -> str:
        """
        Retorna a estrutura de pastas do repositório em formato de árvore.
        Ignora pastas comuns de dependências (.git, node_modules, venv, etc.)
        """
        IGNORE = {
            ".git", "node_modules", "venv", ".venv", "__pycache__",
            ".mypy_cache", ".pytest_cache", "dist", "build", ".idea", ".vscode"
        }

        data = self._get(f"/repos/{self.repo}/git/trees/HEAD", params={"recursive": "1"})
        if not data or "tree" not in data:
            return "Não foi possível ler a estrutura do repositório."

        tree = data["tree"]
        lines = []

        for item in tree:
            path = item["path"]
            parts = path.split("/")

            # ignora pastas bloqueadas e seus filhos
            if any(p in IGNORE for p in parts):
                continue

            # limita profundidade
            if len(parts) > max_depth:
                continue

            indent = "  " * (len(parts) - 1)
            icon = "📁" if item["type"] == "tree" else "📄"
            lines.append(f"{indent}{icon} {parts[-1]}")

        return "\n".join(lines)

    # -------------------------------------------------------------------------
    # STACK
    # -------------------------------------------------------------------------

    def get_stack_hints(self) -> list[str]:
        """
        Infere a stack do projeto olhando arquivos de configuração conhecidos.
        """
        STACK_FILES = {
            "requirements.txt": "Python",
            "pyproject.toml": "Python (pyproject)",
            "setup.py": "Python",
            "Pipfile": "Python (Pipenv)",
            "package.json": "Node.js / JavaScript",
            "pom.xml": "Java (Maven)",
            "build.gradle": "Java/Kotlin (Gradle)",
            "go.mod": "Go",
            "Cargo.toml": "Rust",
            "dbt_project.yml": "dbt",
            "airflow.cfg": "Apache Airflow",
            "docker-compose.yml": "Docker Compose",
            "Dockerfile": "Docker",
            ".github/workflows": "GitHub Actions",
            "terraform": "Terraform (IaC)",
            "spark": "Apache Spark",
        }

        data = self._get(f"/repos/{self.repo}/git/trees/HEAD", params={"recursive": "1"})
        if not data or "tree" not in data:
            return []

        paths = {item["path"].lower() for item in data["tree"]}
        found = []

        for file_hint, tech in STACK_FILES.items():
            if any(file_hint.lower() in p for p in paths):
                found.append(tech)

        return list(dict.fromkeys(found))  # remove duplicatas mantendo ordem

    # -------------------------------------------------------------------------
    # COMMITS
    # -------------------------------------------------------------------------

    def get_recent_commits(self, limit: int = 20) -> list[dict]:
        """Retorna os commits mais recentes do repositório."""
        data = self._get(f"/repos/{self.repo}/commits", params={"per_page": limit})
        if not data:
            return []

        commits = []
        for c in data:
            commits.append({
                "sha": c["sha"],
                "message": c["commit"]["message"].split("\n")[0],  # só primeira linha
                "date": c["commit"]["author"]["date"][:10],
                "author": c["commit"]["author"]["name"],
            })

        return commits

    # -------------------------------------------------------------------------
    # ISSUES
    # -------------------------------------------------------------------------

    def get_open_issues(self) -> list[dict]:
        """Retorna todas as issues abertas (exclui pull requests)."""
        data = self._get(
            f"/repos/{self.repo}/issues",
            params={"state": "open", "per_page": 50}
        )
        if not data:
            return []

        issues = []
        for i in data:
            if "pull_request" in i:  # pula PRs
                continue
            issues.append({
                "number": i["number"],
                "title": i["title"],
                "body": i.get("body") or "",
                "labels": [l["name"] for l in i.get("labels", [])],
                "created_at": i["created_at"][:10],
            })

        return issues

    def get_closed_issues(self, limit: int = 20) -> list[dict]:
        """Retorna issues fechadas recentemente (representa sprints concluídas)."""
        data = self._get(
            f"/repos/{self.repo}/issues",
            params={"state": "closed", "per_page": limit, "sort": "updated"}
        )
        if not data:
            return []

        issues = []
        for i in data:
            if "pull_request" in i:
                continue
            issues.append({
                "number": i["number"],
                "title": i["title"],
                "labels": [l["name"] for l in i.get("labels", [])],
                "closed_at": i["closed_at"][:10] if i.get("closed_at") else "—",
            })

        return issues

    # -------------------------------------------------------------------------
    # SPRINTS (GitHub Projects v2 via GraphQL)
    # -------------------------------------------------------------------------

    def get_sprints(self) -> list[dict]:
        """
        Busca iterações (sprints) do GitHub Projects v2 via GraphQL API.
        Retorna as sprints com seus itens e status.
        """
        owner, repo_name = self.repo.split("/")

        query = """
        query($owner: String!, $repo: String!) {
          repository(owner: $owner, name: $repo) {
            projectsV2(first: 5) {
              nodes {
                title
                items(first: 50) {
                  nodes {
                    fieldValues(first: 10) {
                      nodes {
                        ... on ProjectV2ItemFieldSingleSelectValue {
                          name
                          field { ... on ProjectV2SingleSelectField { name } }
                        }
                        ... on ProjectV2ItemFieldIterationValue {
                          title
                          field { ... on ProjectV2IterationField { name } }
                        }
                      }
                    }
                    content {
                      ... on Issue {
                        title
                        number
                        state
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """

        response = requests.post(
            "https://api.github.com/graphql",
            headers=self.headers,
            json={"query": query, "variables": {"owner": owner, "repo": repo_name}},
        )

        if response.status_code != 200:
            return []

        data = response.json()

        try:
            projects = data["data"]["repository"]["projectsV2"]["nodes"]
        except (KeyError, TypeError):
            return []

        sprints = []

        for project in projects:
            sprint_map = {}  # título da sprint → lista de itens

            for node in project["items"]["nodes"]:
                content = node.get("content")
                if not content:
                    continue

                issue_title = content.get("title", "")
                issue_state = content.get("state", "")
                sprint_title = None
                item_status = None

                for fv in node["fieldValues"]["nodes"]:
                    if not fv:
                        continue
                    field = fv.get("field") or {}
                    field_name = field.get("name", "") if field else ""

                    if field_name.lower() in ("iteration", "sprint", "iteração"):
                        sprint_title = fv.get("title", "Sprint")

                    if field_name.lower() == "status":
                        item_status = fv.get("name", "")

                if not sprint_title:
                    sprint_title = "Backlog / Sem sprint"

                if sprint_title not in sprint_map:
                    sprint_map[sprint_title] = []

                sprint_map[sprint_title].append({
                    "title": issue_title,
                    "status": item_status or ("Done" if issue_state == "CLOSED" else "In Progress"),
                })

            for sprint_title, items in sprint_map.items():
                sprints.append({"title": sprint_title, "items": items})

        return sprints

    def get_current_sprint_scope(self) -> dict | None:
        """
        Lê o Project mais recente (sprint atual) e retorna seu título e descrição.
        Essa descrição é o escopo que o usuário escreve no GitHub Project.

        Returns:
            dict com 'title', 'description' e 'short_description', ou None
        """
        owner, repo_name = self.repo.split("/")

        query = """
        query($owner: String!, $repo: String!) {
          repository(owner: $owner, name: $repo) {
            projectsV2(first: 10, orderBy: {field: UPDATED_AT, direction: DESC}) {
              nodes {
                id
                title
                shortDescription
                readme
              }
            }
          }
        }
        """

        response = requests.post(
            "https://api.github.com/graphql",
            headers=self.headers,
            json={"query": query, "variables": {"owner": owner, "repo": repo_name}},
        )

        if response.status_code != 200:
            return None

        data = response.json()

        try:
            projects = data["data"]["repository"]["projectsV2"]["nodes"]
        except (KeyError, TypeError):
            return None

        if not projects:
            return None

        # Pega o projeto mais recentemente atualizado
        project = projects[0]

        return {
            "title": project.get("title", ""),
            "description": project.get("readme") or project.get("shortDescription") or "",
            "short_description": project.get("shortDescription") or "",
        }
