import csv

def separate_by_year(_file_name):
    files = {}
    writers = {}

    with open(_file_name, encoding='utf-8-sig') as globfile:
        reader = csv.reader(globfile)
        header = next(reader)
        for row in reader:
            if len(row) != len(header) or not all(row):
                continue
            year = row[5].split('-')[0]
            if year not in files:
                files[year] = open(f'{year}.csv', 'w', newline='', encoding='utf-8-sig')
                writers[year] = csv.writer(files[year])
                writers[year].writerow(header)
            writers[year].writerow(row)
    for year in files:
        files[year].close()


file_name = input("Введите название файла: ")
separate_by_year(file_name)

