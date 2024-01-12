import csv
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import Select
import time
import base64
from PIL import Image
from io import BytesIO
import os
from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

import base64
from PIL import Image
from io import BytesIO


class MultiChromeDriver:
    def __init__(self, num_drivers=1):
        self.num_drivers = num_drivers
        self.drivers = []
        self.login_status = False

        for _ in range(self.num_drivers):
            options = webdriver.ChromeOptions()
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
        # while self.login_status == False:
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

    def input(self, driver, file):
        xpath_expression = "//tr[contains(@class, 'odd') or contains(@class, 'even')]//td[@class=' dt-right' and contains(text(), '50%')]/ancestor::tr"
        target_tr = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath_expression))
        )
        if target_tr:
            a_element = target_tr.find_element(By.XPATH, ".//a[@title='Edit']")
            if a_element:
                driver.execute_script("arguments[0].click();", a_element)
                # a_element.click()
                time.sleep(3)

                input_file = driver.find_element(
                    By.XPATH,
                    '//input[@type="file" and contains(@class, "custom-file-input")]',
                )
                input_file.send_keys(file)

            else:
                print("Elemen <a> tidak ditemukan di dalam <tr> yang sesuai.")
        else:
            print("Elemen <tr> tidak ditemukan dengan kriteria yang diberikan.")


def get_url(driver, site_url, index):
    driver.get(site_url.replace("/empty", "/foto_proses"))
    print(f"Driver {index} title: {driver.title}")


def delete(driver):
    # Submit the form
    submit_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                '//div[@class="card-footer"]//button[@type="submit" and contains(@class, "btn btn-warning")]',
            )
        )
    )
    driver.execute_script("arguments[0].click();", submit_button)


# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("./log/autofill_foto_proses.txt"),
        logging.StreamHandler(),
    ],
)


if __name__ == "__main__":
    csv_file = "./csv/psp3/link_karo.csv"
    num_drivers = 1  # Ganti sesuai kebutuhan
    multi_driver = MultiChromeDriver(num_drivers)
    keterangan = "foto 50 persen"
    progress = "50"  # pilih "50" / "100"
    img_file = "C:/Users/ramad/OneDrive/Dokumen/BAN/BAN NEW/ponorogo/OC jpg version"
    img_50_file = "C:/Users/ramad/OneDrive/Dokumen/BAN/BAN NEW/karo/oc 50%.jpg"

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
            temp_data_img = []
            for index, row in enumerate(csv_reader):
                # menambahkan data sementara sebanyak num_driver
                temp_data.append(row["situs"])
                temp_data_img.append(row["image"])

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
                        # memberi alamat lengkap gambar
                        # file_path = os.path.join(img_file, temp_data_img[k])

                        multi_driver.input(
                            multi_driver.get_driver(k),
                            img_50_file,
                        )
                        print("mengisi driver ke", k, "dengan", temp_data[k])
                        logging.info(
                            f"Filled form for situs: {temp_data[k]}, image : {temp_data_img[k]}"
                        )

                    # mengosongkan data sementara dan threads
                    temp_data = []
                    temp_data_img = []
                    threads = []

                    # submit bersamaan
                    for l in range(num_drivers):
                        thread2 = threading.Thread(
                            target=delete,
                            args=(multi_driver.get_driver(l),),  # mengambil driver ke
                        )
                        threads.append(thread2)
                        thread2.start()

                    # menyelesaikan akses url
                    for thread2 in threads:
                        thread2.join()

    finally:
        multi_driver.close_all_drivers()
