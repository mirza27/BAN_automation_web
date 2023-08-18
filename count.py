import os

def count_images_with_keyword(directory, keyword):
    count = 0
    keyword = keyword.lower()

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')) and keyword in file.lower():
                count += 1

    return count

if __name__ == "__main__":
    directory = "C:\\Users\\ramad\\OneDrive\\Dokumen\\BAN\\OC Sumba Timur"
    keyword = "OC"

    total_images_with_keyword = count_images_with_keyword(directory, keyword)
    print(f"Total images with the keyword 'oc': {total_images_with_keyword}")
