import itertools as it
import re
import json
import os
import sys

cwd = os.getcwd()
#sys.exit(0)

# Name of outputted file
output_file = 'newfile.m3u'

# If you want to change the name of a category, ex: "Religion-News" becomes just "News"
category_replacements = {
	'Undefined': '~Misc',
	'General;News': 'News',
	'Culture;News': 'News',
	'Culture;Music': 'Music',
	'Animation;Kids': 'Kids',
	'Entertainment;Family;General': '~Misc',
	'Animation;Kids;Religious': 'Religious',
	'Music;Religious': 'Religious',
	'Education;Kids': 'Kids',
	'Movies;Religious': 'Religious',
	'General;Religious': 'Religious',
	'Relax': 'Outdoor/Travel',
	'Outdoor': 'Outdoor/Travel',
	'Travel': 'Outdoor/Travel',
	'Entertainment;Travel': 'Outdoor/Travel',
	'Auto;Series': 'Auto',
	'Kids;Religious': 'Religious',
	'Culture;Education': 'Culture',
	'Shop;Travel': 'Outdoor/Travel',
	'Education;General': 'Education',
	'Lifestyle;Religious': 'Religious',
	'Entertainment;News': 'News', 
	'Lifestyle;Shop': 'Shop',
	'Auto;Travel': 'Outdoor/Travel',
	'Movies;Series': 'Movies',
	'Cooking;Shop': 'Cooking',
	'Education;Outdoor': 'Outdoor/Travel',
	'Outdoor;Travel': 'Outdoor/Travel',
	'Family;Movies': 'Movies',
	'Animation;Classic': 'Animation',
	'Entertainment;Sports': 'Sports',
	'News;Sports': 'Sports',
	'Culture;Family': 'Culture',
	'Culture;Religious': 'Religious',
	'News;Religious': 'News',
	'Documentary;News': 'News',
	'Documentary;Entertainment': 'Documentary',
	'Auto;Entertainment': 'Auto',
	'Education;Legislative': 'Legislative',
	'Documentary;Entertainment;News': 'News',
	'Culture;Documentary;Entertainment;General;Movies;Music': 'Culture',
	'Business;News': 'News',
	'Entertainment;Music': 'Music',
	'Music;News': 'Music',
	'Culture;Entertainment': 'Entertainment',
	'Documentary;Science': 'Documentary',
	'Classic;Movies': 'Movies'
}
# If you want to change the category for a specific channel link
link_category_replacements = {
'http://cfd-v4-service-channel-stitcher-use1-1.prd.pluto.tv/stitch/hls/channel/62ea4b755e8e770007387b79/master.m3u8?appName=web&appVersion=unknown&clientTime=0&deviceDNT=0&deviceId=2c7c9e97-35fc-11ef-a031-2b5d494037a2&deviceMake=Chrome&deviceModel=web&deviceType=web&deviceVersion=unknown&includeExtendedEvents=false&serverSideAds=false&sid=14cdb377-9292-4d37-85af-4d89aff56e90': 'world poker category'
}


# If you want to add a prefix/suffix to the channel names from specific files
file_name_changes = {
	'ca.m3u': {
		'prefix': '(CA) ',

		'suffix': ' (ENG)'
	},
	'sv.m3u': {
		'prefix': '(SV) ',

		'suffix': ' (ESP)'
	},
	'eng.m3u': {
		'prefix': '(ENG) ',

		'suffix': ''
	},
	'spa.m3u': {
		'prefix': '(SPA) ',

		'suffix': ''
	},
}


#### Internal Stuff #####

# Regex for searching
name_search = r"(?<=\",)(.*?)(?=\n)" # Regex used for finding the channel names from the m3u file
category_search = r"(?<=group-title=\")(.*)(?=\")" # Regex used for finding the category name for a channel

# Internal variables
current_string = ''
all_strings = []
skip_item = False

filenames = next(os.walk(os.path.join(cwd, 'add')), (None, None, []))[2]  # [] if no file
addition_files = list(map(lambda x: os.path.join(cwd, 'add', x), filenames))

filenames = next(os.walk(os.path.join(cwd, 'remove')), (None, None, []))[2]  # [] if no file
removal_files = list(map(lambda x: os.path.join(cwd, 'remove', x), filenames))
removal_links = []



for file_name in removal_files:
	with (open(file_name, 'r')) as f:
		for key,group in it.groupby(f, lambda line: line.startswith('http')):
			if key:
				removal_links.append(''.join(list(group)).strip())


for file_name in addition_files:
	current_file_base = os.path.basename(file_name)
	with (open(file_name, 'r')) as f:
		category_name = ''
		for key,group in it.groupby(f, lambda line: line.startswith('#EXTINF')):
			# if it doesn't begin with the #EXTINF, it should continue adding to the string
			if not key:
				temp_string = ''.join(list(group))

				if temp_string.strip() in '#EXTM3U':
					skip_item = True
				if temp_string.strip() in removal_links:
					skip_item = True
				if temp_string.strip() in link_category_replacements:
					current_string = re.sub(category_name, link_category_replacements[temp_string.strip()], current_string, 1)

				current_string+= temp_string
				

			# otherwise it's a new entry and it should reset the string building
			else:
				if not skip_item:
					if current_string not in all_strings:
						all_strings.append(current_string)
				skip_item = False
				processed_string = ''.join(list(group))

				# checks to see if any changes are needed to the channel name
				channel_name = re.search(name_search, processed_string)
				if channel_name is not None and current_file_base in file_name_changes:
					channel_name = channel_name.group()
					new_channel_name = file_name_changes[current_file_base]['prefix'] + channel_name + file_name_changes[current_file_base]['suffix']
					processed_string = processed_string.replace(channel_name, new_channel_name)

				# searches to see if any category names need to be replaced and replaces them
				regex_result = re.search(category_search, processed_string)
				if regex_result is not None:
					category_name = regex_result.group()
					# replaces the first occurence of the title if its in the replacement dictionary
					if category_name in category_replacements:
						processed_string = re.sub(category_name, category_replacements[category_name], processed_string, 1)
				current_string = processed_string

		if current_string not in all_strings and not skip_item:
						all_strings.append(current_string)
			

all_strings.insert(0, '#EXTM3U\n')

# writes the new playlist to a file
with open(output_file, "w") as txt_file:
	for line in all_strings:
		txt_file.write("".join(line))
