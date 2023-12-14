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

        # element_ulang = WebDriverWait(driver, 5).until(
        #     EC.presence_of_element_located((By.NAME, "email"))
        # )

        # if element_ulang == False:
        #     self.login_status == True

    def input(self, driver, img, progress, keterangan):
        # try:
        #     # Cek apakah elemen dengan class "modal-content" ada
        #     modal_content = WebDriverWait(driver, 20).until(
        #         EC.presence_of_element_located((By.CLASS_NAME, "modal-content"))
        #     )
        # except:
        #     # Jika tidak, cari elemen dengan tautan yang sesuai dan klik
        #     tambah_button = WebDriverWait(driver, 20).until(
        #         EC.presence_of_element_located(
        #             (By.XPATH, '//a[contains(@href, "foto_proses/create")]')
        #         )
        #     )
        #     tambah_button.click()
        time.sleep(5)
        progres_select = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "progres"))
        )
        progres_select = Select(progres_select)
        progres_select.select_by_value(progress)

        # Menunggu elemen dengan menggunakan WebDriverWait
        image_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "file_foto_proses"))
        )
        image_input.send_keys(img)

        # Menunggu elemen dengan menggunakan WebDriverWait
        perihal_textarea = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "keterangan"))
        )
        perihal_textarea.send_keys(keterangan)


def get_url(driver, site_url, index):
    driver.get(site_url.replace("/empty", "/foto_proses/create"))
    print(f"Driver {index} title: {driver.title}")


def submit_form(driver):
    global total_uploads
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
        logging.FileHandler("./log/autofill_foto_proses.txt"),
        logging.StreamHandler(),
    ],
)


if __name__ == "__main__":
    csv_file = "./csv/link_karo2.csv"
    num_drivers = 1  # Ganti sesuai kebutuhan
    multi_driver = MultiChromeDriver(num_drivers)
    keterangan = "foto 50 persen"
    progress = "50"  # pilih "50" / "100"
    img_file = (
        "C:/Users/ramad/OneDrive/Dokumen/BAN/BAN NEW/karo/OC/foto distribusi 50.jpeg"
    )

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
            for index, row in enumerate(csv_reader):
                # menambahkan data sementara sebanyak num_driver
                temp_data.append((row["situs"]), (row["poktan"]))

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
                            multi_driver.get_driver(k),
                            img_file,
                            progress,
                            keterangan,
                        )
                        print("mengisi driver ke", k, "dengan", temp_data[k][1])
                        logging.info(
                            f"Filled form for situs: {temp_data[k][0]}, poktan : {temp_data[k][1]}"
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
