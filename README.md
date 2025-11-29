## xindy (Python port)

Ce dépôt héberge le portage progressif de **xindy** (flexible indexing system) de
CLISP vers Python.

### Développement local

1. Créer un virtualenv et installer les dépendances :

   ```bash
   uv sync --extra dev  # ou pip install -e .[dev]
   ```

2. Lancer les tests et linters :

   ```bash
   uv run pytest
   uv run ruff check
   ```

3. Tester le binaire :

   ```bash
   python -m xindy --version
   ```

Le plan détaillé et la feuille de route sont maintenus dans `PLAN.md`.
