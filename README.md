# abnormalizer

Makes indentation and spacing compliant with *Le Norme*

## Installation

	brew install python3
	git clone https://github.com/galacticgargleblaster/abnormalizer
	pip3 install --editable abnormalizer

## Usage

`abnormalizer [FILE]`

at the moment, abnormalizer operates on `.h` files only

`FILE` is backed up as `FILE.BAK` before work begins

--------

### What does this do?

Makes indentation and spacing compliant with *Le Norme*

### What doesn't this do?

- fix syntactical errors
- reorder the sequence of tokens
- handle formatting of nested struct definitions
- make functions shorter
- change global/typedef/struct/enum names to make them norme-compliant

### Will this break my program?

Maybe.  It's a program that edits your code so you don't have to. 

### The output is ugly!

¯\\\_(ツ)_/¯ make a branch that makes it prettier

### About

This is an atrocious hack, a pile of fragile heuristics built atop pygments, a legitimate syntax-highlighting library.

------------

# Appendix

## Recommended formatting tool options for the *Real World*

from various eras, and for various languages:

- [whatstyle](https://github.com/mikr/whatstyle)
- [clang-format](https://clang.llvm.org/docs/ClangFormat.html)
	- [zed0 clang-format-configurator](https://zed0.co.uk/clang-format-configurator/)
- [uncrustify](https://github.com/uncrustify/uncrustify)
- [indent](https://www.gnu.org/software/indent/manual/indent.html) (`man indent` if you're on *nix)
- [gofmt](https://golang.org/cmd/gofmt/)
- [dart_style](https://github.com/dart-lang/dart_style)

## Further Reading

http://beza1e1.tuxen.de/articles/formatting_code.html

#todo:
- make .c files work
- add include guards to .h
- name-mangle identifiers into g_foo, s_bar, t_baz, etc. 