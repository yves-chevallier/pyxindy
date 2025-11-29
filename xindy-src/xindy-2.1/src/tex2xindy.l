%{
  /*

   $Id: tex2xindy.l,v 1.12 1999/10/13 08:06:44 kehr Exp $
       Added translations: 8 bit hex (^^xx) --> byte, 16/32-bit hex --> UTF-8
       new: <quote> start condition
       fixed error messages (multiple ...)
       Paranoia fix: recognize KEYWORD only in INITIAL start condition
       recognize \n and count lines (multiline entries do exist!)
       merged "." rules
        2000-02-14 Thomas Henlich <henlich@mmers1.mw.tu-dresden.de>

   1.8 Fixed minor quoting bugs (for increased makeindex compatibility).
        1999-07-28 Thomas Henlich <henlich@mmers1.mw.tu-dresden.de>
       Fixed crossref to subitem.
        1999-09-23 Thomas Henlich <henlich@mmers1.mw.tu-dresden.de>

   1.7 Fixed a bug concerning writing to and closing non-existing file (stat)
       Fixed a bug concerning quoting the " character.
       Enhancement for processing glossary files.
        1999-06-14 Thomas Henlich <henlich@mmers1.mw.tu-dresden.de>

   This is the source of `tex2xindy'.

   It tries to parse an TeX-auxiliary-file `.aux' or index-file
   `.idx' into a raw-index-form readable by xindy.

   This program was written since it was not easily possible to
   extract the parser from the old makeindex system. Therefore it does
   not find all errors in the input as the makeindex version.
   Additionally it uses only the default input specifiers of
   makeindex. If other input specifiers (cf. manual page of makeindex)
   are needed, the input specifiers below (starting from the pattern
   KEYWORD, see below) must be changed and the program must be
   recompiled. See the Migration Manual that comes with this
   distribution for further details.

   It can also be used as a template for writing other frontends for
   xindy. Please send us your preprocessors. We are likely to include
   them into the distribution. */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define QUOTE_ECHO qs(yytext)
#define PUT_UTF8_SKIP(X) putwchar (strtoul (yytext+X, NULL, 16))

#define IDX2RAW_NAME "idx2raw"
#define GLO2RAW_NAME "glo2raw"

FILE* attrfd = NULL;

static int lineno    = 1;
static int braces    = 0;
static int xref_mode = 0;
static int glos_mode = 0; /* 0: process index file
			   * 1: process glossary file */
static int auto_glo_idx = 1; /* 0: do not set glos_mode automatically
			      * 1: set glos_mode automatically */
static int errors    = 0;

#define err \
{fprintf(stderr, "line %d: multiple %s's\n", lineno, yytext); errors++;}

#define NO_RANGE     0
#define OPEN_RANGE   1
#define CLOSE_RANGE  2

int range = NO_RANGE;
int quote_caller;
  
/* This function quotes a character, if necessary. */

void qc( char ch ) {
  switch (ch) {
    case '\\' : putchar( '\\' ); break;
    case '"'  : putchar( '\\' ); break;
  }
  putchar(ch);
}

/* Quote an entire string. */

void qs( char* str ) {
  while ( *str ) {
    qc( *str++ );
  }
}

/* Output a character in UTF-8 encoding */  
void putwchar(c)
unsigned long int c;
{
  if (c < 0x80) {
    putchar (c);
  }
  else if (c < 0x800) {
    putchar (0xC0 | c>>6);
    putchar (0x80 | c & 0x3F);
  }
  else if (c < 0x10000) {
    putchar (0xE0 | c>>12);
    putchar (0x80 | c>>6 & 0x3F);
    putchar (0x80 | c & 0x3F);
  }
  else if (c < 0x200000) {
    putchar (0xF0 | c>>18);
    putchar (0x80 | c>>12 & 0x3F);
    putchar (0x80 | c>>6 & 0x3F);
    putchar (0x80 | c & 0x3F);
  }
  else if (c < 0x4000000) {
    putchar (0xF8 | c>>24);
    putchar (0x80 | c>>18 & 0x3F);
    putchar (0x80 | c>>12 & 0x3F);
    putchar (0x80 | c>>6 & 0x3F);
    putchar (0x80 | c & 0x3F);
  }
  else if (c < 0x80000000) {
    putchar (0xFC | c>>30);
    putchar (0x80 | c>>24 & 0x3F);
    putchar (0x80 | c>>18 & 0x3F);
    putchar (0x80 | c>>12 & 0x3F);
    putchar (0x80 | c>>6 & 0x3F);
    putchar (0x80 | c & 0x3F);
  }
  else { /* out of range, output U+FFFD REPLACEMENT CHARACTER */
    fputs("\xef\xbf\xbd",stdout);
    fprintf (stderr, "line %d: character %#lx not in UTF-8 range\n", lineno,c);
  }
}

%}

