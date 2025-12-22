# makeindex4 (manpage)

Edition February 1997 — wrapper around xindy.

## Synopsis

```text
makeindex4 [options]...
```

## Description

`makeindex4` is a wrapper that uses `xindy` as a replacement for
`makeindex`. It aims for compatibility with `makeindex` options and
warns about unsupported ones. Requires `tex2xindy` and `xindy`.

## Python port notes

The Python port implements common `makeindex` flags plus additional compatibility:

- Supports `-c/-l/-o/-t` and `-g/-q/-r/-p/-s`, as well as multiple `.idx` inputs.
- `-s` accepts `.xdy` or a subset of `.ist` keys (unsupported keys emit warnings).
- `-i` reads from stdin (output defaults to stdout if `-o` is omitted).
- `-p any|odd|even` uses the corresponding `.log` file to infer the starting page.

## See also

`xindy(1L)`, `makeindex(1L)`, `tex2xindy(1L)`
