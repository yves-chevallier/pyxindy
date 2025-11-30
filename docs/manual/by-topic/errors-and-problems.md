# xindy by Topic: Errors and Problems

## 3.1 The keyword mappings don't work as expected!

Sometimes the keyword mappings don't work as expected. Especially in
cases with several regular expressions one might get confused about
what rule matches exactly when. We have incorporated a detailed
logging mechanism that lets one step by step follow the rules that
accomplish the keyword mapping.

When running **xindy** you can turn on this feature with the command
line option ``-L`'. This option followed by one of the numbers 1,
2, or 3 turns on the appropriate debugging level. Turning on level 2
or 3 and specifying a log-file with the command line option ``-l`'
a trace of the mappings is recorded in the log-file. A sample output
looks like the following:

> ````
>
> Mappings: (add (merge-rule :eregexp `^\\bf{(.*)}' `\1' :again)).
> Mappings: (add (merge-rule :eregexp `^\\"([AEOUaeou])' `\1')).
>  ...
> Mappings: (compare `\"A\"a' :eregexp `^\\bf{(.*)}')
> Mappings: (compare `\"A\"a' :eregexp `^\\"([AEOUaeou])') match!
> Mappings: (compare `\"a' :eregexp `^\\bf{(.*)}')
> Mappings: (compare `\"a' :eregexp `^\\"([AEOUaeou])') match!
> Mappings: (merge-mapping `\"A\"a') -> `Aa'.
>
> ````

This trace shows that initially two regular expression mappings have
been added to the rule set. The second section shows how the keyword
`
`\"A\"a`
' is compared to these rules and substitutions are
applied as matches are found. In the last line the result of the
keyword mapping is reported.

## 3.2 I'm totally confused by the markup scheme!

A very important feature is the ability to *trace* all markup tags
**xindy** emits in the markup phase. Simply use the command line
switch `-t` or insert the command

> ````
>
> (markup-trace :on)
>
> ````

into the index style. This informs **xindy** to emit additional
pseudo markup that can be used to understand and debug the
markup phase. An example output might look like the following:

> ````
>
> <INDEX:OPEN>
>   <LETTER-GROUP-LIST:OPEN>
>     <LETTER-GROUP:OPEN ["a"]>
>       <INDEXENTRY-LIST:OPEN [0]>
>         <INDEXENTRY:OPEN [0]>
>           <KEYWORD-LIST:OPEN [0]>
>             <KEYWORD:OPEN [0]>
>  ...
>
> ````

The symbolic tags directly lead one to the command that is responsible
for the definition of that markup tag. For example, the tag
`LETTER-GROUP-LIST:OPEN`
 indicates that the command
`markup-letter-group-list`
 is responsible for replacing this
symbolic tag by a real one.
Give it a try if you find yourself confused by your own markup
specification.

---
