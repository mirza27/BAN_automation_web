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


class MultiChromeDriver:
    def __init__(self, num_drivers=1):
        self.num_drivers = num_drivers
        self.drivers = []

        for _ in range(self.num_drivers):
            options = webdriver.ChromeOptions()
            # options.add_argument("--start-minimized")  # Maximize the browser window
            driver = webdriver.Chrome(options=options)
            self.drivers.append(driver)

    def get_driver(self, index):
        if index < 0 or index >= self.num_drivers:
            raise IndexError("Index out of range")
        return self.drivers[index]

    def close_all_drivers(self):
        for driver in self.drivers:
            driver.quit()

    def login(self, driver, email, password):
        login_url = "https://mpo.psp.pertanian.go.id/v.5/login"
        driver.get(login_url)

        email_input = driver.find_element(By.NAME, "email")
        email_input.send_keys(email)

        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(password)

        login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()

    def input(
        self, driver, prov_key, kab_key, kec_key, desa_key, kel_key, ketua_key, nik_key
    ):
        logging.info(
            f"Trying write new poktan for kab: {kab_key}, kec: {kec_key}, desa: {desa_key}, kelompok: {kel_key}"
        )

        # INPUT PROVINSI ==========================
        span_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[@aria-labelledby="select2-provid-container"]')
            )
        )
        time.sleep(1)
        span_element.click()

        # prepare seacrh bar
        search_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
            )
        )

        # input prov key
        search_input.send_keys(prov_key)
        li_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//ul[@id="select2-provid-results"]//li[text()="{prov_key.upper()}"]',
                )
            )
        )
        li_element.click()

        # KABUPATEN ==========================
        span_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[@aria-labelledby="select2-kabid-container"]')
            )
        )
        span_element.click()

        # prepare seacrh bar
        search_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
            )
        )
        # input kab key
        search_input.send_keys(kab_key)
        li_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//ul[@id="select2-kabid-results"]//li[text()="{"KAB. "+ kab_key.upper()}"]',
                )
            )
        )
        li_element.click()

        # KECAMATAN ==========================
        span_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[@aria-labelledby="select2-kecid-container"]')
            )
        )
        span_element.click()

        # prepare seacrh bar
        search_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
            )
        )
        # input kec key
        search_input.send_keys(kec_key)
        li_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//ul[@id="select2-kecid-results"]//li[text()="{kec_key}"]',
                )
            )
        )
        li_element.click()

        # DESA ==========================
        span_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[@aria-labelledby="select2-desaid-container"]')
            )
        )
        span_element.click()

        # prepare seacrh bar
        search_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
            )
        )
        # input desa key
        search_input.send_keys(desa_key)
        li_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//ul[@id="select2-desaid-results"]//li[text()="{desa_key}"]',
                )
            )
        )
        li_element.click()

        # JENIS KELOMPOK ==========================
        span_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.XPATH, '//span[@aria-labelledby="select2-jenisid-container"]')
            )
        )
        span_element.click()

        # prepare seacrh bar
        search_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
            )
        )
        # input kelompok key
        search_input.send_keys("KELOMPOK PERTANIAN")
        li_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//ul[@id="select2-jenisid-results"]',
                )
            )
        )
        li_element.click()

        # NAMA POKTAN ==========================
        driver.find_element(By.NAME, "kelompok").send_keys(kel_key)

        # KETUA ===========================
        target_input = driver.find_element(By.NAME, "ketua")

        target_input.send_keys(ketua_key)

        # NIK ===========================
        target_input = driver.find_element(By.NAME, "nik")

        target_input.send_keys(nik_key)


def get_url(driver, site_url, index):
    driver.get(site_url)
    print(f"Driver {index} getting url where title: {driver.title}")


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
        logging.FileHandler("./log/poktan_maker.txt", mode="w"),
        logging.StreamHandler(),
    ],
)


if __name__ == "__main__":
    csv_file = "./csv/cpcl_tanah_laut.csv"
    num_drivers = 1
    multi_driver = MultiChromeDriver(num_drivers)

    email = "bast@binaagrosiwimandiri.com"
    password = "Lapor"
    url = "https://mpo.psp.pertanian.go.id/v.5/satker/kelompok_penerima/create"

    try:
        for index in range(num_drivers):
            driver = multi_driver.get_driver(index)
            multi_driver.login(driver, email, password)

        data = []
        threads = []

        with open(csv_file, "r") as file:
            csv_reader = csv.DictReader(file)
            temp_data = []
            for index, row in enumerate(csv_reader):
                # menambahkan data sementara sebanyak num_driver
                temp_data.append(
                    (
                        row["Provinsi"],
                        row["Kabupaten"],
                        row["Kecamatan"],
                        row["Desa"],
                        row["kelompok"],
                        row["ketua"],
                        row["NIK"],
                    )
                )

                #  jika sudah kelipatan sebanyak num_driver
                if (index + 1) % num_drivers == 0:
                    # mengaksesk url bersamaan
                    for j in range(num_drivers):
                        thread = threading.Thread(
                            target=get_url,
                            args=(
                                multi_driver.get_driver(j),  # mengambil driver ke
                                url,
                                j,
                            ),
                        )
                        threads.append(thread)
                        thread.start()

                    # menyelesaikan akses url
                    for thread in threads:
                        thread.join()

                    # mengisi inputan sesuai url tanpa thread / 1 persatu
                    for k in range(num_drivers):
                        multi_driver.input(
                            multi_driver.get_driver(k),
                            temp_data[k][0],  # prov
                            temp_data[k][1],  # kab
                            temp_data[k][2],  # kec
                            temp_data[k][3],  # desa
                            temp_data[k][4],  # kelompok
                            temp_data[k][5],  # ketua
                            temp_data[k][6],  # nik
                        )

                    # mengosongkan data sementara dan threads
                    temp_data = []
                    threads = []

                    # submit bersamaan
                    for l in range(num_drivers):
                        thread2 = threading.Thread(
                            target=submit_form,
                            args=(multi_driver.get_driver(l),),  # mengambil driver ke
                        )
                        threads.append(thread2)
                        thread2.start()

                    # menyelesaikan akses url
                    for thread2 in threads:
                        thread2.join()

    finally:
        multi_driver.close_all_drivers()
