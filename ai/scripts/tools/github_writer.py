"""
github_writer.py
Responsável por criar issues e organizá-las no GitHub Projects v2.
"""

import requests


class GitHubWriter:
    """
    Encapsula todas as chamadas de escrita à GitHub API e GraphQL.
    """

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str, repo_full_name: str):
        if not token:
            raise ValueError("GITHUB_TOKEN não encontrado. Verifique seu arquivo .env")

        self.repo = repo_full_name
        self.owner, self.repo_name = repo_full_name.split("/")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _graphql(self, query: str, variables: dict) -> dict:
        """Executa uma query GraphQL na GitHub API."""
        response = requests.post(
            "https://api.github.com/graphql",
            headers=self.headers,
            json={"query": query, "variables": variables},
        )
        response.raise_for_status()
        data = response.json()
        if "errors" in data:
            raise RuntimeError(f"GraphQL error: {data['errors']}")
        return data

    # -------------------------------------------------------------------------
    # ISSUES
    # -------------------------------------------------------------------------

    def create_issue(self, title: str, body: str = "", labels: list[str] = None) -> dict:
        """
        Cria uma issue no repositório.

        Returns:
            dict com 'number', 'id' (node_id) e 'url' da issue criada
        """
        payload = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels

        response = requests.post(
            f"{self.BASE_URL}/repos/{self.repo}/issues",
            headers=self.headers,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

        return {
            "number": data["number"],
            "node_id": data["node_id"],
            "url": data["html_url"],
        }

    # -------------------------------------------------------------------------
    # GITHUB PROJECTS v2
    # -------------------------------------------------------------------------

    def get_project_id(self, project_title: str = None) -> tuple[str, str]:
        """
        Busca o ID do GitHub Project vinculado ao repositório.
        Se project_title for informado, filtra pelo nome.
        Retorna (project_node_id, project_title).
        """
        query = """
        query($owner: String!, $repo: String!) {
          repository(owner: $owner, name: $repo) {
            projectsV2(first: 10) {
              nodes { id title }
            }
          }
        }
        """
        data = self._graphql(query, {"owner": self.owner, "repo": self.repo_name})
        projects = data["data"]["repository"]["projectsV2"]["nodes"]

        if not projects:
            raise RuntimeError(
                f"Nenhum GitHub Project encontrado em {self.repo}.\n"
                "Crie um projeto em: https://github.com/users/{self.owner}/projects"
            )

        if project_title:
            match = next((p for p in projects if project_title.lower() in p["title"].lower()), None)
            if match:
                return match["id"], match["title"]

        # retorna o primeiro projeto encontrado
        return projects[0]["id"], projects[0]["title"]

    def add_issue_to_project(self, project_id: str, issue_node_id: str) -> str:
        """
        Adiciona uma issue ao GitHub Project.
        Retorna o item_id gerado no projeto.
        """
        mutation = """
        mutation($projectId: ID!, $contentId: ID!) {
          addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
            item { id }
          }
        }
        """
        data = self._graphql(mutation, {
            "projectId": project_id,
            "contentId": issue_node_id,
        })
        return data["data"]["addProjectV2ItemById"]["item"]["id"]

    def get_status_field(self, project_id: str) -> tuple[str, str]:
        """
        Busca o ID do campo Status e o ID da opção 'Todo' (ou equivalente).
        Retorna (field_id, option_id).
        """
        query = """
        query($projectId: ID!) {
          node(id: $projectId) {
            ... on ProjectV2 {
              fields(first: 20) {
                nodes {
                  ... on ProjectV2SingleSelectField {
                    id
                    name
                    options { id name }
                  }
                }
              }
            }
          }
        }
        """
        data = self._graphql(query, {"projectId": project_id})
        fields = data["data"]["node"]["fields"]["nodes"]

        for field in fields:
            if field.get("name", "").lower() == "status":
                # procura opção "Todo", "To Do", "Backlog" ou a primeira disponível
                options = field.get("options", [])
                todo_option = next(
                    (o for o in options if o["name"].lower() in ("todo", "to do", "backlog", "a fazer")),
                    options[0] if options else None
                )
                if todo_option:
                    return field["id"], todo_option["id"]

        return None, None

    def set_item_status(self, project_id: str, item_id: str, field_id: str, option_id: str):
        """Define o status de um item no projeto."""
        mutation = """
        mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
          updateProjectV2ItemFieldValue(input: {
            projectId: $projectId
            itemId: $itemId
            fieldId: $fieldId
            value: { singleSelectOptionId: $optionId }
          }) {
            projectV2Item { id }
          }
        }
        """
        self._graphql(mutation, {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "optionId": option_id,
        })
