---
license: cc-by-nc-4.0
language:
- fa
pretty_name: PerSHOP
size_categories:
- 10K<n<100K
task_categories:
- text-classification
- token-classification
- text-generation
task_ids:
- intent-classification
- named-entity-recognition
- dialogue-modeling
tags:
- task-oriented-dialogue
- shopping
- persian
- dialogue-state-tracking
- slot-filling
configs:
- config_name: dialogues
  default: true
  data_files:
  - split: train
    path: data/dialogues/train.jsonl
  - split: validation
    path: data/dialogues/validation.jsonl
  - split: test
    path: data/dialogues/test.jsonl
- config_name: products
  data_files:
  - split: database
    path: data/products/products.jsonl
- config_name: slots
  data_files:
  - split: descriptions
    path: data/products/slots.jsonl
---

# PerSHOP: A Multi-Domain Persian Dataset for Shopping Dialogue Systems

PerSHOP is a Persian task-oriented dialogue dataset in the shopping domain. Each
dialogue is a conversation between a customer and a seller who fill a shopping
basket from a fixed product database. Utterances are annotated with domain,
intent/dialogue act, product category and inline slot spans.

This is the **official release** maintained by the authors, with fixed
dialogue-level train/validation/test splits and the product database used to
collect the dialogues.

| | |
|---|---|
| Dialogues | 1,061 |
| Utterances | 21,923 |
| Domains | 14 product domains + chit-chat |
| Intents / dialogue acts | 20 |
| Slot types | 27 |
| Products in the database | 750 |
| Mean utterances per dialogue | 20.7 |

## Collection

The dialogues were collected at the University of Tehran through a web platform
built for this purpose. About 120 volunteer students (out of roughly 340 enrolled
in the Data Structures and Natural Language Processing courses over three
semesters) took the customer and seller roles and conducted shopping
conversations over a shared product database, following a written guideline.
The dialogues were then annotated by the first author.

The conversations are role-played; the released data contains only the speaker
role (`user` or `system`) and no identifiers of the participants.

## Splits

| Split | Dialogues | Utterances |
|---|---|---|
| train | 849 | 17,482 |
| validation | 106 | 2,242 |
| test | 106 | 2,199 |

* The split is made at the **dialogue level**: all utterances of a dialogue are
  in the same split, so no dialogue context leaks into evaluation data.
* 80/10/10, stratified by each dialogue's primary domain (its most frequent
  product domain), with a fixed seed (42).
* The dialogue IDs of each split are listed in `splits/`, and
  `scripts/make_splits.py` rebuilds the release exactly from the original
  spreadsheets.

Please report results on the `test` split and use `validation` for model
selection.

## Data fields

### `dialogues` (one row per utterance)

| Field | Description |
|---|---|
| `utterance_id` | Utterance ID from the original release (unique; IDs are not contiguous) |
| `dialogue_id` | Dialogue ID (1–1061) |
| `turn_index` | Position of the utterance within its dialogue, from 0 |
| `speaker` | `user` (customer) or `system` (seller) |
| `domain` | Domain in Persian, as annotated (`Chats` for chit-chat turns) |
| `domain_en` | English name of the domain |
| `intent` | Intent or dialogue act, e.g. `Purchase`, `Inform`, `Ask_slot`, `Ask_product`, `Add_product` |
| `super_product` | Product category the turn is about, e.g. `milk`, `water` (null for chit-chat) |
| `text` | Utterance text with annotation markup removed |
| `annotated_text` | Annotated utterance; slots are marked inline as `[span](slot)` (see Corrections) |
| `raw_text` | `RawText` column of the original release, kept unchanged |
| `entities` | Slot spans parsed from `annotated_text`: `value`, `slot`, and `start`/`end` character offsets in `text` |

### `products`

The product database (750 items). Each record has `id`, `full_name`, `domain`,
`domain_en`, `super_product`, `product`, `price` and the attribute slots that
apply to that product (e.g. `brand`, `flavor`, `volume`, `weight`, `fat`).

### `slots`

Names and English descriptions of the product attribute slots.

## Usage

```python
from datasets import load_dataset

dialogues = load_dataset("keyvanmahmoudi/PerSHOP", "dialogues")
products = load_dataset("keyvanmahmoudi/PerSHOP", "products", split="database")
```

## Corrections

Compared with the original spreadsheet, this release applies a small set of
documented corrections, listed in `scripts/corrections.json`:

* 13 utterances had slot markup that could not be parsed (e.g. `(volume)[1.5]`,
  a missing bracket, or a missing slot label). Their syntax was fixed so the
  annotated spans are recoverable; in two of them (`utterance_id` 7835 and
  7879) the `product` and `bag_number` labels had been attached to the wrong
  spans and were swapped back.
* 2 empty user utterances (`utterance_id` 12536 and 13069) were removed.
* The slot `super-product` was renamed `super_product`, matching the naming of
  all other slots.

`raw_text` is unchanged. In 242 cases an utterance follows another utterance by
the same speaker within a dialogue; these are kept as collected.

## License

The dataset (dialogues, annotations and product database) is released under the
[Creative Commons Attribution-NonCommercial 4.0 International](https://creativecommons.org/licenses/by-nc/4.0/)
license. Research and other non-commercial use is permitted with citation of the
paper below.

**Commercial use** — including training, fine-tuning or deploying models for
commercial products or services — is not covered by this license and requires a
separate written agreement with the authors.

Copies of PerSHOP published by third parties are not maintained by the authors;
this license applies to all copies.

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

@article{mahmoudi2024pershop,
  title   = {PerSHOP -- A Persian dataset for shopping dialogue systems modeling},
  author  = {Mahmoudi, Keyvan and Faili, Heshaam},
  journal = {arXiv preprint arXiv:2401.00811},
  year    = {2024}
}
```

## Links

* Paper (IEEE): https://doi.org/10.1109/IICAI70155.2026.11620935
* Preprint: https://arxiv.org/abs/2401.00811
* Code and original files: https://github.com/keyvanmahmoudi/PerSHOP
