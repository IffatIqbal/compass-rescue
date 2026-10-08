# Compass Rescue v0.2 — actual hemibrain connectivity

This version replaces the synthetic ring wiring with **106 reconstructed neurons, 1,932 measured directed connections, and 46,842 synapses** from a public extract of **Janelia hemibrain v1.2.1**. It includes the original CSV, individual neuron IDs, model fitting, perturbation/rescue experiments, an offline viewer, and reproducibility tests.

**This is a complete runnable computational pipeline, not a completed biological rescue study.** It uses real anatomical connectivity and task-fitted dynamics. It does not use the entire fly brain, fit actual recordings, or verify optical/genetic access. Three stimulation *groups* are selected, not three individual neurons.

## Start here

Open **Compass-Rescue.html** in your browser. No server, installation, or internet is needed to replay results. Choose one of eight held-out trials, play or scrub the trajectories, inspect the measured connectivity matrix, and search neuron IDs. Target IDs and reporters are listed explicitly. The viewer replays computed experiments; it does not rerun numerical optimization in the browser.

To regenerate everything using Python 3.10+:

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python prepare.py
python experiment.py
python -m unittest test_pipeline.py
python plot_results.py
```

On Windows replace the activation command with `.venv\Scripts\activate`. The experiment took about 25 seconds in the development environment with single-threaded BLAS; your machine may differ. No account, GPU or API key is required because the measured source extract is bundled.

## What is real, and what is modeled?

| Component | Status |
|---|---|
| 106 neuron body IDs and cell-type labels | Source extract |
| 46 EPG, 18 PEG, 20 PENa, 22 PENb neurons | Source extract |
| EB/PB synapse counts and adjacency | Source extract, retained without graph symmetrization |
| Preferred heading phase | Assumed coordinate derived from source index metadata; non-EPG preferences aligned to measured EPG inputs |
| Excitatory functional weights | Nonnegative task fit with a count-derived ridge prior; not measured physiological strengths |
| Inhibitory stabilization | Fitted population-mean inhibition; **not reconstructed inhibitory neurons or synapses** |
| Time constants, firing rates, noise, actuator dynamics | Modeling assumptions |
| Angular-velocity input | Assumed multiplicative PENa hemisphere gating |
| Reporter neurons | Eight real EPG body IDs, one per phase sector; optical access unverified |
| Stimulation | Three sector groups of real body IDs; independent signed actuation unverified |

The measured graph contributes every allowed recurrent excitatory connection: `W[i,j] = 0` wherever recorded counts are zero. Fitting can weaken recorded edges; no absent excitatory connections are introduced. The separate population-inhibition term is an added effective interaction and is not covered by that adjacency claim. Synapse counts remain available independently of all fitted weights.

## Source and provenance

- Janelia hemibrain dataset version **v1.2.1**.
- Public source: https://github.com/aplbrain/seismic
- Immutable commit: `1a789eefc2ca03c1f79e283069e41d20d12ed91f`.
- File: `neuroaiengines/networks/hemibrain_conn_df_both.csv`.
- SHA-256: `0ef25fab90a598160235b48c30ac7af895289750df19536e30e9047d8833261f`.
- Archived extraction code identifies traced, noncropped EPG/PEN/PEG cells with EB/PB connectivity. Delta7 is removed upstream. This is an existing filtered extract, not a fresh whole-dataset download.
- ROI-specific rows are summed into directed neuron pairs: 2,092 rows → 1,932 pairs. Matrix rows are postsynaptic and columns presynaptic.
- Upstream SEISMIC MIT notice is preserved in `data/SEISMIC-LICENSE.txt`. Cite the original hemibrain resource and the SEISMIC source when using this derived model.

Upstream `pull_data.py` documents extraction intent but contains a literal filename formatting bug. This pipeline relies on the committed CSV, pins its checksum, and does not silently claim to have reproduced the original neuPrint extraction.

## Equations and fit

The state contains one nonnegative rate for each recorded neuron. Let C be measured counts, W fitted excitatory weights on C's support, h a population-inhibition coefficient vector, b a bias, g signed PENa gating, and v sensory angular velocity:

`tau dr/dt = -r + ReLU(W_plant [r * (1 + v g)] - h mean(r) + b + B u)`.

Independent Gaussian process noise is added; rates are clipped to [0,3] as a numerical safeguard. Default dt=0.03 and tau=0.15 model units. The reported reference heading is initialized and integrated only for evaluation. There is **no imposed cosine recurrent graph and no synthetic advection term**.

`prepare.py` uses idealized profiles `r_i(theta)=0.45+0.3 cos(theta-phi_i)` and their derivatives at 96 phases and five velocities. It fits each cell's incoming nonnegative weights, inhibition and bias with bounded least squares. The 0.03 ridge penalty weakly favors count-normalized weights. This establishes a plausible task-constrained model; it does not identify biological dynamics from anatomy. The preferred phase, harmonic target profiles and sign assumptions limit biological interpretation.

Damage weakens outgoing PENa connections with a Gaussian angular profile. It does not delete neurons. The plant's lesion strength/location, gain and time constant vary between trials.

## Controller and evaluation

Eight delayed noisy EPG measurements are projected onto a constant/cosine/sine basis, then reconstructed into estimated circuit activity. This low-dimensional reconstruction assumes the task manifold. The controller estimates lost recurrent current using fixed nominal matrices and projects compensation onto selected phase-sector groups. Commands are clipped to ±0.35. It never receives true heading, turn velocity or an intact parallel circuit's state. Its nominal lesion is centered at 1.0 rad with strength 0.65 regardless of the actual test lesion. It does not compensate the velocity-gated part of lost input explicitly.

Selection searches all 56 three-group combinations at gains [0.5,1,1.5,2]. The objective is mean error plus 0.5 error standard deviation plus mean stimulation cost on six training trials. This is exhaustive only over the stated discrete candidates and law. The selected gain is the upper search endpoint, so no unrestricted optimum is claimed. The fit uses idealized task profiles; selection uses training seeds 310,333,356,379,402,425. Final test seeds 8001,8032,8063,8094,8125,8156,8187,8218 are not used for fitting or selection.

Eight held-out trials compare intact, damaged, constant stimulation, one fixed random target set and selected feedback. Twelve independently sampled target sets provide an additional baseline distribution. Baselines use the same channel count and amplitude bound but are **not energy matched**. Constant stimulation is +0.06 per channel, not an optimized constant input. Equal channel count also does not mean equal number of stimulated neurons. Different sector groups contain different cell counts. Numerical stimulation cost is command-squared cost, not physical energy or total per-cell stimulation dose.

From 7–9 model seconds, both turns and stimulation are off. Hold error and net angular drift are reported separately. Continuous-stimulation runs retain the same frozen targets and gain. Stress tests span five lesion severities and four recurrent gains at a separate seed. They are empirical outcomes, not a proof of impossibility outside a boundary.

## Results and limits

See `RESULTS.md` and the viewer for recorded numbers. Feedback partially compensates the modeled damage; it does not restore intact accuracy. Removing stimulation produces substantial drift, so **durable recovery is not demonstrated**. No significance or generalization claim beyond these model conditions is warranted. Multi-animal validation, measured physiology, omitted inhibitory circuits, realistic optical access and prospective fly experiments remain necessary for biological claims.

## Reproducibility files

- `prepare.py`: verified source import and task fitting.
- `data/hemibrain_conn_df_both.csv`: original source bytes.
- `data/circuit.npz`: counts, fitted weights, inhibition, phase map, IDs and types.
- `data/provenance.json`, `data/neurons.json`: provenance and annotations.
- `model.py`: connectome-constrained dynamics and feedback.
- `experiment.py`: target search, held-out evaluation, random baselines and stress test.
- `test_pipeline.py`: source integrity, orientation/support, replay, numerical and split checks.
- `results/benchmark.json`, `results/trials.csv`: full numerical outputs.
- `viewer.template.html`, `Compass-Rescue.html`: viewer source/output.
- `plot_results.py`, `results/benchmark.png`: exported figure.

Related sources: https://www.virtualflybrain.org/ ; https://neuprint.janelia.org/ ; https://github.com/aplbrain/seismic ; https://www.nature.com/articles/s41586-024-07982-0 .
