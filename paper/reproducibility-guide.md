# Reader's reproducibility guide

Use the [upstream-retrieval candidate](../README.md). It reconstructs the two empirical applications from version-pinned source archives; it does not reproduce the original simulation study. [Manuscript](manuscript.md), [numerical supplement](numerical-supplement.md), [Tables S2-S3](comparison-appendix.md).


## Setup and run

Use Python 3.12 with NumPy 2.3.5, SciPy 1.18.1 and Matplotlib 3.10.7. requirements-plot.txt includes the numerical dependencies. For a new installation, create a virtual environment and install that file; the acceptance check used existing installations rather than testing a fresh installation. From a clean copy containing the files listed in candidate-manifest.json, run:


```sh
python setup_sources.py
python run_all.py --output-dir results
python prepare_diagnostics.py --results-dir results --output results/diagnostics.json
python render_diagnostics.py --input results/diagnostics.json --output-dir results/figures
```

Setup downloads evmissing 1.0.2 and Renext 3.1-4 from the exact URLs in [setup_sources.py](../setup_sources.py), checks their pinned SHA256 hashes, and reads named archive members without executing R. The Brest event CSVs come from Renext; its annual reference is decoded from evmissing's BrestSurgeMaxima. No prebundled annual JSON is needed. The annual aggregators independently compare 27 Plymouth and 162 Brest rows to the source objects.


A completed setup creates sources/ and data/. Existing setup/output directories are rejected to avoid overwriting evidence. On an error, inspect setup-receipt.json, results/receipt.json and the stage logs. The numerical chain has a 120-second overall cap; each application fit is capped at 200,000 calls/30 CPU seconds/60 elapsed seconds, and each audit at 5,000 calls/15 CPU seconds/30 elapsed seconds. Partial output is not a successful run. Plots use English labels and Matplotlib's bundled DejaVu Sans; no macOS-only font is required.


## Verified result and boundaries

The first exact-candidate acceptance passed in 30.14 seconds, including upstream retrieval and plots. [Acceptance receipt](../evidence/acceptance.json) records all 120 scalar comparisons including standard errors: 113 passed, seven original discrepancies remained, and no original flag changed. All 48 printed endpoints and 96 independent solver checks passed. The frozen code was unchanged throughout. See the [source manifest](../evidence/accepted-source-manifest.json), [chain receipt](../evidence/chain-receipt.json) and [render receipt](../evidence/render-receipt.json).


Earlier stopped and separately continued runs remain in the private research record as historical evidence; they are not part of this public package. They are not rewritten as uninterrupted successes. The final acceptance does not re-execute historical R-reference calculations or the simulation study, and does not prove fresh-install or second-machine portability. Data are retrieved from the pinned original package archives under their published terms; see [data provenance and notices](../DATA-PROVENANCE.md). The archived setup receipt records the technical test's contemporaneous licence_cleared=false flag, not an editorial or legal determination. Final public release is separate from the successful technical check.

