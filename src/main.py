import pandas as pd 
import requests
import urlsPc as urlsPc
import utils as Util
import webbrowser
import os

from bs4 import BeautifulSoup
from webs_enum import Webs
from constants import HEADERS, XLSX_EXTENSION, REPORT_NAME, PATH_REPORT, NAN_VALUE



def initializer ():
    for modelo in urlsPc.componentes_pc["componentes_pc"]:
        for sitio_web in modelo["sitios_web"]:
            sitio_web["precio"] = obtainPriceWeb(sitio_web["nombre"],sitio_web["enlace"])
    
    generateExcel()

# FUNCIÓN ENCARGADA DE LLAMAR A LA FUNCIÓN CON SU URL Y RESPECTIVAMENTE WEB
def obtainPriceWeb (webName, url):
    price = ""
    
    if url == "":
        return price
    
    try:
        switch_dict = {
            Webs.PCCOM: inputPricePcCom,
            Webs.AMAZON: webScrappingPrice,
            Webs.REDCOM: webScrappingPrice,
            Webs.COOLMOD: webScrappingPrice
        }
        
        if webName in switch_dict:
            price = switch_dict[webName](webName, url, price)
    except Exception as e:
        print(f"Error al obtener el precio de {webName}: {str(e)}")
        return price
    
    return price;


def inputPricePcCom (webName, url, price):
    #COMO LA WEB DE PCCOM BLOQUEA CUALQUIER ESCARBEO DE DATOS, LOS METEREMOS MANUALMENTE
    print("INTRODUCE EL PRECIO DEL PRODUCTO")
    print("WEB: "+webName)
    webbrowser.open(url)
    print("Mete el precio del producto: ", end="")
    price = Util.convertPrice(input())
    os.system('cls')
    
    return price 



#FUNCIÓN ENCARGADA DE HACER UNA PETICIÓN A LA WEB Y OBTENER LOS DIVS Y CLASS DONDE SE PUEDEN ENCONTRAR EL PRICE (PCCOM BLOQUEA)
def webScrappingPrice(webName, url, price):
    
    page = requests.get(url, headers=HEADERS)

    if page.status_code == 200:
        soup = BeautifulSoup(page.content, "html.parser")
        if webName == Webs.AMAZON:
            div_precio = soup.find(id="corePriceDisplay_desktop_feature_div")
            if div_precio:
                span_precio = div_precio.find('span', class_='a-price-whole')
                if span_precio: 
                    price = span_precio.text
        elif webName == Webs.REDCOM:
            div_precio = soup.find('div',id="col-product-info")
            if div_precio:
                span_precio = div_precio.find('span', class_='product-price')
                if span_precio:
                    price = span_precio['content']
        elif webName == Webs.COOLMOD:
            div_precio = soup.find(id="normalpriceproduct")
            if div_precio:
                span_precio = div_precio.find('span', id="normalpricenumber")
                if span_precio:
                    price = span_precio.text
    
    if price is not None and isinstance(price, str) and price != "" :
        price = Util.convertPrice(price)
    else:
        price = ""
    
    return price; 

def generateExcel():
    headersEx = ["Modelo"] + [web["nombre"] for web in urlsPc.componentes_pc["componentes_pc"][0]["sitios_web"]] + ["MIN"] 
    indexes = [model["modelo"] for model in urlsPc.componentes_pc["componentes_pc"]] 
    data = {}
    
    for header in headersEx:
        data[header] = []
    
    list_min = []
    list_coolmod = []
    list_redcom = []
    list_pccom = []
    list_amazon = []
    list_prod = []
    
    for modelo in urlsPc.componentes_pc["componentes_pc"]:
        list_prod.append(modelo["nombre"]) #AQUI METERIAMOS LOS NOMBRES DE LOS PRODUCTOS
        minX = []
        
        for sitio_web in modelo["sitios_web"]:
            if sitio_web["nombre"] == Webs.AMAZON:
                list_amazon.append(sitio_web["precio"])
                minX.append(sitio_web["precio"])
            elif sitio_web["nombre"] == Webs.PCCOM:
                list_pccom.append(sitio_web["precio"])
                minX.append(sitio_web["precio"])
            elif sitio_web["nombre"] == Webs.REDCOM:
                list_redcom.append(sitio_web["precio"])
                minX.append(sitio_web["precio"])
            elif sitio_web["nombre"] == Webs.COOLMOD:
                list_coolmod.append(sitio_web["precio"])
                minX.append(sitio_web["precio"])
        Util.setMinPrices(list_min, minX)
    
    data["Modelo"] = list_prod
    data["Amazon"] = list_amazon
    data["PcCom"] = list_pccom
    data["RedComp"] = list_redcom
    data["Coolmod"] = list_coolmod
    data["MIN"] = list_min
        
    df = pd.DataFrame(data, index = indexes)
    
    # Crea una nueva fila de DataFrame con la suma total
    new_row = pd.DataFrame([["", NAN_VALUE, NAN_VALUE, NAN_VALUE, NAN_VALUE, NAN_VALUE]] , index=["Total"] , columns=df.columns)

    # Agrega una columna adicional con el valor
    new_row["Total"] = sum(valor for valor in list_min if valor != "")

    # Concatena la nueva fila al DataFrame existente
    df = pd.concat([df, new_row])

    nameExcel = REPORT_NAME + Util.getCurrentDate() + XLSX_EXTENSION

    # Exporta el DataFrame a Excel
    df.to_excel(PATH_REPORT + nameExcel, index=True)
    
    print("Excel generado")



initializer()
