#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time, json

driver = webdriver.Firefox()
driver.get("https://www.bazos.cz")

finderElems = ["", "", ""]

# input parameters
searchingFor = ["octavia 1.6", "octavia 1,6", "octavia 16"]
searchingRemove = ["dsg", "mpi", "fsi", "tsi", "benzín", "benzin", "1.9", "1,9", "16v", "20v", "lpg", "cng", "4x4", "1.8", "1,8", "1.6i", "1,6i", "75kw"]
priceRange = [70000, 150000]

itemsFound = {}
itemsFound['inzeraty'] = []
numbersFound = []

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
    finderElems[1].send_keys(priceRange[0])
    finderElems[2].send_keys(priceRange[1])

def readFromFile(data):
    try:
        with open('data.json') as json_file:
            data = json.load(json_file)

        for i in data["inzeraty"]:
            numbersFound.append(i.get("number"))
            itemsFound["inzeraty"].append(i)
    except:
        return

def writeToFile(data):
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)




readFromFile(itemsFound)
done = False


while not done:
    for x in searchingFor:
        getFinderElems()
        finderElems[0].send_keys(x)
        finderElems[0].send_keys(Keys.RETURN)

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

                    name = i.find_element_by_class_name("nadpis").find_element_by_tag_name("a").get_attribute("innerHTML").lower()
                    
                    for remover in searchingRemove:
                        if remover in name:
                            skip = True
                            break

                    if skip:
                        continue

                    url = i.find_element_by_class_name("nadpis").find_element_by_tag_name("a").get_attribute("href")

                    try:
                        img = i.find_element_by_tag_name("img").get_attribute("src")
                    except:
                        continue
                    price = i.find_element_by_class_name("inzeratycena").find_element_by_tag_name("b").get_attribute("innerHTML")
                    itemsFound["inzeraty"].append({
                        'number': number,
                        'name': name,
                        'img': img,
                        'price': price,
                        'seen': False,
                        'url': url,
                        })

                    print(name)
                    print("\t", number)
                    print("\t", price)

            stranky = driver.find_element_by_class_name("strankovani").find_elements_by_tag_name("a")[-1]

            try:
                dalsiBtn = stranky.find_element_by_tag_name("b")

                if dalsiBtn.get_attribute("innerHTML") == "Další":
                    driver.get(stranky.get_attribute("href"))
            except:
                print("searching done")
                allAdverts = True


    writeToFile(itemsFound)

driver.close()
