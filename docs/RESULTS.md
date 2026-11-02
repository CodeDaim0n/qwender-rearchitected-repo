# Measured results and interpretation

[← Repository overview](../README.md) · [Architecture](ARCHITECTURE.md) · [Research paper](Credit_Architecture_Research_Paper.pdf)

## What the comparison establishes

**Component separation preserved all seven tested credit assessments.** The experiment then evaluates the additional workflow controls separately. It does not establish better underwriting or superior language quality.

## Controlled variables

Both arms use the same applications, exact score/attribution tensors, policy semantics, unadapted Qwen3.5-0.8B weights, prompts and generation settings. Each applicable paragraph is actually generated twice; no output cache is used. Greedy decoding uses a 320-token cap with thinking disabled and seed 20261102. Execution is on CPU with four Torch threads.

The scorecard is rebuilt using the original source and data splits. Its rounded ROC-AUC is 0.778 and KS is 0.437. The [scorer compilation evidence](../results/scorer_parity_metrics.json) reports zero sign inversions and zero AUC/KS difference; [attribution parity](../results/attribution_parity.json) reports zero fixed-point local-accuracy residual.

## Seven paired requests

| Original request fixture | Outcome | Raw model probability | Paragraph | Complete assessment |
| --- | --- | --- | --- | --- |
| [approval_with_controls](../results/approval_with_controls.json) | AC | 5.8% | VERIFIED | Identical |
| [decline_close_to_approval](../results/decline_close_to_approval.json) | DD | 69.9% | VERIFIED | Identical |
| [invalid_input_missing_field](../results/invalid_input_missing_field.json) | II | 84.3% | WITHHELD_BY_VERIFIER | Identical |
| [malformed_override_attempt](../results/malformed_override_attempt.json) | OVERRIDE_ATTEMPT | — | No language call | Identical |
| [malformed_string_value](../results/malformed_string_value.json) | MALFORMED_TYPE | — | No language call | Identical |
| [manual_review_not_behavioural](../results/manual_review_not_behavioural.json) | MR | 10.6% | WITHHELD_BY_VERIFIER | Identical |
| [standard_approval](../results/standard_approval.json) | AS | 32.5% | VERIFIED | Identical |

[All paired inputs, evidence, prompts, raw generations and JSON responses](../results/paired_responses.json) · [Run summary](../results/summary.json)

### Interpret the language result correctly

Five requests invoke the writer in each arm: three paragraphs pass verification and two are withheld. The two malformed requests invoke no writer. This common base-model result is not comparable to the original author's reported 98.1% verification rate from a LoRA-adapted writer. That adaptation was not reproduced.

The fixture named `invalid_input_missing_field` contains an explicit null. It reaches the policy and receives outcome `II`. An absent required key is a malformed request and is refused earlier.

## External policy equivalence

The independent calculations and OPA policy match the original tensor policy on **30,000 applications plus 29 selected boundary cases**. Ten returned fields are compared exactly: calculations, flags, risk-band index/one-hot, triggers, outcome index/one-hot, final reasons, model probability and frozen calibrated probability. There are zero differences.

[Field-by-field policy evidence](../results/policy_parity.json) · [Comparison script](../scripts/check_policy_parity.py)

This is evidence on the tested benchmark and selected boundaries. It is not a formal proof for every signed-64-bit input or all future portfolio policies.

## Added workflow controls

The twelve [workflow scenarios](../results/governance_cases.json) use the actual approval-with-controls request and assessment. They exercise valid recording, stale policy/evidence, untrusted source, cross-tenant evidence, unknown and assess-only principals, missing approval, changes before recording and retry behavior. All twelve produce their expected outcomes.

The original assessment API has no external recording workflow. Its corresponding capability is recorded as **not implemented**, not as an unsafe write or an incorrect credit decision. These tests measure additional functionality, not a like-for-like win rate over the original.

The [original tests](../results/logs/upstream-tests-final.log) pass 43 tests plus 6 subtests. The [added suite](../results/logs/modular-tests.log) passes 17 tests. Together these are 60 repository tests, separate from the 12 workflow scenarios and 30,029 policy inputs.

## Independent policy release

A deliberately relaxed synthetic policy changes the decline fixture from `DEMO_DECLINE` to `MANUAL_REVIEW`. The fixed-point margin remains **842436674**, and the scorer/attribution SHA-256 remains identical. No Qwen model is loaded.

[Release evidence](../results/policy_release.json) · [Executable experiment](../scripts/policy_release_experiment.py)

Both architectures can update policy without retraining the writer. Our demonstrated distinction is the independent policy artifact/runtime boundary and its explicit approval identity. The local approval in this test is synthetic.

## What is not demonstrated

| Topic | Interpretation |
| --- | --- |
| Inference performance | Single observations in fixed arm order; no randomized latency or cost advantage claim |
| Underwriting | Same benchmark model and synthetic policy; no improved prediction or real-world probability-of-default validation |
| Text quality | Same writer and verifier; semantic limitations remain |
| Actionability | Bounded recourse searches predefined moves; no causal or real-world feasibility guarantee |
| Enterprise integration | Source, identity and approval assertions are fixtures; no production bank integration |
| Deployment | Modular Python and an OPA subprocess; no distributed isolation, high availability or load benchmark |

## Reproduce or inspect

Use the [quickstart](QUICKSTART.md) for the smallest runnable path. The [model manifest](../models/model_manifest.json) pins the upstream commit, official Qwen revision, OPA version and identities. The [research paper](Credit_Architecture_Research_Paper.pdf) contains the full methodology and actual generated paragraph examples.
