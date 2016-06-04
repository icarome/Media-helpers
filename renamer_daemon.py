#!/usr/bin/python
# -*- coding: utf-8 -*
import media_helpers as mh
import os
import shutil
import time
import re
from datetime import datetime
WATCH_FOLDER = '/media/Arquivos/Episódios'
END_FOLDER = '/media/Arquivos/icaronascimento/Series/' #The folder where the files renamed will be moved to following this standard: END_FOLDER/SERIES_NAME/SERIES_NAME S[SEASON]E[EPISODE].FILE_EXTENSION(mp4, avi or mkv)
SUB_LANG = 'pob' #opensubtitle language to search. ex: all, en, por, pob, esp, fr etc...
VIDEO_FILE_EXT=('.mp4', '.mkv', '.avi')
#------------------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------------------------#
#					Main
#------------------------------------------------------------------------------------------------#
os.chdir(WATCH_FOLDER)
list_of_files=os.listdir(WATCH_FOLDER)
watch_folder=WATCH_FOLDER
while True:
	try:
		time.sleep(1)
		if len(list_of_files) == 0 and os.getcwd()!=WATCH_FOLDER:
			to_remove=os.getcwd()
			os.chdir(WATCH_FOLDER)
			os.rmdir(to_remove)
			list_of_files=os.listdir(WATCH_FOLDER)
			continue
		for working_file in list_of_files:
			if os.path.isdir(working_file):
				watch_folder=working_file
				continue
			if not working_file.lower().endswith(VIDEO_FILE_EXT):
				os.remove(working_file)
				continue
			f_path=mh.get_path(working_file)[0]
			working_file=mh.get_path(working_file)[1]
			if working_file.count('.') > 1:
				string = working_file.split('.')
			else:
				string = working_file.split()
				file_ext=string[-1]
				string.pop(-1)
				string.extend(file_ext.split('.'))
			if not os.path.exists(f_path + working_file):
				mh.log("{0}\tMain: {1} não existe!\nVerifique a localização do arquivo e tente novamente.".format(str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second), working_file))
				continue
			mh.log("{0}\tmain: {1} encontrado. Organizando agora".format(str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second), working_file))
			path = END_FOLDER
			i=0
			flag=0
			seriename = []
			for var in string:
				if re.match("[a-zA-Z0-9]+$", var):
					seriename.append(var)
			for var in seriename:
				i=i+1
				if re.match("[A-z][0-9]", var):
					break
				if re.match("[0-9]", var):
					flag=1
					break
			if flag==1:
				if len(string[i-1][1:])>2:
					epi="E"+seriename[i-1][2:]
					temp=" S"+seriename[i-1][:2]
				else:
					epi="E"+seriename[i-1][1:]
					temp=" S0"+seriename[i-1][:1]
			else:
				epi=seriename[i-1][3:].title()
				temp=" "+seriename[i-1][:3].title()
			seriename = mh.str_build(seriename[:i-1])
			serie=mh.conf_name(seriename)
			file_name=serie+temp+epi+"."+string[-1]
			file_wd=path+serie+"/"
			file_location=file_wd+file_name
			if not os.path.exists(file_wd):
			       	os.makedirs(file_wd)
			if mh.file_not_in_use(working_file):
				shutil.move(working_file, file_location)
				mh.log("{0}\tMain: Arquivo movido para {1}".format(str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second), file_location))
				mh.download(file_location, SUB_LANG)
		if os.path.isdir(watch_folder):
			os.chdir(watch_folder)
		list_of_files=os.listdir(os.getcwd())
	except KeyboardInterrupt:
		print "Encerrando..."
		time.sleep(0.5)		
		exit()
