"""This module is intended to read in a csv file of CR #### and road alias names and then return
two separate dictionaries which are inverse of each other (One of the format CR ####: Alias and the other
Alias: CR####. The dictionaries will then be used to query and update local GIS data"""

import arcpy
import os
import csv
from road_alias import *

CR_to_alias_dict = CR_to_named_alias_dict('Road Aliases.csv')
print(CR_to_alias_dict)

named_to_CR_dict = named_alias_to_CR_dict(CR_to_alias_dict)
print(named_to_CR_dict)

in_FC = 'Roads'
field = 'CSV_Alias'
field_type = 'TEXT'
field_dict = {field:field_type}

check_fields(in_FC, field_dict)

update_roads_from_csv(CR_to_alias_dict, named_to_CR_dict, in_FC)









#with open('Alternate Road Names.csv', 'r') as csv_file:
 #   csv_reader = csv.reader(csv_file)

  #  for line in csv_reader:
   #     print(line)

