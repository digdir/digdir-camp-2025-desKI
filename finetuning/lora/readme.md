# 🧪 LoRA Fine-Tuning and Inference

This folder contains scripts for fine-tuning language models with LoRA and testing them locally.

## 🚀 Training

Use `accelerate` to train the model across multiple GPUs:

```bash
accelerate launch --multi_gpu train_distributed.py
```

The model architecture, LoRA settings, and training parameters are set in `config_lora.py`.

⚠️ **Important:**  
Make sure to update `model_save_path` and `tokenizer_save_path` in the `train_distributed.py` file.

---

## ⚙️ Model Selection

In `config_lora.py`, scroll to the bottom and uncomment the model you want to train:

```python
# config = MistralConfig()
# config = LLaMA3InstructConfig()
config = Gemma3nConfig()  # currently selected
```

Only one config should be active at a time.


## 📂 Dataset Format

The CSV file used for training must in the following format:

"spm","svar"


## 🤖 Inference

To quickly test your trained model, run `inference.py`.

It loads the LoRA adapter and generates a response to a hardcoded prompt.

Make sure `lora_model_path` in the script points to your trained model folder:




