# file.py
import argparse

# Membuat parser argumen
parser = argparse.ArgumentParser(description="Contoh penggunaan argumen.")

# Menambahkan argumen opsional
parser.add_argument("--driver", type=int, default=3, help="num driver")

# Parsing argumen
args = parser.parse_args()

# Mengakses argumen
parameter = args.driver
print("Parameter yang diberikan:", parameter)
print("type", type(parameter))
