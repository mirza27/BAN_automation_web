import subprocess
import pandas as pd

while True:
    # Baca CSV
    df = pd.read_csv("csv/link_tana_toraja2.csv")

    # Periksa panjang CSV, jika 0
    if len(df) == 0 & len(df) < 1:
        break  # Keluar dari perulangan jika kondisi terpenuhi
    elif len(df) <= 2:  # jika link csv kurang dari 3
        driver = str(len(df))
        subprocess.run(
            [
                "python",
                "report_upload/autoupload_spk.py",
                "--driver",
                driver,
            ]
        )
    else:  # jika link csv lebih dari 3
        subprocess.run(["python", "report_upload/autoupload_spk.py"])

    # refresh item link
    subprocess.run(["python", "get_link/getlink_specific.py"])
