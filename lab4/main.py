"""
Единый скрипт для:
 - загрузки аннотаций,
 - вычисления яркости изображений,
 - обработки DataFrame,
 - визуализации,
 - сохранения результатов.
"""

import os
import cv2
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
#                 ФУНКЦИИ РАБОТЫ С ДАННЫМИ
# ============================================================

def load_annotation_data(annotation_file):
    """
    Загружает данные из CSV и возвращает DataFrame с двумя колонками:
    absolute_path, relative_path.
    """
    df = pd.read_csv(annotation_file)
    df = df[['absolute_path', 'relative_path']]
    return df


def add_brightness_column(df, brightness_values):
    """Добавляет колонку яркости в DataFrame."""
    df['brightness'] = brightness_values
    return df


def sort_by_brightness(df, ascending=True):
    """Сортирует DataFrame по яркости."""
    sorted_df = df.sort_values('brightness', ascending=ascending)
    return sorted_df.reset_index(drop=True)


def filter_by_brightness(df, min_brightness=None, max_brightness=None):
    """Фильтрует DataFrame по диапазону яркости."""
    filtered_df = df.copy()

    if min_brightness is not None:
        filtered_df = filtered_df[filtered_df['brightness'] >= min_brightness]

    if max_brightness is not None:
        filtered_df = filtered_df[filtered_df['brightness'] <= max_brightness]

    return filtered_df.reset_index(drop=True)


def get_statistics(df):
    """Возвращает статистику по яркости."""
    return {
        'total_images': len(df),
        'min_brightness': round(df['brightness'].min(), 2),
        'max_brightness': round(df['brightness'].max(), 2),
        'mean_brightness': round(df['brightness'].mean(), 2),
        'median_brightness': round(df['brightness'].median(), 2)
    }


def save_dataframe(df, output_file):
    """Сохраняет DataFrame в CSV."""
    df.to_csv(output_file, index=False, encoding='utf-8')


# ============================================================
#                 ФУНКЦИИ АНАЛИЗА ИЗОБРАЖЕНИЙ
# ============================================================

def calculate_brightness(image_path):
    """
    Вычисляет среднюю яркость изображения.
    """
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Не удалось загрузить изображение: {image_path}")

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        brightness = image_rgb.mean()

        return round(brightness, 2)

    except Exception as e:
        raise RuntimeError(f"Ошибка при вычислении яркости для {image_path}: {e}")


def process_images_brightness(image_paths):
    """
    Вычисляет яркость для списка изображений.
    """
    brightness_values = []

    for image_path in image_paths:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Файл не найден: {image_path}")

        brightness = calculate_brightness(image_path)
        brightness_values.append(brightness)

    return brightness_values


# ============================================================
#                 ВИЗУАЛИЗАЦИЯ ДАННЫХ
# ============================================================

def plot_brightness_distribution(sorted_df, output_plot):
    """
    Строит график яркости отсортированных изображений.
    """
    plt.figure(figsize=(12, 6))

    plt.plot(
        range(len(sorted_df)),
        sorted_df['brightness'],
        marker='o',
        linestyle='-',
        linewidth=1,
        markersize=3,
        alpha=0.7
    )

    plt.title('Распределение средней яркости изображений птиц', fontsize=14, pad=20)
    plt.xlabel('Номер изображения', fontsize=12)
    plt.ylabel('Средняя яркость', fontsize=12)

    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_plot, dpi=300, bbox_inches='tight')
    plt.close()


# ============================================================
#                       ОСНОВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    annotation_file = r"/home/magistrr/coding/python/labs_py/application-programming-labs-2025/web-scraping/ann.csv"
    image_paths = r"/home/magistrr/coding/python/labs_py/application-programming-labs-2025/web-scraping/images"

    try:
        # 1. Загружаем таблицу
        df = load_annotation_data(annotation_file)

        # 2. Получаем список путей к изображениям
        image_paths = df['absolute_path'].tolist()

        # 3. Считаем яркость
        brightness_values = process_images_brightness(image_paths)

        # 4. Добавляем колонку
        df = add_brightness_column(df, brightness_values)

        # 5. Статистика
        stats = get_statistics(df)

        # 6. Сортировка
        sorted_df = sort_by_brightness(df, ascending=False)

        # 7. Фильтрация (пример)
        filtered_df = filter_by_brightness(df, min_brightness=150)

        # 8. Построение графика
        plot_brightness_distribution(sorted_df, 'bird_brightness_plot.png')

        # 9. Сохранение данных
        save_dataframe(df, 'bird_images_analysis.csv')

        print("Анализ завершён успешно!")
        print(f"Статистика: {stats}")

    except FileNotFoundError as e:
        print(f"Ошибка: Файл не найден — {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()
