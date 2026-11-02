# Run the experiment

[← Repository overview](../README.md) · [Architecture](ARCHITECTURE.md) · [Results](RESULTS.md)

Choose the smallest path that answers your question.

| Goal | Path | Qwen required? |
| --- | --- | --- |
| Inspect measured behavior | Read the committed JSON and report | No |
| Test the authority and execution controls | Lightweight governance tests | No |
| Run a credit assessment without a paragraph | Restore or rebuild deterministic artifacts, then `demo.py` | No |
| Reproduce both complete credit responses | Full rebuild and paired generation | Yes |

## 1. Lightweight governance tests

```bash
git clone https://github.com/CodeDaim0n/qwender-rearchitected-repo.git
cd qwender-rearchitected-repo
python -m venv .venv
source .venv/bin/activate
pip install networkx pytest
PYTHONPATH=. python -m pytest tests/test_governance.py -q
```

These tests need neither Torch nor model artifacts. They cover the in-process
context, authority and sandbox recording rules. They do not evaluate credit
scoring or Qwen.

## 2. Rebuild the full experiment from public sources

Use Python 3.12 on Linux x86-64. Allow several GB for the official Qwen snapshot,
rebuilt checkpoint, deterministic artifacts and dependencies. Runtime depends on
your CPU, network and filesystem; the paper's original GPU build time is not a
promise for this rebuild.

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
python scripts/reproduce.py
```

The reproducibility script runs these stages in order:

| Stage | Result |
| --- | --- |
| Pinned upstream checkout | Original implementation and UCI benchmark files |
| Original training search | Native XGBoost scorecard and calibration artifacts |
| Exact compilation | Scoring tensors, TreeSHAP tables and original policy audit |
| Pinned official Qwen snapshot | Common unadapted base writer |
| Bundled checkpoint build | Original-layout base checkpoint |
| Component extraction | Standalone score/attribution artifact and external policy data |
| Policy comparison | 30,000 rows and 29 selected boundary cases |
| Paired generation | Both paths independently generate applicable paragraphs |
| Governance and release checks | Workflow cases, independent policy change and tests |

The script restores omitted XGBoost feature names/types if needed by the installed
pandas/XGBoost combination. It does not modify tree parameters and does not train
the writer's LoRA adapter.

### Reuse a local base snapshot

```bash
python scripts/reproduce.py --base /absolute/path/to/qwen-snapshot
```

### Skip language generation

```bash
python scripts/reproduce.py --no-language
```

This option still builds the original-layout checkpoint, so it still needs the
base weights. Its outputs are deterministic-only and must not be represented as
a fresh reproduction of the committed paired language-generation experiment.

## 3. Restore the exact measured artifacts

The [artifact restoration guide](../DOWNLOAD_MODELS.md) describes a separately
distributed 1.90 GB archive in four parts. If you already have those parts, use
the procedure below. Public readers can use the pinned rebuild above instead.

Download all four parts to one directory, then run:

```bash
python scripts/restore_model_bundle.py /absolute/path/to/parts --extract
cp /absolute/path/to/parts/separated-models/* models/
```

The restore script verifies each part's SHA-256 before completing the archive
and safely extracting it. The directories contain the original-layout base
checkpoint and separated deterministic artifacts. The archive does not contain
the original author's fine-tuned writer.

### Install OPA for a restored artifact set

The full rebuild installs OPA automatically. A manual restore needs the pinned
Linux x86-64 binary in `bin/opa`:

```bash
mkdir -p bin
curl -L https://openpolicyagent.org/downloads/v1.22.0/opa_linux_amd64_static -o bin/opa
chmod +x bin/opa
```

Check its SHA-256 against `models/model_manifest.json` before use. The model
restore archive contains model artifacts and licences, not this OPA executable.
The downloadable code-and-results archive from the original run includes it.

## 4. Run the credit workflow

With dependencies, OPA and compiled artifacts present:

```bash
python scripts/demo.py --record
python scripts/demo.py --request fixtures/decline_close_to_approval.json
```

`--record` records to an in-memory SQLite sandbox by default. The default fixture
returns approval with controls and a 5.8% raw model probability. These calls do
not load Qwen. The explanation status is `NOT_GENERATED`.

To attach the writer:

```bash
python scripts/demo.py --checkpoint /absolute/path/original-layout-base-checkpoint
```

To run both architectures against the same requests after a rebuild:

```bash
PYTHONPATH=vendor/qwenderwriter:. python scripts/compare.py \
  --checkpoint vendor/qwenderwriter/artifacts/checkpoints/CompiledCreditLLM-0.8B-UCI-base \
  --upstream vendor/qwenderwriter
```

## Troubleshooting

| Symptom | Meaning and action |
| --- | --- |
| Missing `scorer-attribution.safetensors` | Git contains native weights and metadata; restore or rebuild the compiled artifact |
| Missing `bin/opa` | Install the pinned binary, or use the full rebuild |
| Compiled receipt mismatch | Artifact identity has changed; do not bypass the check; restore the approved artifact set |
| Unapproved policy code/data change | Rego or policy data differs from the loaded approval identity; use an explicit controlled release |
| Paragraph withheld | Inspect raw generation and verifier violations; deterministic assessment is still returned |
| Slow CPU generation | Reference kernels are used; disable generation when you only need deterministic assessment |
| OPA unavailable or writer exception | The exception propagates; this prototype does not provide a general availability fallback |

Rerunning comparison scripts overwrites the corresponding local `results/`
artifacts. Keep a copy if you want to compare your run with the published one.
