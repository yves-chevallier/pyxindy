# État de la migration xindy (CLISP → Python)

## Avancement global

- [x] Parseur S-expressions (`dsl/sexpr`) avec commentaires, strings, mots-clés.
- [x] Lecteur `.raw` → `RawIndexEntry`, support `:key`, `:tkey`, `:attr`, extras.
- [x] Interpréteur `.xdy` (`dsl/interpreter`) : `require`, `searchpath`, `define-*`, `markup-*`, `merge-to`, `sort-rule`, `#+FEATURE`, mapc/progn, basetypes (arabic, roman).
- [x] Modèle locref (`locref/*`) : classes standard/var, matching alphabets/enum, comparaisons, ranges basiques.
- [x] Construction d’index (`index/*`) : tri + sort-rule, merge-to, crossrefs, hiérarchie, regroupement par lettre, détection de plages contiguës.
- [x] Rendu (`markup/renderer`) : backend texte/TeX, directives `markup-*`, locref formats par attribut, ranges, crossrefs, groupes de lettres, profondeur max.
- [x] CLI principale (`xindy/cli.py`) : options `-M/-o/-L/-C/-l/-t`, `XINDY_SEARCHPATH`, charge style+raw, rend vers stdout/fichier, logging d’erreurs.
- [x] tex2xindy minimal (`tex/tex2xindy.py`) : conversion `.idx → .raw`, CLI avec encodage/logs, tests `infII`.
- [x] Snapshots attr2/attr3/ranges1 : fusion d’attributs/ranges par attribut corrigée (tests réactivés).
- [x] Modules/langues avancés : charge les modules (rule-sets, use-rule-set, inherit-from) et snapshots de langues `french`/`deutsch` vérifiés.
- [x] Outils TeX complets (options makeindex4) et gestion d’attributs complexes/manquants (wrapper makeindex4, compression d’espaces, log/output, attr auto).

## Couverture de tests (pytest)

- [x] 47 tests actuels passent (`uv run pytest`) : dsl, index, markup, raw, CLI, tex2xindy, snapshots `ex1/ex2/deep/simple/attr2/attr3/ranges1/french/deutsch`.
- [ ] Tests langues/modules supplémentaires (autres mappings/langues) à ajouter.

## Points restants pour 100% de migration

- [ ] Étendre encore le loader de modules/langues et ajouter des snapshots pour d’autres styles des dossiers `modules/` (règles, ordres de tri, alphabets).
- [ ] Compléter tex2xindy : options makeindex4, parsing TeX plus robuste (macros, escapes), pipeline CLI bout-en-bout.
- [ ] Documentation finale (README, usage CLI, exemples) et packaging.
- [ ] Vérifier les scripts d’erreur (err1/err2/xref-1) et scénarios makefile historiques.
