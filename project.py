import csv
from math import nan
import re
import pandas as pd
import numpy as np
import numpy
from sklearn import tree
from sklearn import preprocessing
from sklearn.model_selection import train_test_split 
from sklearn.model_selection import GridSearchCV
from unidecode import unidecode
import mysql.connector


def to_str(var):
    if type(var) is list:
        return str(var)[1:-1] # list
    if type(var) is numpy.ndarray:
        try:
            return str(list(var[0]))[1:-1] # numpy 1D array
        except TypeError:
            return str(list(var))[1:-1] # numpy sequence
    return str(var)
def convert(data):
    number = preprocessing.LabelEncoder()
    data = number.fit_transform(data)
    data=np.nan_to_num(data, nan=-9999, posinf=33333333, neginf=33333333) # fill holes with default value
    return data


cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1', database='bama',
                              auth_plugin='mysql_native_password')
cursor = cnx.cursor(buffered=True)
cursor.execute("SELECT * FROM bamacars3")
records = cursor.fetchall()
print(len(records))
row = []
for idx in range (len(records)):
    car_name = records[idx][0]
    model = records[idx][1]
    mileage = records[idx][2]
    mileage = records[idx][2].replace(",", "")
    city = records[idx][3].split('،')[0]
    price = records[idx][4] 
    price = records[idx][4].replace(",", "")  
    row.append([car_name,model,mileage,city,price])

col_names = ['car_name','model','mileage','city','price']
df = pd.DataFrame(row,columns=col_names)

for i in df.index:
    if df['price'][i] =='قیمت توافقی' or df['price'][i] =='بدون قیمت' or df['price'][i].find('پیش') != -1:
        df =  df.drop(index=i,axis=0) 
for i in df.index:
    if df['mileage'][i] == '' or df['mileage'][i] == '-':
        df = df.drop(index=i , axis=0)
car_name_unique = np.unique(df['car_name'])
city_unique = np.unique(df['city'])

carname_le = preprocessing.LabelEncoder()
df['car_name'] = carname_le.fit_transform(df['car_name'])

city_le = preprocessing.LabelEncoder()
df['city'] = city_le.fit_transform(df['city'])

x = df[['car_name','model','mileage','city']]
y = df['price']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.20)
#print(df.head(5))
  
df = df.drop([df.index[388] , df.index[1400] , df.index[2452] , df.index[2453]])
#print(np.where(df.applymap(lambda x: x == ''))[0])
clf = tree.DecisionTreeClassifier()
clf = clf.fit(x_train,y_train)
predict = clf.score(x_test,y_test)

car_name_input = input('لطفا نام ماشین را به فارسی تایپ کنید و کلید اینتر را فشار دهید:')
car_name_input_text = (re.sub(r'[^\w\s]',' ',car_name_input)).strip()
model_input = input('لطفا مدل ماشین را به سال تایپ کنید(مانند 1400) و کلید اینتر را فشار دهید:')
mileage_input = int(input('لطفا کارکرد ماشین را وارد کنید و کلید اینتر را فشار دهید:'))
city_input = input('لطفا نام شهر فروشنده را وارد نمایید و اینتر بزنید:')
city_input_text = (re.sub(r'[^\w\s]',' ',city_input)).strip()
if any(car_name_input_text in s for s in car_name_unique):
    matching1 = [s for s in car_name_unique if car_name_input_text in s]
    car_predict = np.where(car_name_unique == matching1)[0]
else:
    print(' لطفا از لیست داده شده یک مورد را انتخاب کنید:.نام ماشین وارد شده در لیست ماشین های موجود نمی باشد',car_name_unique)
if (int(model_input) in range(1300,1401)) or (int(model_input) in range(1900,2022)):
    model_predict = int(model_input)
else:
    print('مدل وارد شده باید در فرمت سال میلادی یا شمسی باشد')
if any(city_input_text in s for s in city_unique):
    matching = [s for s in city_unique if city_input_text in s]
    city_predict = np.where(city_unique == matching)[0]
else:
    print(' لطفا از لیست داده شده یک مورد را انتخاب کنید:.نام شهر وارد شده در لیست شهرهای موجود نمی باشد',car_name_unique)
data = [[car_predict,model_predict,mileage_input,city_predict]]
predict_price = clf.predict(data)
print(predict_price)
cnx.commit()
cnx.close()
