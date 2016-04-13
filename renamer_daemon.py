#!/usr/bin/python
# -*- coding: utf-8 -*
import sys
import os
import re
import array
import shutil
from datetime import datetime
import time
from subprocess import Popen, PIPE
import urllib2
import gzip
import struct
WATCH_FOLDER = '/path/to/folder'
END_FOLDER = '/path/to/folder/' #The folder where the files renamed will be moved to following this standard: END_FOLDER/SERIES_NAME/SERIES_NAME S[SEASON]E[EPISODE].FILE_EXTENSION(mp4, avi or mkv)
SUB_LANG = 'pob' #opensubtitle language to search. ex: all, en, por, pob, esp, fr etc...

def get_path(path_string):
		path_string=path_string.split('/')
		path_list=path_string[:len(path_string)-1]
		out=[]
		if not path_list:
			path=os.getcwd() + '/'
			filename=path_string[-1]
		else:
			new_path_string=[]
			for folder in path_list:
				if folder=='':
					out.extend(['/'])
					continue
				else:
					out.extend([folder])
			path = ''
			for folder in out:
				if not folder == '/':			
					path=path + folder + '/'
				else:
					path=path + folder
			filename=path_string[-1]
		return [path, filename]

def conf_name(name):
	a = 'http://thetvdb.com/api/GetSeries.php?seriesname='
	b = urllib2.quote(name)
	data = a + b
	answer = urllib2.urlopen(data).read()
	new_answer = answer.split("\n")
	out = ''
	exit = 0
	for line in new_answer:
		if '<SeriesName>' in line:
	        	for l in line[12:]:
			      	if not '<' in l:
	                		out = out + l
	        		else:
	                        	exit=1
	                             	break
	             	if exit == 1:
	                	break
		
	return out


def log(message):
	home= os.getenv('HOME')
	if os.path.exists(home+"/tvrenamer.log"):
		working_file=home+"/tvrenamer.log"
		logfile = open(working_file, 'r+')
		oldlog = logfile.read()
	else:
		oldlog = '#Logfile TV Renamer\n'
	newlog = oldlog + "-----------------------------------------------\n" + str(datetime.today().day) +"-"+ str(datetime.today().month)+"-"+ str(datetime.today().year)+"\t"+ str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second) +"\n" + message + "\n"
	logfile = open(working_file, 'w+')
	logfile.write(newlog)
	logfile.close()

def file_not_in_use(f_to_test):
	size = os.stat(f_to_test).st_size
	time.sleep(1)
	d_size = os.stat(f_to_test).st_size
	while d_size != size:
		size = os.stat(f_to_test).st_size
		time.sleep(1)
		d_size = os.stat(f_to_test).st_size
	return True

