import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver

# Buat instance WebDriver
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(options=options)


def kecamatan_check(driver, input, kec_key):
    try:
        input.send_keys(kec_key)
        li_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//ul[@id="select2-kecid-results"]//li[text()="{kec_key}"]',
                )
            )
        )
        li_element.click()
        return 1

    except:
        return 0


def desa_check(driver, input, desa_key):
    try:
        input.send_keys(desa_key)
        li_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    f'//ul[@id="select2-desaid-results"]//li[text()="{desa_key}"]',
                )
            )
        )
        li_element.click()
        return 1

    except:
        return 0


def login(driver, email, password):
    login_url = "https://mpo.psp.pertanian.go.id/v.5/login"
    driver.get(login_url)

    email_input = driver.find_element(By.NAME, "email")
    email_input.send_keys(email)

    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(password)

    login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    login_button.click()


email = "bast@binaagrosiwimandiri.com"
password = "Lapor"

with open("./csv/address_not_found2.csv", "w", newline="") as not_found_csv_file:
    not_found_csv_writer = csv.writer(not_found_csv_file)

    # Menulis header
    not_found_csv_writer.writerow(["No", "Kecamatan", "Desa"])

    # Baca data dari file CSV
    with open("./csv/cpcl_serdang.csv", "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        not_found_desa_set = set()  # Set untuk menyimpan desa yang tidak ditemukan

        login(driver, email, password)

        # Daftar kecamatan/desa yang tidak ditemukan
        not_found = []
        kec_before = ""
        desa_before = ""

        for row in csv_reader:
            no_key = row["No"]
            prov_key = row["Provinsi"]
            kab_key = row["Kabupaten"]
            kec_key = row["Kecamatan"]
            desa_key = row["Desa"]

            driver.get("https://mpo.psp.pertanian.go.id/v.5/satker/kelompok_penerima")
            print(f"Kab: {kab_key}, Kec: {kec_key}, Desa :{desa_key}")

            #  jika poktan sebelumnya sama dan tidak ada
            if kec_before == kec_key and desa_key == desa_before:
                print("kecamatan / desa sama\n")
                continue

            # INPUT PROVINSI ==========================
            span_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//span[@aria-labelledby="select2-provid-container"]')
                )
            )
            span_element.click()

            # prepare seacrh bar
            search_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        'input[class="select2-search__field"][type="search"]',
                    )
                )
            )

            # input prov key
            search_input.send_keys(prov_key)
            li_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        f'//ul[@id="select2-provid-results"]//li[text()="{prov_key.upper()}"]',
                    )
                )
            )
            li_element.click()

            # KABUPATEN ==========================
            span_element = driver.find_element(
                By.XPATH, '//span[@aria-labelledby="select2-kabid-container"]'
            )
            span_element.click()

            # prepare seacrh bar
            search_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        'input[class="select2-search__field"][type="search"]',
                    )
                )
            )
            # input kab key
            search_input.send_keys(kab_key)
            li_element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        f'//ul[@id="select2-kabid-results"]//li[text()="{"KAB. "+ kab_key.upper()}"]',
                    )
                )
            )
            li_element.click()

            # KECAMATAN ==========================
            span_element = driver.find_element(
                By.XPATH, '//span[@aria-labelledby="select2-kecid-container"]'
            )
            span_element.click()

            # prepare seacrh bar
            search_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        'input[class="select2-search__field"][type="search"]',
                    )
                )
            )

            is_exist = kecamatan_check(driver, search_input, kec_key)
            if is_exist == 10:
                not_found.append(f"kec: {kec_key}")
                not_found_csv_writer.writerow([no_key, kec_key, "undefined"])
                kec_before = kec_key

                desa_before = desa_key
                continue  # lanjut ke lokasi berikutnya
            else:
                kec_before = kec_key

            # DESA ==========================
            span_element = driver.find_element(
                By.XPATH, '//span[@aria-labelledby="select2-desaid-container"]'
            )
            span_element.click()

            # prepare seacrh bar
            search_input_desa = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        'input[class="select2-search__field"][type="search"]',
                    )
                )
            )
            is_exist2 = desa_check(driver, search_input_desa, desa_key)
            if is_exist2 == 0:
                not_found.append(f"kec: {kec_key}, desa:{desa_key}")
                not_found_csv_writer.writerow([no_key, kec_key, desa_key])

            desa_before = desa_key

    # Tutup browser
print(not_found)


driver.quit()
