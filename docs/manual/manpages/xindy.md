# xindy (manpage)

Edition February 1997 — a flexible indexing system.

## Synopsis

```
xindy [-t] [-l logfile] [-o outfile] [-f filterprog] [-L n] [-v] indexstyle rawindex
```

## Description

`xindy` is a general-purpose index processor driven by an index style
and a raw index file.

## Options

- `-o outfile` — write the tagged index to `outfile` (default: `rawindex` with `.ind`).
- `-l logfile` — write logging information to `logfile`.
- `-f filterprog` — run `filterprog` on the raw index before reading (stdin → stdout).
- `-L n` — set logging level to 1, 2, or 3.
- `-t` — activate `markup-trace`, emitting symbolic markup tags.
- `-v` — display the version number.
- `-help` — show a summary of command-line options.

## See also

`tex2xindy(1L)`, `makeindex(1L)`, `makeindex4(1L)`

For format details of `indexstyle` and `rawindex`, see the main manual.
