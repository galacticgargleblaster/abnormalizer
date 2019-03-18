# abnormalizer

## Installation

`tbd`

## Usage

`abnormalizer [FILE]`

abnormalizer operates on `.c` and `.h` files only

`FILE` is backed up as `FILE.BAK` before work begins

## What does this do?

Makes indentation, spacing, naming of include guards and identifiers compliant with *Le Norme*

## What doesn't this do?

Fix syntactical errors, handle formatting of nested struct definitions

## Will this break my program?

Maybe.  It's a program that edits your code so you don't have to. 

### Why???

It is a software person's duty to minimize the repetition of tasks which they themselves have done before.

This is a lazy hack built atop pygments, a syntax-highlighting library.

### *Real World* formatters for *Real World* code style standards

from various eras, and for various languages:

- [uncrustify](https://github.com/uncrustify/uncrustify)
- [clang-format](https://clang.llvm.org/docs/ClangFormat.html)
- indent (`man indent` if you're on *nix)
- [gofmt](https://golang.org/cmd/gofmt/)
- [dart_style](https://github.com/dart-lang/dart_style)


http://beza1e1.tuxen.de/articles/formatting_code.html

indenting local and global
spacing in function prototypes
spacing around assignments at global scope
header guards
auto-prefixing