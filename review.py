import time
import tkinter as tk
from tkinter import font, simpledialog
from threading import Thread
import pyperclip
import cv2
import pytesseract
import re
import pyautogui
import logging



prev_found_texts = []


# Инициализируем логгер
logger = logging.getLogger(__name__)


# Функция для запроса координат у пользователя
def get_coordinates():

    root = tk.Tk()
    root.withdraw()  # Скрыть главное окно Tkinter
    x1 = simpledialog.askinteger("Координаты", "Введите начальную координату X:", parent=root)
    y1 = simpledialog.askinteger("Координаты", "Введите начальную координату Y:", parent=root)
    x2 = simpledialog.askinteger("Координаты", "Введите конечную координату X:", parent=root)
    y2 = simpledialog.askinteger("Координаты", "Введите конечную координату Y:", parent=root)
    click_x = simpledialog.askinteger("Координаты для клика", "Введите координату X для клика:", parent=root)
    click_y = simpledialog.askinteger("Координаты для клика", "Введите координату Y для клика:", parent=root)
    root.destroy()

    logger.info('получили координаты и вернули их')
    return (x1, y1, x2, y2), (click_x, click_y)


# Функция для копирования
def copy_to_clipboard(text_to_copy, *args):

    pyperclip.copy(text_to_copy)
    print(f"Text copied to clipboard: {text_to_copy}")
    click_x, click_y = args
    pyautogui.click(click_x, click_y)
    pyautogui.hotkey('ctrl', 'v')
    logger.info('копировали')


# Функция обновления текста
def update_text(window_, bbox_, click_coordinates_):
    logger.info('второй поток запущен')

    while True:
        logger.info('в цикле обновления текста')
        global prev_found_texts

        app_font = font.Font(size=18)  # Установленный размер шрифта
        filename = 'Image.png'
        screenshot = pyautogui.screenshot(region=bbox_)  # Захват изображения по заданным координатам
        screenshot.save(filename)
        img = cv2.imread(filename)
        text = pytesseract.image_to_string(img)
        found_texts = re.findall(r'\d{4}-\d{4}', text)

        if found_texts != prev_found_texts:
            for widget in window_.winfo_children():
                widget.destroy()
                logger.info('widget.destroy()')

            update_frame = tk.Frame(window_)
            update_frame.pack(fill='both', expand=True)

            for text in found_texts:

                text_button_frame = tk.Frame(update_frame)
                text_button_frame.pack(fill='x', padx=5, pady=5)

                label = tk.Label(text_button_frame, text=text, font=app_font)
                label.pack(side='left')

                button = tk.Button(text_button_frame, text="Copy", font=app_font,
                                   command=lambda t=text: copy_to_clipboard(t, *click_coordinates_))
                button.pack(side='right')

            prev_found_texts = found_texts

        logger.info('цикл обновления текста завершен')
        time.sleep(1)


# Основная функция
def main():

    # Конфигурируем логирование
    logging.basicConfig(
        level=logging.WARNING,  # настройка - DEBUG, продакшен - WARNING
        filename="logs.log",  # добавляем логи в файл
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    # Выводим в консоль информацию о начале запуска бота
    logger.info('Starting bot')

    # Запрашиваем координаты у пользователя
    bbox, click_coordinates = get_coordinates()

    # Инициализация окна
    window = tk.Tk()
    window.title("Detected Text")
    window.geometry('800x300')  # Расширенное окно для размещения текста и кнопок
    logger.info('расширенное окно')

    # Инициализация второго потока
    thread = Thread(target=update_text, args=(window, bbox, click_coordinates))
    thread.daemon = True  # Поток завершится при завершении основного потока
    thread.start()
    logger.info('Запущен второй поток')

    window.mainloop()


if __name__ == "__main__":
    main()
