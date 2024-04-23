import tkinter as tk
from tkinter import font, simpledialog
import pyperclip
import numpy as np
import pyscreenshot as ImageGrab
import cv2
import pytesseract
import re
import pyautogui

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
    return (x1, y1, x2, y2), (click_x, click_y)

# Основной код программы
if __name__ == "__main__":
    bbox, (click_x, click_y) = get_coordinates()  # Запрашиваем координаты у пользователя

    # Инициализация основного окна
    window = tk.Tk()
    window.title("Detected Text")
    window.geometry('800x300')  # Расширенное окно для размещения текста и кнопок

    app_font = font.Font(size=18)  # Установленный размер шрифта
    filename = 'Image.png'
    prev_found_texts = []

    def update_text():
        global prev_found_texts
        screen = np.array(ImageGrab.grab(bbox=bbox))  # Захват изображения по заданным координатам
        cv2.imwrite(filename, screen)
        img = cv2.imread(filename)
        text = pytesseract.image_to_string(img)
        found_texts = re.findall(r'\d{4}-\d{4}', text)
        
        if found_texts != prev_found_texts:
            for widget in window.winfo_children():
                widget.destroy()

            update_frame = tk.Frame(window)
            update_frame.pack(fill='both', expand=True)

            for text in found_texts:
                text_button_frame = tk.Frame(update_frame)
                text_button_frame.pack(fill='x', padx=5, pady=5)
                
                label = tk.Label(text_button_frame, text=text, font=app_font)
                label.pack(side='left')
                
                button = tk.Button(text_button_frame, text="Copy", font=app_font, command=lambda t=text: copy_to_clipboard(t))
                button.pack(side='right')
            
            prev_found_texts = found_texts

        window.after(1000, update_text)

    def copy_to_clipboard(text_to_copy):
        pyperclip.copy(text_to_copy)
        print(f"Text copied to clipboard: {text_to_copy}")
        pyautogui.click(click_x, click_y)
        pyautogui.hotkey('ctrl', 'v')

    update_text()
    window.mainloop()
