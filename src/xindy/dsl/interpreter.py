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
    sort_rules: list[tuple[str, str]] = field(default_factory=list)
    sort_rule_orientations: list[str] = field(
        default_factory=lambda: ["forward"] * 8
    )

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
            for form in parse_many(content):
                self._eval_form(form)
        finally:
            self._file_stack.pop()

    def _eval_form(self, form: object) -> None:
        if not isinstance(form, list) or not form:
            return
        head = form[0]
        if not isinstance(head, Symbol):
            return
        dispatch = {
            "searchpath": self._handle_searchpath,
            "require": self._handle_require,
            "define-location-class": self._handle_define_location_class,
            "define-attributes": self._handle_define_attributes,
            "define-letter-groups": self._handle_define_letter_groups,
            "define-sort-rule-orientations": self._handle_define_sort_orientations,
            "sort-rule": self._handle_sort_rule,
        }
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
        join_length = self._parse_int_option(kwargs.get("min-range-length"), default=2)
        hierdepth = self._parse_int_option(kwargs.get("hierdepth"), default=0)
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
        self.state.sort_rules.append((pattern, replacement))

    def _coerce_orientation(self, value: object) -> str:
        if isinstance(value, Symbol):
            return value.name.lower()
        if isinstance(value, str):
            return value.lower()
        raise StyleError("orientations must be string or symbol")

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
