# Empirical replication of block maxima with missing observations

Felix Han · Independent researcher · canglangzhuoxi@gmail.com

Partial computational replication of Simpson and Northrop (2026), DOI [10.1002/env.70075](https://doi.org/10.1002/env.70075). This covers the Plymouth and Brest empirical applications, not the original simulations or a new method.

[Manuscript](paper/manuscript.pdf) · [Supplement](paper/supplement.pdf) · [Reader guide](paper/reproducibility-guide.md) · [Data provenance](DATA-PROVENANCE.md)

Use Python 3.12. In a fresh checkout, install requirements-plot.txt in your environment, then run from this repository root:

```sh
python -m pip install -r requirements-plot.txt
python setup_sources.py
python run_all.py --output-dir results
python prepare_diagnostics.py --results-dir results --output results/diagnostics.json
python render_diagnostics.py --input results/diagnostics.json --output-dir results/figures
```

Setup downloads the two pinned upstream archives and verifies their SHA256 hashes. Source data are not mirrored here. It creates sources/ and data/ locally; use a clean directory. Read receipt status fields after each stage.

The single bounded local acceptance passed: 113/120 primary comparisons, all 48 printed endpoints and 96 solver checks. Seven primary discrepancies remain, with separate reference-optimizer evidence. Existing dependencies were used; fresh installation and another machine were not tested. Historical reference calculations are retained evidence, not re-executed by this advertised chain.

Code: GPL-3.0-or-later. Article and author-created supplementary prose/figures: CC BY 4.0, limited to the author's rights. Third-party source, observations and published comparison targets retain their own rights and notices. See [licence scope](LICENSE-SCOPE.md).

OpenAI Codex assisted implementation, evidence organization and drafting; NumPy/SciPy performed calculations and Matplotlib produced diagnostic plots. The named human author is responsible for the work. This repository is a replication submission candidate, not evidence of journal acceptance.
