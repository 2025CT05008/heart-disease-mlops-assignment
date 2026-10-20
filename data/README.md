# Dataset source and regeneration

The dataset is the UCI Heart Disease dataset, which combines records from the
Cleveland, Hungarian, Switzerland, and VA Long Beach sources. The repository
includes the combined raw CSV at `data/raw/heart_disease_combined.csv`, so
re-running the project does not require a download.

To download and combine the four processed source files from the
[UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/45/heart+disease),
run this from the repository root (requires an internet connection):

```bash
python scripts/download_data.py
```

Then regenerate the cleaned CSV and EDA figures:

```bash
python scripts/prepare_data.py
```

The downloader fetches the official UCI archive and writes the combined raw CSV
with a `source` column. Read the UCI dataset page for the variable descriptions.

The script writes `data/cleaned/heart_disease_cleaned.csv` and the figures in
`reports/figures/`. It removes the source identifier, validates and cleans the
feature columns, and converts the original `num` target to a binary `target`
(0 means no disease; any value above 0 means disease present). Missing feature
values are handled by the fitted training pipeline rather than filled using
the full dataset.

Dataset attribution: Janosi, A., Steinbrunn, W., Pfisterer, M., and Detrano, R.
Heart Disease. UCI Machine Learning Repository, 1988.