def hashFile(name): 
      try: 
                 
                longlongformat = '<q'  # little-endian long long
                bytesize = struct.calcsize(longlongformat) 
                    
                f = open(name, "rb") 
                    
                filesize = os.path.getsize(name) 
                hash = filesize 
                    
                if filesize < 65536 * 2: 
                       return "SizeError" 
                 
                for x in range(65536/bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  
                         
    
                f.seek(max(0,filesize-65536),0) 
                for x in range(65536/bytesize): 
                        buffer = f.read(bytesize) 
                        (l_value,)= struct.unpack(longlongformat, buffer)  
                        hash += l_value 
                        hash = hash & 0xFFFFFFFFFFFFFFFF 
                 
                f.close() 
                returnedhash =  "%016x" % hash 
                return returnedhash 
    
      except(IOError): 
                return "IOError"

def get_token():
	xml = """<?xml version="1.0"?>\n<methodCall>\n\t<methodName>LogIn</methodName>\n
\t<params>\n\t\t<param>\n\t\t\t<value><string></string></value>\n\t\t</param>\n\t\t<param>\n\t\t\t<value><string></string></value>\n
\t\t</param>\n\t\t<param>\n\t\t\t<value><string>"""+ SUB_LANG + """</string></value>\n\t\t</param>\n\t\t<param>\n\t\t\t<value><string>SolEol 0.0.8</string></value>\n\t\t</param>\n\t</params>\n</methodCall>"""
	headers = {'Content-Type': 'text/xml'}
	answer = urllib2.Request('http://api.opensubtitles.org/xml-rpc', data=xml, headers=headers)
	answer = urllib2.urlopen(answer)
	answer = answer.read()
	new_answer = answer.split("\n")
	i=0
	for var in new_answer:
		if '<name>status</name>' in var:
			output=new_answer[i+2].replace('      <string>', '')
			status=output.replace('</string>', '')
			if status == '200 OK':
				token=new_answer[i-4].replace('      <string>', '')
				token=token.replace('</string>', '')
				return token
				break
		i=i+1


def download(name):
	xml = """<?xml version="1.0"?>\n<methodCall>\n\t<methodName>SearchSubtitles</methodName>\n\t<params>\n\t\t<param>\n\t\t\t<value><string>"""+get_token()+"""</string></value>\n\t\t</param>\n\t\t<param>\n\t\t\t<value>\n\t\t\t\t<array>\n\t\t\t\t\t<data>\n\t\t\t\t\t\t<value>\n\t\t\t\t\t\t\t<struct>\n\t\t\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t\t\t<name>sublanguageid</name>\n\t\t\t\t\t\t\t\t\t\t<value><string>pob</string></value>\n\t\t\t\t\t\t\t\t</member>\n\t\t\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t\t\t<name>moviehash</name>\n\t\t\t\t\t\t\t\t\t\t<value><string>"""+hashFile(name)+"""</string></value>\n\t\t\t\t\t\t\t\t</member>\n\t\t\t\t\t\t\t</struct>\n\t\t\t\t\t\t</value>\n\t\t\t\t\t</data>\n\t\t\t\t</array>\n\t\t\t</value>\n\t\t</param>\n\t</params>\n</methodCall>"""
	headers = {'Content-Type': 'text/xml'}
	answer = urllib2.Request('http://api.opensubtitles.org/xml-rpc', data=xml, headers=headers)
	answer = urllib2.urlopen(answer).read()
	new_answer = answer.split("\n")
	i=0
	exit=0
	for var in new_answer:
		if '<name>SubDownloadLink</name>' in var:
			output=new_answer[i+2].replace('            <string>', '')
			url=output.replace('</string>', '')
			file_name = name.replace('.mp4', '')
			download = urllib2.urlopen(url)
			download_file = open(file_name, 'wb')
			download_file.write(download.read())
			download_file.close()
			with gzip.open(file_name, 'rb') as f:
	   			srt = open(file_name + ".srt", 'wb')
				srt.write(f.read())
				srt.close()
			os.remove(file_name)
			exit=1
			break
		i=i+1
	if exit==1:
		log("Subtitle saved as: " + file_name + ".srt")
	else:
		log("No subtitle found for " + name)


os.chdir(WATCH_FOLDER)
list_of_files=os.listdir(WATCH_FOLDER)
watch_folder=WATCH_FOLDER
while True:
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
		if not working_file.lower().endswith(('.mp4', '.mkv', '.avi')):
			os.remove(working_file)
			continue
		f_path=get_path(working_file)[0]
		#if f_path == '/':
		#	f_path=''
		working_file=get_path(working_file)[1]
		#print working_file
		if working_file.count('.') > 1:
			string = working_file.split('.')
		else:
			string = working_file.split()
			file_ext=string[-1]
			string.pop(-1)
			string.extend(file_ext.split('.'))
		
		codex=0
		if string[-1] == "mp4" or string[-1] == "mkv" or string[-1] == "avi" :
			codex=1
		if codex==0:
			continue
		if not os.path.exists(f_path + working_file):
			log(working_file + " não existe!\nVerifique a localização do arquivo e tente novamente.")
			continue
		path = END_FOLDER
		i=0
		i2=0
		flag=0
		seriename = []
		for var in string:
			##print var + " nada"
			if re.match("[a-zA-Z0-9]+$", var):
				seriename.append(string[i2])
				##print seriename
			i2=i2+1
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
			temp=" " +seriename[i-1][:3].title()
		h1 = str(seriename[:i-1])
		h1 = h1.replace("[\'", "")
		h1 = h1.replace("\', \'", " ")
		h1 = h1.replace("\']", "")
		serie=conf_name(h1)
		if len(serie)>=1:
			sn=serie + temp + epi +"."+string[-1]
			exit=0
			d=path+serie+"/"
			fl=d+sn
		    	if not os.path.exists(d):
		        	os.makedirs(d)
			if file_not_in_use(working_file):
				shutil.move(working_file, fl)
				download(fl)
			log("Arquivo movido para " + fl)
		else:
			log("Série não encontrada" + h1)
	if os.path.isdir(watch_folder):
		os.chdir(watch_folder)
	list_of_files=os.listdir(os.getcwd())
