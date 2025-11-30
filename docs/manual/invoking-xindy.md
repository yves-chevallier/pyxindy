# Invoking xindy

## Command Line Options

The following command line options are accepted:

```text
xindy  [-h] [-t] [-v] [-l logfile] [-o outfile]
       [-L n] [-f filterprog]
       indexstyle raw-index
```

The argument `indexstyle` names a file, containing the index style
description. The argument `raw-index` names a file, containing the
raw index. Both arguments are mandatory.

- **`-h`** Gives a short summary of all command line options.
- **`-l`** Writes helpful information into the specified
  `logfile`. For example, the keyword mappings are written into this
  file, so one can check if the intended mappings were actually
  performed this way.
- **`-o`** Explicitly defines the name of the `output` file. If not
  given, the name of the `raw-index` is used with its extension
  changed to ``.ind`' (or added, if it had no extension at all).
- **`-t`** Enters tracing mode of the symbolic markup tags. The
  format of the emitted tags can be defined with the command
  `markup-trace`.
- **`-L`** Sets the xindy logging-level to _n_.
- **`-f`** Runs `filterprog` on `raw-index` before reading. The program
  must act as a filter reading from stdin and writing to stdout. The
  most obvious use of this option in conjunction with TeX is to run
  `-f tex2xindy` on the index file prior to reading the entries into
  xindy.
- **`-v`** Shows the version number of xindy.

Errors and warnings are reported to `stdout` and additionally to
the logfile if `-l` was specified.

## Search Path

The system uses the concept of a _search path_ for finding the
index style files and modules. The searchpath can be set with the
environment variable `XINDY_SEARCHPATH` which must contain a list
of colon-separated directories. If it ends with a colon, the built-in
searchpath is added to the entire searchpath. See the command
`searchpath` for further details.
