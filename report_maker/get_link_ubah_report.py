from bs4 import BeautifulSoup
import csv


def extract_data_from_html(file_path, out_name):
    try:
        # Buka file HTML
        with open(file_path, "r", encoding="utf-8") as html_file:
            html_content = html_file.read()

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
                        link_ubah = links[0]
                        href_ubah = link_ubah["href"]

                        data.append((nomor, href_ubah, poktans, desa))

        # Simpan data dalam file CSV
        with open(out_name, "w", newline="", encoding="utf-8") as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["no", "situs", "poktan", "desa"])
            for idx, (nomor, situs, poktan, desa) in enumerate(data, start=1):
                csv_writer.writerow([nomor, situs, poktan, desa])

    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred:", str(e))


# Contoh penggunaan: ganti dengan path file HTML yang sesuai
file_path = "./html/report_hapus.html"
out_name = "./csv/report_hapus.csv"

extract_data_from_html(file_path, out_name)
