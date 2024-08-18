from csv import DictWriter
from openpyxl import Workbook
from scipy.io import savemat

"""
 data should be in the format list of dictionary
 data = [
     {'name': 'Alice', 'age': 30, 'city': 'New York'},
     {'name': 'Bob', 'age': 25, 'city': 'Los Angeles'},
     {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}
 ]
"""


def export_to_csv(data, path_to_file):
    with open(path_to_file, 'w', newline='') as csvfile:
        fieldnames = data[0].keys()
        writer = DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def export_to_excel(data, path_to_file):
    wb = Workbook()
    ws = wb.active
    ws.append(list(data[0].keys()))
    for row in data:
        ws.append(list(row.values()))
    wb.save(path_to_file)


def export_to_mat(data, path_to_file):
    mat_data = {key: [d[key] for d in data] for key in data[0].keys()}
    savemat(path_to_file, mat_data)
