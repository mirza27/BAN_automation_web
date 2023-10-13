import csv
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import Select
import time
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


class driverChrome:
    def __init__(self):
        self.page = None
        self.driver = driver = webdriver.Chrome()  # Ganti dengan driver yang sesuai
        self.data = []  # link poktan dalam 1 desa

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

    def get_100(self):
        # Buka URL menggunakan Selenium
        self.driver.get("https://mpo.psp.pertanian.go.id/v.5/satker/kelompok_penerima")

        # mengakses 100 baris pada tabel
        select_element = self.driver.find_element(By.NAME, "kt_datatable_length")
        self.driver.execute_script("arguments[0].value = '100';", select_element)
        time.sleep(5)
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change'))", select_element
        )
        # time.sleep(10)

    def input_loc(self, prov_key, kab_key, kec_key, desa_key):
        logging.info(
            f"Trying check poktan for kab: {kab_key}, kec: {kec_key}, desa: {desa_key}"
        )

        # INPUT PROVINSI ==========================
        span_element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[@aria-labelledby="select2-provid-container"]')
            )
        )
        time.sleep(1)
        span_element.click()

        # prepare seacrh bar
        search_input = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
            )
        )

        # input prov key
        search_input.send_keys(prov_key)
        li_element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//ul[@id="select2-provid-results"]//li[text()="{prov_key.upper()}"]',
                )
            )
        )
        li_element.click()

        # KABUPATEN ==========================
        span_element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[@aria-labelledby="select2-kabid-container"]')
            )
        )
        span_element.click()

        # prepare seacrh bar
        search_input = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
            )
        )
        # input kab key
        search_input.send_keys(kab_key)
        li_element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//ul[@id="select2-kabid-results"]//li[text()="{"KAB. "+ kab_key.upper()}"]',
                )
            )
        )
        li_element.click()

        # KECAMATAN ==========================
        span_element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[@aria-labelledby="select2-kecid-container"]')
            )
        )
        span_element.click()

        # prepare seacrh bar
        search_input = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
            )
        )
        # input kec key
        search_input.send_keys(kec_key)
        li_element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//ul[@id="select2-kecid-results"]//li[text()="{kec_key}"]',
                )
            )
        )
        li_element.click()

        # DESA ==========================
        span_element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[@aria-labelledby="select2-desaid-container"]')
            )
        )
        span_element.click()

        # prepare seacrh bar
        search_input = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
            )
        )
        # input desa key
        search_input.send_keys(desa_key)
        li_element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//ul[@id="select2-desaid-results"]//li[text()="{desa_key}"]',
                )
            )
        )
        li_element.click()

        # menunggu tabel siap
        time.sleep(10)
        self.page = self.driver.page_source

    def get_poktan(self):
        # Buat objek BeautifulSoup dari HTML
        soup = BeautifulSoup(self.page, "html.parser")

        # Mencari semua elemen <tr> dengan class "odd" atau "even"
        rows = soup.find_all("tr", class_=["odd", "even"])

        if len(rows) > 1:
            for row in rows:
                tds = row.find_all("td")  # mengambil data 1 baris

                kelompok = tds[1].text.strip()
                jenis = tds[2].text.strip()

                # jika pktan kapital
                if kelompok.isupper() and jenis == "KELOMPOK PERTANIAN":
                    links = row.find_all("a")
                    link = links[0]["href"]

                    self.data.append(
                        (
                            kelompok,
                            link,
                        )
                    )
        else:
            return

    def update_poktan(self):
        for i in self.data:
            kelompok = i[0]
            link = i[1]

            self.driver.get(link)
            poktan = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, "kelompok"))
            )

            kelompok = poktanTitle(kelompok)  # mengubah ke title

            poktan.clear()
            poktan.send_keys(kelompok)

            submit_form(self.driver)
            time.sleep(1)

            logging.info(f"Success update for poktan : {kelompok}")

        # mengkosongkan link poktan
        self.data = []


def poktanTitle(poktan):
    # ubah upper menjadi tittle
    words = poktan.split()
    words = [word.capitalize() for word in words]
    for i, word in enumerate(words):
        if word.upper() in ["II", "III", "IV", "VI", "VII", "VIII", "IX"]:
            words[i] = word.upper()

    # Menggabungkan kata-kata kembali menjadi string
    result = " ".join(words)

    return result


def submit_form(driver):
    # Submit the form
    submit_button = driver.find_element(
        By.CSS_SELECTOR, 'button[type="submit"].btn.btn-warning'
    )
    submit_button.click()


# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("./log/get_link_upper_poktan.txt", mode="w"),
        logging.StreamHandler(),
    ],
)


if __name__ == "__main__":
    csv_file = "./csv/cpcl_tanah_laut.csv"
    num_drivers = 1
    email = "bast@binaagrosiwimandiri.com"
    password = "Lapor"

    try:
        Chrome = driverChrome()

        with open(csv_file, "r") as file:
            csv_reader = csv.DictReader(file)

            Chrome.login(email, password)  # login terlebih dahulu

            kec_before = ""
            desa_before = ""

            for row in csv_reader:
                no_key = row["No"]
                prov_key = row["Provinsi"]
                kab_key = row["Kabupaten"]
                kec_key = row["Kecamatan"]
                desa_key = row["Desa"]

                # jika kecamatan sama
                if kec_before == kec_key and desa_key == desa_before:
                    print("kecamatan / desa sama")
                    continue

                Chrome.get_100()

                kec_before = kec_key
                desa_before = desa_key
                Chrome.input_loc(prov_key, kab_key, kec_key, desa_key)

                Chrome.get_poktan()
                Chrome.update_poktan()

    finally:
        Chrome.driver.quit()
