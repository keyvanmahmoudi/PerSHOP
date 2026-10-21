# PerSHOP: A Multi-Domain Persian Dataset for Shopping Dialogue Systems

PerSHOP is a Persian task-oriented dialogue dataset in the shopping domain:
1,061 customer–seller dialogues (21,923 utterances) over 14 product domains,
annotated with domain, intent/dialogue act and slot spans, together with the
750-item product database used to collect them.

* Paper (IEEE, IICAI 2026): https://doi.org/10.1109/IICAI70155.2026.11620935
* Preprint: https://arxiv.org/abs/2401.00811
* Hugging Face: https://huggingface.co/datasets/keyvanmahmoudi/PerSHOP

## Repository contents

| Path | Contents |
|---|---|
| `PerSHOP.xlsx` | Original annotated dialogues |
| `Products_DataBASE.xlsx` | Original product database, slot descriptions and domain taxonomy |
| `data/dialogues/{train,validation,test}.jsonl` | Official splits, one utterance per line |
| `data/products/products.jsonl` | Product database |
| `data/products/slots.jsonl` | Slot names and descriptions |
| `splits/` | Dialogue IDs of each split and split statistics |
| `scripts/make_splits.py` | Rebuilds `data/` and `splits/` from the original spreadsheets |
| `scripts/corrections.json` | Documented corrections applied to the original annotations |
| `notebooks/` | Baseline experiments from the paper (BERT/XLM-R and GPT-5.1 intent classification and slot extraction) |

## Official splits

| Split | Dialogues | Utterances |
|---|---|---|
| train | 849 | 17,482 |
| validation | 106 | 2,242 |
| test | 106 | 2,199 |

The split is made at the dialogue level (no dialogue appears in more than one
split), 80/10/10, stratified by each dialogue's primary product domain, with a
fixed seed. To rebuild it:

```bash
pip install pandas openpyxl
python scripts/make_splits.py --dialogues PerSHOP.xlsx --products Products_DataBASE.xlsx --out .
```

The release fixes 13 unparseable slot annotations, removes 2 empty utterances
and renames the slot `super-product` to `super_product`; every change is listed
in `scripts/corrections.json`. Field descriptions are documented in the
[dataset card on Hugging Face](https://huggingface.co/datasets/keyvanmahmoudi/PerSHOP).

## Collection

The dialogues were collected at the University of Tehran through a dedicated web
platform. About 120 volunteer students from the Data Structures and Natural
Language Processing courses took the customer and seller roles over three
semesters, following a written guideline, and the dialogues were then annotated
by the first author. The released data contains speaker roles only and no
participant identifiers.

## License

* **Data** (`PerSHOP.xlsx`, `Products_DataBASE.xlsx`, `data/`, `splits/`):
  [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) — see
  [`LICENSE-DATA`](LICENSE-DATA). Commercial use, including training or
  deploying models for commercial products or services, requires a separate
  written agreement with the authors.
* **Code** (`notebooks/`, `scripts/`): MIT — see [`LICENSE`](LICENSE).

## Citation

```bibtex
@inproceedings{mahmoudi2026pershop,
  title     = {PerSHOP: A Multi-Domain Persian Dataset for Shopping Dialogue Systems},
  author    = {Mahmoudi, Keyvan and Faili, Heshaam},
  booktitle = {2026 International Interdisciplinary Conference on Artificial Intelligence: Engineering, Health, Finance and Humanities (IICAI)},
  pages     = {1--6},
  year      = {2026},
  address   = {Tehran, Iran},
  doi       = {10.1109/IICAI70155.2026.11620935}
}
```
