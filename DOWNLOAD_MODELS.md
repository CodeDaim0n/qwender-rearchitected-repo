# Download and restore the measured model artifacts

The full model archive is 1.90 GB and is stored in four verified parts. Download every part into the same folder. Access uses your ChatGPT account.

- [Model archive part 1](https://chatgpt.com/library?file_id=libfile_f2c2db37c6f881a4b5d38bd8f8a7d4a9&account_id=f0aa4426-3e93-47d5-959c-1b8c17dea492) — Credit_Architecture_Model_Bundle.tar.part-001
- [Model archive part 2](https://chatgpt.com/library?file_id=libfile_0b54649bcfd081a4b49654b6f7bbae01&account_id=f0aa4426-3e93-47d5-959c-1b8c17dea492) — Credit_Architecture_Model_Bundle.tar.part-002
- [Model archive part 3](https://chatgpt.com/library?file_id=libfile_1d03eb53518481a48bbb981cb92b7749&account_id=f0aa4426-3e93-47d5-959c-1b8c17dea492) — Credit_Architecture_Model_Bundle.tar.part-003
- [Model archive part 4](https://chatgpt.com/library?file_id=libfile_f82aac5e97d481a48d7ef79e7f31bd6b&account_id=f0aa4426-3e93-47d5-959c-1b8c17dea492) — Credit_Architecture_Model_Bundle.tar.part-004

From this experiment directory, run:

```bash
python scripts/restore_model_bundle.py /absolute/path/to/downloaded/parts --extract
```

The script verifies the SHA-256 of each part using `models/archive_manifest.json`, joins the TAR and safely extracts it. The extracted directories contain the rebuilt original-layout Qwen3.5-0.8B base checkpoint and the separated model artifacts. Copy the `separated-models` contents into this project's `models/` directory, then run:

```bash
python scripts/demo.py --record
python scripts/demo.py --checkpoint /absolute/path/original-layout-base-checkpoint
```

This bundle contains the common unadapted base writer used in our measured comparison, not the author's LoRA-adapted writer. No model weights were fine-tuned for this experiment. Original author and base-model licence files are included in the archive. Native XGBoost weights are also committed directly to this repository.
