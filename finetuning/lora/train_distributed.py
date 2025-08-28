from config_lora import config  
from load_model_and_tokenizer import load_model_and_tokenizer as load_fn
from dataset import load_qa_dataset
from transformers import Trainer, TrainingArguments, DataCollatorForLanguageModeling
from transformers import AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling, EarlyStoppingCallback
import torch
from torch.distributed import is_initialized, destroy_process_group


# Fine-tunes a language model on a QA dataset using Hugging Face Trainer.
# Loads model, tokenizer, and dataset from config and helper files.
# ⚠️ Important: update the save path when training a new model


torch.set_float32_matmul_precision('high')


model, tokenizer = load_fn(config)
#model.train()
dataset = load_qa_dataset(config.dataset_path, tokenizer, config.max_length)

print("✅ Dataset loaded with", len(dataset), "examples")

args = TrainingArguments(
    output_dir=config.model_save_path,
    per_device_train_batch_size=config.batch_size,
    gradient_accumulation_steps= config.grad_acc_steps,
    num_train_epochs=config.num_epochs,
    learning_rate=config.lr,
    weight_decay = config.weight_decay,
    warmup_steps= config.warmup_steps,
    fp16=config.fp16,
    logging_steps=10,
    save_steps=100,
    save_total_limit=1,
    report_to="tensorboard",
    disable_tqdm=False,        
    logging_first_step=True, 
    logging_dir = "./logs",
    logging_strategy = "epoch"

)


trainer = Trainer(
    model=model,
    args=args,
    train_dataset=dataset,
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
)

trainer.train()

trainer.save_model("gemma3n_30_07_brukers")
tokenizer.save_pretrained("gemma3n_30_07_brukers")

if is_initialized():
    destroy_process_group()