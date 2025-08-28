import pandas as pd
from torch.utils.data import Dataset

# === Dataset loader for question-answer fine-tuning ===
#
# This file defines a helper function to load a QA dataset from a CSV file
# and preprocess it into a PyTorch-compatible format.
#
# The dataset should have two columns: "spm" (question) and "svar" (answer).
#
# The prompt part is masked out from the loss function by setting its token IDs to -100,
# so the model is only trained to generate the answer.


def load_qa_dataset(path, tokenizer, max_length, subset=None):
    
    df = pd.read_csv(path)
    df = df.dropna(subset=["spm", "svar"])  # Fjern rader med mangler
    df["spm"] = df["spm"].astype(str)
    df["svar"] = df["svar"].astype(str)


    if subset:
        df = df[:subset]
        
    class QADataset(Dataset):
        def __init__(self, dataframe):
            self.tokenizer = tokenizer
            self.max_length = max_length
            self.examples = []
            
            for _, row in dataframe.iterrows():
                prompt = f"Spørsmål: {row['spm']}\nSvar:"
                response = row["svar"]
                
                full_text = prompt + " " + response
                tokenized = tokenizer(
                    full_text,
                    truncation=True,
                    max_length=max_length,
                    padding="max_length",
                    return_tensors="pt"
                )
                
                labels = tokenized["input_ids"].clone()
                # Masker prompt-delen så modellen ikke "straffes" for å kopiere den
                prompt_ids = tokenizer(prompt, truncation=True, max_length=max_length)["input_ids"]
                labels[0, :len(prompt_ids)] = -100  # -100 ignoreres av loss-funksjonen
                self.examples.append({
                    "input_ids": tokenized["input_ids"].squeeze(),
                    "attention_mask": tokenized["attention_mask"].squeeze(),
                    "labels": labels.squeeze(),
                })
                
        def __len__(self):
            return len(self.examples)
            
        def __getitem__(self, idx):
            return self.examples[idx]
    
    return QADataset(df)