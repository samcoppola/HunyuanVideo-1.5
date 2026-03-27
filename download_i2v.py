"""Download i2v models (transformer + vision_encoder) from HuggingFace."""
import os
os.environ["HF_HUB_DISABLE_XET"] = "1"
from huggingface_hub import snapshot_download, list_repo_files

token = os.environ.get("HF_TOKEN")
if not token:
    raise RuntimeError("Set HF_TOKEN before running this script.")

# List all vision_encoder files in the repo to find exact paths
print("Checking vision_encoder files in tencent/HunyuanVideo-1.5 ...")
all_files = list(list_repo_files("tencent/HunyuanVideo-1.5", token=token))
vision_files = [f for f in all_files if "vision_encoder" in f]
print(f"Found {len(vision_files)} vision_encoder files:")
for f in vision_files[:20]:
    print(f"  {f}")
print()

if not vision_files:
    print("ERROR: no vision_encoder files found in the repo!")
    exit(1)

print("Downloading transformer/480p_i2v_distilled and vision_encoder ...")
snapshot_download(
    repo_id="tencent/HunyuanVideo-1.5",
    local_dir="./ckpts",
    allow_patterns=["transformer/480p_i2v_distilled/**"] + vision_files,
    token=token,
    local_dir_use_symlinks=False,
)

print()
print("Done!")
