import csv
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys


class WebBot:
    def __init__(self):
        # Inisialisasi driver Selenium (pastikan Anda memiliki driver sesuai dengan browser yang Anda gunakan)
        self.driver = webdriver.Chrome()

    def login(self, email, password):
        login_url = "https://mpo.psp.pertanian.go.id/v.5/login"
        self.driver.get(login_url)

        email_input = self.driver.find_element(By.NAME, "email")
        email_input.send_keys(email)

        password_input = self.driver.find_element(By.NAME, "password")
        password_input.send_keys(password)

        login_button = self.driver.find_element(
            By.CSS_SELECTOR, 'button[type="submit"]'
        )
        login_button.click()

    def access_report_page(self, url):
        self.driver.get(url)

        # Temukan elemen tombol menggunakan selektor CSS
        button = self.driver.find_element(
            By.CSS_SELECTOR,
            'button[data-toggle="modal"][data-target="#pilih_spp_modal"]',
        )

        # Klik tombol
        button.click()

        search_input = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="search"]'))
        )

        search_text = "836"
        self.driver.execute_script(
            "arguments[0].value = arguments[1]", search_input, search_text
        )
        time.sleep(3)
        search_input.send_keys(Keys.RETURN)
        time.sleep(3)

        xpath_selector = f'//tr[contains(.//span, "{search_text}") and (@class="odd" or @class="even")]'
        row = self.driver.find_element(By.XPATH, xpath_selector)

        # Temukan elemen <button> di dalam baris dan klik
        button = row.find_element(By.CSS_SELECTOR, "button.btn-pilih")
        button.click()

    def close(self):
        time.sleep(5)
        # Tutup browser setelah selesai
        self.driver.quit()


# Inisialisasi objek WebBot
web_bot = WebBot()

try:
    # Informasi login
    email = "bast@binaagrosiwimandiri.com"
    password = "Lapor"

    # Melakukan login
    web_bot.login(email, password)

    # Akses halaman yang diberikan
    report_page_url = "https://mpo.psp.pertanian.go.id/v.5/pelaporan/50839/spp/create"
    web_bot.access_report_page(report_page_url)

finally:
    # Tutup browser setelah selesai
    web_bot.close()
