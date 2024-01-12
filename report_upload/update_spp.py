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
from selenium.webdriver.common.action_chains import ActionChains


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
        login_url = "https://mpo.psp.pertanian.go.id/v.5.1/login"
        driver.get(login_url)

        email_input = driver.find_element(By.NAME, "email")
        email_input.send_keys(email)

        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(password)

        captcha_input = input("Masukkan Captcha: ")

        # Masukkan nilai ke dalam elemen input
        captcha_textbox = driver.find_element(By.ID, "captcha")
        captcha_textbox.send_keys(captcha_input)

        login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()

    def input(self, driver, kode1, total):
        hasil = float(total) * 0.2
        hasil2 = float(total) * 0.8

        spp_doc = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//a[@title="Edit"]'))
        )
        spp_doc = driver.find_elements(By.XPATH, '//a[@title="Edit"]')

        if len(spp_doc) >= 2:
            href_1 = spp_doc[0].get_attribute("href")
            ActionChains(driver).move_to_element(spp_doc[1]).click().perform()

            time.sleep(3)
            # input nilai
            nilai_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.NAME, "nilai_diterima"))
            )
            nilai_element.clear()
            driver.execute_script(
                "arguments[0].value = arguments[0].value + arguments[1];",
                nilai_element,
                hasil,
            )

            # submit doc pertama
            submit_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        '.modal-footer button[type="submit"].btn.btn-warning',
                    )
                )
            )
            driver.execute_script("arguments[0].click();", submit_button)

        # MENGHAPUS SPP KEDUA
        script = (
            "document.querySelectorAll('button[onclick*=deleteFotoProses]')[1].click();"
        )
        driver.execute_script(script)
        is_delete = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    '//button[text()="Ya, Hapus!"]',
                )
            )
        )
        is_delete.click()

        # RELOAD HALAMAN SAAT INI UNTUK MEMASUKKAN SPP KEDUA
        current_url = driver.current_url
        new_url = current_url + "/create"
        driver.get(new_url)
        time.sleep(3)
        # input nilai
        nilai_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "nilai_diterima"))
        )
        nilai_element.clear()
        driver.execute_script(
            "arguments[0].value = arguments[0].value + arguments[1];",
            nilai_element,
            hasil2,
        )

        button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'button[data-toggle="modal"][data-target="#pilih_spp_modal"]',
                )
            )
        )
        button.click()

        # menyiapkan kolom search
        search_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="search"]'))
        )

        driver.execute_script("arguments[0].value = arguments[1]", search_input, kode1)
        time.sleep(3)
        search_input.send_keys(Keys.RETURN)

        # PENGISIAN DOKUMEN PERTAMA =========================
        # menamcari item spp
        xpath_selector = (
            f'//tr[contains(.//span, "{kode1}") and (@class="odd" or @class="even")]'
        )
        row = row = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, xpath_selector))
        )

        # Temukan elemen <button> di dalam baris dan klik
        button = row.find_element(By.CSS_SELECTOR, "button.btn-pilih")
        button.click()


def get_url(driver, site_url, index):
    driver.get(site_url.replace("/empty", "/spp"))
    print(f"Driver {index} title: {driver.title}")


def submit_form(driver):
    # Submit the form
    submit_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '.modal-footer button[type="submit"].btn.btn-warning')
        )
    )
    driver.execute_script("arguments[0].click();", submit_button)


# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("./log/autofill_spp.txt", mode="w"),
        logging.StreamHandler(),
    ],
)


if __name__ == "__main__":
    csv_file = "./csv/psp1/link_bondowoso.csv"
    num_drivers = 1  # Ganti sesuai kebutuhan
    multi_driver = MultiChromeDriver(num_drivers)
    kode1 = "00855T"

    try:
        email = "bast@binaagrosiwimandiri.com"
        password = "L@por@n_"

        for index in range(num_drivers):
            driver = multi_driver.get_driver(index)
            multi_driver.login(driver, email, password)

        data = []
        threads = []
        with open(csv_file, "r") as file:
            csv_reader = csv.DictReader(file)
            temp_data = []
            temp_data_total = []
            for index, row in enumerate(csv_reader):
                # menambahkan data sementara sebanyak num_driver
                temp_data.append(row["situs"])
                temp_data_total.append(row["total"])

                #  jika sudah kelipatan sebanyak num_driver
                if (index + 1) % num_drivers == 0:
                    # mengaksesk url bersamaan
                    for j in range(num_drivers):
                        thread = threading.Thread(
                            target=get_url,
                            args=(
                                multi_driver.get_driver(j),  # mengambil driver ke
                                temp_data[j],
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
                            multi_driver.get_driver(k), kode1, temp_data_total[k]
                        )
                        print("mengisi driver ke", k, "dengan", temp_data_total[k])
                        logging.info(
                            f"Filled form for situs: {temp_data[k]}, total: {temp_data_total[k]}"
                        )

                    # mengosongkan data sementara dan threads
                    temp_data = []
                    temp_data_total = []
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
