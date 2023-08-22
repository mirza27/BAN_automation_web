from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


def login(driver, email, password):
    login_url = "https://mpo.psp.pertanian.go.id/v.5/login"
    driver.get(login_url)

    email_input = driver.find_element(By.NAME, "email")
    email_input.send_keys(email)

    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(password)

    login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    login_button.click()


def extract_data_from_html(url, out_name):
    try:
        # Inisialisasi driver Selenium
        driver = webdriver.Chrome()  # Ganti dengan driver yang sesuai

        email = "bast@binaagrosiwimandiri.com"
        password = "Lapor"
        login(driver, email, password)

        # Buka URL menggunakan Selenium
        driver.get(url)

        # mengakses 100 baris pada tabel
        select_element = driver.find_element(By.NAME, "kt_datatable_length")
        driver.execute_script("arguments[0].value = '100';", select_element)
        time.sleep(5)
        driver.execute_script(
            "arguments[0].dispatchEvent(new Event('change'))", select_element
        )
        time.sleep(10)

        html_content = driver.page_source

        # Buat objek BeautifulSoup dari HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # Mencari semua elemen <tr> dengan class "odd" atau "even"
        rows = soup.find_all("tr", class_=["odd", "even"])

        # Inisialisasi list untuk menyimpan data
        data = []

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
                        data.append(
                            (
                                nomor,
                                formatted_nomor,
                                href_ubah,
                                poktans,
                                desa,
                            )
                        )

        # Simpan data dalam file CSV
        with open(out_name, "w", newline="", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["no", "nomor", "situs", "poktan", "data_kolom_tiga"])
            for idx, (
                nomor,
                formatted_nomor,
                situs,
                poktan,
                data_kolom_tiga,
            ) in enumerate(data, start=1):
                csv_writer.writerow(
                    [nomor, formatted_nomor, situs, poktan, data_kolom_tiga]
                )

    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred:", str(e))


# Contoh penggunaan: ganti dengan path file HTML yang sesuai
url_path = "https://mpo.psp.pertanian.go.id/v.5/pelaporan/90656/detail_kegiatan?delegasiid=2120"
out_name = "./csv/tes.csv"

extract_data_from_html(url_path, out_name)
