## xindy (Python port)

Ce dépôt héberge le portage progressif de **xindy** (flexible indexing system) de
CLISP vers Python.

### Utilisation rapide

- Générer un index depuis un `.raw` et un style `.xdy` :

  ```bash
  xindy -M path/to/style.xdy -o output.ind path/to/index.raw
  ```

- Convertir un fichier TeX `.idx` en `.raw` :

  ```bash
  uv run python -m xindy.tex.tex2xindy path/to/input.idx -o output.raw
  ```

- Utiliser l’interface type `makeindex` :

  ```bash
  uv run python -m xindy.tex.makeindex4 path/to/input.idx -o output.ind -t output.ilg -c
  ```

Les modules/styles xindy historiques (`xindy-src/xindy-2.1/modules`) sont
résolus automatiquement via `require`. Les options `-l/-c/-o/-t` sont supportées
par le wrapper `makeindex4`.

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
