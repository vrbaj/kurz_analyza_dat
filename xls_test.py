from openpyxl import Workbook


wb = Workbook()
ws = wb.active
print(ws)
ws1 = wb.create_sheet('Sheet1')
ws2 = wb.create_sheet('Sheet2')
ws2.title = "Nový"
ws2 = wb["Nový"]
print(wb.sheetnames)
for sheet in wb:
    print(sheet.title)
ws2["A4"] = 7
hodnota = ws2["A4"]
print(f"hodnota {hodnota}")
for radek in ws2.iter_rows(min_row=1, max_col=3):
    for bunka in radek:
        print(bunka, bunka.value)
for idx1, radek in enumerate(ws2.iter_rows(min_row=1, max_col=3)):
    for idx2, bunka in enumerate(radek):
        bunka.value = f"{idx1},{idx2}"
ws2.delete_cols(1)
ws2.delete_rows(1)


wb.save('test.xlsx')