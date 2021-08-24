#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import mysql.connector
import time, json
import numpy as np

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')  # Last I checked this was necessary.

driver = webdriver.Chrome('/snap/bin/chromium.chromedriver' ,options=options)
driver.get("https://www.bazos.cz")

print("Driver running.")

try:
    with open('../config.json') as json_file:
        data = json.load(json_file)
except:
    print("config not found")

mydb = mysql.connector.connect(
  host=data.get("host"),
  user=data.get("user"),
  password=data.get("password"),
  database=data.get("database")
)

mycursor = mydb.cursor()

print("MySQL connector active.")

finderElems = ["", "", ""]

def wait_for(condition_function):
  start_time = time.time()
  while time.time() < start_time + 3:
    if condition_function():
      return True
    else:
      time.sleep(0.1)

def link_has_gone_stale():
    try:
        # poll the link with an arbitrary call
        driver.find_elements_by_id("container_one")
        return False
    except StaleElementReferenceException:
        return True

def getFinderElems():
    finderElems[0] = driver.find_element_by_id("hledat")
    finderElems[1] = driver.find_element_by_name("cenaod")
    finderElems[2] = driver.find_element_by_name("cenado")
    for x in finderElems:
        x.clear()

mycursor.execute("SELECT * FROM scrapping")

scrappings = mycursor.fetchall()

for scrapper in scrappings:
    if scrapper[5] == False:
        continue

    sql = "SELECT inzerat.number FROM inzerat INNER JOIN scrapping ON scrapping.id = inzerat.scrappingId WHERE scrapping.id = %s"
    par = (scrapper[0], )

    mycursor.execute(sql, par)

    numbersFoundArr = np.array(mycursor.fetchall())
    numbersFound = []
    
    for x in numbersFoundArr:
        numbersFound.append(str(int(x)))

    searchingFors = (''.join(scrapper[1])).split(";")
    searchingRemove = (''.join(scrapper[2])).replace(" ", "").split(";")

    for searchingFor in searchingFors:
        getFinderElems()
        finderElems[0].send_keys(searchingFor)
        finderElems[1].send_keys(scrapper[3])
        finderElems[2].send_keys(scrapper[4])
        finderElems[0].send_keys(Keys.RETURN)
        print("Searching for %s." % (searchingFor, ))

        allAdverts = False

        while not allAdverts:
            wait_for(link_has_gone_stale)

            adverts = driver.find_elements_by_class_name("inzeraty")

            for i in adverts:
                skip = False
                number = i.find_element_by_class_name("nadpis").find_element_by_tag_name("a").get_attribute("href").split("inzerat/")[1].split("/")[0]

                if number in numbersFound:
                    continue
                else:
                    numbersFound.append(number)

                    filter_text = i.find_element_by_class_name("nadpis").find_element_by_tag_name("a").get_attribute("innerHTML").lower() + i.find_element_by_class_name("popis").get_attribute("innerHTML").lower()
                    
                    if len(scrapper[2]) != 0:
                        for remover in searchingRemove:
                            if remover in filter_text:
                                skip = True
                                break

                    if skip:
                        continue

                    url = i.find_element_by_class_name("nadpis").find_element_by_tag_name("a").get_attribute("href")
                    name = i.find_element_by_class_name("nadpis").find_element_by_tag_name("a").get_attribute("innerHTML")
                    desc = i.find_element_by_class_name("popis").get_attribute("innerHTML")

                    try:
                        img = i.find_element_by_tag_name("img").get_attribute("src")
                    except:
                        continue
                    price = int(i.find_element_by_class_name("inzeratycena").find_element_by_tag_name("b").get_attribute("innerHTML").replace(" ", "").replace("Kč", ""))

                    sql = "INSERT INTO inzerat (number, name, description, img, price, seen, url, scrappingId) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                    par = (number, name, desc, img, price, False, url, scrapper[0])
                    
                    mycursor.execute(sql, par)
                    mydb.commit()

                    print(name)
                    print("\t", number)
                    print("\t", price)


            try:
                stranky = driver.find_element_by_class_name("strankovani").find_elements_by_tag_name("a")[-1]
                dalsiBtn = stranky.find_element_by_tag_name("b")

                if dalsiBtn.get_attribute("innerHTML") == "Další":
                    driver.get(stranky.get_attribute("href"))
            except:
                print("Searching for %s done." % (searchingFor, ))
                allAdverts = True

driver.close()
