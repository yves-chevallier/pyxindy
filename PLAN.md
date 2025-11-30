# Plan de portage de xindy (CLISP → Python)

## 1. Architecture actuelle (résumé)
- `src/base.lsp` expose le socle partagé : gestion des paquets, macros utilitaires (`info`, `oops`, `assert!`), journalisation, helpers de slots CLOS, fonctions d’exit. Il héberge aussi des primitives génériques (ex. `split-list`) utilisées partout.
- `src/locref.lsp` décrit les types structurants des localisation (classes de pages, séparateurs, références simples/rangées, crossrefs) et les algorithmes pour parser/comparer des chaînes de localisation.
- `src/idxstyle.lsp` implémente l’interpréteur des fichiers `.xdy` : définition des attributs, classes, alphabets, règles d’ordonnancement, chargement de modules (`modules/lang`, `modules/ord`, …), système de `*features*`, lecture récursive de fichiers de style.
- `src/index.lsp` gère le cœur métier : lecture de `.raw` (S-expr), création et fusion des entrées, construction des groupes de lettres, application des règles de tri/merge, génération des structures finales avant output.
- `src/markup.lsp` contient le moteur de rendu (TeX/LaTeX, plain text, …). Il s’appuie sur les méthodes `do-markup-*` pour produire `.ind`, gère les options `:tree`, `:flat`, hiérarchies, séparateurs, etc.
- `src/tex2xindy.l` (LEX) convertit des fichiers `.idx` TeX en `.raw`. `makeindex4.in` et `xindy.in` orchestrent CLI, variables d’environnement et chemins de modules.
- `modules/` regroupe des styles pré-définis (alphabets par langue, règles typographiques, markup TeX). Chaque module est un fichier Lisp chargé via `require`.
- `tests/` contient des couples `.raw` + `.xdy` + `.cmp` (résultat attendu) et quelques scripts `.sh` pour valider des erreurs. Le Makefile exécute `xindy` sur chaque jeu puis compare avec `cmp`.
- Flux global : `tex2xindy` (ou autre producteur) → `.raw` → interprétation `.xdy` → construction `index` (tri/mapping/ranges) → `markup` → fichier `.ind`.

## 2. Architecture Python cible
- Créer un paquet `xindy/` structuré (p.ex. `core/`, `dsl/`, `locref/`, `index/`, `markup/`, `cli/`, `tex/`).
- Représenter les concepts CLOS par des `dataclasses`/classes Python : `LocationClass`, `LocationReference`, `IndexEntry`, `LetterGroup`, etc., avec API proche des getters/setters existants.
- Implémenter un parseur S-expression (inspiré du format `.raw`) et un petit interpréteur dédié au DSL `.xdy` : support des formes utilisées (`defun`, `progn`, `mapc`, `#+/-`, `define-*`, `markup-*`, `sort-rule`, etc.). Objectif : compatibilité sans devoir embarquer un interpréteur CL généraliste.
- Remplacer les dépendances CL externes par des équivalents Python : `re` (regex) pour `sort-rule`/`map-attributes`, `functools`/`itertools` pour les opérations sur listes, `logging` natif, etc.
- Isoler les modules `.xdy` dans des ressources Python (précompilés ou chargés via parseur) et prévoir un loader qui respecte `XINDY_SEARCHPATH`.
- Construire une CLI (`python -m xindy` ou entrée `xindy/__main__.py`) qui accepte les mêmes options clés que l’outil original et qui orchestre chargement style + raw + markup.
- Prévoir une API programmable (p.ex. `xindy.process(style_path, raw_path, output, options)`), pour faciliter les tests automatisés.

## 3. Stratégie TDD et couverture de tests
- **Socle** : introduire `pytest` avec linting basique. Chaque composant port écope de tests unitaires (parser `.raw`, parser `.xdy`, algorithmes de tri, ranges, mappings).
- **Fixtures d’entrée** : réutiliser les fichiers existants dans `xindy-src/xindy-2.1/tests/` comme données de test. Fournir des helpers pytest pour lire `.raw`/`.xdy`/`.cmp`.
- **Tests incrémentaux** : 
  - Étapes précoces : tests unitaires sur les parseurs et les dataclasses, plus quelques snapshots sur la construction de structures internes à partir de `startup.raw`.
  - Dès que le pipeline minimal fonctionne, créer une suite `tests/integration/test_regression.py` qui itère sur un sous-ensemble des jeux `attr1`, `startup`, `ex1`, compare la sortie `.ind` générée avec `.cmp`.
  - Activer progressivement l’ensemble complet (`ALLTESTS` du Makefile) en fonction des fonctionnalités supportées (ranges, mappings, langues, erreurs).
  - Reporter les tests d’erreur (`err1`, `err2`, `xref-1.sh`) pour vérifier les messages et codes retour via `subprocess`/`CliRunner`.
