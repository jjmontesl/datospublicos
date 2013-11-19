#
# -*- coding: latin-1 -*-

# Import dondevanmisimpuestos data to cubes model.

import sys
from sqlalchemy.engine import create_engine
import re
import datetime
import csv
import random
import re

from elementtidy.TidyHTMLTreeBuilder import TidyHTMLTreeBuilder as TB
from xml.etree import ElementTree
import os


PROCEDURE_RANGE = [7763, 19855]
#PROCEDURE_RANGE = [19730, 19730]

FILE_SQLITE = "sqlite:///../../cubes/datospublicos-cubes.sqlite"

DIR_DATA = "data"

cache = {}
connection = None

def main():
 
    global connection
    
    # Open source
    engine = create_engine(FILE_SQLITE)
    connection = engine.connect()
    
    # Cleanup
    
    transaction = connection.begin();
    connection.execute("DELETE FROM dates");
    connection.execute("DELETE FROM pcpg_process");
    connection.execute("DELETE FROM pcpg_company");
    transaction.commit();
    
    
    # Import facts and dimension data
    transaction = connection.begin();
    import_pcpg()
    transaction.commit();

def save_object(table, row):
    
    if (table in cache):
        if (row["id"] in cache[table]):
            # TODO: Check that values are consistent
            
            return row["id"]
    else:
        cache[table] = {}
    
    keys = row.keys();
    sql = "INSERT INTO " + table + " ("
    sql = sql + ", ".join(keys)
    sql = sql + ") VALUES ("
    values = []
    for key in keys:
        if (isinstance(row[key], unicode)):
            values.append(row[key].encode('utf-8').replace("'", "''"))
        else:
            values.append(str(row[key]).replace("'", "''"))
    sql = sql + ", ".join([ ("'" + value + "'") for value in values])
    sql = sql + ")"
    
    #print "Inserting - Table: %-14s Id: %s Data: %20r" % (table, row["id"], row)
    #print sql
    
    connection.execute(sql);
    
    cache[table][row["id"]] = row
                              
    return row["id"]

def cleanup(value):
    
    value = value.replace("\n", " ")
    value = value.strip()
    
    return value

def sanitize(value):
    if (value == ""):
        value = "(BLANK)"
    elif (value == None):
        value = "(NULL)"
    else:
        value = re.sub('[^\w]', "_", value.strip())
    return value


def extract_number(text):
    
    result = re.sub(r'&#\d+', '', text)
    result = re.sub(r'[^0-9\,\.]', '', result)
    
    numPoints = result.count('.')
    numCommas = result.count(',')
    
    result = result.replace(",", ".")
     
    if ((numPoints > 0 and numCommas > 0) or (numPoints == 1) or (numCommas == 1)):
        decimalPart = result.split(".")[-1]
        integerPart = "".join ( result.split(".")[0:-1] )
    else:
        integerPart = result.replace(".", "")
        
    result = int(integerPart) + (float(decimalPart) / pow(10, len(decimalPart) ))
    
    return result
    
def insert_date (year, month, day):
    
    row = { }
    prefix = "date"
    
    date = datetime.date(int(year), int(month), int(day));

    if date != None:
        row["id"] = sanitize(datetime.datetime.strftime(date, "%Y-%m-%d"))
        row[prefix + "_year"] = date.year
        row[prefix + "_quarter"] = ((date.month - 1) / 3) + 1
        row[prefix + "_month"] = date.month
        row[prefix + "_day"] = date.day
        row[prefix + "_week"] = date.isocalendar()[1]

        if row[prefix + "_month"] == 12 and row[prefix + "_week"] <= 1:
            row[prefix + "_week"] = 52
        if row[prefix + "_month"] == 1 and row[prefix + "_week"] >= 52:
            row[prefix + "_week"] = 1

    return save_object ("dates", row)    

def elementtext(element, _addtail=False):
    '''
    Returns a list of text strings contained within an element and its sub-elements.
    Helpful for extracting text from prose-oriented XML (such as XHTML or DocBook).
    '''
    result = []
    if element.text is not None:
        result.append(element.text)
    for elem in element:
        result.append(elementtext(elem, True))
    if _addtail and element.tail is not None:
        result.append(element.tail)
    
    return cleanup(" ".join(result))


def import_pcpg():
    
    print "Processing PCPG files"
    
    count = 0
    for i in range(PROCEDURE_RANGE[0], PROCEDURE_RANGE[1] + 1):
        import_pcpg_file(i)
        count = count + 1
    
    print "Imported %d facts " % (count)
        
