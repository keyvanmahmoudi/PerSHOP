"""Upload the official PerSHOP release to the Hugging Face Hub.

Before running:
    pip install -U huggingface_hub
    hf auth login            # paste a token with "write" access

Then, from the release folder:
    python scripts/upload_to_hf.py --repo keyvanmahmoudi/PerSHOP
"""

import argparse
from pathlib import Path

from huggingface_hub import HfApi


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="keyvanmahmoudi/PerSHOP")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root)

    api = HfApi()
    api.create_repo(args.repo, repo_type="dataset", exist_ok=True)

    # Dataset card: the Hub reads it from README.md at the repository root.
    api.upload_file(
        path_or_fileobj=str(root / "hf_dataset_card.md"),
        path_in_repo="README.md",
        repo_id=args.repo,
        repo_type="dataset",
        commit_message="Add dataset card",
    )
    api.upload_folder(
        folder_path=str(root),
        repo_id=args.repo,
        repo_type="dataset",
        allow_patterns=["data/**", "splits/**", "scripts/make_splits.py", "scripts/corrections.json", "LICENSE-DATA"],
        commit_message="Add official PerSHOP release with dialogue-level splits",
    )
    print(f"Done: https://huggingface.co/datasets/{args.repo}")


if __name__ == "__main__":
    main()