KEYWORD  \\indexentry
KEYWORDG \\glossaryentry
ENCAP    \|
ACTUAL   @
ESCAPE   \\
LEVEL    !
IS       :
QUOTE    \"
ROPEN    \(
RCLOSE   \)
ARGOPEN  \{
ARGCLOSE \}
HEX8BIT  \^^[8-9a-fA-F][0-9a-fA-F]
HEX16BIT \^^^^[0-9a-fA-F]{1,4}
HEX32BIT \^{8}[0-9a-fA-F]{1,8}


%s key print skip2location location encap xref is skiplocation
%x quote
%%

<INITIAL>^{KEYWORD}[ \t]*{ARGOPEN} {
                            printf("(indexentry :tkey ((\"");
                            xref_mode = 0;
                            if (auto_glo_idx) 
                              glos_mode = 0;
                            BEGIN(key); }

<INITIAL>^{KEYWORDG}[ \t]*{ARGOPEN} {
                            printf("(indexentry :tkey ((\"");
                            xref_mode = 0;
                            if (auto_glo_idx) 
                              glos_mode = 1;
                            BEGIN(key); }

{ESCAPE}{QUOTE}        { QUOTE_ECHO; }
{QUOTE}                { quote_caller = YY_START;
                         BEGIN(quote); }
<key,print>{ENCAP}     { printf("\")) :attr \"");
                         range = NO_RANGE; BEGIN(encap); }
<key,print>{IS}        { if (glos_mode == 1)
                           {
                             printf("\")) :attr \"is\" :xref (\"");
                             range = NO_RANGE;
			     if (attrfd) fprintf(attrfd, "\txref\n");
		           BEGIN(is);
			   }
                         else
			   QUOTE_ECHO; }
<key>{LEVEL}           { printf("\") (\""); }
<print>{LEVEL}         { printf("\") (\""); BEGIN(key); }
<key,print>{ARGOPEN}   { QUOTE_ECHO; braces++; }
<key,print>{ARGCLOSE}  { if ( braces > 0 )
                           {QUOTE_ECHO; braces--;}
                         else
			   {printf("\"))");
		         BEGIN(skip2location);}
                       }

<key>{ACTUAL}          { printf("\" \""); BEGIN(print); }
<print>{ACTUAL}        { err; }

<encap>{ENCAP}         { err; }
<encap>{ROPEN}         { range = OPEN_RANGE; }
<encap>{RCLOSE}        { range = CLOSE_RANGE; }
<encap>{ARGOPEN}       { /* close :attr "... */
                         printf("\" :xref (\"");
			 if (attrfd) fprintf(attrfd, "\txref\n");
		         braces++;
		         BEGIN(xref);
                       }
<encap>{ARGCLOSE}      { if ( braces > 0 )
                           {QUOTE_ECHO; braces--;}
                         else {
			   putchar('"');
			   if (attrfd) fprintf(attrfd, "\tlocref\n");
			   switch (range) {
			     case OPEN_RANGE : printf(" :open-range");
			       break;
			     case CLOSE_RANGE: printf(" :close-range");
			       break;
			   }
			   BEGIN(skip2location);
			 }
                       }
<encap>\n             { QUOTE_ECHO;
                        if (attrfd) {
			  fwrite(yytext, sizeof(char), 1, attrfd);
			}
                        lineno++;
	              }
<encap>.              { QUOTE_ECHO;
                        if (attrfd) {
			  fwrite(yytext, sizeof(char), 1, attrfd);
			}
	              }


<xref>{LEVEL}          { printf("\") (\""); }
<xref,is>{ARGOPEN}     { QUOTE_ECHO; braces++; }
<xref>{ARGCLOSE}       { if     ( braces >   1 )
                           {QUOTE_ECHO; braces--;}
                         else if ( braces == 1 )
		           { braces--; }
                         else {
		           printf("\")");
			   xref_mode = 1;
		           BEGIN(skip2location);
		         }
                       }
<is>{ARGCLOSE}         { if     ( braces > 0 )
                           {QUOTE_ECHO; braces--;}
                         else {
		           printf("\")");
			   xref_mode = 1;
		           BEGIN(skip2location);
		         }
                       }

