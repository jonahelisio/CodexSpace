# Python-First Core

This project is moving away from the React prototype in [App.tsx](/home/jody/Desktop/CodexSpace/App.tsx) and toward a Python-first field engine.

Files:
- `field_engine.py`: safe formula compilation, grid sampling, and sign/surface classification
- `field_map.py`: CLI for generating full field samples, slices, summaries, and optional surface exports
- `exports.py`: CSV, JSON, XYZ, OBJ, and PLY writers

The core model is now field-first:
- `value < -epsilon` => `negative`
- `abs(value) <= epsilon` => `surface`
- `value > epsilon` => `positive`

Example commands:

```bash
python3 field_map.py --preset sphere --resolution 25 --outdir outputs/sphere
python3 field_map.py --preset gyroid --bound 5 --resolution 35 --epsilon 0.08 --outdir outputs/gyroid
python3 field_map.py --formula "sin(x)*cos(y) + sin(y)*cos(z) + sin(z)*cos(x)" --bound 5 --resolution 35
```

Primary outputs:
- `field_samples.csv`: full sampled field with values and region labels
- `slice_*.csv`: slice-plane subset for 2D field-map inspection
- `field_summary.json`: counts, range, and run parameters
- `surface_points.*`: optional near-zero export for meshing or viewing
- `negative_points.*`, `surface_points.*`, `positive_points.*`: optional separate layer-style exports
- `field_regions_color.ply`: optional single PLY with colors for inside/surface/outside regions
