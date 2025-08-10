import json
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import Dataset  # Используем PyTorch Dataset вместо datasets.Dataset
import torch

from pathlib import Path

# Определение датасета
class TextPairDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx] if self.labels is not None else None
        encoding = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        item = {
            "input_ids": encoding["input_ids"].squeeze(),
            "attention_mask": encoding["attention_mask"].squeeze(),
        }
        if label is not None:
            item["labels"] = label
        return item


# Загрузка токенизатора и модели
def model_predict():
    checkpoint_path = "tblp/roberta_bin_clf"
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)

    return model, tokenizer

# Функция для предсказания
def predict(model,tokenizer, text):
    model.eval()  # Переводим модель в режим оценки
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    encoding = tokenizer(
        text,
        max_length=64,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )
    input_ids = encoding["input_ids"].to(device)
    attention_mask = encoding["attention_mask"].to(device)

    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        pred = torch.argmax(logits, dim=1).cpu().numpy()[0]

    return pred
