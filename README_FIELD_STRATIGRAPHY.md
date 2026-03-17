# Field Stratigraphy

This note documents a useful extension of the current field engine model:
instead of dividing the sampled field into only three regions,

- `negative`
- `surface`
- `positive`

we can divide it into multiple ordered bands around the implicit surface.

That layered interpretation is what we will call `field stratigraphy`.

## Core Idea

The current engine classifies each sampled point by comparing its field value `f(x, y, z)` to a threshold `epsilon`.

- `f < -epsilon` -> `negative`
- `|f| <= epsilon` -> `surface`
- `f > epsilon` -> `positive`

This is already a 3-layer model.

Field stratigraphy extends that same idea by introducing more thresholds around zero and treating them as nested layers.

Example with `e = epsilon`:

- `f < -3e` -> deep negative
- `-3e <= f < -e` -> inner transition band
- `-e <= f <= e` -> surface core
- `e < f <= 3e` -> outer transition band
- `f > 3e` -> far positive

This turns a single near-zero shell into a stack of meaningful regions.

## Why This Matters

The field engine is not only producing a surface. It is describing how space behaves around the surface.

With stratigraphy:

- the zero-crossing is no longer the only interesting event
- near-surface behavior becomes visible
- positive and negative space can be partitioned into shells, not just signs
- the model can be read as a layered field, not only a binary inside/outside split

This is especially useful when the outputs are being used for:

- visual explanation
- artistic decomposition
- implicit-form analysis
- transition-zone modeling
- thickened shell extraction
- comparing inner and outer field behavior

## Nested Bands

The clean way to do this is to work with nested bands, not separate unrelated exports.

That distinction matters.

If you run the engine once with `epsilon = e` and again with `epsilon = 3e`, the second run does not automatically give you a new independent object. It gives you a larger near-zero region that contains the first one.

In other words:

- thin surface: `|f| <= e`
- fat surface: `|f| <= 3e`

The fat surface includes the thin surface.

So the mathematically clean interpretation is not:

- "these are two separate surfaces"

It is:

- "these are nested level bands around the same zero set"

The useful region is often the difference between them:

- shell-only band: `e < |f| <= 3e`

That band is unique.
It is not duplicated by the inner surface.
It is the extra thickness surrounding the original near-zero core.

## Why Nested Bands Are Better Than Unrelated Exports

Separate unrelated exports can be misleading because they encourage viewing each threshold run as a different object.

That causes several problems:

- overlapping geometry may be counted twice
- the wider band may appear to replace the thinner one instead of containing it
- the field loses its ordered structure
- interpretation becomes visual rather than mathematical

Nested bands avoid that.

They preserve containment:

- every smaller band sits inside a larger band
- each band represents a specific interval of field values
- together the bands form a partition of the sampled field

This lets you say exactly what each region means.

For example:

- `|f| <= e` = immediate surface core
- `e < |f| <= 2e` = first offset shell
- `2e < |f| <= 3e` = second offset shell

Those statements are precise.
They do not depend on a viewer's interpretation of overlapping exports.

## The Difference View

This is the most important practical idea.

If you want a `fat solid surface`, compute it as a band difference, not just as a second surface export.

Given thresholds `e1 < e2`:

- inner band: `|f| <= e1`
- outer band: `|f| <= e2`
- shell-only band: `e1 < |f| <= e2`

The shell-only band is the clean stratigraphic layer between the two surfaces.

This gives you three distinct components:

- central surface core
- surrounding shell
- remaining positive/negative far field

That is much more useful than exporting `surface@e1` and `surface@e2` as if they were separate solids.

## Symmetric and Signed Stratigraphy

There are two main ways to build stratigraphy.

### 1. Symmetric bands by absolute value

This ignores sign inside each band and groups points by distance from zero in field-value space.

Example:

- `|f| <= e`
- `e < |f| <= 2e`
- `2e < |f| <= 3e`
- `|f| > 3e`

This is good when the main goal is shell thickness around the implicit surface.

### 2. Signed bands

This preserves whether the point lies on the negative side or positive side of the field.

Example:

- `f < -3e`
- `-3e <= f < -2e`
- `-2e <= f < -e`
- `-e <= f <= e`
- `e < f <= 2e`
- `2e < f <= 3e`
- `f > 3e`

This is better when the negative and positive sides have different meanings and should not be merged.

For this project, signed bands are likely the more powerful model because the engine already treats `negative`, `surface`, and `positive` as distinct outputs.

## Interpreting the Three Existing Outputs

Under the current engine, the three outputs can already be understood as the first stratigraphic cut:

- `negative` = field values clearly below zero
- `surface` = the near-zero tolerance band
- `positive` = field values clearly above zero

So the current model is not replaced by field stratigraphy.
It is generalized by it.

The existing triplet becomes the base layer from which richer subdivisions can be built.

## Example: Default Epsilon and `3 * epsilon`

Let `e` be the base epsilon.

Run A:

- `negative_A`: `f < -e`
- `surface_A`: `|f| <= e`
- `positive_A`: `f > e`

Run B:

- `negative_B`: `f < -3e`
- `surface_B`: `|f| <= 3e`
- `positive_B`: `f > 3e`

From these two thresholds, the real stratigraphic pieces are:

- deep negative: `f < -3e`
- inner negative shell: `-3e <= f < -e`
- surface core: `-e <= f <= e`
- outer positive shell: `e < f <= 3e`
- far positive: `f > 3e`

If you want a symmetric thick shell around the surface, use:

- thick shell: `e < |f| <= 3e`

If you want a full fattened surface body, use:

- fat surface body: `|f| <= 3e`

If you want both core and shell separated, keep:

- core: `|f| <= e`
- shell: `e < |f| <= 3e`

That is the clean decomposition.

## Beginning Formula for Band Thresholds

If the current epsilon is already working well, a simple starting stratigraphy is:

- band 0: `|f| <= e`
- band 1: `e < |f| <= 2e`
- band 2: `2e < |f| <= 3e`

Or signed:

- `f < -3e`
- `-3e <= f < -2e`
- `-2e <= f < -e`
- `-e <= f <= e`
- `e < f <= 2e`
- `2e < f <= 3e`
- `f > 3e`

This works because the bands are ordered, interpretable, and easy to compute.

## Relationship to Grid Density

Grid density still matters.

If the grid is coarse, a very thin band may contain too few samples to read well.
If the grid is dense, thinner bands become usable.

So stratigraphy works best when:

- `epsilon` is chosen with grid step in mind
- the number of bands is not so high that each band becomes sparse

A practical rule is:

- coarse grid -> fewer, wider bands
- dense grid -> more, thinner bands

## Recommended Mental Model

Think of the field as geology around an implicit zero-level seam.

- the zero seam is the center
- epsilon defines the first visible layer around it
- larger multiples of epsilon define surrounding strata
- signed bands preserve which side of the seam the material belongs to

This is why `field stratigraphy` is a useful name.

It treats the field as a layered structure, not just a thresholded surface.

## Summary

Field stratigraphy means dividing field-value space into ordered, nested bands around zero.

The important implementation idea is:

- use nested thresholds
- compute shells by interval differences
- avoid treating wider-threshold exports as unrelated objects

The clean formulation is interval-based:

- core: `|f| <= e`
- shell 1: `e < |f| <= 2e`
- shell 2: `2e < |f| <= 3e`
- far field: `|f| > 3e`

Or with sign preserved:

- negative strata
- surface core
- positive strata

This keeps the field engine mathematically consistent while opening much richer modeling and visualization possibilities.
