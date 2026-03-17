# Python Core

Parser-first breeding engine for implicit formulas.

Modules:
- `ast_nodes.py`: formula node types
- `parser.py`: safe parse from formula text to AST
- `serializer.py`: AST back to formula text
- `validator.py`: structure and numeric checks
- `breeder.py`: subtree crossover on validated ASTs
- `analyze_offspring_space.py`: estimate the bounded offspring space for two parsed parents
- `enumerate_offspring.py`: generate labeled JSON for all unique single-swap offspring

This package is intended to replace the string-splice breeding logic in `App.tsx`.