<skip2location>[ \t]*{ARGOPEN} {
                        if (xref_mode)
			  { BEGIN(skiplocation); }
			else
			  { printf(" :locref \"");
			    BEGIN(location);
			  }
                       }

<location>{ARGCLOSE}  { printf("\")\n"); BEGIN(0); }
<skiplocation>{ARGCLOSE} { printf(")\n"); BEGIN(0); }

<key,print,xref,is,location>\n {
                        QUOTE_ECHO;
                        lineno++; }
<key,print,xref,is,location>{HEX8BIT}  { qc (strtoul (yytext+2, NULL, 16)); }
<key,print,xref,is,location>{HEX16BIT} { PUT_UTF8_SKIP(4); }
<key,print,xref,is,location>{HEX32BIT} { PUT_UTF8_SKIP(8); }
<key,print,xref,is,location>. {
                        QUOTE_ECHO; }

<quote>\n              { QUOTE_ECHO;
                         lineno++;
                         BEGIN(quote_caller); }
<quote>{HEX8BIT}       { qc (strtoul (yytext+2, NULL, 16));
                         BEGIN(quote_caller); }
<quote>{HEX16BIT}      { PUT_UTF8_SKIP(4);
                         BEGIN(quote_caller); }
<quote>{HEX32BIT}      { PUT_UTF8_SKIP(8);
                         BEGIN(quote_caller); }
<quote>.               { QUOTE_ECHO;
                         BEGIN(quote_caller); }

\n                    { lineno++; }
.                     { ; }

%%


main(int argc, char* argv[])
{
  char * program_invocation_short_name;

  if ( argc > 1 ) {
    fprintf(stderr, "This is `tex2xindy' $Revision: 1.12 $.\n");
    fprintf(stderr, "Writing attribute names to file \"%s\".\n\n", argv[1]);
    attrfd = fopen(argv[1], "w");
  }

  program_invocation_short_name = strrchr(argv[0], '/');
  
  if (program_invocation_short_name == NULL)
    program_invocation_short_name = argv[0]; /* no '/' in program name */
  else
    program_invocation_short_name++; /* point to program name, after '/' */

  if (strcmp(program_invocation_short_name, IDX2RAW_NAME) == 0) {
    /* enforce index mode */
    glos_mode = 0;
    auto_glo_idx = 0;
  }

  if (strcmp(program_invocation_short_name, GLO2RAW_NAME) == 0) {
    /* enforce glossary mode */
    glos_mode = 1;
    auto_glo_idx = 0;
  }

  yylex();
  if (attrfd) fclose(attrfd);
  if (errors > 0) {
      exit( 1 );
  } else {
      exit( 0 );
  }
}

/*
  $Log: tex2xindy.l,v $
  Revision 1.12  1999/10/13 08:06:44  kehr
  Changed revision number message back to RCS-tag. No functional changes.

  Revision 1.11  1999/10/13 08:05:10  kehr
  Merged bugfix from Thomas Henlich with my own modifications.

  Revision 1.10  1999/09/23 06:53:32  kehr
  Fixed wrong raw index generation for cross-ref keywords.

  Revision 1.9  1999/04/27 09:01:17  kehr
  Defined a clean exit code as suggested by Klaus Guntermann
  <guntermann@iti.informatik.tu-darmstadt.de>.

  Revision 1.8  1999/04/27 08:57:48  kehr
  Added quoting patch sent by Thomas Henlich <thenlich@Rcs1.urz.tu-dresden.de>

  Revision 1.7  1999/04/27 08:56:59  kehr
  Another checkin.

  Revision 1.6  1997/02/13 14:42:50  kehr
  Minor changes.

  Revision 1.5  1997/01/21 16:44:36  kehr
  Bugfix: State <print> was not changed back to <key> if {LEVEL} was found.

  Revision 1.4  1997/01/17 16:30:37  kehr
  Rewrote makeindex4 and heavily modified tex2xindy.

  Revision 1.3  1996/07/19  17:15:18  kehr
  Made this program comaptible with lex by correctly enclosing all
  actions--stupid bug, 'cause lex didn't complain and flex did some
  wonderful matching of all the actions such that no error was
  discovered.

  Revision 1.2  1996/07/11  14:16:55  kehr
  Complete Major checkin before changing the letter-groups.

  Revision 1.1  1996/06/24  08:53:57  kehr
  Initial checkin of the Makefile, README and tex2xindy.
*/
