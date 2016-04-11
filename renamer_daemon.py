#!/usr/bin/python
# -*- coding: utf-8 -*
import sys
import os
import re
from tvdb_api import Tvdb
from tvdb_exceptions import tvdb_shownotfound
import array
import shutil
from datetime import datetime
import time
from subprocess import Popen, PIPE
import requests
import urllib2
import gzip
import struct
WATCH_FOLDER = '/path/to/folder/'
END_FOLDER = '/path/to/file/renamed' #The folder where the files renamed will be moved to following this standard: END_FOLDER/SERIES_NAME/SERIES_NAME S[SEASON]E[EPISODE].FILE_EXTENSION(mp4, avi or mkv)
SUB_LANG = 'pob' #opensubtitle language to search. ex: all, en, por, pob, esp, fr etc...

def path(path_string):
	path_string=path_string.split('/')
	path_list=path_string[:len(path_string)-1]
	new_path_string=''
	for folder in path_list[1:]:
		new_path_string=new_path_string + '/' + folder
	out=[new_path_string + '/', path_string[:len(path_string)]]
	return out


def log(message):
	home= os.getenv('HOME')
	if os.path.exists(home+"/tvrenamer.log"):
		working_file=home+"/tvrenamer.log"
		logfile = open(working_file, 'w+')
		oldlog = logfile.read()
	else:
		oldlog = '#Logfile TV Renamer\n'
	newlog = oldlog + "-----------------------------------------------\n" + str(datetime.today().day) +"-"+ str(datetime.today().month)+"-"+ str(datetime.today().year)+"\t"+ str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second) +"\n" + message + "\n"
	logfile = open(working_file, 'w')
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
	xml = """<?xml version="1.0"?>
<methodCall>
 <methodName>LogIn</methodName>
 <params>
  <param>
   <value><string></string></value>
  </param>
  <param>
   <value><string></string></value>
  </param>
  <param>
   <value><string>"""+ SUB_LANG + """</string></value>
  </param>
  <param>
   <value><string>SolEol 0.0.8</string></value>
  </param>
 </params>
</methodCall>"""
	headers = {'Content-Type': 'text/xml'}
	answer = requests.post('http://api.opensubtitles.org/xml-rpc', data=xml, headers=headers).text
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
	xml = """<?xml version="1.0"?>
<methodCall>
 <methodName>SearchSubtitles</methodName>
 <params>
  <param>
   <value><string>"""+get_token()+"""</string></value>
  </param>
  <param>
   <value>
    <array>
     <data>
      <value>
       <struct>
        <member>
         <name>sublanguageid</name>
         <value><string>pob</string>
         </value>
        </member>
        <member>
         <name>moviehash</name>
         <value><string>"""+hashFile(name)+"""</string></value>
        </member>
       </struct>
      </value>
     </data>
    </array>
   </value>
  </param>
 </params>
</methodCall>"""
	headers = {'Content-Type': 'text/xml'}
	answer = requests.post('http://api.opensubtitles.org/xml-rpc', data=xml, headers=headers).text
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
		f_path=path(working_file)[0]
		working_file=path(working_file)[1]
		if working_file.count('.') > 1:
			string = working_file.split('.')
		else:
			string = working_file.split()
			aux=string[len(string)-1]
			string.pop(len(string)-1)
			string.extend(aux.split('.'))
		tam=len(string)
		codex=0
		if string[tam-1] == "mp4" or string[tam-1] == "mkv" or string[tam-1] == "avi" :
			codex=1
		if codex==0:
			continue
		if not os.path.exists(dirw + working_file):
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
		##print epi
		##print temp	
		t=Tvdb()
		oc=0
		h1 = str(seriename[:i-1])
		h1 = h1.replace("[\'", "")
		h1 = h1.replace("\', \'", " ")
		h1 = h1.replace("\']", "")
		##print h1
		try:
			serie=t.search(h1)
			a=1
		except tvdb_shownotfound:
			a=0
		oc=oc+1
		if len(serie)>=1:
			sn=serie[0]['seriesname'] + temp + epi +"."+string[tam-1]
			exit=0
			d=path+serie[0]['seriesname']+"/"
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
