#
# -*- coding: latin-1 -*-

# Import dondevanmisimpuestos data to cubes model.

import sys
from sqlalchemy.engine import create_engine
import re
import datetime
import csv
import random

FILE_SQLITE = "sqlite:///dvmi-cubes.sqlite"

FILE_CCAA_BUDGET = "../public/data/BudgetData.csv"
FILE_CCAA_CENSUS_PREFIX = "../public/data/Censo"
FILE_CCAA_CENSUS_YEARS = [2006, 2007, 2008, 2009, 2010, 2011, 2012]
FILE_PGE_PREFIX = "../pge/parser/output/"
FILE_PGE_YEARS = ["2008", "2009", "2010", "2011", "2012", "2012P", "2013", "2013P", "2014P"]

cache = {}
connection = None

def main():
 
    global connection
    
    # Open source
    engine = create_engine(FILE_SQLITE)
    connection = engine.connect()
    
    # Cleanup
    
    transaction = connection.begin();
    connection.execute("DELETE FROM ccaa");
    connection.execute("DELETE FROM ccaa_census");
    connection.execute("DELETE FROM ccaa_budget");
    
    connection.execute("DELETE FROM pge_sections");
    connection.execute("DELETE FROM pge_organisms");
    
    connection.execute("DELETE FROM pge_groups");
    connection.execute("DELETE FROM pge_concepts");
    connection.execute("DELETE FROM pge_concepts_l1");
    connection.execute("DELETE FROM pge_concepts_l2");
    connection.execute("DELETE FROM pge_concepts_l3");
    
    connection.execute("DELETE FROM pge_expenses");
    transaction.commit();
    
    
    # Import facts and dimension data
    transaction = connection.begin();
    ccaa_census = import_ccaa_census()
    transaction.commit();

    transaction = connection.begin();
    import_ccaa()
    import_ccaa_budget(ccaa_census)
    transaction.commit();

    transaction = connection.begin();
    import_pge_sections()
    import_pge_organisms()
    transaction.commit();
    
    import_pge_expenses(ccaa_census)

    

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
    sql = sql + ", ".join([ ("'" + str(row[key]).replace("'", "''") + "'") for key in keys])
    sql = sql + ")"
    
    #print "Inserting - Table: %-14s Id: %s Data: %20r" % (table, row["id"], row)
    #print sql
    
    connection.execute(sql);
    
    cache[table][row["id"]] = row
                              
    return row["id"]

def sanitize(value):
    
    if (value == ""):
        value = "(BLANK)"
    elif (value == None):
        value = "(NULL)"
    else:
        value = re.sub('[^\w]', "_", value.strip())
    return value


