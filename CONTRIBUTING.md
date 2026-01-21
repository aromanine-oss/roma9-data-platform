\# Contributing to roma9-data-platform



This project follows a team-oriented Git workflow, even when developed by a single contributor.



\## Branching strategy

\- main: stable, production-ready code

\- feature/\*: all development work



\## Workflow

1\. Pull latest main

2\. Create a feature branch

3\. Commit small, focused changes

4\. Open a Pull Request

5\. Merge into main



\## Commit convention

<type>(scope): description



Types:

\- feat

\- fix

\- refactor

\- docs

\- chore

\- test



\## Data versioning rules

\- Raw and large data files are not versioned

\- Generated artifacts are ignored

\- Git tracks logic, schemas and documentation



\## dbt rules

\- dbt\_packages/ is ignored

\- packages.yml and package-lock.yml are versioned

\- Models must include tests and documentation when applicable



