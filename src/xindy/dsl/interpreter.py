"""Interpreter for the xindy style (.xdy) DSL."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from xindy.locref import (
    Alphabet,
    BaseType,
    CategoryAttribute,
    Enumeration,
    LayerElement,
    LocClassLayer,
    LocClassSeparator,
    StandardLocationClass,
    VarLocationClass,
    checked_make_standard_location_class,
    checked_make_var_location_class,
    make_category_attribute,
    prefix_match_for_radix_numbers,
    prefix_match_for_roman_numbers,
)

from .sexpr import Keyword, Symbol, parse_many


class StyleError(RuntimeError):
    """Raised when the interpreter encounters invalid input."""


@dataclass
class StyleState:
    """Holds the mutable state built while interpreting .xdy files."""

    basetypes: dict[str, BaseType] = field(default_factory=dict)
    location_classes: dict[str, StandardLocationClass | VarLocationClass] = field(
        default_factory=dict
    )
    attributes: dict[str, CategoryAttribute] = field(default_factory=dict)
    attribute_groups: list[list[str]] = field(default_factory=list)
    search_paths: list[Path] = field(default_factory=list)
    loaded_files: set[Path] = field(default_factory=set)
    letter_groups: list[str] = field(default_factory=list)
    sort_rules: list[tuple[str, str, bool]] = field(default_factory=list)
    sort_rule_orientations: list[str] = field(
        default_factory=lambda: ["forward"] * 8
    )
    merge_rules: list[tuple[str, str, bool]] = field(default_factory=list)
    markup_options: dict[str, object] = field(default_factory=dict)
    features: set[str] = field(default_factory=set)

    def register_basetype(self, basetype: BaseType) -> None:
        self.basetypes[basetype.name] = basetype


class StyleInterpreter:
    """Evaluate .xdy files into a :class:`StyleState`."""

    def __init__(self, state: StyleState | None = None):
        self.state = state or StyleState()
        self._file_stack: list[Path] = []
        if not self.state.basetypes:
            self._register_default_basetypes()

    def load(
        self,
        path: str | Path,
        *,
        extra_search_paths: Sequence[Path] | None = None,
    ) -> StyleState:
        """Interpret ``path`` and return the populated :class:`StyleState`."""
        if extra_search_paths:
            self.state.search_paths.extend(
                Path(p).resolve() for p in extra_search_paths
            )
        self._eval_file(Path(path))
        return self.state

    # ---------------------------- internal helpers ----------------------------

    def _register_default_basetypes(self) -> None:
        uppercase = tuple(chr(c) for c in range(ord("A"), ord("Z") + 1))
        lowercase = tuple(chr(c) for c in range(ord("a"), ord("z") + 1))
        digits = tuple(str(d) for d in range(10))
        self.state.register_basetype(Alphabet(name="ALPHA", symbols=uppercase))
        self.state.register_basetype(Alphabet(name="alpha", symbols=lowercase))
        self.state.register_basetype(Alphabet(name="digits", symbols=digits))
        self.state.register_basetype(
            Enumeration(
                name="arabic-numbers",
                base_alphabet=digits,
                match_func=lambda text: prefix_match_for_radix_numbers(text, 10),
            )
        )
        self.state.register_basetype(
            Enumeration(
                name="roman-numbers-uppercase",
                base_alphabet=tuple("IVXLCDM"),
                match_func=lambda text: prefix_match_for_roman_numbers(
                    text, lowercase=False
                ),
            )
        )
        self.state.register_basetype(
            Enumeration(
                name="roman-numbers-lowercase",
                base_alphabet=tuple("ivxlcdm"),
                match_func=lambda text: prefix_match_for_roman_numbers(
                    text, lowercase=True
                ),
            )
        )

    def _current_dir(self) -> Path:
        return self._file_stack[-1].parent if self._file_stack else Path.cwd()

    def _eval_file(self, path: Path) -> None:
        path = path.resolve()
        if path in self.state.loaded_files:
            return
        if not path.exists():
            raise FileNotFoundError(path)
        self.state.loaded_files.add(path)
        self._file_stack.append(path)
        try:
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = path.read_text(encoding="latin-1")
            forms = parse_many(content)
            pending_feature: str | None = None
            for form in forms:
                if pending_feature:
                    if pending_feature in self.state.features:
                        self._eval_form(form)
                    pending_feature = None
                    continue
                if isinstance(form, Symbol) and form.name.startswith("#+"):
                    pending_feature = form.name[2:]
                    continue
                self._eval_form(form)
        finally:
            self._file_stack.pop()

    def _eval_form(self, form: object) -> None:
        if not isinstance(form, list) or not form:
            return
        head = form[0]
        if not isinstance(head, Symbol):
            return
        # reader conditional #+FEATURE
        if head.name.startswith("#+"):
            feature = head.name[2:]
            if feature in self.state.features:
                for subform in form[1:]:
                    self._eval_form(subform)
            return
        dispatch = {
            "searchpath": self._handle_searchpath,
            "require": self._handle_require,
            "define-location-class": self._handle_define_location_class,
            "define-attributes": self._handle_define_attributes,
            "define-letter-groups": self._handle_define_letter_groups,
            "define-letter-group": self._handle_define_letter_group,
            "define-sort-rule-orientations": self._handle_define_sort_orientations,
            "sort-rule": self._handle_sort_rule,
            "merge-to": self._handle_merge_to,
            "markup-index": self._handle_markup_index,
            "markup-letter-group-list": self._handle_markup_letter_group_list,
            "markup-letter-group": self._handle_markup_letter_group,
            "markup-indexentry": self._handle_markup_indexentry,
            "markup-indexentry-list": self._handle_markup_indexentry_list,
            "markup-locref": self._handle_markup_locref,
            "markup-locref-list": self._handle_markup_locref_list,
            "markup-locref-layer": self._handle_markup_locref_layer,
            "markup-locclass-list": self._handle_markup_locclass_list,
            "markup-crossref-list": self._handle_markup_crossref_list,
            "markup-range": self._handle_markup_range,
            "progn": self._handle_progn,
        }
        if head.name == "mapc":
            self._handle_mapc(form[1:])
            return
        handler = dispatch.get(head.name)
        if handler:
            handler(form[1:])

    def _handle_searchpath(self, args: list[object]) -> None:
        if len(args) != 1 or not isinstance(args[0], list):
            raise StyleError("searchpath expects one list argument")
        new_paths = []
        for entry in args[0]:
            rel = self._stringify(entry)
            candidate = Path(rel)
            if not candidate.is_absolute():
                candidate = (self._current_dir() / candidate).resolve()
            new_paths.append(candidate)
        self.state.search_paths = new_paths

    def _handle_require(self, args: list[object]) -> None:
        if len(args) != 1:
            raise StyleError("require expects exactly one argument")
        target = self._stringify(args[0])
        resolved = self._resolve_module(target)
        if resolved is None:
            raise FileNotFoundError(f"Unable to locate required file: {target}")
        self._eval_file(resolved)

    def _handle_define_location_class(self, args: list[object]) -> None:
        if len(args) < 2:
            raise StyleError("define-location-class requires name and layers")
        name = self._stringify(args[0])
        layer_tokens = args[1]
        if not isinstance(layer_tokens, list):
            raise StyleError("layer list must be a list")

        kwargs = self._parse_keyword_args(args[2:])
        hierdepth = self._parse_int_option(kwargs.get("hierdepth"), default=0)
        contains_roman = any(
            isinstance(tok, (str, Symbol)) and "roman" in self._stringify(tok)
            for tok in layer_tokens
            if not isinstance(tok, Keyword)
        )
        default_join = 3 if hierdepth or contains_roman else 2
        join_length = self._parse_int_option(
            kwargs.get("min-range-length"),
            default=default_join,
        )
        is_var = kwargs.get("var", False)

        layers = self._build_locclass_layers(layer_tokens)
        if is_var:
            loccls = checked_make_var_location_class(name, layers, hierdepth)
        else:
            loccls = checked_make_standard_location_class(
                name,
                layers,
                join_length,
                hierdepth,
            )
        self.state.location_classes[name] = loccls

    def _handle_define_attributes(self, args: list[object]) -> None:
        if len(args) != 1 or not isinstance(args[0], list):
            raise StyleError("define-attributes requires one list argument")
        attr_groups: list[list[str]] = []
        for group in args[0]:
            if not isinstance(group, list):
                raise StyleError("attribute groups must be lists")
            converted = [self._stringify(item) for item in group]
            attr_groups.append(converted)
            for attr_name in converted:
                if attr_name not in self.state.attributes:
                    self.state.attributes[attr_name] = make_category_attribute(
                        attr_name
                    )
        self.state.attribute_groups.extend(attr_groups)

    def _handle_define_letter_groups(self, args: list[object]) -> None:
        if len(args) != 1 or not isinstance(args[0], list):
            raise StyleError("define-letter-groups expects one list argument")
        letters = [self._stringify(item) for item in args[0]]
        self.state.letter_groups = letters

    def _handle_define_letter_group(self, args: list[object]) -> None:
        if not args:
            raise StyleError("define-letter-group expects a name")
        name = self._stringify(args[0])
        kwargs = self._parse_keyword_args(args[1:])
        after = kwargs.get("after")
        before = kwargs.get("before")
        groups = list(self.state.letter_groups)
        if not groups:
            # seed with default alphabet if none provided yet
            if self.state.basetypes:
                first = next(iter(self.state.basetypes.values()))
                groups = list(first.base_alphabet)
        if after:
            marker = self._stringify(after)
            if marker in groups:
                idx = groups.index(marker) + 1
                groups.insert(idx, name)
                self.state.letter_groups = groups
                return
        if before:
            marker = self._stringify(before)
            if marker in groups:
                idx = groups.index(marker)
                groups.insert(idx, name)
                self.state.letter_groups = groups
                return
        if name not in groups:
            groups.append(name)
        self.state.letter_groups = groups

    def _handle_define_sort_orientations(self, args: list[object]) -> None:
        if not args:
            raise StyleError("define-sort-rule-orientations expects arguments")
        orientations = []
        for arg in args:
            if isinstance(arg, list):
                orientations.extend(self._coerce_orientation(item) for item in arg)
            else:
                orientations.append(self._coerce_orientation(arg))
        if not orientations:
            orientations = ["forward"] * 8
        self.state.sort_rule_orientations = orientations

    def _handle_sort_rule(self, args: list[object]) -> None:
        if len(args) < 2:
            raise StyleError("sort-rule requires pattern and replacement")
        pattern = self._stringify(args[0])
        replacement = self._stringify(args[1])
        again = False
        use_basic_regex = False
        for token in args[2:]:
            if isinstance(token, Keyword):
                if token.name == "again":
                    again = True
                if token.name == "bregexp":
                    use_basic_regex = True
        if use_basic_regex:
            pattern = (
                pattern.replace("\\(", "(")
                .replace("\\)", ")")
                .replace("{", "\\{")
                .replace("}", "\\}")
            )
        self.state.sort_rules.append((pattern, replacement, again))

    def _coerce_orientation(self, value: object) -> str:
        if isinstance(value, Symbol):
            return value.name.lower()
        if isinstance(value, str):
            return value.lower()
        raise StyleError("orientations must be string or symbol")

    def _handle_merge_to(self, args: list[object]) -> None:
        if len(args) < 2:
            raise StyleError("merge-to requires from/to")
        from_attr = self._stringify(args[0])
        to_attr = self._stringify(args[1])
        drop = False
        if len(args) > 2 and isinstance(args[2], Keyword) and args[2].name == "drop":
            drop = True
        self.state.merge_rules.append((from_attr, to_attr, drop))

    # ---------------------------- markup placeholders ----------------------------
    def _handle_markup_index(self, args: list[object]) -> None:
        self.state.markup_options["index"] = self._parse_markup_kwargs(args)

    def _handle_markup_letter_group_list(self, args: list[object]) -> None:
        self.state.markup_options["letter_group_list"] = self._parse_markup_kwargs(args)

    def _handle_markup_letter_group(self, args: list[object]) -> None:
        self.state.markup_options["letter_group"] = self._parse_markup_kwargs(args)

    def _handle_markup_indexentry(self, args: list[object]) -> None:
        entries = self.state.markup_options.setdefault("indexentries", {})
        kwargs = self._parse_markup_kwargs(args)
        depth = kwargs.pop("depth", 0)
        entries[depth] = kwargs

    def _handle_markup_indexentry_list(self, args: list[object]) -> None:
        self.state.markup_options["indexentry_list"] = self._parse_markup_kwargs(args)

    def _handle_markup_locref(self, args: list[object]) -> None:
        locrefs = self.state.markup_options.setdefault("locref", {})
        kwargs = self._parse_markup_kwargs(args)
        key = kwargs.get("attr") or "__default__"
        locrefs[key] = kwargs

    def _handle_markup_locref_list(self, args: list[object]) -> None:
        kwargs = self._parse_markup_kwargs(args)
        class_name = (
            self._stringify(kwargs["class"]) if "class" in kwargs else "__default__"
        )
        depth = self._parse_int_option(kwargs.get("depth"), default=0)
        lists = self.state.markup_options.setdefault("locref_lists", {})
        by_depth = lists.setdefault(class_name, {})
        by_depth[depth] = {key: value for key, value in kwargs.items() if key != "class"}
        # maintain legacy structure for simple uses
        if class_name == "__default__" and depth == 0:
            locref_list = self.state.markup_options.setdefault("locref_list", {})
            locref_list.update(kwargs)

    def _handle_markup_locref_layer(self, args: list[object]) -> None:
        kwargs = self._parse_markup_kwargs(args)
        class_name = (
            self._stringify(kwargs["class"]) if "class" in kwargs else "__default__"
        )
        depth = self._parse_int_option(kwargs.get("depth"), default=0)
        layer_idx = self._parse_int_option(kwargs.get("layer"), default=0)
        layers = self.state.markup_options.setdefault("locref_layers", {})
        by_depth = layers.setdefault(class_name, {})
        by_layer = by_depth.setdefault(depth, {})
        by_layer[layer_idx] = {
            key: value for key, value in kwargs.items() if key not in {"class", "depth", "layer"}
        }

    def _handle_markup_locclass_list(self, args: list[object]) -> None:
        kwargs = self._parse_markup_kwargs(args)
        self.state.markup_options["locclass_list"] = kwargs

    def _handle_markup_crossref_list(self, args: list[object]) -> None:
        self.state.markup_options["crossref_list"] = self._parse_markup_kwargs(args)

    def _handle_markup_range(self, args: list[object]) -> None:
        kwargs = self._parse_markup_kwargs(args)
        self.state.markup_options["range"] = kwargs

    def _parse_markup_kwargs(self, args: list[object]) -> dict[str, object]:
        kwargs: dict[str, object] = {}
        idx = 0
        while idx < len(args):
            token = args[idx]
            if isinstance(token, Keyword):
                key = token.name.replace("-", "_")
                if idx + 1 < len(args) and not isinstance(args[idx + 1], Keyword):
                    kwargs[key] = args[idx + 1]
                    idx += 2
                else:
                    kwargs[key] = True
                    idx += 1
            else:
                idx += 1
        return kwargs

    def _handle_mapc(self, args: list[object]) -> None:
        # crude handling of (mapc #'(lambda (x) (pushnew x *features*)) '(STEP1 ...))
        for arg in args:
            if (
                isinstance(arg, list)
                and arg
                and isinstance(arg[0], Symbol)
                and arg[0].name == "quote"
                and isinstance(arg[1], list)
            ):
                for sym in arg[1]:
                    if isinstance(sym, Symbol):
                        self.state.features.add(sym.name)

    def _handle_progn(self, args: list[object]) -> None:
        for subform in args:
            self._eval_form(subform)

    # ------------------------------------------------------------------ parsing helpers

    def _parse_keyword_args(self, tokens: list[object]) -> dict[str, object]:
        result: dict[str, object] = {}
        idx = 0
        while idx < len(tokens):
            token = tokens[idx]
            if not isinstance(token, Keyword):
                raise StyleError(f"Unexpected token {token!r} in argument list")
            key = token.name
            if key in {"var"}:
                result[key] = True
                idx += 1
                continue
            if idx + 1 >= len(tokens):
                raise StyleError(f"Keyword :{key} missing value")
            result[key] = tokens[idx + 1]
            idx += 2
        return result

    def _parse_int_option(self, value: object | None, default: int) -> int:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return int(value)
        if isinstance(value, Symbol):
            if value.name == "none":
                return 0
            return int(value.name)
        if isinstance(value, str):
            if value.lower() == "none":
                return 0
            return int(value)
        raise StyleError(f"Cannot convert {value!r} to integer option")

    def _build_locclass_layers(self, layers: list[object]) -> list[LayerElement]:
        result: list[LayerElement] = []
        idx = 0
        while idx < len(layers):
            token = layers[idx]
            if isinstance(token, Keyword) and token.name == "sep":
                idx += 1
                if idx >= len(layers):
                    raise StyleError("Unexpected end of list after :sep")
                sep_value = self._stringify(layers[idx])
                result.append(LocClassSeparator(separator=sep_value))
            else:
                basetype_name = self._stringify(token)
                basetype = self.state.basetypes.get(basetype_name)
                if basetype is None:
                    raise StyleError(f"Unknown basetype '{basetype_name}'")
                result.append(LocClassLayer(basetype=basetype))
            idx += 1
        return result

    def _resolve_module(self, name: str) -> Path | None:
        candidate = Path(name)
        if candidate.is_absolute() and candidate.exists():
            return candidate
        search_roots = [self._current_dir(), *self.state.search_paths]
        seen = set()
        for root in search_roots:
            if root in seen:
                continue
            seen.add(root)
            target = (root / name).resolve()
            if target.exists():
                return target
        return None

    def _stringify(self, value: object) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, Symbol):
            return value.name
        raise StyleError(f"Expected string-like value, got {value!r}")


__all__ = ["StyleInterpreter", "StyleState", "StyleError"]
