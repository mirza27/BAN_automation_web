import csv
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
import logging

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

    def input(self, driver, nomor_sk, sk_id):
        # tambah sk
        button = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    'a[data-toggle="modal"][data-target="#my_modal"]',
                )
            )
        )
        button.click()

        # menyiapkan kolom search
        search_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="search"]'))
        )

        driver.execute_script(
            "arguments[0].value = arguments[1]", search_input, nomor_sk
        )
        time.sleep(2)
        search_input.send_keys(Keys.RETURN)

        xpath_selector = (
            f'//tr[contains(.//span, "{nomor_sk}") and (@class="odd" or @class="even")]'
        )
        row = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    xpath_selector,
                )
            )
        )

        # Temukan elemen <button> di dalam baris dan klik
        radio = WebDriverWait(row, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'label[for="{sk_id}"]'))
        )
        radio.click()


def get_url(driver, site_url):
    driver.get(site_url.replace("/empty", "/sk"))
    print(f"Driver title: {driver.title}")


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
        logging.FileHandler("./log/autofill_sk.txt", mode="w"),
        logging.StreamHandler(),
    ],
)


if __name__ == "__main__":
    csv1 = "./csv/link_ponorogo.csv"
    num_drivers = 8  # Ganti sesuai kebutuhan
    multi_driver = MultiChromeDriver(num_drivers)
    sk_file = "173.A.PROD/KPTS/SR.340/B.5/9/2023"
    skid = "skid_3596"

    try:
        email = "bast@binaagrosiwimandiri.com"
        password = "Lapor"

        for index in range(num_drivers):
            driver = multi_driver.get_driver(index)
            multi_driver.login(driver, email, password)

        threads = []
        with open(csv1, "r") as file:
            csv_reader = csv.DictReader(file)
            temp_data = []
            for index, row in enumerate(csv_reader):
                # menambahkan data sementara sebanyak num_driver
                temp_data.append(row["situs"])

                #  jika sudah kelipatan sebanyak num_driver
                if (index + 1) % num_drivers == 0:
                    # mengaksesk url bersamaan
                    for j in range(num_drivers):
                        thread = threading.Thread(
                            target=get_url,
                            args=(
                                multi_driver.get_driver(j),  # mengambil driver ke
                                temp_data[j],
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
                            sk_file,  # temp_data[k][1],  # nomor_spp
                            skid,
                        )
                        logging.info(
                            f"Filled form for situs: {temp_data[k]}, sk file :{sk_file} "
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