def import_ccaa_budget(ccaa_census):
    
    print "Processing CCAA budgets"
    
    count = 0
    header = None
    with open(FILE_CCAA_BUDGET, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            
            count = count + 1
            fact = { "id" : count }
            
            if (header == None):
                header = row
                continue
            
            arow = {}
            for header_index in range (0,  len(header)):
                arow[(header[header_index])] = row[header_index]
            
            # Process row
            fact["date_year"] = arow["Ano"]
            fact["ccaa_id"] = arow["Idcomu"]
            fact["function_code"] = arow["Codigo"]
            fact["function_label"] = arow["Funcion"]
            fact["amount"] = arow["Total"]
            fact["amount_per_capita"] = float(arow["Total"]) / float( ccaa_census[str(arow["Ano"])] )
            fact["amount_per_ccaa_capita"] = float(arow["Total"]) / float( ccaa_census[arow["Idcomu"] + "-" + str(arow["Ano"])] )
            
            save_object ("ccaa_budget", fact)
            
    print "Imported %d facts " % (count)
    
def import_ccaa_census():
    
    print "Processing CCAA census"
    
    ccaa_census = {}
    
    count = 0
    for year in FILE_CCAA_CENSUS_YEARS:
        fileyear = year
        #if (fileyear == 2011): fileyear = 2010 # hack broken 2011 file
        with open(FILE_CCAA_CENSUS_PREFIX + str(fileyear) + ".csv", 'rb') as f:
            header = None
            census_year = 0
            reader = csv.reader(f)
            for row in reader:
                
                if (header == None):
                    header = row
                    continue
                
                arow = {}
                for header_index in range (0,  len(header)):
                    arow[(header[header_index])] = row[header_index]
                
                count = count + 1
                fact_male = { "id" : count, 
                             "date_year": year,
                             "ccaa_id": arow["Idcomu"], 
                             "genre": "Varones", 
                             "amount": arow["Varones"] }
                save_object ("ccaa_census", fact_male)
                
                count = count + 1
                fact_male = { "id" : count, 
                             "date_year": year,
                             "ccaa_id": arow["Idcomu"], 
                             "genre": "Mujeres", 
                             "amount": arow["Mujeres"] }
                save_object ("ccaa_census", fact_male)   
                
                ccaa_census[arow["Idcomu"] + "-" + str(year)] = float(arow["Varones"]) + float(arow["Mujeres"])
                if (not str(year) in ccaa_census): ccaa_census[str(year)] = 0   
                ccaa_census[str(year)] =  ccaa_census[str(year)] +  ccaa_census[arow["Idcomu"] + "-" + str(year)]   
                
    print "Imported %d facts " % (count)
    
    return ccaa_census    

def import_ccaa():
    
    print "Processing CCAA"
    
    count = 0
    header = None
    with open(FILE_CCAA_CENSUS_PREFIX + str(FILE_CCAA_CENSUS_YEARS[0]) + ".csv", 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            
            count = count + 1
            fact = {}
            #fact = { "id" : count }
            
            if (header == None):
                header = row
                continue
            
            arow = {}
            for header_index in range (0,  len(header)):
                arow[(header[header_index])] = row[header_index]
            
            # Process row
            fact["id"] = arow["Idcomu"]
            fact["ccaa_label"] = arow["Comunidad"]
            
            save_object ("ccaa", fact)
            
    print "Imported %d facts " % (count)

def import_pge_sections():
    
    print "Processing PGE sections"
    
    sections = {}
    
    count = 0
    for year in FILE_PGE_YEARS:
        header = None
        with open(FILE_PGE_PREFIX + str(year) + "/top_level_sections.csv", 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                
                count = count + 1
                fact = {}
                #fact = { "id" : count }
                
                if (header == None):
                    header = row
                    continue
                
                arow = {}
                for header_index in range (0,  len(header)):
                    arow[(header[header_index])] = row[header_index]
                
                # Process row
                fact["id"] = arow["Id"]
                fact["name"] = arow["Id"] + " " + arow[" Nombre"]
                
                save_object ("pge_sections", fact)
            
    print "Imported %d facts " % (count)

def import_pge_organisms():
    
    print "Processing PGE organisms"
    
    count = 0
    for year in FILE_PGE_YEARS:
        header = None
        filename = FILE_PGE_PREFIX + str(year) + "/child_sections.csv"
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                
                count = count + 1
                fact = {}
                #fact = { "id" : count }
                
                if (header == None):
                    header = row
                    continue
                
                arow = {}
                for header_index in range (0,  len(header)):
                    arow[(header[header_index])] = row[header_index]
                
                # Process row
                fact["id"] = sanitize(arow["Id"])
                fact["name"] = arow["Id"] + " " + arow["Organismo"]
                fact["pge_sections_id"] = arow["Sección"]
                fact["organism_type"] = arow["Tipo"]
                
                save_object ("pge_organisms", fact)
            
    print "Imported %d facts " % (count)

def save_unknown_organism (organism_id):

    sect = {}
    sect["id"] = organism_id.split("_")[0]
    sect["name"] = sect["id"] + " N/D"
    save_object ("pge_sections", sect)
    
    fact = {}
    fact["id"] = sanitize(organism_id)
    fact["name"] = organism_id + " N/D"
    fact["pge_sections_id"] = sect["id"]
    fact["organism_type"] = -1
    save_object ("pge_organisms", fact)
    

def import_pge_expenses(ccaa_census):
    
    expenses = {}
    count = 0
    for year in FILE_PGE_YEARS:
        
        transaction = connection.begin();
        
        filename = FILE_PGE_PREFIX + str(year) + "/expenses.csv"
        print "Processing PGE file: %s" % (filename)
        with open(filename, 'rb') as f:
            reader = csv.reader(f, delimiter = "|")
            for row in reader:
                
                count = count + 1
                fact = {}
                #fact = { "id" : count }
                
                # Process row
                fact["id"] = row[0]
                fact["date_year"] = year # row[1]
                fact["pge_organism_id"] = row[2] + "_" + row[3] + "_" + row[4]
                save_unknown_organism(fact["pge_organism_id"])
                
                fact["pge_group_id"] = row[5] 
                fact["pge_concept_id"] = row[6]
                
                fact["concept"] = row[7]
                
                fact["amount"] = float(row[8]) * 1000.0
                
                year_census = year # fact["date_year"]
                if (year_census == "2012P"): year_census = "2012"
                if (year_census == "2013"): year_census = "2012"
                if (year_census == "2013P"): year_census = "2012"
                if (year_census == "2014P"): year_census = "2012"
                if (year_census == "2014P"): year_census = "2012"
                fact["amount_per_capita"] = float( fact["amount"] ) / float( ccaa_census[str(year_census)] ) 
                
                if (fact["pge_concept_id"] == ""):
                    if (fact["pge_group_id"] != ""):
                        save_object ("pge_groups", { "id": fact["pge_group_id"], "name": fact["pge_group_id"] + " " + fact["concept"] } )
                else:
                    levelstring = (row[6][0] + ("X" if (len(row[6]) < 2) else row[6][1]) + 
                                              ("X" if (len(row[6]) < 3) else row[6][2]) + 
                                              ("XX" if (len(row[6]) < 5) else row[6][3:5]))
                    
                    if (len(row[6]) == 1): save_object ("pge_concepts_l1", { "id": levelstring[0], "level1": fact["concept"] })
                    if (len(row[6]) == 2): save_object ("pge_concepts_l2", { "id": levelstring[0:2], "level2": fact["concept"], "level1_id": levelstring[0] })
                    if (len(row[6]) == 3): save_object ("pge_concepts_l3", { "id": levelstring[0:3], "level3": fact["concept"], "level2_id": levelstring[0:2] })
                    save_object ("pge_concepts", {"id": fact["pge_concept_id"], "name": fact["pge_concept_id"] + " " + fact["concept"] ,
                                                  "level3_id": levelstring[0:3] } )

                    # Filter summary entries
                    # Only save if there are no other expenses in this category
                    found = False
                    for expense in expenses.values():
                        if (expense["id"].startswith(fact["id"])):
                            found = True
                            #print "Not inserting %s as children exist: %s" % (fact["pge_concept_id"], expense["pge_concept_id"])
                            break

                    for i in range (1, len(row[6])):
                        possible_parent = fact["id"][0:-i]
                        if (possible_parent in expenses):
                            #print "Removing existing item: this %s is child of an existing %s" % (fact["pge_concept_id"], possible_parent)
                            del expenses[possible_parent]
                    
                    if (not found):
                        expenses[fact["id"]] = fact
    
        # Write facts
        for fact in expenses.values():
            save_object ("pge_expenses", fact)
        
        transaction.commit()
        
        expenses = {}
            
    print "Imported %d facts " % (count)

if __name__ == "__main__":
    main()

