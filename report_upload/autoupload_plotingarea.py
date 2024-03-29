import csv
import os
import threading
from selenium import webdriver
import logging
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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

    def input(self, driver, file, tanggal, no_surat, perihal):
        # mengisi tanggal
        tanggal_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "tgl"))
        )
        tanggal_element.clear()
        tanggal_element.send_keys(tanggal)

        # mengisi surat
        nomor_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "nomor"))
        )
        nomor_element.clear()
        nomor_element.send_keys(no_surat)

        file_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "file_spasial"))
        )
        file_input.send_keys(file)

        # Isi textarea perihal
        perihal_textarea = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.NAME, "perihal"))
        )
        perihal_textarea.clear()
        perihal_textarea.send_keys(perihal)


def get_url(driver, site_url, index):
    driver.get(site_url.replace("/empty", "/spasial"))
    print(f"Driver {index} title: {driver.title}")


def submit_form(driver):
    # Submit the form
    submit_button = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'button[type="submit"].btn.btn-warning')
        )
    )
    # submit_button = driver.find_element(
    #     By.CSS_SELECTOR, 'button[type="submit"].btn.btn-warning'
    # )
    # submit_button.click()
    driver.execute_script("arguments[0].click();", submit_button)


# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("./log/autofill_ploting_area.txt", mode="w"),
        logging.StreamHandler(),
    ],
)


if __name__ == "__main__":
    csv_file = "./csv/psp2/link_tana_toraja.csv"
    num_drivers = 1  # Ganti sesuai kebutuhan
    multi_driver = MultiChromeDriver(num_drivers)
    tanggal = "30-10-2023"
    perihal = "ploting area"
    default_zip = (
        "C:/Users/ramad/OneDrive/Dokumen/BAN/BAN NEW/ploting_tana_toraja_zip.zip"
    )
    # zip_file = "C:/Users/ramad/OneDrive/Dokumen/BAN/BAN NEW/ploting_karo.zip"
    file_dir = "C:/Users/ramad/OneDrive/Dokumen/BAN/BAN NEW/tana toraja/kml zip"

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
                    (row["situs"], row["no"], row["poktan"], row["tanggal"])
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
                        # memberi alamat lengkap gambar
                        no_surat = temp_data[k][1] + "/" + temp_data[k][2]
                        file_path = os.path.join(
                            file_dir, temp_data[k][1] + "_" + temp_data[k][2] + ".zip"
                        )

                        if os.path.exists(file_path):  # jika file ada
                            multi_driver.input(
                                multi_driver.get_driver(k),
                                file_path,
                                temp_data[k][3],
                                no_surat,
                                perihal,
                            )

                        else:  # jika zip tidak ada
                            file_path = default_zip
                            multi_driver.input(
                                multi_driver.get_driver(k),
                                file_path,
                                temp_data[k][3],
                                no_surat,
                                perihal,
                            )

                        print("mengisi driver ke", k, "dengan", temp_data[k])
                        logging.info(
                            f"Filled form for situs: {temp_data[k]}, dengan file zip"
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
