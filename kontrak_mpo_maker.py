import csv
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
import logging
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC


def login(driver, email, password):
    login_url = "https://mpo.psp.pertanian.go.id/v.5/login"
    driver.get(login_url)

    email_input = driver.find_element(By.NAME, "email")
    email_input.send_keys(email)

    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(password)

    login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    login_button.click()


def input(driver, url, prov_key, kab_key, kec_key, desa_key, kel_key, target_key):
    driver.get(url)
    # INPUT PROVINSI
    span_element = driver.find_element(
        By.XPATH, '//span[@aria-labelledby="select2-provid-container"]'
    )
    span_element.click()

    # prepare seacrh bar
    search_input = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
        )
    )

    # input prov key
    search_input.send_keys(prov_key)
    time.sleep(3)
    search_input.send_keys(Keys.ENTER)

    # KABUPATEN
    span_element = driver.find_element(
        By.XPATH, '//span[@aria-labelledby="select2-kabid-container"]'
    )
    span_element.click()

    # prepare seacrh bar
    search_input = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
        )
    )
    # input kab key
    search_input.send_keys(kab_key)
    time.sleep(3)
    search_input.send_keys(Keys.ENTER)

    # KECAMATAN
    span_element = driver.find_element(
        By.XPATH, '//span[@aria-labelledby="select2-kecid-container"]'
    )
    span_element.click()

    # prepare seacrh bar
    search_input = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
        )
    )
    # input kec key
    search_input.send_keys(kec_key)
    time.sleep(3)
    search_input.send_keys(Keys.ENTER)

    # DESA
    span_element = driver.find_element(
        By.XPATH, '//span[@aria-labelledby="select2-desaid-container"]'
    )
    span_element.click()

    # prepare seacrh bar
    search_input = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
        )
    )
    # input desa key
    search_input.send_keys(desa_key)
    time.sleep(3)
    search_input.send_keys(Keys.ENTER)

    # KELOMPOK
    span_element = driver.find_element(
        By.XPATH, '//span[@aria-labelledby="select2-kelompokid-container"]'
    )
    span_element.click()

    # prepare seacrh bar
    search_input = WebDriverWait(driver, 2).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[class="select2-search__field"][type="search"]')
        )
    )
    # input kelompok key
    search_input.send_keys(kel_key)
    time.sleep(3)
    search_input.send_keys(Keys.ENTER)

    # TARGET
    # Temukan elemen input berdasarkan atribut 'name'
    target_input = driver.find_element(By.NAME, "target")

    # Masukkan nilai angka yang Anda inginkan
    target_input.send_keys(target_key)


def submit_form(driver):
    # Submit the form
    submit_button = driver.find_element(
        By.CSS_SELECTOR, 'button[type="submit"].btn.btn-warning'
    )
    submit_button.click()


options = webdriver.ChromeOptions()
driver = driver = webdriver.Chrome(options=options)

if __name__ == "__main__":
    try:
        email = "bast@binaagrosiwimandiri.com"
        password = "Lapor"
        url = "https://mpo.psp.pertanian.go.id/v.5/pelaporan/105466/create_distribusi?delegasiid=2481"

        login(driver, email, password)
        input(
            driver,
            url,
            "sumatera utara",
            "tapanuli selatan",
            "batang angkola",
            "sigalangan",
            "makmur",
            60,
        )

        time.sleep(4)
        submit_form(driver)

    finally:
        driver.close()
