from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import Select
import time
import csv
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys


class driverChrome:
    def __init__(self):
        self.page = None
        self.page_number = 1
        self.driver = webdriver.Chrome()  # Ganti dengan driver yang sesuai
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

    def get_100(self, url):
        # Buka URL menggunakan Selenium
        self.driver.get(url)

        # mengakses 100 baris pada tabel
        select_element = self.driver.find_element(By.NAME, "kt_datatable_length")
        self.driver.execute_script("arguments[0].value = '100';", select_element)
        time.sleep(5)
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change'))", select_element
        )
        time.sleep(10)

        # menyimpan halaman
        self.page = self.driver.page_source

    def next_page(self):
        next = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Next"))
        )
        next.click()

        print("berada di halaman", self.page_number)
        element = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//a[@aria-controls="kt_datatable" and text()="{self.page_number - 1}"]',
                )
            )
        )
        # menunggu sampai ada elemen angka bilang sebelumnya
        WebDriverWait(self.driver, 20).until(EC.staleness_of(element))

        # menyimpan halaman
        self.page = self.driver.page_source

    def get_link(self):
        soup = BeautifulSoup(self.page, "html.parser")
        rows = soup.find_all("tr", class_=["odd", "even"])

        # Loop melalui setiap baris
        for row in rows:
            # Mencari elemen <td> berdasarkan index
            tds = row.find_all("td")
            if len(tds) >= 3:
                desa = tds[2].text.strip()  # Mengambil teks dari kolom ke-3

                nomor_td = row.find("td", class_="dt-right dtr-control")
                poktan_td = row.find("span", class_="bg-warning- font-weight-bold")

                if nomor_td:  # jika syarat
                    nomor = nomor_td.text.strip()
                    poktans = poktan_td.text.strip()

                    links = row.find_all("a")
                    if len(links) >= 2:
                        link_ubah = links[1]  # ambil link ubah atau lapor
                        href_ubah = link_ubah["href"]

                        formatted_nomor = f"{nomor}/bam/poligon"
                        self.data.append(
                            (
                                nomor,
                                formatted_nomor,
                                href_ubah,
                                poktans,
                                desa,
                            )
                        )


if __name__ == "__main__":
    url = "https://mpo.psp.pertanian.go.id/v.5/pelaporan/105466/detail_kegiatan?delegasiid=3028"
    email = "bast@binaagrosiwimandiri.com"
    password = "Lapor"
    out_name = "./csv/link_karo2.csv"
    page_max = 11

    try:
        Chrome = driverChrome()

        Chrome.login(email, password)

        Chrome.get_100(url)
        Chrome.get_link()

        while Chrome.page_number < page_max:
            Chrome.page_number += 1
            Chrome.next_page()

            Chrome.get_link()

        # menulis ke csv
        with open(out_name, "w", newline="", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(  # menulis kolom
                ["no", "no_bam", "situs", "poktan", "desa"]
            )

            for idx, (nomor, formated_nomor, situs, poktan, desa) in enumerate(
                Chrome.data, start=1
            ):
                csv_writer.writerow([nomor, formated_nomor, situs, poktan, desa])

    finally:
        Chrome.driver.quit()
