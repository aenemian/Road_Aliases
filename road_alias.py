import arcpy
import os
import csv
from nguid import getWorkspace, setWorkspace

setWorkspace(r'C:\Users\jroland\Documents\ArcGIS\Projects\Python Testing\Python Testing.gdb')

def CR_to_named_alias_dict(in_csv):
    """This function returns a dictionary of CR ####: Alias_name key value pairs"""
    CR_to_alias = {}

    with open(in_csv) as csv_file:
        csv_reader = csv.reader(csv_file)

        for line in csv_reader:
            CR_to_alias[line[0]] = line[1]

    return CR_to_alias

def named_alias_to_CR_dict(in_dict):
    """This function takes in a dictionary returned by CR_to_named_alias_dict
     and reverses the key value pairs into a dictionary of Road_name: CR Alias key value pairs"""
    #I should look at combining this function and the function above to return a tuple of dictionaries. Could
    #provide a more elegant solution
    alias_to_CR = {}
    for k,v in in_dict.items():
        alias_to_CR[v] = k

    return alias_to_CR

def update_roads_from_csv(in_dict_1, in_dict_2, in_FC):
    """This function takes in the returns of CR_to_named_alias_dict and named_alias_to_CR_dict and
    updates the field CSV_Alias for road centerline data if the county road name matches the CSV road name.
    If the CR #### is an alias and not the official name, the county road is added as the CSV_Alias."""

    road_name_field = 'Street'
    alias_field = 'CSV_Alias'
    fields = [road_name_field, alias_field]

    #key 1 = CR ####, value 1 = road alias
    for key, value in in_dict_1.items():
        with arcpy.da.UpdateCursor(in_FC, fields) as cursor:
            for row in cursor:
                match_string = row[0].strip()

                if match_string == key:
                    print(f'{key} matched')
                    print(f'adding alias {value} to {key}')
                    row[1] = value
                    cursor.updateRow(row)
                    input(' ')

    #key 2 = road name, value 2 = CR alias
    for key, value in in_dict_2.items():
        with arcpy.da.UpdateCursor(in_FC, fields) as cursor:
            for row in cursor:
                match_string = row[0].strip()

                if match_string == key:
                    print(f'{key} matched')
                    print(f'adding alias {value} to {key}')
                    row[1] = value
                    cursor.updateRow(row)
                    input(' ')

def match_single(known_match, in_FC):
    """This function is for testing arcpy matching with csv file strings"""

    fields = ['Street',]

    with arcpy.da.SearchCursor(in_FC, fields) as cursor:
        for row in cursor:
            #test whether whitespace is causing the issue
            compare_string = row[0].strip()
            if compare_string == known_match:
                print(f'{known_match} found and paired')
                input(' ')
            else:
                print(f'{known_match} could not be paired')

def check_fields(in_FC, in_fields_dict):
    """This function takes in a feature class and a dictionary of the form {field: fieldType}.
    If the any of the fields provided are not found within the feature class, they are added
    to the feature class. Returns True if all fields are already in the feature class (check_counter == 0) and
    False if any fields are added."""
    check_counter = 0

    for field, fieldType in in_fields_dict.items():
        if field not in arcpy.ListFields(in_FC):
            arcpy.AddField_management(in_FC, field, fieldType)
            print(f'Added field {field} to feature class {in_FC}')
            check_counter += 1
        else:
            print(f'Field {field} already in feature class {in_FC}')

    if check_counter == 0:
        return True
    else:
        return False

def create_road_tables(Roads_FC, Roads_Compare_FC):
    """This function is designed to take in two feature classes, one is our in-house roads data, the other is
    the TX_DoT roads, and returns a CSV file of the road names for each."""

    wkspace = getWorkspace()
    roads_out_table = 'Roads.csv'
    roads_out_path = r'C:\Users\jroland\Documents\ArcGIS\Projects\Python Testing\PyCharmScripts'
    TX_DoT_roads_out_table = 'TX_DoT_Roads.csv'
    TX_DoT_roads_out_path = roads_out_path

    #delete csv files if they already exist, handle error if file does not exist without exiting function
    if os.path.exists(os.path.join(roads_out_path, roads_out_table)):
        os.remove(os.path.join(roads_out_path, roads_out_table))

    if os.path.exists(os.path.join(TX_DoT_roads_out_path, TX_DoT_roads_out_table)):
        os.remove(os.path.join(TX_DoT_roads_out_path, TX_DoT_roads_out_table))

    #create and return tables
    roads_csv = arcpy.TableToTable_conversion(Roads_FC, roads_out_path, roads_out_table)
    TX_DoT_roads_csv = arcpy.TableToTable_conversion(Roads_Compare_FC, TX_DoT_roads_out_path,
                                                     TX_DoT_roads_out_table)
    return roads_csv, TX_DoT_roads_csv

