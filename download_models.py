import os
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"  # disable fast transfer (uses too much RAM on CPU pods)

from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="tencent/HunyuanVideo-1.5",
    local_dir="/workspace/HunyuanVideo-1.5/ckpts",
    allow_patterns=[
        "config.json",
        "LICENSE",
        "NOTICE",
        "README*.md",
        "scheduler/**",
        "text_encoder/**",
        "vae/**",
        "transformer/480p_t2v_distilled/**",
    ],
)
print("Download completo.")
