## xindy (Python port)

Ce dépôt héberge le portage progressif de **xindy** (flexible indexing system) de
CLISP vers Python.

### Installation

```bash
uv sync            # installe les dépendances
uv run pip install -e .  # ou uv build && pip install dist/xindy-*.whl
```

### Utilisation rapide

- Générer un index depuis un `.raw` et un style `.xdy` :

  ```bash
  uv run xindy -M path/to/style.xdy -o output.ind path/to/index.raw
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

### CLI xindy

```bash
uv run xindy [-M style.xdy] [-o output.ind] [-L searchpath] [-C encoding] [-l logfile] [-t] input.raw
```

- `-M/--module` : style `.xdy` à utiliser (par défaut `<raw>.xdy`)
- `-o/--output` : cible du rendu (`stdout` si absent)
- `-L/--searchpath` : chemins additionnels pour `require` (cumule avec `XINDY_SEARCHPATH`)
- `-C/--codepage` : encodage de sortie (utf-8 par défaut)
- `-l/--log` : écrit un log succinct
- `-t/--trace` : affiche les traces Python en cas d’erreur

### tex2xindy

```bash
uv run tex2xindy input.idx -o output.raw --input-encoding latin-1 --output-encoding utf-8
```

- Gère hiérarchies `!`, affichage `@`, encap `|`, macros TeX basiques/escapes, crossrefs `see{target}` → `:xref`.
- Produit des `:tkey` quand l’affichage diffère du tri.

### makeindex4

```bash
uv run makeindex4 input.idx -o output.ind -t output.ilg [-c] [-l]
```

- `-c` : compresse les espaces dans les clés (comme makeindex)
- `-l` : ignore les espaces pour le tri (insert un `sort-rule " " ""`)
- Génère un style temporaire, détecte les attributs/crossrefs, charge `tex/makeidx4.xdy`.

### Exemples rapides

- Rejouer un fixture historique :

  ```bash
  uv run xindy -M xindy-src/xindy-2.1/tests/ex1.xdy \
        -o /tmp/ex1.ind xindy-src/xindy-2.1/tests/ex1.raw
  ```

- Chaîner `.idx → .ind` en une commande :

  ```bash
  uv run makeindex4 xindy-src/xindy-2.1/tests/infII.idx -o /tmp/infII.ind
  ```

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