- **Automatisation** : fournir une cible `pytest -m integration` équivalente au `make testsuite` historique pour faciliter la CI. Les tests devront isoler les chemins générés pour éviter d’écrire dans le dépôt d’origine.

## 4. Plan d’exécution par étapes
| Étape | Objectif principal | Livrables clés | Validation TDD |
| --- | --- | --- | --- |
| 0. Préparation | Structurer le projet Python (`src/`, `tests/`), config `pyproject`, outilage (`pytest`, `ruff`). Documenter l’installation. | Structure de package, config CI simple. | Tests vides + check lint/codestyle pour assurer pipeline prêt. |
| 1. Parseurs S-expr | Porter un parseur S-expression tolérant (commentaires `;`, symboles, strings) et lecteur `.raw` → `RawIndexEntry` Python. Inclure support basique de `:key`, `:locref`, `:attr`. | Module `xindy.dsl.sexpr`, `xindy.raw.reader`, dataclasses. | Tests unitaires sur `tests/*raw` (ex. `startup.raw` → 13 entrées). |
| 2. Socle `base` | Implémenter `xindy.core.base`: gestion des features (`FeatureSet`), logging, erreurs, `split_list`, conversion d’arguments, pour préparer l’interprète `.xdy`. | API pythonique + docstrings + mapping minimal de macros. | Tests sur `split_list`, `FeatureSet`, `assert!` via pytest. |
| 3. Modèle locref | Recréer `locref.lsp`: classes de localisation (standard, var, crossref), parsing des chaînes par alphabet, ranges, comparateurs, caches. | `xindy.locref` avec dataclasses + parser de chaine + matchers. | Tests unitaires dérivés des cas `ranges1.raw`, `startup.raw`. |
| 4. Interpréteur `.xdy` minimal | Construire le moteur de style : parse `.xdy`, évaluer `define-*`, charger modules, gérer `#+FEATURE`. Supporter les formes utilisées dans `startup.xdy`, `attr*.xdy`. | `xindy.dsl.interpreter`, module loader, représentation `IndexStyle`. | Tests scriptés : exécuter `startup.xdy` et vérifier que les classes/attributs attendus existent. |
| 5. Construction d’index | Implémenter l’équivalent de `index.lsp`: fusion des entrées, tri par règles alphabétiques, grouping, hiérarchies, ranges/crossrefs. Supporter custom `sort-rule`. | `xindy.index.builder`, `xindy.index.models`. | Tests unitaires ciblés (tri simple, ranges). Lancer première intégration `startup` → `.cmp`. |
|   ↳ état courant | Parser `.raw` + `.xdy` produisent désormais un objet `Index` avec `IndexLetterGroup`/`IndexNode` (hiérarchies, fusion de locrefs, plages numériques basiques), prennent en compte les `sort-rule` simples, appliquent les premiers `merge-to` (redirection/dropping d’attributs), capturent les crossrefs (entrées sans locref) et exposent les marqueurs de progression (10 % → 100 %). | Modules `xindy.index.builder`, `.hierarchy`, `.grouping`, `.order`. | Tests unitaires `tests/index/*` basés sur `attr1`, `simple.*`, `sort-rule.*`, `merge.*`, `crossref.*`. |
|   ↳ prochaines étapes | Étendre les nœuds pour gérer mapping/crossrefs avancés (avec messages `verified/unverified`) et préparer les compteurs/progressions nécessaires à `markup`. | À implémenter : validations crossrefs, follow-attributes, calcul fin des pourcentages dynamiques, support des ranges non numériques, amortissement `sort-rule` complet. | Nouveaux tests sur `ex1`, `ranges1`, `mappings`, `xref-1`. |
|   ↳ reste à faire (étapes détaillées) | 5a. Support de `sort-rule` et des alphabets personnalisés ✅ • 5b. Fusion/mapping des attributs (`merge-to`, `map-attributes`) ✅ • 5c. Crossrefs (`add-crossref`) et follow-attributes (structure en place, validation/rendu à finaliser) • 5d. Calcul des statistiques (pourcentages, ordres de traitement) — progrès partiel (marqueurs 10‑100 %, reste à intégrer au rendu) • 5e. Couche d’intégration `raw+style` → `Index` pour tous les jeux de tests historiques. | Modules `xindy.index.sorting`, `.merge`, `.crossref`, instrumentation du builder. | Tests unitaires + premières intégrations (`attr1`, `ex1`, `ranges1`, `mappings`, `xref-1`). |
| 6. Markup & output | Porter `markup.lsp` pour générer TeX/texte. Support `markup-index`, `markup-indexentry`, `markup-locref`, `markup-letter-group`, `:tree/:flat`. | `xindy.markup`, générateur CLI occupant `stdout`. | Tests de rendu sur `ex1`, `ex2`, `deep`. Comparaison stricte avec `.cmp`. |
|   ↳ état courant | Renderer texte configurable (groupes, locrefs, ranges, crossrefs, templates d’entrée, wrappers index/groupe, profondeur max). Les directives `markup-*` sont collectées par l’interpréteur et transposées en config du renderer. | Module `xindy.markup`. | Tests unitaires `tests/markup/*` utilisant les fixtures synthétiques. |
|   ↳ sous-étapes | 6a. Implémenter le backend de rendu (structure → flux) ✅ • 6b. Support des options `markup-*` et du mode verbose (partiel) • 6c. Gestion des ranges/crossrefs au rendu (partiel) • 6d. Snapshots `.ind` pour `ex1`, `ex2`, `deep` et mapping vers les options TeX/LaTeX. | Module `xindy.markup`. | Tests de rendu + snapshots. |
| 7. CLI `xindy` | Implémenter `xindy/cli.py` (argparse), gestion des options (`-o`, `-l`, `-L`, `-t`, `-M`, `-C`, etc.), variables d’environnement (`XINDY_SEARCHPATH`). Créer entrée console script. | CLI fonctionnelle + doc (README). | Tests CLI (via `pytest` + `CliRunner`) sur `attr1`, `attr2`, `err1/err2`. |
|   ↳ état courant | CLI argparée disponible (`-M/-o/-L/-C/-l/-t`), chargement style + raw, rendu vers stdout/fichier, support `XINDY_SEARCHPATH`, erreurs loguées. | Tests CLI `tests/test_cli.py` (stdout vs fichier, --version). | |
| 8. Modules et langues | Porter/convertir les fichiers dans `modules/` vers du Python (ou générer des `.json` compilés). S’assurer que les tests `french`, `deutsch`, `mappings`, `ranges1`, `xref-1` passent. | Données modules, loader configurable, doc. | Étendre la suite d’intégration pour couvrir `ALLTESTS` du Makefile. |
| 9. Outils TeX | Réimplémenter `tex2xindy` et `makeindex4` en Python: parsing `.idx`, conversion `raw`, options du man. Ajouter tests dédiés (`infII`, `makeindex4` scenario). | `xindy.tex.tex2xindy`, CLI(s), doc manpage Py. | Tests d’intégration: générer `.raw` depuis `infII.idx`, puis pipeline complet comparé à `.cmp`. |
| 10. CLI/CI finalisation | Nettoyage, doc utilisateur (README + tutoriel), packaging (wheel), scripts d’import pour modules custom, exemples. | Docs, packaging, guidelines de contribution. | Re-lancer toute la suite de régression + vérifications manuelles (échantillons réels). |

