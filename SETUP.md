# HunyuanVideo 1.5 — RunPod Setup Guide

## Token necessari

| Token | Tipo consigliato | Dove ottenerlo | Quando serve |
|---|---|---|---|
| `HF_TOKEN` | **Classic (Read)** | huggingface.co → Settings → Access Tokens | Scaricare i modelli. Il Classic accede automaticamente ai repo gated. Non usare Fine-grained (non ha accesso ai gated di default). |
| `ANTHROPIC_API_KEY` | Standard | console.anthropic.com | Solo con `REWRITE=true` negli script di generazione |

> **Prerequisito vision-encoder**: prima di scaricare `vision-encoder`, devi aver accettato i termini di `black-forest-labs/FLUX.1-Redux-dev` su HuggingFace con il tuo account.

---

## Caso 1 — Nuovo pod, workspace esistente

Il Network Volume ha già repo, venv e modelli. Basta attivare il venv e impostare i token:

```bash
cd /workspace/HunyuanVideo-1.5
git pull                                    # aggiorna il codice
source .venv/bin/activate

export HF_TOKEN="hf_..."                    # Classic token HF
export ANTHROPIC_API_KEY="sk-ant-..."       # solo se usi rewrite
```

Poi lancia lo script di generazione che ti serve (vedi sezione **Generazione**).

---

## Caso 2 — Nuovo workspace (da zero)

### Opzione A — Pod CPU + Pod GPU (consigliato, risparmia denaro)

Il download da ~118 GB non richiede GPU. Farlo su un pod CPU (~$0.02/h) e poi
switchare alla A100 solo per installare il venv e generare (~20 min, ~$0.63).

**Step 1 — Pod CPU** (qualsiasi template con Python):
```bash
export HF_TOKEN="hf_..."
bash setup_cpu.sh         # clone + download ~118 GB, 30-60 min
```
Poi **ferma il pod CPU** e crea un pod A100 attaccando lo stesso Network Volume.

**Step 2 — Pod A100** (modelli già sul volume):
```bash
export HF_TOKEN="hf_..."
bash setup_runpod.sh      # crea venv + pip install; salta download (già presenti)
```

---

### Opzione B — Solo pod GPU (tutto in uno)

```bash
export HF_TOKEN="hf_..."
bash setup_runpod.sh      # clone + venv + download + verifica
```

---

### Dettaglio manuale (senza script)

#### 1. Clona il repo e installa le dipendenze

```bash
cd /workspace
git clone https://github.com/samcoppola/HunyuanVideo-1.5.git
cd HunyuanVideo-1.5

apt-get install -y python3.11 python3.11-venv   # se non già presente
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Imposta i token

```bash
export HF_TOKEN="hf_..."
export ANTHROPIC_API_KEY="sk-ant-..."    # opzionale, solo per rewrite
```

### 3. Scarica i modelli

```bash
# Base — sempre richiesto (text_encoder + vae + scheduler, ~26 GB)
python download.py base

# Scegli il transformer in base al task (uno alla volta per gestire lo spazio):
python download.py t2v-480p        # T2V 480p (~33 GB)
python download.py t2v-720p        # T2V 720p (~33 GB)
python download.py i2v-480p        # I2V 480p (~33 GB)
python download.py i2v-720p        # I2V 720p (~59 GB)

# Solo per I2V — richiede accesso a FLUX.1-Redux-dev:
python download.py vision-encoder  # (~1 GB)

# Opzionale — solo se usi --sr true:
python download.py sr-1080p        # (~32 GB)
```

### 4. (Solo I2V) Carica la tua immagine

Carica l'immagine tramite Jupyter in `/workspace/HunyuanVideo-1.5/`.

---

## Modelli disponibili

| Nome | Disco | VRAM minima | GPU consigliata | Task | Note |
|---|---|---|---|---|---|
| `base` | ~26 GB | — | — | tutti | text_encoder + vae + scheduler — **sempre richiesto** |
| `t2v-480p` | ~33 GB | **24 GB** | RTX 3090 / 4090 | T2V | risoluzione 768×512 |
| `t2v-720p` | ~33 GB | **40 GB** | A100 40GB | T2V | risoluzione 1280×720 |
| `i2v-480p` | ~33 GB | **24 GB** | RTX 3090 / 4090 | I2V | risoluzione 768×512 |
| `i2v-720p` | ~59 GB | **40 GB** | A100 40GB | I2V | risoluzione 1280×720 |
| `vision-encoder` | ~1 GB | ~1 GB extra | — | I2V | SigLIP — **richiesto per tutti i task I2V** |
| `sr-1080p` | ~32 GB | +8 GB extra | A100 40GB+ | tutti | upscaler a 1080p, solo con `--sr true` |

> La VRAM indicata è con group offloading attivo (`--overlap_group_offloading false`).
> Senza offloading servirebbero 80+ GB di VRAM.

**Spazio disco minimo per task:**
- T2V 480p: ~59 GB (base + t2v-480p)
- T2V 720p: ~59 GB (base + t2v-720p)
- I2V 480p: ~60 GB (base + i2v-480p + vision-encoder)
- I2V 720p: ~86 GB (base + i2v-720p + vision-encoder)
- **I2V 720p + SR 1080p: ~118 GB** (base + i2v-720p + vision-encoder + sr-1080p) ← massima qualità

**Liberare spazio:** elimina i transformer che non usi:
```bash
rm -rf ckpts/transformer/480p_t2v_distilled
rm -rf ckpts/transformer/720p_i2v_distilled
rm -rf ckpts/transformer/1080p_sr_distilled   # se non usi sr
```

---

## Generazione

Ogni script ha le variabili editabili in cima al file (`PROMPT`, `IMAGE_PATH`, `VIDEO_LENGTH`, `REWRITE`).

| Script | Task | Modelli richiesti |
|---|---|---|
| `bash run_t2v_480p.sh` | T2V 480p | base + t2v-480p |
| `bash run_t2v_720p.sh` | T2V 720p | base + t2v-720p |
| `bash run_i2v_480p.sh` | I2V 480p | base + i2v-480p + vision-encoder |
| `bash run_i2v_720p.sh` | I2V 720p | base + i2v-720p + vision-encoder |
| **`bash run_via_appia.sh`** | **I2V 720p→1080p** | **base + i2v-720p + vision-encoder + sr-1080p** |

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
bash run_via_appia.sh
```

I video vengono salvati in `./outputs/`.

### Parametri utili

| Parametro | Valori | Note |
|---|---|---|
| `VIDEO_LENGTH` | 33 / 65 / 97 | frames: 33≈2s, 65≈4s, 97≈6s |
| `REWRITE` | true / false | Claude ottimizza il prompt in cinese (più efficace) |
| `--sr true` | — | Upscala a 1080p, richiede sr-1080p scaricato |
| `--enable_cache false` | — | Disabilita deepcache per massima qualità (più lento) |
| `--save_pre_sr_video` | — | Salva anche il video 720p prima dell'upscaling |

### GPU consigliate per massima qualità (I2V 720p + SR)

| GPU | VRAM | Costo RunPod | Note |
|---|---|---|---|
| A100 40GB PCIe | 40 GB | ~$1.89/h | Minimo per 720p; usa `--overlap_group_offloading false` |
| A100 80GB SXM | 80 GB | ~$2.99/h | Consigliato: margine sufficiente, più rapido |
| H100 SXM | 80 GB | ~$4.69/h | Massima velocità, non necessario per qualità |

> Con A100 40GB la generazione di 97 frame a 720p + SR richiede ~10-15 minuti.
