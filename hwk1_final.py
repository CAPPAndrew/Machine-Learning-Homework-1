import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import requests

def street_address_form(row):
	if np.isnan(row['ADDRESS STREET NUMBER']):
		address_string = str((row['ADDRESS STREET NUMBER'])) + ' ' + str(row['ADDRESS STREET DIRECTION']) + ' ' + str(row['ADDRESS STREET NAME']) + ' ' + str(row['ADDRESS STREET SUFFIX'])
	else:
		address_string = str(int((row['ADDRESS STREET NUMBER']))) + ' ' + str(row['ADDRESS STREET DIRECTION']) + ' ' + str(row['ADDRESS STREET NAME']) + ' ' + str(row['ADDRESS STREET SUFFIX'])
	return address_string
	
def form_dataset():
	alley_lights_df = pd.read_csv("311_Service_Requests_-_Alley_Lights_Out.csv")
	graffiti_df = pd.read_csv("311_Service_Requests_-_Graffiti_Removal.csv")
	buildings_df = pd.read_csv("311_Service_Requests_-_Vacant_and_Abandoned_Buildings_Reported.csv")
	
	buildings_df.columns = ['Type of Service Request', 'Service Request Number', 'Creation Date', 'LOCATION OF BUILDING ON THE LOT (IF GARAGE, CHANGE TYPE CODE TO BGD).', 'IS THE BUILDING DANGEROUS OR HAZARDOUS?', 'IS BUILDING OPEN OR BOARDED?', 'IF THE BUILDING IS OPEN, WHERE IS THE ENTRY POINT?', 'IS THE BUILDING CURRENTLY VACANT OR OCCUPIED?', 'IS THE BUILDING VACANT DUE TO FIRE?', 'ANY PEOPLE USING PROPERTY? (HOMELESS, CHILDEN, GANGS)', 'ADDRESS STREET NUMBER', 'ADDRESS STREET DIRECTION', 'ADDRESS STREET NAME', 'ADDRESS STREET SUFFIX', 'Zip Code', 'X Coordinate', 'Y Coordinate', 'Ward', 'Police District', 'Community Area', 'Latitutde', 'Longitude', 'Location']
	buildings_df['Completion Date'] = buildings_df['Creation Date']
	buildings_df['Street Address'] = buildings_df.apply(lambda row:street_address_form(row), axis = 1)
	combined_df = pd.concat([alley_lights_df, graffiti_df, buildings_df], join = 'inner')
	combined_df2 = pd.concat([alley_lights_df, buildings_df], join = 'inner')

	return combined_df, combined_df2, alley_lights_df, graffiti_df, buildings_df

def date_rows(row):
	start_date = datetime.datetime.strptime(row['Creation Date'], '%m/%d/%Y')
	try:
		end_date = datetime.datetime.strptime(row['Completion Date'], '%m/%d/%Y')
	except TypeError:
		end_date = start_date
	difference_date = end_date - start_date
	response_time = difference_date.days
	
	return response_time

def form_tables(combined_df, alley_lights_df, graffiti_df, buildings_df):
	service_requests = combined_df['Type of Service Request'].unique()
	print(combined_df['Type of Service Request'].value_counts())
	type_df = combined_df['Type of Service Request'].value_counts()
	type_plot = type_df.plot(kind='bar', title ="V comp", figsize=(15, 10), legend=True, fontsize=12)
	plt.show()
		
	combined_df['Response Time'] = combined_df.apply(lambda row:date_rows(row), axis = 1)
			
	date_dict = {}
	location_dict = {}
	response_dict = {}
	community_dict = {}
	for x in service_requests:
		request_df = combined_df.loc[combined_df['Type of Service Request'] == x]
		date_dict[x] = request_df['Creation Date'].value_counts()
		location_dict[x] = request_df['Street Address'].value_counts()
		response_dict[x] = request_df['Response Time'].value_counts()
		community_dict[x] = request_df['Community Area'].value_counts()
		
	date_df = pd.DataFrame(data = date_dict)
	date_df = date_df.sort_values(by = ['Alley Light Out'], ascending = False)
	date_df.head(10).to_csv('alo_top_ten_dates.csv')
	date_df = date_df.sort_values(by = ['Graffiti Removal'], ascending = False)
	date_df.head(10).to_csv('gr_top_ten_dates.csv')
	date_df = date_df.sort_values(by = ['Vacant/Abandoned Building'], ascending = False)
	date_df.head(10).to_csv('vab_top_ten_dates.csv')
	
	location_df = pd.DataFrame(data = location_dict)	
	location_df.to_csv("Location.csv")
	
	location_df = location_df.sort_values(by = ['Alley Light Out'], ascending = False)
	location_df.head(10).to_csv('alo_top_ten_loc.csv')
	location_df = location_df.sort_values(by = ['Graffiti Removal'], ascending = False)
	location_df.head(10).to_csv('gr_top_ten_loc.csv')
	location_df = location_df.sort_values(by = ['Vacant/Abandoned Building'], ascending = False)
	location_df.head(10).to_csv('vab_top_ten_loc.csv')
	
	response_df = pd.DataFrame(data = response_dict)
	response_df = response_df.sort_values(by = ['Alley Light Out'], ascending = False)
	response_df.head(10).to_csv('alo_top_ten_re.csv')
	response_df = response_df.sort_values(by = ['Graffiti Removal'], ascending = False)
	response_df.head(10).to_csv('gr_top_ten_re.csv')
	response_df = response_df.sort_values(by = ['Vacant/Abandoned Building'], ascending = False)
	response_df.head(10).to_csv('vab_top_ten_re.csv')	
	
	community_df = pd.DataFrame(data = community_dict)
	community_df.to_csv("community.csv")

