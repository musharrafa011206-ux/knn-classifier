import math
import json  # Добавили для сохранения выборки


def read_point(prompt):
    """Запрашивает координаты точки, возвращает кортеж (x, y)."""
    while True:
        try:
            x = float(input("Введите координату точки по оси x: "))
            y = float(input("Введите координату точки по оси y: "))
            return (x, y)
        except ValueError:
            print("Ошибка: координаты должны быть числами. Попробуйте снова.")


def collect_points():
    """Диалог ввода обучающих точек. Возвращает словарь структуры (1)."""
    data = {}
    while True:
        point = read_point("Введите координаты точки")
        label = input("Введите метку класса объекта: ").strip()
        data.setdefault(label, []).append(point)

        answer = input("Добавить ещё одну точку? (y — да, любой другой символ — нет): ")
        if answer.lower() != 'y':
            if len(data) < 2:
                print("Ошибка: нужно минимум 2 различных метки классов. Продолжите ввод.")
                continue
            if any(len(pts) < 3 for pts in data.values()):
                print("Ошибка: для каждого класса нужно минимум 3 точки. Продолжите ввод.")
                continue
            break
    return data


def read_k(total):
    """Запрашивает k, проверяя условие 1 <= k <= total."""
    while True:
        try:
            k = int(input(f"Введите количество ближайших соседей k (1..{total}): "))
            if 1 <= k <= total:
                return k
            print(f"Ошибка: k должно быть от 1 до {total}.")
        except ValueError:
            print("Ошибка: k должно быть целым числом.")


def distance(p1, p2):
    """Евклидово расстояние между двумя кортежами координат."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def neighbours(data, point, k):
    """k ближайших соседей: список [(расстояние, метка, точка), ...]."""
    all_neighbours = []
    for label, points in data.items():
        for p in points:
            d = distance(p, point)
            all_neighbours.append((d, label, p))
    all_neighbours.sort(key=lambda item: item[0])
    return all_neighbours[:k]


def predict(data, point, k):
    """Предсказанная метка класса для точки point."""
    neighbours_list = neighbours(data, point, k)
    votes = {}
    for d, label, p in neighbours_list:
        votes[label] = votes.get(label, 0) + 1

    max_votes = max(votes.values())
    candidates = [label for label, v in votes.items() if v == max_votes]

    if len(candidates) == 1:
        return candidates[0]

    # Ничья: побеждает метка с ближайшим соседом
    for d, label, p in neighbours_list:
        if label in candidates:
            return label


# === НОВЫЕ ФУНКЦИИ ===

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
    # Превращаем списки обратно в кортежи, как было в ЛР1
    return {label: [tuple(p) for p in points] for label, points in raw.items()}


def get_centers(data):
    """Возвращает словарь {метка: (средний_x, средний_y)} (Вариант 2)."""
    centers = {}
    for label, points in data.items():
        sum_x = sum(p[0] for p in points)
        sum_y = sum(p[1] for p in points)
        count = len(points)
        centers[label] = (sum_x / count, sum_y / count)
    return centers



def main():
    print("=== Классификация методом k ближайших соседей ===")

    # Пытаемся загрузить данные
    DATA_FILE = "data.json"
    data = load_data(DATA_FILE)

    if data is not None:
        total_saved = sum(len(pts) for pts in data.values())
        answer = input(f"Найдена сохранённая выборка ({total_saved} точек). Использовать? (y/n): ")
        if answer.strip().lower() != "y":
            data = None

    if data is None:
        data = collect_points()
        save_data(data, DATA_FILE)

    total = sum(len(pts) for pts in data.values())
    labels = set(data.keys())
    print(f"\nВведено {total} точек, метки классов: {', '.join(labels)}")

    # Вывод центров классов (Вариант 2)
    centers = get_centers(data)
    print("\nЦентры классов:")
    for label, (cx, cy) in centers.items():
        print(f"  Класс {label}: ({cx:.2f}, {cy:.2f})")

    print("\nВведите координаты точки неизвестного класса.")
    point = read_point("Введите координаты неизвестной точки")

    k = read_k(total)
    neighbours_list = neighbours(data, point, k)
    predicted = predict(data, point, k)

    print(f"\nБлижайшие соседи точки {point}:")
    for d, label, p in neighbours_list:
        print(f"{p}  расстояние {d:.2f}  метка {label}")

    votes = {}
    for d, label, p in neighbours_list:
        votes[label] = votes.get(label, 0) + 1
    votes_str = ", ".join(f"{label} – {v}" for label, v in votes.items())
    print(f"\nГолоса: {votes_str}")
    print(f"Предсказанная метка класса: {predicted}")


if __name__ == '__main__':
    main()