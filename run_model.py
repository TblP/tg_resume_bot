from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import Dataset  # Используем PyTorch Dataset вместо datasets.Dataset
import torch


def model_predict():
    checkpoint_path = "tblp/roberta_bin_clf"
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
    model = AutoModelForSequenceClassification.from_pretrained(checkpoint_path)

    return model, tokenizer


def predict(model,tokenizer, text):
    """Предсказывает класс текста с помощью модели классификации.
            Args:
                model: Предобученная модель для классификации последовательностей.
                tokenizer: Токенизатор для преобразования текста.
                text (str): Входной текст для классификации.

            Returns:
                int: Предсказанный класс (0 или 1).
            """
    model.eval()
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
