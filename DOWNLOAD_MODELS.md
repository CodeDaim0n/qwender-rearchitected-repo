# Models: public rebuild and artifact restoration

[← Overview](README.md) · [Quickstart](docs/QUICKSTART.md) · [Model identities](models/model_manifest.json)

The public, reproducible path is the **pinned rebuild**. Native XGBoost weights,
normalized trees, calibration and credit policy data are committed here. The
larger Qwen and compiled attribution files are rebuilt from the pinned official
model and source versions.

## Rebuild from public sources

After creating the environment in the [quickstart](docs/QUICKSTART.md):

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
python scripts/reproduce.py
```

The script obtains the official [Qwen3.5-0.8B model](https://huggingface.co/Qwen/Qwen3.5-0.8B)
and the pinned [Qwenderwriter source](https://github.com/maximer-v/qwenderwriter),
then builds both assessment paths. See [model_manifest.json](models/model_manifest.json)
for exact source/model revisions and identities. It uses the common unadapted
base writer, not the original author's fine-tuned release.

## Restore a measured artifact bundle you already have

The separately distributed model archive is 1.90 GB in four checksum-verified
parts. Account-specific download URLs are intentionally not included in this
public repository. Public repository access does not grant access to a private
artifact store.

If you have the four parts, put them in one directory and run:

```bash
python scripts/restore_model_bundle.py /absolute/path/to/parts --extract
cp /absolute/path/to/parts/separated-models/* models/
```

The script verifies every SHA-256 against [archive_manifest.json](models/archive_manifest.json),
joins the TAR and safely extracts it. The extracted directories contain:

| Directory | Contents |
| --- | --- |
| `original-layout-base-checkpoint/` | The rebuilt bundled Qwen base checkpoint and deterministic buffers |
| `separated-models/` | Standalone scorer/attribution tensors, policy data, native scorecard and metadata |
| `licenses/` | Original implementation and official base-model licences/model card |

The model archive does not contain the OPA executable. Follow the pinned OPA
installation in the [quickstart](docs/QUICKSTART.md#install-opa-for-a-restored-artifact-set),
then run:

```bash
python scripts/demo.py --record
python scripts/demo.py --checkpoint /absolute/path/original-layout-base-checkpoint
```

All recording is to a local sandbox. No weights were fine-tuned for this
experiment. The implementation/model artefacts retain their respective licences.
