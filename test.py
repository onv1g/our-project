# Превращаем градусы в радианы и зеркалим данные на 360° (вторая половина круга)
all_angles = np.deg2rad(angles + [a + 180 for a in angles])
# Удваиваем список значений, чтобы для каждой половины круга была своя высота столбца
all_values = values + values
# Вычисляем ширину столбца в радианах (0.8 — чтобы между ними был небольшой зазор)
width = np.deg2rad(interval * 0.8)
# Создаем список отметок (шагов) для сетки от 0 до 360 градусов
tick_degrees = list(range(0, 360, interval))

# Создаем графическое окно (fig) и полярные оси (ax) на черном фоне
fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={'projection': 'polar'}, facecolor='black')
# Делаем фон внутри самого круга черным
ax.set_facecolor('black')
# Рисуем саму диаграмму: углы, значения, ширина, цвет заливки и обводки
ax.bar(all_angles, all_values, width=width, color='#00FF00', edgecolor='black', alpha=0.9)

# Указываем, в каких местах круга будут стоять отметки (радианы)
ax.set_xticks(np.deg2rad(tick_degrees))
# Подписываем эти места градусами (белым цветом)
ax.set_xticklabels([f"{d}°" for d in tick_degrees], color='white', fontsize=9)

# Устанавливаем 0 градусов на "Север" (верхушка круга)
ax.set_theta_zero_location('N')
# Задаем направление отсчета: -1 означает "по часовой стрелке"
ax.set_theta_direction(-1)
# Рисуем сетку (паутину): белая, пунктирная и очень прозрачная
ax.grid(color='white', alpha=0.15, linestyle='--')

# Создаем специальный виджет для PyQt, который умеет отображать графики Matplotlib
canvas = FigureCanvas(fig)
# Получаем текущий "укладчик" элементов (layout) из окна приложения
current_layout = window.layout()

if current_layout is not None:
    # Проходим по всем элементам в окне с конца в начало
    for i in reversed(range(current_layout.count())):
        item = current_layout.itemAt(i) # Получаем элемент по индексу
        widget = item.widget()         # Извлекаем сам графический объект (виджет)
        # Если это старый график или серая рамка-заполнитель, удаляем их
        if isinstance(widget, (FigureCanvas, QLineEdit)) and widget != input_field:
            widget.setParent(None)     # Отрываем виджет от окна (удаляем из видимости)

    # Вставляем новый холст с графиком в самое начало (вверх) интерфейса
    current_layout.insertWidget(0, canvas, alignment=Qt.AlignCenter)
    # Команда принудительно перерисовать холст, чтобы картинка появилась
    canvas.draw()
