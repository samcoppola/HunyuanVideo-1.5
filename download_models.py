from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="tencent/HunyuanVideo-1.5",
    local_dir="/workspace/HunyuanVideo-1.5/ckpts",
    ignore_patterns=[
        "transformer/720p_t2v/*",
        "transformer/720p_t2v_distilled/*",
        "transformer/480p_i2v/*",
        "transformer/480p_i2v_distilled/*",
        "transformer/480p_i2v_step_distilled/*",
        "transformer/720p_i2v/*",
        "transformer/720p_i2v_distilled/*",
        "upsampler/*",
        "vision_encoder/*",
        "assets/*",
    ],
    local_dir_use_symlinks=False,
)
print("Download completo.")
