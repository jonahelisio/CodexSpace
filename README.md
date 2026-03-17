# CodexSpace

CodexSpace is an experimental Python-first environment for implicit field exploration, scalar-field sampling, and AST-based cross breeding of formulas.

This public snapshot includes:

- a safe field engine for evaluating formulas over `(x, y, z)`
- a CLI for sampling and exporting field regions
- a parser-first Python breeding core for subtree crossover
- a small GitHub Pages site in `docs/`

Project areas:

- `field_engine.py`: safe formula compilation and field sampling
- `field_map.py`: CLI for grid sampling, summaries, slices, and exports
- `exports.py`: CSV / JSON / XYZ / OBJ / PLY export helpers
- `python_core/`: parser, serializer, validator, breeder, and offspring enumeration tools
- `docs/`: project website for GitHub Pages

Start here:

- `README_PYTHON_FIRST.md`
- `README_FIELD_LANGUAGE.md`
- `README_FIELD_STRATIGRAPHY.md`
- `python_core/README.md`

This repository is an early public snapshot of an active project.
