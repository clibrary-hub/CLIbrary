"""Build a small index from N manifests for fast comparison."""
import argparse, json, random, shutil, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from sentence_transformers import SentenceTransformer
from clibrary_hub.build_index import load_manifests, build_indices
import faiss

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest-dir", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--model", required=True)
    p.add_argument("--n", type=int, default=50)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    all_manifests = load_manifests(args.manifest_dir)
    random.seed(args.seed)
    manifests = random.sample(all_manifests, min(args.n, len(all_manifests)))
    cli_names = {m["name"] for m in manifests}
    print(f"Using {len(manifests)} manifests: {sorted(cli_names)[:5]}...")

    # Save the subset names for eval filtering
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "subset_clis.json").write_text(json.dumps(sorted(cli_names)))

    model = SentenceTransformer(args.model)
    cli_idx, cli_meta, trig_idx, trig_meta, ex_idx, ex_meta, dim = build_indices(
        manifests, model, model_name=args.model
    )

    faiss.write_index(cli_idx, str(args.output_dir / "cli_index.faiss"))
    faiss.write_index(trig_idx, str(args.output_dir / "trigger_index.faiss"))
    faiss.write_index(ex_idx, str(args.output_dir / "example_index.faiss"))
    for name, data in [("cli_meta", cli_meta), ("trigger_meta", trig_meta), ("example_meta", ex_meta)]:
        (args.output_dir / f"{name}.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))

    print(f"Done. CLIs={len(cli_meta)}, dim={dim}")

if __name__ == "__main__":
    main()
