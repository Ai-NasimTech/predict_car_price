import requests
from bs4 import BeautifulSoup
import re
import sys
import time
import mysql.connector
cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1', database='bama',
                              auth_plugin='mysql_native_password')
cursor = cnx.cursor(buffered=True)
#cursor.execute("CREATE DATABASE bama")
#cursor.execute("CREATE TABLE bamacars3 (car_name VARCHAR(255), model VARCHAR(255), mileage VARCHAR(255), city VARCHAR(255), price VARCHAR(255))")
cursor.execute("SELECT * FROM bamacars3")
records = cursor.fetchall()


url = "https://bama.ir/car/all-brands/all-models/all-trims?page="
row = []
for page in range(1,200):
    req = requests.get(url+str(page))
    #print(req)
    soup = BeautifulSoup(req.text , 'html.parser')
    cars = soup.find_all('li',attrs={'class':'car-list-item-li list-data-main'})
    for idx in range(len(cars)):
        name = cars[idx].find('div', class_="title")
        name_text = (re.sub(r'\s+',' ',name.text)).strip()
        name_split = name_text.split('|')
        car_name = name_split[0]
        car_name = (re.sub('[^\w\s]', '', car_name))
        model = name_split[1]
        model = (re.sub('[^\w\s]', '', model))
        mileage_text = cars[idx].find('div', class_="car-func-details")
        mileage_split = (re.sub(r'\s+',' ',mileage_text.text)).strip().split('|')[0]
        mileage = mileage_split.split(' ')[1]
        if mileage == 'صفر':
            mileage = '0'
        city = cars[idx].find('div',class_='city-area').text.strip()
        #date = cars.find('span',class_='mod-date-car-page')
        #if date:
        #date = date.text.strip()
        has_price = cars[idx].find('p', class_='cost single-price')
        no_price = cars[idx].find('p',class_='cost small')
        installment_price = cars[idx].find('p',class_='cost installment-cost')
        blured_price = cars[idx].find('p',class_='cost blured single-price')
        if has_price:
            price = has_price.text.strip().split(' ')[0]
        elif no_price:
            price = no_price.text.strip()
        elif installment_price:
            price1 = cars[idx].findAll('p',class_='cost installment-cost')[0].text
            price2 = cars[idx].findAll('p',class_='cost installment-cost')[1].text
            price = price1 +' و '+ price2
        elif blured_price:
            price = blured_price.text.strip().split(' ')[0]
        else:
            price = 'بدون قیمت'
        #print(car_name,'|',model,'|',mileage,'|',city,'|',price)
        flag = False
        for record in records:
            if (car_name,model,mileage,city,price) == record:
                flag = True
                break
        if flag:
            break
        row.append([car_name,model,mileage,city,price])
        #if row[idx] == row[idx-1]:
            #sys.exit()

#print(records[-1])
sql = "INSERT IGNORE INTO bamacars3(car_name, model, mileage, city, price) VALUES (%s, %s, %s,%s,%s)"
cursor.executemany(sql, row)
cnx.commit()
cnx.close()
