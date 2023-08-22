from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class driverChrome:
    def __init__(self):
        self.is_logged = False
        self.page = 1
        self.driver = driver = webdriver.Chrome()  # Ganti dengan driver yang sesuai
        self.data = []  # Inisialisasi list untuk menyimpan data

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

        if self.page != 1:
            # Buat selector CSS berdasarkan atribut data-dt-idx
            selector = f'ul.pagination li.paginate_button.page-item:not(.disabled) a.page-link[data-dt-idx="{self.page}"]'

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )  # menunggu hingga tabel siap

            # klik halaman ke..
            javascript = f"""
                var element = document.querySelector('{selector}');
                if (element) {{
                    element.click();
                }}
            """

            # Jalankan skrip JavaScript
            self.driver.execute_script(javascript)
            time.sleep(5)

        html_content = self.driver.page_source
        self.page += 1

        return html_content

    def extract_link(self, html):
        # Buat objek BeautifulSoup dari HTML
        soup = BeautifulSoup(html, "html.parser")

        # Mencari semua elemen <tr> dengan class "odd" atau "even"
        rows = soup.find_all("tr", class_=["odd", "even"])

        # Loop melalui setiap baris
        for row in rows:
            # Mencari elemen <td> berdasarkan index
            tds = row.find_all("td")
            if len(tds) >= 3:
                desa = tds[2].text.strip()  # Mengambil teks dari kolom ke-3

                nomor_td = row.find("td", class_="dt-right dtr-control")
                poktan_td = row.find("span", class_="bg-warning- font-weight-bold")

                if nomor_td:
                    nomor = nomor_td.text.strip()
                    poktans = poktan_td.text.strip()

                    links = row.find_all("a")
                    if len(links) >= 2:
                        link_ubah = links[1]
                        href_ubah = link_ubah["href"]
                        # situs = href_ubah.replace("/empty", "/spasial/create")

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
        print(f"Berhasil mengambil link pada halaman {self.page}")

    def save_to_csv(self, filename):
        # Simpan data dalam file CSV
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["no", "nomor", "situs", "poktan", "data_kolom_tiga"])
            for idx, (
                nomor,
                formatted_nomor,
                situs,
                poktan,
                data_kolom_tiga,
            ) in enumerate(self.data, start=1):
                csv_writer.writerow(
                    [nomor, formatted_nomor, situs, poktan, data_kolom_tiga]
                )


# Contoh penggunaan: ganti dengan path file HTML yang sesuai
url_path = "https://mpo.psp.pertanian.go.id/v.5/pelaporan/90656/detail_kegiatan?delegasiid=2120"
out_name = "./csv/tes.csv"
max_page = 2

if __name__ == "__main__":
    try:
        # Inisialisasi object driver Selenium
        Chrome_driver = driverChrome()

        email = "bast@binaagrosiwimandiri.com"
        password = "Lapor"
        Chrome_driver.login(email, password)  # login terlebih dahulu

        while Chrome_driver.page <= max_page:
            content = Chrome_driver.get_100(url_path)  # mengambil konten 100 html
            Chrome_driver.extract_link(content)  # mengambil link pada halaman

        Chrome_driver.save_to_csv(out_name)  # simpan ke dalam csv

    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred:", str(e))