def start_days(row):
	start_days = datetime.datetime.strptime(row['Creation Date'], '%m/%d/%Y')
	
	return start_days

def block_find(row):	
	address_string = row["Street Address"]
	household_inc, black_estimate, white_estimate = address_lookup(address_string)	
	block_string = str(household_inc) + " " + str(black_estimate) + " " + str(white_estimate)
	
	return (block_string)

def block_split(row, indexer):
	blocks = row['Blocks']
	block_fragment = blocks.split()[indexer]
	
	return block_fragment

def block_retrieve(changed_df):
	changed_df['Creation Date in Days'] = changed_df.apply(lambda row:start_days(row), axis = 1)
	changed_df = changed_df.sort_values(by = ['Creation Date in Days'], ascending = False)
	shortened_df = changed_df.head(90)
		
	shortened_df['Blocks'] = shortened_df.apply(lambda row:block_find(row), axis = 1)
	shortened_df['Household Income in Past 12 Months'] = shortened_df.apply(lambda row:block_split(row, 0), axis = 1)
	shortened_df['Estimate of Black Population'] = shortened_df.apply(lambda row:block_split(row, 1), axis = 1)
	shortened_df['Estimate of White Population'] = shortened_df.apply(lambda row:block_split(row, 2), axis = 1)
	shortened_df.to_csv('block_info.csv')

	return shortened_df
	
def address_lookup(address_string):
	address_list = address_string.split()
	st_number = address_list[0]
	st_direction = address_list[1]
	st_address = address_list[2]
	st_suffix = address_list[3]
	address = 'https://geocoding.geo.census.gov/geocoder/geographies/address?street={}+{}+{}+{}&city=Chicago&state=IL&benchmark=4&vintage=410&format=json'.format(st_number, st_direction, st_address, st_suffix)

	json_results = requests.get(address)
	rv = json_results.json()
	try:
		blkgrp = rv['result']['addressMatches'][0]['geographies']['Census Blocks'][0]['BLKGRP']
		county = rv['result']['addressMatches'][0]['geographies']['Census Blocks'][0]['COUNTY']
		tract = rv['result']['addressMatches'][0]['geographies']['Census Blocks'][0]['TRACT']
		block_info = info_retrieve(blkgrp, county, tract)
	except KeyError:
		print("error")
		return (0,0,0)

	return block_info

def info_retrieve(blkgrp, county, tract):
	search_term = 'NAME,B19001_001E,B02009_001E,B02008_001E'
	key = '<Insert Key Here>'
	address = 'https://api.census.gov/data/2015/acs5?get={}&for=block+group:{}&in=state:17+county:{}+tract:{}&key={}'.format(search_term, blkgrp, county, tract, key)

	json_results = requests.get(address)
	json_dict = json_results.json()

	household_inc = json_dict[1][1]
	black_estimate = json_dict[1][2]
	white_estimate = json_dict[1][3]
	
	return household_inc, black_estimate, white_estimate

def run_homework():
	combined_df, combined_df2, alley_lights_df, graffiti_df, buildings_df = form_dataset()
	form_tables(combined_df, alley_lights_df, graffiti_df, buildings_df)
	changed_df = block_retrieve(combined_df2)