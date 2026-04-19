import os
import pandas as pd


def create_exel_file(percents, data_of_intervals, intervals, filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(script_dir, 'excel_files')

    # Создаем папку, если ее нет
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    numbers = []
    gaps_thing = []
    gaps_percents = []
    intervals_angles = []
    intervals_beta = []

    # Список для новой структуры данных
    azimuth_groups = []

    orig_gaps = list(data_of_intervals.values())
    orig_percents = list(percents.values())

    # 1. Первая половина интервалов (0-180)
    for i in range(1, len(intervals)):
        az_min = intervals[i - 1] + 1
        az_max = intervals[i]
        b_min = (90 - intervals[i - 1]) % 360
        b_max = (90 - intervals[i]) % 360

        count_abs = orig_gaps[i - 1]
        count_pct = orig_percents[i - 1]

        # Данные для Excel
        intervals_angles.append(f"{az_min}-{az_max}")
        intervals_beta.append(f"{b_min}-{b_max}")
        gaps_thing.append(count_abs)
        gaps_percents.append(count_pct)

        # Добавляем в azimuth_groups
        azimuth_groups.append({
            'beta_min': b_max,  # Обычно min меньше max, при необходимости поменяйте местами
            'beta_max': b_min,
            'azimuth_min': az_min,
            'azimuth_max': az_max,
            'count_abs': count_abs,
            'count_pct': round(count_pct, 1),
            'azimuth_center': (az_min + az_max) / 2
        })

    # 2. Вторая половина интервалов (180-360)
    for i in range(1, len(intervals)):
        az_min = (intervals[i - 1] + 180) + 1
        az_max = (intervals[i] + 180)
        b_min = (90 - (intervals[i - 1] + 180)) % 360
        b_max = (90 - (intervals[i] + 180)) % 360

        count_abs = orig_gaps[i - 1]
        count_pct = orig_percents[i - 1]

        intervals_angles.append(f"{az_min}-{az_max}")
        intervals_beta.append(f"{b_min}-{b_max}")
        gaps_thing.append(count_abs)
        gaps_percents.append(count_pct)

        # Добавляем в azimuth_groups
        azimuth_groups.append({
            'beta_min': b_max,
            'beta_max': b_min,
            'azimuth_min': az_min,
            'azimuth_max': az_max,
            'count_abs': count_abs,
            'count_pct': round(count_pct, 1),
            'azimuth_center': (az_min + az_max) / 2
        })

    # Порядковые номера для Excel
    for i in range(1, len(intervals_angles) + 1):
        numbers.append(i)

    # Создание DataFrame и сохранение
    data = {
        '№ п/п': numbers,
        'интервал в азимутах': intervals_angles,
        'интервал в бета': intervals_beta,
        'количество разрывов(шт)': gaps_thing,
        'количество разрывов(%)': gaps_percents
    }

    df = pd.DataFrame(data)
    full_path = os.path.join(folder_path, f"{filename}.xlsx")
    df.to_excel(full_path, index=False)

    print(azimuth_groups)
    return azimuth_groups  # Возвращаем словарь для дальнейшего использования