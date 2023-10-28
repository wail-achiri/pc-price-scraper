from datetime import datetime


def getCurrentDate ():
    localcurrentdateandtime = datetime.now()
    currentdatetime = localcurrentdateandtime.strftime("%m_%d_%Y") # Get the current date from the local date and time
    return currentdatetime

def convertPrice (price):
    price = float(price.replace(",", "."))
    return price


def setMinPrices (list_min, minValues): 

    filteredValues = [valor for valor in minValues if valor != "" and valor != 0] 
    
    if filteredValues == [] :
        list_min.append("")
    else:
        list_min.append(min(filteredValues))



