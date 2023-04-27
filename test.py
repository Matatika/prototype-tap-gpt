from bs4 import BeautifulSoup
import sys
import os
cwd = os.getcwd()
print(sys.version + " CWD " + cwd)

with open("output/find-and-update.company-information.service.gov.uk/company/03007129/filing-history/MzM2NDE1Mjc2NWFkaXF6a2N4/document?format=xhtml", encoding="utf-8") as f:
    data = f.read()
print("LEN " + str(len(data)))
soup = BeautifulSoup(data, features="html.parser")
text = soup.find_all("body")
if len(text) != 0:
    text = text[0].get_text()
else:
    text = ""
print(text)
