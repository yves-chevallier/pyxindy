# xindy Manual

This is the migrated copy of the historic xindy 2.0 manual (Edition: February 1998) that
previously lived as HTML under `vendor/xindy-2.1/Doc/`. The content is unchanged aside
from light Markdown formatting so it is easier to browse alongside the rest of the docs.
Images referenced by the manual now live in `docs/assets/`.

Note: the Python port ships console scripts named `xindy-py`, `texindy-py`, and `makeindex-py`
instead of the originals referenced in the upstream text. Command semantics are unchanged.

### Python port entry points

- `xindy-py`: run the index processor on `.raw` with a `.xdy` style.
- `texindy-py`: convert LaTeX `.idx` to xindy `.raw`.
- `makeindex-py`: makeindex-compatible wrapper on top of xindy.
- `makeglossaries-py`: glossaries helper that routes to `makeindex-py`/xindy based on `.aux`.