def import_pcpg_file(file_num):
    
    if (not os.path.exists(DIR_DATA + "/licitacion-" + str(file_num) + ".html")):
        print "File not found  %s" % file_num
        return
        
    with open(DIR_DATA + "/licitacion-" + str(file_num) + ".html", 'rb') as f:
        
        html = f.read()
        tb = TB()
        tb.feed(str(html))
        e = tb.close()
        
        
        #r = e.find('.//{http://www.w3.org/1999/xhtml}div[@id="tabs-3"]//{http://www.w3.org/1999/xhtml}table') 
        #ElementTree.dump(r)
        #print elementtext(r)
        
 
        fact = { "id" : file_num }
        
        if (e.find(".//{http://www.w3.org/1999/xhtml}div/{http://www.w3.org/1999/xhtml}h2[2]/{http://www.w3.org/1999/xhtml}span[2]") == None):
            print "Ignoring file %s" % file_num
            return
        
        # Process row
        
        fact["procedure_state_label"] = e.findtext(".//{http://www.w3.org/1999/xhtml}div/{http://www.w3.org/1999/xhtml}h2[2]/{http://www.w3.org/1999/xhtml}span[2]")
        fact["procedure_state"] = sanitize(fact["procedure_state_label"])
        
        fact["procedure_type_label"] = cleanup(elementtext(e.find(".//{http://www.w3.org/1999/xhtml}table[1]/{http://www.w3.org/1999/xhtml}tr[2]/{http://www.w3.org/1999/xhtml}td")))
        fact["procedure_type"] = sanitize(fact["procedure_type_label"])
        
        fact["procedure_purpose"] = elementtext(e.find(".//{http://www.w3.org/1999/xhtml}table[1]/{http://www.w3.org/1999/xhtml}tr[2]/{http://www.w3.org/1999/xhtml}td[3]"))
        
        fact["procedure_contract_label"] = elementtext(e.find(".//{http://www.w3.org/1999/xhtml}table[2]/{http://www.w3.org/1999/xhtml}tr[2]/{http://www.w3.org/1999/xhtml}td"))
        fact["procedure_contract"] = sanitize(fact["procedure_contract_label"])

        fact["procedure_amount"] = extract_number(elementtext(e.find(".//{http://www.w3.org/1999/xhtml}table[1]/{http://www.w3.org/1999/xhtml}tr[2]/{http://www.w3.org/1999/xhtml}td[4]")))
       
        #fact["offers_place"] =  "Rexistro xeral do Edificio Administrativo da Xunta de Galicia"
        #fact["offers_place2"] = "rua Concepcion Arenal, 8 - 36201 Vigo"
        #fact["offers_date"] = "05-12-2008"
        
        resolution = e.find('.//{http://www.w3.org/1999/xhtml}div[@id="tabs-3"]//{http://www.w3.org/1999/xhtml}table')
        
        if (resolution != None):
            for tr in resolution.findall('{http://www.w3.org/1999/xhtml}tr'):
                if (elementtext(tr.find("{http://www.w3.org/1999/xhtml}td[1]")) == "Provisional"):
                    date = elementtext(tr.find("{http://www.w3.org/1999/xhtml}td[5]")).split("-")
                    fact["contractor_date_provisional"] = insert_date(date[2], date[1], date[0])
                elif (elementtext(tr.find("{http://www.w3.org/1999/xhtml}td[1]")) == "Adxudicado"):
                    
                    company_name = elementtext(tr.find("{http://www.w3.org/1999/xhtml}td[3]")).upper()
                    company = { "id": sanitize(company_name), "name": company_name }
                    fact["contractor_company_id"] = save_object("pcpg_company", company)
                    
                    if (elementtext(tr.find("{http://www.w3.org/1999/xhtml}td[4]")) != ""):
                        fact["contractor_amount"] = extract_number(elementtext(tr.find("{http://www.w3.org/1999/xhtml}td[4]")))
                        date = elementtext(tr.find("{http://www.w3.org/1999/xhtml}td[5]")).split("-")
                        fact["contractor_date_final"] = insert_date(date[2], date[1], date[0])
                    else:
                        print "ERROR: Missing amount in %s" % file_num
        
        print fact
        
        save_object ("pcpg_process", fact)
            
if __name__ == "__main__":
    main()


