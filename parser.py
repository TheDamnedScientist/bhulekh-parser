from bs4 import BeautifulSoup
from itertools import zip_longest
from tkinter import filedialog
import pandas as pd
import re
import tkinter as tk

# Hide the root window
root = tk.Tk()
root.withdraw()

# Ask user to select an HTML file
file_path = filedialog.askopenfilename(
    title="Select an HTML file",
    filetypes=[("HTML files", "*.html *.htm"), ("All files", "*.*")]
)

# Check if file was selected
if file_path:
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    file_name = soup.title.string
    # Example: print title tag
    print("Title:", file_name)
else:
    print("No file selected.")

headers = [
    "Select-Village *",
    "land_type",
    "Bhulekh-खाता-संख्या *",
    "फसली-वर्ष *",
    "खातेदार-का-नाम *",
    "खातेदार-का-अंतिम-नाम",
    "पिता/-पति-/-संरक्षक-का-नाम *",
    "gender",
    "Address-*",
    "caste",
    "allBhaumikYears",
    "totalHissa",
    "individualHissa",
    "bhaumik_year",
    "legal_case_desc"
]

surnames = ["सिंह", "सिह", "कुमार", "देवी", "सि‍ह"]

# Extract common details
tr_common = soup.find('tr', class_='sub-heading', style='border-bottom: 1px solid #e8e8e8;')
div_tags = tr_common.find_all('div')
div_data = [div.get_text(separator=',', strip=True).split(',') for div in div_tags]

village_name = div_data[0][-1]
address = village_name
pargana = re.sub('\(|\)', '', div_data[1][-1])
tehsil = div_data[2][-1]
district = div_data[3][-1]
phasli_year = div_data[4][-1]
part = div_data[5][-1]
khata_number = div_data[6][-1]
caste = "सामान्‍य"

# extracting land type
trs = soup.find_all("tr", class_="sub-heading")

# Look for the one that contains 'श्रेणी :'
target_tr = None
for tr in trs:
    if tr.get_text(strip=True).startswith("श्रेणी"):
        target_tr = tr
        break

td_tags = target_tr.find_all("td")
td_data = [td.get_text(separator=',', strip=True).split(',') for td in td_tags]
land_type = td_data[0][-1].split('/')[0].strip()

# Extract all matching data rows
tr = soup.find('tr', class_='sub-heading', style='border: 1px solid #000;')
td_tags = tr.find_all('td')
td_data = [td.get_text(separator=',', strip=True).split(',') for td in td_tags]

# Join the 2nd column
td_data[1] = [' '.join(td_data[1])]

# separating the name field
names_list = [element.split('/') for element in td_data[0]]
names_list = list(zip(*names_list))
names_list = [list(item) for item in names_list]
person_name = [re.split('\d', element)[0] for element in names_list[0]]
person_name = [item.strip() for item in person_name]

first_name = []
last_name = []
for name in person_name:
    full_name = name.split()
    if name == "श्रीमती झवरी देवी":
        pass
    if len(full_name) > 1:
        if ("श्री" in full_name or "श्रीमती" in full_name) and len(full_name) == 2:
            first_name.append(name)
            last_name.append('')
        else:
            first_name.append(' '.join(full_name[0:-1]))
            last_name.append(full_name[-1])
    else:
        for sur in surnames:
            if sur in name:
                name = name.replace(sur, "")
                first_name.append(name)
                last_name.append(sur)
                break
        else:
            first_name.append(name)
            last_name.append('')

parents_name = [item.strip() for item in names_list[1]]
pieces_list = [re.search('\d+', element) for element in names_list[0]]
total_pieces_prep = re.search('\d+', names_list[0][-1])
if total_pieces_prep:
    total_pieces = total_pieces_prep.group(0)
else:
    total_pieces = re.search('\d+', td_data[0][-1]).group(0)

pieces = []
for element in pieces_list:
    try:
        pieces.append(element.group(0))
    except:
        pieces.append('N/A')

# create the gender column
gender = []
for person in person_name:
    if 'देवी' in person or 'श्रीमती' in person:
        gender.append('महिला')
    else:
        gender.append('पुरुष')
        
num_items = len(person_name)

td_data.pop(0)
bhaumiki_year = int(re.search('\d+', td_data[0][0]).group(0))
# td_data = [names_list[0], names_list[1], gender, names_list[2]] + td_data
# td_data = [person_name, names_list[1], gender, names_list[2], pieces] + td_data
td_data = [[village_name]*num_items, [land_type]*num_items, [khata_number]*num_items, [phasli_year]*num_items, first_name, last_name, parents_name, gender, [address]*num_items, [caste]*num_items, [bhaumiki_year]*num_items, [total_pieces]*num_items, pieces, [bhaumiki_year]*num_items, [None]*num_items]
rows = zip_longest(*td_data, fillvalue='')

df = pd.DataFrame(rows, columns=headers)
df = df.drop(df.index[-1])
df.to_excel(f'output_table_{file_name.lower()}.xlsx', index=False)

print(f"✅ Done! File saved as 'output_table_{file_name.lower()}.xlsx' in this executable's directory.")
input("Press 'Enter' to exit...")