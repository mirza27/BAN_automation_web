import csv
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os


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

    def input(self, driver, nomor, tanggal, nilai):
        nomor_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "nomor"))
        )
        nomor_element.send_keys(nomor)  # mengisi input nomor

        tanggal_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "tgl"))
        )
        tanggal_element.send_keys(tanggal)  # mengisi input tanggal

        nilai_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "nilai"))
        )
        nilai_element.clear()
        # nilai_element.send_keys(nilai)
        driver.execute_script(
            "arguments[0].value = arguments[0].value + arguments[1];",
            nilai_element,
            nilai,
        )

        # driver.find_element(By.NAME, "file_bast").send_keys(
        #     invoice
        # )  # mengisi input file


def get_url(driver, site_url, index):
    driver.get(site_url.replace("/empty", "/bast/create"))
    print(f"Driver {index} title: {driver.title}")


def submit_form(driver):
    global total_uploads
    # Submit the form
    submit_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'button[type="submit"].btn.btn-warning')
        )
    )
    submit_button.click()

    time.sleep(20)


# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("./log/autofill_bast.txt", mode="w"),
        logging.StreamHandler(),
    ],
)


if __name__ == "__main__":
    csv_file = "./csv/psp3/link_karo.csv"
    num_drivers = 1  # Ganti sesuai kebutuhan
    multi_driver = MultiChromeDriver(num_drivers)
    tanggal = "20-11-2023"
    file_bast_path = "C:/Users/ramad/OneDrive/Dokumen/BAN/BAN NEW"

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
                temp_data.append(
                    (
                        row["situs"],
                        row["no_bam"],
                        row["bast"],
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
                                temp_data[j][0],
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
                            temp_data[k][1],  # nomor bast
                            tanggal,  # tanggal
                            temp_data[k][2],  # nilai nominal rupiah
                        )
                        print("mengisi driver ke", k, "dengan", temp_data[k])
                        logging.info(
                            f"Filled form for situs: {temp_data[k][0]}, nomor: {temp_data[k][1]}, nilai:  {temp_data[k][2]}"
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