## 5. Alignement TDD ↔ fonctionnalités
- **Phase 1‑3** : priorités unitaires pour verrouiller les parseurs/datatypes. Objectif : aucun test d’intégration tant que la représentation interne n’est pas stabilisée.
- **Phase 4** : ajouter tests sur l’interpréteur en s’appuyant sur de très petits styles (`startup.xdy`). Détecter rapidement les écarts de syntaxe.
- **Phase 5-6** : introduction des premiers tests d’intégration (pipeline complet). Maintenir un snapshot des sorties `.ind` dans `tests/expected`. Utiliser `pytest` parametrized pour comparer toutes les paires `.raw/.xdy`.
- **Phase 7-9** : tests CLI + tests d’erreurs (scripts `err1.sh`, `err2.sh`, `xref-1.sh`) rejoués en Python. L’objectif est de garantir les codes retour et messages d’erreur identiques, afin de préserver la compatibilité avec les workflows existants.
- **Couverture continue** : chaque correction de bug doit d’abord reproduire l’écart via un test (unitaire ou intégration), ensuite la solution est appliquée. Les tests `ALLTESTS` servent de garde-fou final avant release.

Ce plan fournit la visibilité nécessaire pour aborder le portage intégral en plusieurs sessions, tout en gardant des étapes livrables et testables dès les premières fonctionnalités.