def clean_road_tables(roads_csv, tx_dot_csv):
    """This function removes unnecessary header information and columns from csv files for simplifying
    road name comparisons. Returns cleaned csv table information. Uses csv DictReader and DictWriter methods
    for managing header information."""

    clean_road_csv = 'Roads_cleaned.csv'
    clean_tx_dot_csv = 'TX_DoT_Roads_cleaned.csv'
    roads_csv_name_field = ['Street']
    tx_dot_csv_name_field = ['MAP_LBL']
    hctx_abbrev = 'HCTX'
    tx_dot_abbrev = 'TXDOT'

    #delete and replace cleaned tables if they already exist
    try:
        os.remove(clean_road_csv)
        os.remove(clean_tx_dot_csv)
    except OSError:
        print('Cleaned CSV files do not yet exist. Creating now.')

    #get column headers from roads csv and use to write cleaned csv
    with open(roads_csv, 'r') as csv_file:
        print('Reading roads_csv')
        csv_reader = csv.DictReader(csv_file)

        #test to make sure lines are being read correctly passed
        # for line in csv_reader:
        #     print(line['Street'])

        with open(clean_road_csv, 'w', newline='') as new_csv_file:
            print('Writing cleaned_roads_csv')
            csv_writer = csv.DictWriter(new_csv_file, fieldnames=roads_csv_name_field, extrasaction='ignore')
            #write headers/fields
            csv_writer.writeheader()

            for row in csv_reader:
                csv_writer.writerow(row)

    #
    #
    # #get column headers for tx_dot_roads_csv and use to write cleaned csv
    # with open(tx_dot_csv, 'r') as csv_file_2:
    #     print('Reading tx_dot_csv')
    #     csv_reader = csv.DictReader(csv_file_2)
    #
    #     with open(clean_tx_dot_csv, 'w', newline='') as new_csv_file_2:
    #         print('Writing cleaned_tx_dot_csv')
    #         csv_writer = csv.DictWriter(new_csv_file_2, fieldnames=tx_dot_csv_name_field, extrasaction='ignore')
    #         csv_writer.writeheader()
    #
    #         for row in csv_reader:
    #             csv_writer.writerow(row)


