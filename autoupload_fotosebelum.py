import csv
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import Select
import time


class MultiChromeDriver:
    def __init__(self, num_drivers=1):
        self.num_drivers = num_drivers
        self.drivers = []

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
        login_url = "https://mpo.psp.pertanian.go.id/v.5/login"
        driver.get(login_url)

        email_input = driver.find_element(By.NAME, "email")
        email_input.send_keys(email)

        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(password)

        login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()

    def input(self, driver, img, keterangan):
        time.sleep(2)

        # isi file gambar
        image_input = driver.find_element(By.NAME, "file_foto_sebelum")
        image_input.send_keys(img)

        # Isi textarea perihal
        perihal_textarea = driver.find_element(By.NAME, "keterangan")
        perihal_textarea.send_keys(keterangan)


def get_url(driver, site_url, index):
    site_fix = site_url.replace("/empty", "/foto_sebelum/create")
    driver.get(site_fix)
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
        logging.FileHandler("./log/autofill_foto_sebelum.txt"),
        logging.StreamHandler(),
    ],
)


if __name__ == "__main__":
    csv_file = "./csv/link_bondowoso.csv"
    num_drivers = 1  # Ganti sesuai kebutuhan
    multi_driver = MultiChromeDriver(num_drivers)
    keterangan = "foto 0 persen"
    img_file = (
        "C:/Users/ramad/OneDrive/Dokumen/BAN_autofill/img/foto_proses_50_bondowoso.jpg"
    )

    try:
        email = "bast@binaagrosiwimandiri.com"
        password = "Lapor"

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
                temp_data.append((row["situs"], row["image"]))

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
                            img_file,
                            keterangan,
                        )
                        print("mengisi driver ke", k, "dengan", temp_data[k][1])
                        logging.info(
                            f"Filled form for situs: {temp_data[k][0]}, img_file: {temp_data[k][1]}"
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
