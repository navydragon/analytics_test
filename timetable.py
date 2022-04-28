
import pandas as pd
import requests
from bs4 import BeautifulSoup

url = "https://roat-rut.ru/spectimetable"
r = requests.get(url)

soup = BeautifulSoup(r.text,'lxml')

hrefs =soup.findAll('a')

hrefs = hrefs[6:]

arr = hrefs
print("Всего элементов:",len(arr))

result = []
i = 0
for elem in arr:
  i+=1
  print("parsing elem",i)
  href = elem.get('href')
  if "B625.exe" in href:
    tables = pd.read_html(href,encoding="windows-1251")
    work_table =tables[1]
    if len(result) == 0:
      result = work_table
    else:
      result = pd.concat([result, work_table])

result.info()