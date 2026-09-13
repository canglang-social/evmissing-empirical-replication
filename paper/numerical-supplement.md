# Numerical supplement

## Saved discrepancy evidence

Plymouth conditions are [remove years, adjust]; Brest conditions 2 and 3 mean reduced adjusted and reduced naive. All seven rows failed the original test; the final column shows the separate reference error, not a replacement result. Values are displayed to nine decimals; original JSON determines status.


Table S1. Primary discrepancies and separate reference-optimizer values.


| Dataset| Condition| Quantity| Primary| Published| Absolute error| Limit| Reference| Reference error|
|---|---|---|---:|---:|---:|---:|---:|---:|
| Plymouth | [False, True] | par0 | 128.776231113 | 128.770000000 | 0.006231113 | 0.005100000 | 128.771317149 | 0.001317149 |
| Plymouth | [False, True] | return100 | 215.478293518 | 216.000000000 | 0.521706482 | 0.510000000 | 215.510400474 | 0.489599526 |
| Plymouth | [True, True] | par1 | 17.657292743 | 17.650000000 | 0.007292743 | 0.005100000 | 17.653982487 | 0.003982487 |
| Plymouth | [True, True] | se0 | 4.605521290 | 4.600000000 | 0.005521290 | 0.005100000 | 4.604730745 | 0.004730745 |
| Plymouth | [True, False] | se0 | 4.544831541 | 4.550000000 | 0.005168459 | 0.005100000 | 4.545716410 | 0.004283590 |
| Brest | 2 | scale σ | 11.924808852 | 11.930000000 | 0.005191148 | 0.005100000 | 11.925930995 | 0.004069005 |
| Brest | 3 | scale σ | 12.004301678 | 12.010000000 | 0.005698322 | 0.005100000 | 12.007526508 | 0.002473492 |

Reference evidence uses the unmodified R 4.4.2 nmmin body with local platform shims and the independent density, not a full R package execution. Fixed quartile/zero-shape starts, maxit=500 and relative tolerance sqrt(machine epsilon) were used. All reference optimizer status codes were zero. These receipts establish the numerical explanation, not the exact original author environment. They were not rerun for this editorial pass.


Sources: [Plymouth primary](../evidence/table4_comparison.json), [Plymouth reference](../evidence/nmmin_reference_result.json), [Brest primary](../evidence/brest_table_comparison.json), [Brest reference](../evidence/brest_nmmin_reference.json).

## Computational settings

Python 3.12, NumPy 2.3.5, SciPy 1.18.1. Point fitting uses Nelder–Mead with maxfev=5000 per start, xatol=1e-8, fatol=1e-9; three quartile-based starts request shape 0, −0.2 and +0.2, capped toward zero where required for initial support. Converged starts must agree in objective within 1e-5. Profile nuisance fits use maxfev=5000, xatol=1e-7, fatol=1e-8, with a zero-shape fallback for an infeasible profile start. Bracketing allows 20 expansions; Brent allows 50 iterations with xtol=1e-5; endpoint likelihood residual must be at most 0.001.


Standard errors use central finite-difference observed information, step sizes 1e-5 times max(1,|μ|), max(1,σ), and 1 for shape; the half-step calculation must change each standard error by at most 0.001 and information must be positive definite. These are local checks, not certificates of global optimality. Numerical details are inspectable in [replay.py](../replay.py), [audit_endpoints.py](../audit_endpoints.py) and the original application scripts/receipts.


## Distinct counts and historical validation

The 120 scalar comparisons comprise parameters, standard errors, return levels and interval endpoints across eight configurations. Original outcomes remain 113 pass and seven fail. The 48 printed endpoints are a subset of these 120. The 96 subsequent solver checks instead use two independent nuisance starts per endpoint; they are not 96 additional published quantities or an acceptance score.


The earlier packaged local chain completed both aggregations/fits and Plymouth's 48 checks, then stopped after 42 Brest checks at the former 10 CPU second audit limit. Only the remaining six checks were completed in a separately capped continuation. At that historical checkpoint the default cap had changed to 15 CPU seconds without a full-chain rerun. Original stopped and continuation receipts are preserved. A separate replay compared 96 fitted quantities (excluding standard errors), maximum change 7.12e-6; this is a third, distinct count.


A development calibration reused 40 datasets (ten per parent distribution) across six methods. Its revised numerical regression passed 240 dataset/method units. This does not reproduce the original simulation-performance study; 348 small-sample descriptive summaries do not support coverage or heavy-tail performance claims. Calibration failures, fixes and costs remain in the state ledger and original receipts, outside the paper's empirical claim.


## Final candidate acceptance

The subsequent frozen upstream-retrieval candidate completed its first uninterrupted acceptance in 30.135660 elapsed seconds: setup 5.868547, numerical chain 21.825473, diagnostic data 0.913200 and plots 1.515001 seconds. It verified the two pinned archive hashes, reconstructed all annual inputs, and preserved every original flag in 120 scalar comparisons including standard errors (113 pass, seven fail). All 48 printed endpoints and 96 solver checks passed. Maximum scalar change from the saved primary values was 1.510259887e-5. [Full receipt](../evidence/acceptance.json), [frozen candidate](../evidence/accepted-source-manifest.json), [setup receipt](../evidence/setup-receipt.json), [uninterrupted chain](../evidence/chain-receipt.json).


The run used existing Python 3.12, NumPy 2.3.5, SciPy 1.18.1 and Matplotlib 3.10.7 installations. No fresh dependency installation or another-machine test was performed. Historical R-reference calculations were not rerun. This acceptance validates the exact local candidate; successful retrieval is not a data-licensing determination or a guarantee of publication.

