# Command List

Here is the complete list of xindy's commands that may be used in
the index style. The symbol `name` always refers to a string. We
separate the commands into the _processing_ and
_markup_ commands. The commands are listed in alphabetical order.

The parenthesis `` [`' and  ``]` ' denote optional parts of the
syntax and ``{ `' and ``}`' denote the grouping of elements. A
vertical bar indicates alternatives. However, the enclosing round
braces _are_ part of the syntax and must be supplied.

## Processing Commands

Here follows the list of processing commands.

### define-alphabet

```text
(define-alphabet name string-list)
```

Defines `name` to be the alphabet consisting of all elements of the
`string-list`. Examples:

```text
  (define-alphabet "example-alphabet" ("An" "Example" "Alphabet"))
```

defines an alphabet consisting of exactly three symbols. For the
successor relationship holds: `succ("An")="Example"` and
`succ("Example")="Alphabet"`. The built-in alphabet `digits` is
defined as follows:

```text
  (define-alphabet "digits"
                   ("0" "1" "2" "3" "4" "5" "6" "7" "8" "9"))
```

### define-attributes

```text
(define-attributes attribute-list)
```

Defines all attributes the raw index may contain. Parameter
`attribute-list` is a list of list of strings. The nesting level
must not be more than 2. So `(..(..)..)` is allowed, whereas
`(..(..(..)..)..)` is not.

The list has two kinds of elements: strings and list of strings. A
single string is treated as if it were a single element list. So the
lists `("definition")` and `( ("definition") )` are equivalent.
All elements forming a list are a so-called _attribute group_. The
members of a group are written to the output file before any member
of the following groups are written.

Examples of valid attributes lists are:

`("definition" "usage")` defines two attribute groups. The first
one contains all references with the attribute `definition` and the
second one all with the attribute `usage`.

`(("definition" "important") "usage")` defines two attribute
groups. The first one contains all references with the attributes
`definition` or `important` and the second one all with the
attribute `usage`. In the attribute group `("definition"
"important")` the attribute `definition` overrides `important`.

### define-crossref-class

```text
(define-crossref-class name [:unverified])
```

Defines `name` to be a class of cross references. We distinguish
two types of cross reference classes. _Verified_ cross reference
classes can be checked for dangling references. If for instance a
cross reference points to the non-existent keyword `foo' a warning is
issued and the user is advised to correct the invalid cross reference.
This is the default. If for some reasons this mechanism must be
deactivated the switch `:unverified` can be used to suppress this
behaviour.

### define-letter-group

```text
(define-letter-group name [:before lgname] [:after lgname]
                          [:prefixes list-of-prefixes])

(define-letter-groups list-of-letter-groups)
```

This command defines a letter group with name `name`, which must be
a string value, grouping all index entries that have a _sort key_
beginning with the prefix `name`. The command

```text
  (define-letter-group "a")
```

is equivalent to the command

```text
  (define-letter-group "a" :prefixes ("a"))
```

Using the latter form one can associate more than one prefix with a
given letter group. Also further prefixes can be added to an already
existing letter group by simply defining the same letter group again.
This results not in a redefinition but in adding more prefixes to the
currently defined prefixes.

Example:

```text
  (define-letter-group "a")
```

defines a letter group containing all index entries beginning with the
string `"a"`.

```text
  (define-letter-group "c" :after "a")
```

defines a letter group containing all index entries beginning with the
string `"c"`. The letter group appears behind the letter group "a"

```text
  (define-letter-group "b" :after "a" :before "c")
```

inserts letter group "b" between letter group "a" and "c". This allows
incremental definition of letter groups by extending already defined
ones.

The arguments `:after` and `:before` define a partial order on
the letter groups. xindy tries to convert this partial order into
a total one. If this is impossible due to circular definitions, an
error is reported. If more than one possible total ordering can
result, it is left open which one is used, so one should always define
a complete total order.

### define-letter-groups

The command `define-letter-groups` (with an `s' at the end) is
simply an abbreviation for a sequence of
`define-letter-group` definitions where the elements are ordered in
the ordering given by the list. Example:

```text
  (define-letter-groups ("a" "b" "c")
```

equals the definitions

```text
  (define-letter-group "a")
  (define-letter-group "b" :after "a")
  (define-letter-group "c" :after "b")
```

See also commands `markup-letter-group-list` and
`markup-letter-group` for further information.

### define-location-class

```text
(define-location-class name layer-list
                       [:min-range-length num]
                       [:hierdepth depth]
                       [:var])
```

Defines `name` to be a location class consisting of the given list
of layers. A list of layers consists of names of basetypes and/or
strings representing separators. Separators must follow the
keyword argument `:sep`. If the keyword `:min-range-length` is
specified we define the _minimum range length_ to be used when
building ranges. The argument `num` must be a positive integer
number or the keyword `none` in which case the building of ranges
is disallowed. If the switch `:var` is specified the declared class
is of type _variable_, i.e. it is a _var-location-class_. Since
building of ranges is currently only allowed for standard classes
`:var` and `:min-range-length` must not be used together. The
keyword argument `:hierdepth` can be used to declare that the
location references have to be tagged in a hierarchical form. Its
argument `depth` must be an integer number indicating the number of
layers the hierarchy does contain. See command
`markup-locref-list` for more information. Examples:

```text
  (define-location-class "page-numbers" ("arabic-numbers")
                         :minimum-range-length 3)
```

Defines the location class `page-numbers` consisting of one layer
which is the alphabet `arabic-numbers`. Since the minimum
range length is set to 3 the location references 2, 3 and 4 don't form
a range because the range length is only 2. But the references 6, 7,
8, and 9 are enough to form a range. Some example instances of this
class are `0`, `1`, ... `2313`, etc.

```text
  (define-location-class "sections" :var
     ("arabic-numbers" :sep "."
      "arabic-numbers" :sep "."
      "arabic-numbers"))
```

defines a variable location class. Valid instances are `1`,
`1.1`, `1.2`, `2`, `2.4.5`, but none of `2-3` (wrong
separator), `1.2.3.4` (more than 3 layers), `2.3.iv` (roman
number instead of arabic one).

### define-location-class-order

```text
(define-location-class-order list)
```

Defines the order in which the location classes are written to the
output file. The parameter `list` is a list of names of
location classes. Examples:

```text
  (define-location-class-order
      ("page-numbers" "sections" "xrefs"))
```

tells the system that the page numbers should appear before the
section numbers and that the cross references should appear at the
end. If this command is omitted, the declaration order of the
location classes in the index style is implicitly used as the output
order. In the case that a location class does not appear in the list,
the output may behave unexpectedly, so one should always enumerate all
used location classes when using this command.

### define-rule-set

```text
(define-rule-set name
        [ :inherit-from ("rule-set" "rule-set-2") ]
        :rules (<rule>...) )
```

A complete specification of a multi-phase sorting process for a
language requires that some rules have to appear in several subsequent
sorting phases. Rule sets can be used to define a set of rules that
can be instantiated in an arbitrary sorting phase. Basically, they
offer means to separate the definition of sorting rules from their
instantiation, hence, acting as a wrapper for calls to `sort-rule`.
They do not add new functionality that is not already present with
`sort-rule`.

A rule can be of the form:

```text
  <rule> ::= ("pattern" "replacement"
              [:string|:bregexp|:egegexp] [:again])
```

The following incomplete example defines a new rule set of name
`isolatin1-tolower` that inherits definitions from rule set
`latin-tolower`, overriding or adding the sort rules in the list of
`:rules`.

```text
   (define-rule-set "isolatin1-tolower"

     :inherit-from ("latin-tolower")

     :rules (("À" "à" :string :again)
             ("Á" "á" :string :again)
             ("Â" "â" :string :again)
             ("Ã" "ã" :string :again)
             ("Ä" "ä" :string :again)
             ("Å" "å" :string :again)
             ("Æ" "æ" :string :again)
          ...
            )
   ...)
```

Rule sets can be instantiated with the command `use-rule-set`. For
further descriptions on the sorting model refer to the command
`sort-rule`.

### define-sort-rule-orientations

```text
(define-sort-rule-orientations (orientations...))
```

---

Defines the order for the different sorting phases. The currently
implemented _orientations_ are `forward` and `backward`. This
command must precede all `sort-rule` commands in an index style. It
defines the orientations and implicitly sets the maximum number of
sorting phases performed.

For further descriptions on the sorting model refer to the command
`sort-rule`.

### merge-rule

```text
(merge-rule pattern replacement [:again]
                                [:bregexp | :eregexp | :string])
```

Defines a keyword mapping rule that can be used to generate the
_merge key_ from the _main key_ of an index entry. This mapping
is necessary to map all keywords that are differently written but
belong to the same keyword to the same canonical keyword.

The parameter `pattern` can be a POSIX-compliant regular expression
or an ordinary string. The implementation uses the GNU Rx regular
expression library which implements the POSIX regular expressions.
Regular expressions (REs) can be specified as _basic regular
expressions_ (BREs) or _extended regular expressions_ (EREs). You
can use the switch `:bregexp` to force the interpretation of the
pattern as a BRE, or `:eregexp` to interpret it as an ERE. If you
want xindy to interpret the pattern literally, use the switch
`:string`. If none of these switches is selected, xindy uses
an auto-detection mechanism to decide, if the pattern is a regular
expression or not. If it recognizes the pattern as a RE, it interprets
it as an ERE by default.

The parameter `replacement` must be
a string possibly containing the special characters `&`
(substitutes for the complete match) and
`\1`
,...,
`\9`

(substituting for the _n_-th submatch. Examples:

```text
  (merge-rule "A" "a")
```

replaces each occurrence of the uppercase letter ``A`' with its
lowercase counterpart.

```text
  (merge-rule "\~"([AEOUaeou])" "\1")
```

transforms the TeX umlaut-letters into their stripped counterparts,
such that `
`\"A`
' is treated as an ``A`' afterwards.

The following sequences have a special meaning:

`
`~n`
' : End of line symbol (_linefeed_).

`
`~b`
' : The ISO-Latin character with the lowest ordinal number.

`
`~e`
' : The ISO-Latin character with the highest ordinal number.

`
`~~`
' : The tilde character.

`
`~"`
' : The double quote character.

Tilde characters and double quotes have to be quoted themselves with a
tilde character. The special characters `
`~b`' and`
`~e`
' allow the definition of arbitrary sorting orders by
rules. In connection with an additional character every position in
the alphabet can be described. E.g. `
`m~e`
' is
lexicographically placed between ``m`' and ``n`'.

Due to efficiency, rules that just exchange characters or substitute
constant character sequences are not treated as regular expressions.
Therefore, instead of using the rule

```text
  (merge-rule "[A-Z]" "&ampx")
```

it is more efficient (though less comfortable) to use

```text
  (merge-rule "A" "Ax")
  (merge-rule "B" "Bx")
  ...
  (merge-rule "Z" "Zx")
```

Usually rules are applied in order of their definition. Rules with a
special prefix precede those that begin with a class of characters, so
that the search pattern `` alpha`' is checked before  ``._` ', but
``auto `' and ``a._`' are checked in order of their definition.

The first rule from a style file that matches the input is
applied and the process restarts behind the substituted text. If no
rule could be applied, the actual character is copied from the input
and the process continues with the next character.

Sometimes it is necessary to apply rules anew to the result of a
transformation. By specifying the keyword argument `:again` in the
merge rule the rule is marked as _mutable_, which means that after
using this rule the transformation process shall restart at the same
place. E.g. the rule

```text
  (merge-rule "\$(.*)\$" "\1" :again)
```

deletes _all_ surrounding `
`$`
' symbols from the input.

See also command `sort-rule`.

### merge-to

```text
(merge-to attr-from attr-to [:drop])
```

A _merge rule_ says that the attribute `attr-from` can be used
to build ranges in `attr-to`. Both attributes must name valid
attribute names. The switch `:drop` indicates, that the original
location reference with attribute `attr-from` has to be dropped
(removed), if a successful range was built with location references in
attribute `attr-to`. A detailed description is given in the section
about processing phases.

### require

```text
(require filename)
```

This command allows to load more index style modules. The module is
searched in the directories defined in the search path. The file is
read in and processing of the current file continues. The argument
`filename` must be a string. This allows to decompose the
index style into several modules that can be included into the topmost
index style file. Example:

```text
  (require "french/alphabet.xdy")
  (require "french/sort-rules.xdy")
  (require "tex/locations.xdy")
  (require "tex/markup.xdy")
```

Submodules can load other submodules as well. If a file is required
that was already loaded, the `require` command is simply ignored
and processing continues without including this file twice. See also
command `searchpath`.

### searchpath

```text
(searchpath {path-string | path-list})
```

This command adds the given paths to the list of paths, xindy
searches for index style files. The argument `path-string` must be
a colon-separated string of directory names. If this path ends with a
colon the default search path is added to the end of the path list.
Example:

```text
  (searchpath ".:/usr/local/lib/xindy:/usr/local/lib/xindy/english:")
```

adds the specified directories to the search path. Since the last path
ends with a colon, the built-in search path is added at the end.
Specifying

```text
  (searchpath ("."
               "/usr/local/lib/xindy"
               "/usr/local/lib/xindy/english"
               :default))
```

yields exactly the same result as the example above. Here
`path-list` must be a list of strings and/or the keyword(s)
`:default` and `:last`. The keyword `:default` signifies that
the default pathnames are to be inserted at the specified position in
the list. The keyword `:last` allows to insert the currently active
paths at the indicated position. Since this allows to insert the
built-in paths at any position and incrementally adding new paths to
the search path, this version of the command ist more flexible than
the first version.

### sort-rule

```text
(sort-rule pattern replacement [:run level] [:again])
```

Defines a keyword mapping rule that can be used to generate the
_sort key_ of an index entry from the _merge key_. This key is
used to sort the index entries lexicographically after they have been
merged using the merge key.

The argument `:run` indicates that this rule is only in effect
a the specified _level_ (default is level 0). For a detailed
discussion on the definition of sort rules for different layers refer
to the documentation about the new sorting scheme
(`new-sort-rules`) that comes with this distribution.

See command `merge-rule` for more information about keyword
rules.

### use-rule-set

```text
(use-rule-set [:run phase]
              [:rule-set ( <rule-set>... ))
```

This command instantiates the gives rule sets to be in effect at
sorting phase `phase`. The order of the rule sets given with
argument `:rule-set` is significant. Rule set entries of rule set
appearing at the beginning of the list override entries in rule sets
at the end of the list.

The following example declares that in phase 0 the rule sets
`din5007` and `isolatin1-tolower` should be active, whereas in
phase 2 the other rule sets have to be applied.

```text
  (use-rule-set :run 0
                :rule-set ("din5007" "isolatin1-tolower"))

  (use-rule-set :run 1
                :rule-set ("resolve-umlauts"
                           "resolve-sharp-s"
                           "isolatin1-tolower"
                           ))
```

For a discussion on rule sets refer to command `define-rule-set`.

## Markup Commands

The following commands can be used to define the markup of the index.
They don't have any influence on the indexing process. Since the
markup scheme is characterized by the concept of _environments_,
the syntax and naming scheme of all commands follows a simple
structure.

The commands can be separated into _environment_ and
_list-environment_ commands. All commands of the first group
support the keyword arguments `:open` and `:close`, whereas the
second group additionally supports the keyword argument `:sep`. If
one of these keyword arguments is missing, the default markup tag is
_always_ the empty tag. The `:open` tag is always printed before
the object itself and the `:close` tag is always printed after the
object has been printed. If a list is printed the `:sep`tag is
printed between two elements of the list but not before the first
element, or after the last one. All commands dealing with a list have
the suffix ``-list`' as part of their command name.

Since the number of commands and the heavy usage of _default_ and
_specialized_ tags makes the markup somehow complex (but very
powerful) we have added a mechanism to trace the markup tags
xindy omits during its markup phase with the command
`markup-trace`.

Here follows the list of markup commands in alphabetical order with
some of the commands grouped together.

### markup-attribute-group-list

```text
(markup-attribute-group-list [:open string] [:close string]
                             [:sep string])
```

Location class groups consist of lists of attribute groups. The markup
of this list can be defined with the command
`markup-attribute-group-list`.

### markup-attribute-group

```text
(markup-attribute-group      [:open string] [:close string]
                             [:group group-num])
```

To allow different markup for different attribute groups the command
`markup-attribute-group` can be specialized on the group number with
the keyword argument `:group` which must be an integer number. Given
the groups `("definition" "theorem")` and `("default")` with group
numbers 0 and 1, then

```text
  (markup-attribute-group :open "<group0>" :close "</group0>"
                          :group 0)

  (markup-attribute-group :open "<group1>" :close "</group1>"
                          :group 1)
```

can assign different markup for both groups in a SGML-based language.

### markup-crossref-list

```text
(markup-crossref-list       [:open string] [:close string]
                            [:sep string]
                            [:class crossref-class])
```

A crossref class group contains cross references of the same class.
The separator between the classes is defined with the
`(markup-locclass-list :sep)`-parameter. A list of cross references
can be tagged with the command `markup-crossref-list` that
specializes on the `:class` argument.

### markup-crossref-layer-list

```text
(markup-crossref-layer-list [:open string] [:close string]
                            [:sep string]
                            [:class crossref-class])
```

Each cross reference is determined by a list of layers indicating
the target of the cross reference. To define suitable markup for
such a list the command `markup-crossref-layer-list` can be used.

### markup-crossref-layer

```text
(markup-crossref-layer      [:open string] [:close string]
                            [:class crossref-class])
```

Each layer of a cross reference can be assigned two tags that
specialize on the class of the reference, like all other commands.

A suitable markup for a cross reference class `see` within LaTeX2e
could look like that:

```text
  (markup-crossref-list :class "see" :open "\emph{see} "
                                     :sep  "; ")
  (markup-crossref-layer-list :class "see" :sep ",")
  (markup-crossref-layer :class "see"
                                     :open "\textbf{" :close "}")
```

An example output could look like

> ... _see_ **house**; **garden**,**winter**; **greenhouse**

### markup-index

```text
(markup-index [:open string] [:close string]
              [ :flat | :tree | :hierdepth depth ])
```

Defines the markup tags that enclose the whole index via the
`:open` and `:close` parameters. Examples:

```text
  (markup-index :open  "Here comes the index~n"
                :close "That's all folks!~n")
```

defines that the `:open` string is printed before the rest of the
index and the `:close` string appears after the index is printed.

Additionally one can specify the form of the generated index. It is
possible to produce flat indexes by specifying the switch `:flat`,
to generate a tree with the `:tree` switch or any kind of mixture
between both by specifying the depth up to which trees shall be built
with the parameter `:hierdepth`. Its argument `depth` is the
number of layers that can be formed into a tree. Therefore `:flat`
is an abbrevation of `:hierdepth 0` and `:tree` is an
abbrevation of `:hierdepth max-depth`, with `max-depth` being
the maximum number of layers a keyword has. An example: the keywords

```text
  ("tree" "binary" "AVL")
  ("tree" "binary" "natural")
```

can be transformed in the following ways:

A flat index (`:flat` or `:hierdepth 0`)

```text
  tree binary AVL
  tree binary natural
```

with `:hierdepth 1`

```text
  tree
     binary  AVL
     binary  natural
```

and a tree (`:tree` or `:hierdepth` > 1)

```text
  tree
     binary
        AVL
        natural
```

Most often one will create tree-like indexes or ones that are flat.

### markup-indexentry-list

```text
(markup-indexentry-list [:open string] [:close string]
                        [:sep string]  [:depth integer])

(markup-indexentry      [:open string] [:close string]
                        [:depth integer])
```

Letter groups consists of a list of index entries. The command
`markup-indexentry-list` defines the markup of these lists. The
markup can be specialized on the depth if the index is hierarchically
organized. The command

```text
  (markup-indexentry-list :open  "\begin{IdxentList}"
                          :close "\end{IdxentList}"
                          :sep   "~n")
```

defines that the index entries of all layers are wrapped into the
given markup tags. If additionally

```text
  (markup-indexentry-list :open  "\begin{IdxentListII}"
                          :close "\end{IdxentListII}"
                          :sep   "~n"
                          :depth 2)
```

is defined, all index entry lists of all layers (except layer 2) are
tagged according to the first specification, and the index entry list
within depth 2 are tagged according to the second rule.

### markup-indexentry

The command `markup-indexentry` defines the markup of an index entry
at a given depth. Since index entries may also contain subentries and
the markup for subentries may be different in different layers, the
optional keyword argument `:depth` can be used to assign different
markup for different layers. If depth is ommited the default markup
for all possible depths is defined. The top-most index entries have
depth 0.

```text
  (markup-indexentry :open  "\begin{Indexentry}"
                     :close "\end{Indexentry}")
```

defines that the index entries of all layers are wrapped into the
given markup tags. If additionally

```text
  (markup-indexentry :open  "\begin{IndexentryII}"
                     :close "\end{IndexentryII}"
                     :depth 2)
```

is defined, all index entries of all layers (except layer 2) are tagged
according to the first specification, and the index entries with depth
2 are tagged according to the second rule.

### markup-keyword-list

```text
(markup-keyword-list [:open string] [:close string]
                     [:sep string] [:depth integer])

(markup-keyword      [:open string] [:close string]
                     [:depth integer])
```

The print key of an index entry consists of a list of strings. The
markup of this list can be defined with the command
`markup-keyword-list`. The keyword argument `:depth` may be
specified to define the markup of the list at a particular depth.

### markup-keyword

The keyword of an index entry consists of a list of strings. Each of
these components is tagged with the strings defined with the command
`markup-keyword`. Since we maybe need different markup for
different layers, the optional keyword argument can be used to
specialize this markup for some depth.

### markup-letter-group-list

```text
(markup-letter-group-list [:open string] [:close string]
                          [:sep string])

(markup-letter-group  [:open string] [:close string] [:group group-name]
                      [:open-head string] [:close-head string]
                      [:upcase | :downcase | :capitalize])
```

The first command defines the markup of the letter group with name
`group-name`. Since the markup of letter groups often contains the
name of the letter group as a part of it, the other keyword arguments
allow an additional markup for this group name. If one of the
parameters `:open-head` and `:close-head` is specified
additional markup is added as can be described as follows:

```text
  <OPEN>
     IF (:open-head OR :close-head)
       <OPEN-HEAD>
         transformer-of(<GROUP-NAME>)
       <CLOSE-HEAD>
     FI
     <INDEXENTRIES...>
  <CLOSE>
```

Here, `transformer-of` is a function that possibly transforms the
string representing the group name into another string. The
transformers we currently support can be specified with the switches
`:upcase`, `:downcase` and `:capitalize` which result in the
corresponding string conversions. If none of them is specified no
transformation is done at all.

### markup-letter-group

The command `markup-letter-group` defines the markup of the list of
letter groups.

### markup-locclass-list

```text
(markup-locclass-list [:open string] [:close string]
                      [:sep string])
```

Each index entry contains a list of location class groups. This markup
command can be used to define the markup of this list.

### markup-locref

```text
(markup-locref [:open string] [:close string]
               [:class locref-class]
               [:attr  attribute]
               [:depth integer])
```

The markup tags of a location reference can be specialized on the
three arguments `:class`, `:attr` and additionally, if
sub-references are used, `:depth`. Most often one will only use a
tag depending on the attribute. For example, all location references
with the attribute `definition` should appear in a font series like
bold, emphasizing the importance of this location reference; those
with the attribute `default` in font shape italic. The markup in
this case would not specialize on the depth or any particular class. A
valid definition, suitable for a usage within HTML, could look like
this.

```text
  (markup-locref :open "<B>" :close "</B>" :attr "definition")
  (markup-locref :open "<I>" :close "</I>" :attr "default")
```

### markup-locref-class

```text
(markup-locref-class [:open string] [:close string]
                     [:class locref-class])
```

All location references of a particular location reference class can
be wrapped into the tags defined by this command. It specializes on
the keyword argument `:class`.

### markup-locref-layer

```text
(markup-locref-layer      [:open string] [:close string]
                          [:depth integer] [:layer integer]
                          [:class locref-class])
```

The command allows tagging elements of a layer list differently. The
first element of this list can be specialized with `:layer 0`, the
next element with `:layer 1`, etc.

### markup-locref-layer-list

```text
(markup-locref-layer-list [:open string] [:close string]
                          [:sep string]
                          [:depth integer]
                          [:class locref-class])
```

A location reference contains a list of location reference layers. The
list command can markup this list. It specializes on the class of the
location references and the depth (if sub-references are used).

### markup-locref-list

```text
(markup-locref-list [:open string] [:close string] [:sep string]
                    [:depth integer] [:class locref-class])
```

An attribute group contains a list of location references and/or
ranges. Additionally a layered location reference itself may contain
sub-references that are stored as a list of location references. We
specialize the markup for these lists on the location class they
belong to with the keyword argument `:class`, and on `:depth`
that specializes on the different subentry levels when using
location references with sub-references.

Given is a list of location references that have the class description

```text
  (define-location-class "Appendix"
                         ("ALPHA" :sep "-" "arabic-numbers")
                         :hierdepth 2)
```

This location class has instances like `A-1`, `B-5`, etc. The
keyword argument `:hierdepth 2` informs xindy to markup these
location references in a hierarchical form. With the commands

```text
  (markup-locref-list            :sep "; "
                       :depth 0  :class "Appendix")
  (markup-locref-list  :open " " :sep ","
                       :depth 1  :class "Appendix")
  (markup-locref-layer :open "{\bf " :close "}" :layer 0
                       :depth 0  :class "Appendix")
```

we obtain a markup sequence for some example data that could look like

```text
  {\bf A} 1,2,5; {\bf B} 5,6,9; {\bf D} 1,5,8; ...
```

### markup-range

```text
(markup-range [:open string] [:close string] [:sep string]
              [:class locref-class]
              [:length num] [:ignore-end])
```

---

A range consists of two location references. Markup can be specified
with the `:open` and `:close` arguments and one separator given
by the argument `:sep`.

Since both location references are tagged with markup defined by the
command `markup-locref` a specialization on attributes or depth is
not necessary. Specialization is allowed on the class they belong to,
because the separator between two location refences may be different
for each location class. Argument `:length` can be used to define
different markup for different lengths. In conjunction with
`:length` is may be useful not to print the second location
reference at all. For example, one wishes to markup ranges of length 1
in the form _Xf._ instead of _X--Y_. This can be accomplished
with the switch `:ignore-end`.

The markup tags for a range _(X,Y)_ can be described as follows:

```text
  <OPEN>
    Markup of location reference X
  <SEP>
    IF (not :ignore-end)
       Markup of location reference Y
    FI
  <CLOSE>
```

The following tags can be used to define a range of page numbers
(given in a location class `page-numbers`) without considering the
open and close parameters:

```text
  (markup-range :sep "-" :class "page-numbers")
```

Location ranges then appear separated by a hyphen in a form like this:

```text
   ..., 5-8, 19-23, ...
```

### markup-trace

```
(markup-trace [:on] [:open string] [:close string])
```

---

This command can be used to activate the tracing of all
markup commands xindy executes. The switch `:on` activates the
trace. If `:on` is omitted, the command line flag `-t` can be
used as well. All tags which are emitted but not yet defined
explicitly by the user are tagged with a symbolic notation indicating
the commands that must be used to define this tag. The defaults for
the keyword argument `:open` is `` <`' and for `:close` is
 ``>`'. The beginning of an example output could look like:

```text
  <INDEX:OPEN>
    <LETTER-GROUP-LIST:OPEN>
      <LETTER-GROUP:OPEN ["a"]>
        <INDEXENTRY-LIST:OPEN [0]>
          <INDEXENTRY:OPEN [0]>
            <KEYWORD-LIST:OPEN [0]>
              <KEYWORD:OPEN [0]>
   ...
```

We use a simple indentation scheme to make the structure of the tags
visible. The symbolic tag `<LETTER-GROUP:OPEN ["a"]>` for example
indicates that the tag that can be specified with the command

```text
  (markup-letter-group :open "XXX" :group "a" ... )
```

is emitted at this point in the markup process. By incrementally
adding markup commands to the index, more and more tags can be defined
until the whole markup is defined. This general mechanism should allow
everyone understand the markup process. The best is to start with a
small index, define the complete markup and afterwards process the
whole index. Additionally one can enclose the symbolic tags into an
environment that is neutral to the document preparation system, such
as a comment. For TeX this could be

```
  (markup-trace :open "%%" :close "~n")
```

or a definition in the TeX document like

```text
  \def\ignore#1{}
```

combined with the command

```text
  (markup-trace :open "\ignore{" :close "}")
```

## Raw Index Interface

This section can be skipped if the reader is not interested in
adapting xindy to a new document preparation system.

The raw index is the file that represents the index that is to be
processed. Since many different document preparation systems may use
different forms of index representations, their output must be
transformed in a form readable by xindy. We also could have
written an configurable parser performing this task, but usually a
tool written with some text processing tools such as `perl`,
`sed` or `awk` can achieve the same task as well. Therefore,
adapting xindy to a completely different system can mostly be
done by writing an appropriate raw index filter.

The format of the raw index interface of xindy is defined as
follows:

### indexentry

```text
(indexentry { :key string-list [:print string-list]
            | :tkey list-of-layers }
            [:attr string]
            { :locref string  [:open-range | :close-range]
            | :xref string-list } )
```

---

The pseudo variable _string_ is a sequence of characters
surrounded by double quotes, e.g.

```text
  "Hi, it's me"  "one"  "a string with two \"double quotes\""
```

are three examples of valid strings. If you need to include a
double quote as a literal character, you must quote it itself with a
backslash as shown in the third example. A _string list_ is simply
a list of strings separated by whitespaces and surrounded by round
braces. An example of a string list is

```text
  ("This" "is" "a" "list" "of" "strings")
```

So far about the syntax. The semantics of the different elements are
described here.

**`:key`**
The argument _string list_ defines the keyword of
the index entry. It must be a list of strings, since the keyword may
consist of different layers such as `("heap" "fibonacci")`.

**`:print`**
The optional _print key_ defines the way the
keyword has to be printed in the markup phase.

**`:tkey`**
Another possibility to define the keys of an
index entry is with the `:tkey` keyword argument. It can be used
instead of the `:key` and `:print` arguments. Instead of
specifying separately the key and the corresponding print key, we
define the keyword by its layers. Each layer consist of a list of one
or two strings. The first string will be interpreted as the main key,
whereas the second one will become the print key. If the print key is
ommited, the main key is taken instead. So the definition

```text
  :tkey (("This") ("is") ("a") ("bang" "BANG !!!"))
```

is equivalent to

```text
  :key   ("This" "is" "a" "bang")
  :print ("This" "is" "a" "BANG !!!")
```

**`:locref`**
The reference an index entry describes can be a
_location reference_ or a _cross reference_. The switch
`:locref` describes a location reference. Its optional arguments
are `:open-range` and `:close-range`. The _string_ that must
be supplied must somehow encode the location reference. It might look
like the string `"25"` representing the page number 25, or
`"Appendix-I"` representing the first appendix numbered in
uppercase roman numerals.

**`:open-range`,`:close-range`**
These are switches that do not
take any arguments. They describe the beginning and ending of a
_range_, starting or ending from the location reference that is
given by the argument `:locref`. If they are supplied, the
location reference may have influence on the way ranges are build.

**`:xref`**
These arguments choose the second alternative. The argument
_string list_ of parameter `:xref` describes where the index entry
should point to.

**`:attr`**
This parameter may be used to tag a location reference with a
certain attribute or it names the class of a cross reference. It may
also used to associate different markup for different attributes in
the markup phase. If this parameter is omitted or is the empty string,
the indexentry is declared to have the attribute `default`.

Some examples:

```text
  (indexentry :key ("airplane") :locref "25" :attr "default")
```

defines an index entry with the key `airplane' indexed on page '25'.
This index entry has the attribute `default`.

```text
  (indexentry :key ("house") :xref ("building") :attr "see")
```

defines a cross reference with the key 'house' pointing to the term
'building'. This cross reference belongs to the cross reference class
`see`.

```text
  (indexentry :key ("house") :xref ("building") :open-range)
```

is an invalid specification, since `:open-range` mustn't be used
together with cross references.
