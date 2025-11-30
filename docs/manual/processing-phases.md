# Processing Phases

## The Startup Phase

After the system is started, xindy reads in the index style that
is passed as a command line argument. Each `require` command is
executed and the internal data structures representing the index style
are built up. The index style must completely be read in before the
raw index can be read.

## The Processing Phase

The processing phase starts with reading the complete raw index. The
name of the raw index file must be passed via the command line. All
index entries are read in and pre-processed. All attributes and
cross reference classes are checked if they are already known to the
system. All strings representing location references are matched
against all known location classes. Appropriate warnings are issued,
if errors are encountered.

After the raw index has completely been read in, the
location references of each index entry are merged, separated and
sorted and the building of ranges takes place. This phase is the most
complex one and we will describe it in detail.

1. All location references are separated according to the class they
   belong to. These groups are called _location class groups_. Possible
   groups are all defined location and crossref classes. See the
   commands `define-location-class` and `define-crossref-class` for a
   description of how these classes can be defined. The classes are
   sorted according to an order defined with
   `define-location-class-order`.
2.  The processing of each location class group differs for location
    classes and crossref classes:

    - Cross references are sorted lexicographically based on the
      ISO-Latin alphabet.
    - For location references, consider the following list:

        ```text
        _13_, _14_, _15_, _18_, **12**, **13**, **14**, **16**, 14, 16
         ```

    Italics use the `important` attribute, bold values use
    `definition`, and unformatted values are `default`. Assume these
    attribute groups:

    ```lisp
    (define-attribute-groups (("definition" "important")
                              ("default")))

    (merge-to "definition" "default" :drop)
    ```

    Substitution rules turn the list into:

     > _13_, _14_, _15_, _18_, **12**, **16**, 14, 16

     because the attribute groups implicitly define `"definition"`
     substituting `"important"`.

     `merge-to` adds helper references (shown in parentheses) to aid
     range building:

     > _13_, _14_, _15_, _18_, **12**, **16**, (13), 14, (15), 16, (18)

     Parents are the original values, while the generated entries are
     _children_ used only for range construction.

     Ranges are then built per attribute. Because `:drop` is set, the
     process starts with the `default` attribute, producing the range
     `13--16`. The children (13) and (15) were used to form that range,
     so parents _13_ and _15_ are dropped. After unsuccessful attempts
     to extend ranges and removing (18), the remaining list is:

     > _14_, _18_, **12**, **16**, 13--16

     Attributes are finally ordered and merged lexicographically,
     yielding:

     > (**12**, _14_, **16**, _18_) (13--16)

After all index entries have been processed the letter groups are
formed and the index entries and location references are transformed
into tree like structures as defined in the index style.

## The Markup Phase

After the index has completely been processed, the markup phase
traverses the tree-like structure of the index. Each step triggers the
appropriate markup events resulting in the emitting of markup tags.
This phase can be traced by using the command line option `-t`.

