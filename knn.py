import json
def save_data(data, path):
    """Сохраняет выборку в JSON-файл."""
    # JSON не умеет хранить кортежи (tuple), поэтому превращаем их в списки (list)
    plain = {label: [list(p) for p in points] for label, points in data.items()}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(plain, f, ensure_ascii=False)

def load_data(path):
    """Читает выборку из файла; None, если файла нет или он повреждён."""
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    # Превращаем списки обратно в кортежи, как было в твоей ЛР1
    return {label: [tuple(p) for p in points] for label, points in raw.items()}