import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

# Настройка Chrome
service = Service(ChromeDriverManager().install())
options = webdriver.ChromeOptions()
# Раскомментируйте для headless-режима:
# options.add_argument("--headless")
# options.add_argument("--window-size=1920x1080")

# Инициализация браузера
driver = webdriver.Chrome(service=service, options=options)

# URL для парсинга
url = "https://www.divan.ru/category/osveshchenie"

# Список для хранения данных
parsed_data = []

try:
    # Открываем страницу
    driver.get(url)
    time.sleep(3)  # Ожидание загрузки


    def parse_page():
        """Функция для парсинга текущей страницы"""
        products = driver.find_elements(By.CSS_SELECTOR, 'div.swiper-slide.WaG4w._NtQG.H6c9z.ui-5nyfV')

        for product in products:
            try:
                # Парсим название
                name = product.find_element(By.CSS_SELECTOR, 'a.ui-GPFV8.dM3t2.ProductName span').text.strip()

                # Парсим цену
                try:
                    price = product.find_element(By.CSS_SELECTOR, 'span.ui-LD-ZU.OtETQ').text.strip()
                except NoSuchElementException:
                    try:
                        price = product.find_element(By.CSS_SELECTOR, 'span.ui-LD-ZU.ui-SVNym.emGSJ').text.strip()
                    except NoSuchElementException:
                        price = "Цена не указана"

                # Парсим ссылку
                link = product.find_element(By.CSS_SELECTOR, 'a.ui-GPFV8').get_attribute('href')

                parsed_data.append([name, price.replace('\xa0', ' '), link])

            except Exception as e:
                print(f"Ошибка при парсинге товара: {e}")


    # Парсим первую страницу
    parse_page()

    # Обрабатываем пагинацию
    while True:
        try:
            next_page = driver.find_element(By.CSS_SELECTOR, 'a[data-testid="pagination-button-next"]')
            if next_page:
                next_page.click()  # Кликаем по кнопке вместо перехода по URL
                time.sleep(3)
                parse_page()
            else:
                break
        except NoSuchElementException:
            print("Пагинация завершена")
            break

    # Сохраняем в CSV
    with open("divan_lighting.csv", 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Название товара', 'Цена', 'Ссылка на товар'])
        writer.writerows(parsed_data)

    print("Парсинг завершен. Данные сохранены в divan_lighting.csv")

except Exception as e:
    print(f"Произошла ошибка: {e}")

finally:
    if 'driver' in locals():
        driver.quit()
