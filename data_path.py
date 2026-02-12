import os

# Получаем путь к директории текущего скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))

# Переходим на уровень выше
#parent_dir = os.path.dirname(script_dir)

# Получаем путь к JSON
path_to_json = os.path.join(script_dir, 'gaps.json')

