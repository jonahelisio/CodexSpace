# Field Language

This note defines a cleaner vocabulary for discussing field-engine outcomes.

The goal is to separate:

- what is mathematically valid
- what is spatially meaningful
- what genuinely produces a field-native surface
- what only becomes interesting after downstream reconstruction

It also avoids terms that feel unnecessarily harsh or misleading in project discussion.

## Formula vs Field

In the broad mathematical sense, a `formula` is any valid expression.

Examples:

- `x**2 + y**2 + z**2 - 1`
- `sin(x) * cos(y)`
- `1 - 0.5`

So yes, `1 - 0.5` is formally a formula.

But not every formula is useful for spatial modeling.

For this project, it helps to distinguish four levels:

- `formula`: any valid mathematical expression
- `field formula`: a formula evaluated over `(x, y, z)`
- `spatial field formula`: a field formula whose value changes with position
- `surface-bearing field`: a spatial field whose sampled region contains a usable near-zero structure

Under this vocabulary:

- `1 - 0.5` is a valid formula
- it can be evaluated as a field formula
- it is not meaningfully spatial
- it is not surface-bearing

## Spatially Inert Field

Preferred term:

- `spatially inert field`

Definition:

A field whose value does not vary across the sampled spatial region in any meaningful way, or varies so little that it behaves as effectively constant for the current analysis.

Typical signs:

- `sample_min == sample_max`, or nearly so
- only one sign appears across the sampled grid
- no near-zero band is detected
- the exported point cloud represents a filled region of one class rather than a structured surface

Example:

- `1 - 0.5`

This evaluates to `0.5` everywhere, so every sampled point is `positive`.

Why this term is useful:

- it is accurate
- it is neutral
- it describes behavior rather than judging quality

## Surface-Bearing Field

Preferred term:

- `surface-bearing field`

Definition:

A field that produces a meaningful near-zero region in the sampled domain and therefore supports extraction of a readable implicit surface or surface band.

Typical signs:

- sign variation exists
- a near-zero band is detected
- the exported `surface` points correspond to a coherent structure

This is the main success case for the field engine.

## Sign-Structured Field

Preferred term:

- `sign-structured field`

Definition:

A field that contains both positive and negative regions in the sampled domain, even if the near-zero surface is sparse, thin, or not yet useful.

This is weaker than a surface-bearing field, but still spatially meaningful.

It indicates that the field is organizing space, even if the current sampling or threshold is not ideal.

## Surface-Band-Only Field

Preferred term:

- `surface-band-only field`

Definition:

A field that yields detectable near-zero samples but does not yet show robust sign-separated structure across the sampled grid.

This can happen when the surface is thin, sampling is coarse, or the field behavior is unusual.

## Reconstruction-Derived Form

Preferred term:

- `reconstruction-derived form`

Definition:

A form that becomes visible only after a downstream reconstruction tool infers a mesh or envelope from exported point data.

This is different from a field-native surface.

The field engine may only provide:

- a classified point cloud
- a dense volume of one class
- or a sparse cloud with weak structure

The later tool then contributes major interpretive geometry.

This is still valuable, but it should be named separately from field-native surface discovery.

## Field-Native Form

Preferred term:

- `field-native form`

Definition:

A shape or structure that is already present in the field logic itself and can be observed directly through sign structure, surface band detection, or zero-set sampling, before downstream reconstruction adds interpretation.

This is the primary category for implicit-surface work.

## Reconstruction-Derived Artifact

Preferred term:

- `reconstruction-derived artifact`

Definition:

A mesh or form produced by a reconstruction process from input data that does not itself contain a clear field-native surface.

This is not necessarily a mistake.
It may still be visually rich or analytically useful.

It simply means the visible form owes much of its existence to the reconstruction process rather than to a well-formed implicit surface in the original field.

## Recommended Replacement for "Degenerate"

The word `degenerate` is common in mathematics, but it can sound harsher than necessary in project language.

For this work, preferred replacements are:

- `spatially inert`
- `constant-field`
- `non-varying`
- `structurally thin`
- `reconstruction-derived`

Recommended usage:

- use `spatially inert field` for formulas like `1 - 0.5`
- use `reconstruction-derived form` or `reconstruction-derived artifact` for the downstream Meshlab result

Avoid using `degenerate` in user-facing writing unless the context is explicitly mathematical.

## The `offspring_002_degen1` Case

The run in `outputs/offspring_002_degen1` is best described as:

- a `spatially inert field`
- with a `reconstruction-derived form`

Why:

- the formula is `1 - 0.5`
- the field value is `0.5` everywhere
- the sampled domain contains no zero crossing
- all `27,000` samples are classified as `positive`
- the later mesh results arise from reconstructing the exported cloud, not from a field-native implicit surface

This makes the case useful, but in a different category than a successful offspring surface.

## Suggested Taxonomy

For current project discussion, this vocabulary should be sufficient:

- `surface-bearing field`
- `sign-structured field`
- `surface-band-only field`
- `spatially inert field`
- `field-native form`
- `reconstruction-derived form`
- `reconstruction-derived artifact`

## Summary

The main distinction is:

- some outputs are interesting because the field itself contains meaningful structure
- some outputs are interesting because a later reconstruction process extracts or invents form from the exported data

Both are valid lines of exploration.
They should simply be named differently.

For this project, the preferred language is:

- `spatially inert field` instead of `degenerate field`
- `reconstruction-derived form` instead of implying that the field engine alone produced the visible mesh
