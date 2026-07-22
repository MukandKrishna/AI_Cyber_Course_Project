# Frozen Feature Tables

This folder contains the modelling inputs used for the PASYDA experiments.

- `pair_level_features_base_frozen.csv` is the frozen base feature table copied from `../eda/pair_level_features.csv`.
- `pair_level_features_enhanced.csv` is the derived feature table built by `../../src/features/build_enhanced_features.py`.

Use the base table for the core experiments and the enhanced table for the contextual-feature and ablation runs.

Do not edit the frozen base file directly. If you need a new feature set, create another derived table here and document how it was produced.