def compare_road_tables(cleaned_roads_csv, cleaned_tx_dot_roads_csv):
    """This function takes in two CSV files containing the roads names for our in-house roads data and the
    TX_DOT_Roads data and creates a set of names for each table. The sets are then compared for symmetric
    difference, and returns a set of names that are in either table but not both. Returns a new csv file where
    Roads_CSV_set ^ TX_DoT_Roads_CSV_set, and the containing dataset indicated """

    roads_set = set()
    tx_dot_set = set()
    hctx_abbrev = 'HCTX'
    txdot_abbrev = 'TXDOT'
    hctx_compare_csv = 'HCTX_for_compare.csv'
    txdot_compare_csv = 'TXDOT_for_compare.csv'

    #open csv table and call next to get header line
    with open(cleaned_roads_csv, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        csv_header = next(csv_reader)

        for row in csv_reader:
            if row not in roads_set:
                roads_set.add(row)




def translate_road_names(road_string):
    """This function is utilized by the compare_road_tables function and searches for common differences in
    spelling that may arise from transcription errors or differences in standardization. It takes in a road
    name as a string, then checks as to whether there are standardization differences (County Road instead of CR, etc)
    and adjusts the name to match our in-house standard to allow for better matching and comparison. This function
    compares the full street name with suffix included. TX_DoT roads appear to use both CR and County Road and sometimes
    only a four digit number, but highways appear to be labeled only with a number."""
    pass

def select_single_road_UNUSED(in_FC, target_FC):
    """This function is a test function for developing a more complex function and takes in two feature classes.
    in_FC is the feature class table that we want to use to select features from the target_FC.
    This is intended to be used for identifying conflicts in road naming between two separate road feature classes. This
    function is intended to select only a single road from target_FC."""

    #Make sure any data locks are cleared
    if arcpy.Exists('PECAN_RD_TEST'):
        arcpy.Delete_management('PECAN_RD_TEST')
    if arcpy.Exists('TX_DOT_PECAN_RD_TEST'):
        arcpy.Delete_management('TX_DOT_PECAN_RD_TEST')

    #We will test on a single road, one that we know has a conflict - Pecan Rd / CR2928
    in_FC_road_field = 'Street'
    in_FC_selection_name = 'PECAN RD'

    in_FC_SQL_clause = """{0} = '{1}'""".format(arcpy.AddFieldDelimiters(in_FC, in_FC_road_field), in_FC_selection_name)

    #Create layer from where clause to use in select by location
    in_FC_road_layer = arcpy.MakeFeatureLayer_management(in_FC,'PECAN_RD_TEST',in_FC_SQL_clause)
    print(f'{in_FC_road_layer} layer successfully created')

    #Selection returns a layer, but we want to create a layer with a name that we can search for a delete
    #prior to running the function
    target_FC_road_selection = arcpy.SelectLayerByLocation_management(target_FC, 'WITHIN_A_DISTANCE', in_FC_road_layer,
                                                                  '3 METERS')

    target_FC_road_layer = arcpy.MakeFeatureLayer_management(target_FC_road_selection, 'TX_DOT_PECAN_RD_TEST')
    print(f'{target_FC_road_layer} layer successfully created')

    #get the number of road segments
    road_count = arcpy.GetCount_management(target_FC_road_layer)
    print(f'There are {road_count} number of street centerlines selected.')

def road_selection_test_BROKEN(in_FC, target_FC, buffer_distance):
    """This function is a step up from select_single_road. It loops through the parts of a road with a known
    naming conflict, Pecan Rd, and compares it to TX_DoT road that has a CR alias. selection is limited to one
    road segment with function limit_selection(). Function returns a dictionary where the key is the 9-1-1 road name and
    value is the conflicting TX_DOT name. Only conflicting names should be added. Currently selects way too many
    roads to be usable, need to implement limit selection, but also to get a better initial selection."""

    in_FC_search_field = ('Street',)
    target_FC_search_field = ('MAP_LBL',)
    name_conflict_dict = {}

    #loop through in FC
    with arcpy.da.SearchCursor(in_FC, in_FC_search_field) as cursor_1:
        for row in cursor_1:
            in_FC_road_name = row[0]
            near_selection = arcpy.SelectLayerByLocation_management(target_FC, 'WITHIN_A_DISTANCE', in_FC,
                                                                    buffer_distance)
            num_selected = int(arcpy.GetCount_management(near_selection).getOutput(0))
            print(f'Layer {near_selection} has been selected')
            print(f'{num_selected} number of road segments selected')

            while num_selected > 1:
                #buffer distance is a string of the type {number}{unit} so it needs to be converted to an integer
                limit_distance, limit_unit = buffer_distance.split()
                limit_distance = int(limit_distance)

                #if the buffer distance unit number is greater than 1, reduce that number by 1 and select again
                while limit_distance > 1:
                    limit_distance = limit_distance - 1
                    new_buffer_distance = str(limit_distance) + " " + limit_unit
                    near_selection = arcpy.SelectLayerByLocation_management(target_FC, 'WITHIN_A_DISTANCE', in_FC,
                                                                            new_buffer_distance)
                num_selected = int(arcpy.GetCount_management(near_selection).getOutput(0))
                print(f'{num_selected} number of road segments selected after limiting.')

                if limit_distance == 1:
                    print('Could not reduce to single road selection with buffer')
                    break

            #compare to target_FC road name - there has to be a better way to do this
            with arcpy.da.SearchCursor(near_selection, target_FC_search_field) as cursor_2:
                for row in cursor_2:
                    if row[0] != in_FC_road_name:
                        name_conflict_dict[in_FC_road_name] = row[0]
                        print(f'Name conflict between {in_FC_road_name} and {row[0]}')

    return name_conflict_dict




