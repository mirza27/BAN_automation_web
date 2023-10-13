from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading


# Inisialisasi WebDriver
driver = webdriver.Chrome()


def login(driver, email, password):
    login_url = "https://mpo.psp.pertanian.go.id/v.5/login"
    driver.get(login_url)

    email_input = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    # email_input = driver.find_element(By.NAME, "email")
    email_input.send_keys(email)

    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(password)

    login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
    login_button.click()


email = "bast@binaagrosiwimandiri.com"
password = "Lapor"

driver = webdriver.Chrome()


def open_tab_and_load_link(link, window_number):
    driver.switch_to.window(driver.window_handles[window_number])
    driver.get(link)


# Buka tiga tab browser
# Buka tiga tab browser
login(driver, email, password)


# Masukkan link ke masing-masing tab
links = [
    "https://mpo.psp.pertanian.go.id/v.5/pelaporan/79238/empty",
    "https://mpo.psp.pertanian.go.id/v.5/pelaporan/79239/empty",
    "https://mpo.psp.pertanian.go.id/v.5/pelaporan/79240/empty",
]

# Thread untuk membuka dan memuat link pada setiap tab
threads = []
for i, link in enumerate(links):
    thread = threading.Thread(
        target=open_tab_and_load_link,
        args=(
            link,
            i,
        ),
    )
    threads.append(thread)
    thread.start()

# Tunggu hingga semua thread selesai
for thread in threads:
    thread.join()

# Anda sekarang memiliki tiga tab dengan link yang berbeda
