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
import xml.etree.ElementTree as ET
#------------------------------------------------------------------------------------------------#

def log(message):
	home= os.getenv('HOME')
	working_file=home+"/tvrenamer.log"
	if os.path.exists(home+"/tvrenamer.log"):
		logfile = open(working_file, 'r+')
		oldlog = logfile.read()
	else:
		oldlog = '#Logfile TV Renamer\n'
	newlog = oldlog + "-----------------------------------------------\n" + str(datetime.today().day) +"-"+ str(datetime.today().month)+"-"+ str(datetime.today().year)+"\t"+ str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second) +"\n" + message + "\n"
	logfile = open(working_file, 'w+')
	logfile.write(newlog)
	logfile.close()
	print message

#------------------------------------------------------------------------------------------------#
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

#------------------------------------------------------------------------------------------------#

def str_build(lista):
	string = ''
	for word in lista:
		string = string + ' ' + word
	return string[1:]
#------------------------------------------------------------------------------------------------#

def conf_name(name):
	a = 'http://thetvdb.com/api/GetSeries.php?seriesname='
	b = urllib2.quote(name)
	data = a + b
	i=0
	while i<3:
		try:
			answer = urllib2.urlopen(data).read()
			i=0
			break
		except urllib2.URLError:
			i+=1
			log("{0}\tconf_name: Erro de conexão com internet. Tentativa {1} de 3".format(str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second), i))
	if i==3:		
		return name
	new_answer = answer
	out = ''
	exit = 0
	root = ET.fromstring(new_answer)
	for n in root.iter('SeriesName'):
		out = n.text
	return out

#------------------------------------------------------------------------------------------------#



def file_not_in_use(f_to_test):
	size = os.stat(f_to_test).st_size
	time.sleep(1)
	d_size = os.stat(f_to_test).st_size
	while d_size != size:
		size = os.stat(f_to_test).st_size
		time.sleep(1)
		d_size = os.stat(f_to_test).st_size
	return True

#------------------------------------------------------------------------------------------------#

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

#------------------------------------------------------------------------------------------------#

def get_token(sub_lang):
	xml = """<?xml version="1.0"?>\n<methodCall>\n\t<methodName>LogIn</methodName>\n
\t<params>\n\t\t<param>\n\t\t\t<value><string></string></value>\n\t\t</param>\n\t\t<param>\n\t\t\t<value><string></string></value>\n
\t\t</param>\n\t\t<param>\n\t\t\t<value><string>"""+ sub_lang + """</string></value>\n\t\t</param>\n\t\t<param>\n\t\t\t<value><string>SolEol 0.0.8</string></value>\n\t\t</param>\n\t</params>\n</methodCall>"""
	headers = {'Content-Type': 'text/xml'}
	answer = urllib2.Request('http://api.opensubtitles.org/xml-rpc', data=xml, headers=headers)
	i=0
	while i<3:
		try:
			answer = urllib2.urlopen(answer)
			answer = answer.read()
			i=0
			break
		except urllib2.URLError:
			i+=1
			log("{0}\tget_token: Erro ao adquirir token {1} de 3. Tentando novamente.".format(str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second), i))
			time.sleep(0.5)
	if i == 3:	
		return -1
	new_answer = answer
	i=0
	root = ET.fromstring(new_answer)
	for n in root.iter('member'):
		if n.find('name').text == 'token':
			token = n.find('value').find('string').text
			log("{0}\tget_token: Token adiquirido com sucesso".format(str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second)))
			return token
		i=i+1

#------------------------------------------------------------------------------------------------#

def download(name, lang):
	log("{1}\tdownload: Baixando legenda para {0}".format(name, str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second)))
	token=get_token(lang)
	hash_file=hashFile(name)
	if token == -1:
		log("{0}\tdownlod: Falha ao adquirir token.".format(str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second)))
		return -1
	xml = """<?xml version="1.0"?>\n<methodCall>\n\t<methodName>SearchSubtitles</methodName>\n\t<params>\n\t\t<param>\n\t\t\t<value><string>"""+token+"""</string></value>\n\t\t</param>\n\t\t<param>\n\t\t\t<value>\n\t\t\t\t<array>\n\t\t\t\t\t<data>\n\t\t\t\t\t\t<value>\n\t\t\t\t\t\t\t<struct>\n\t\t\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t\t\t<name>sublanguageid</name>\n\t\t\t\t\t\t\t\t\t\t<value><string>pob</string></value>\n\t\t\t\t\t\t\t\t</member>\n\t\t\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t\t\t<name>moviehash</name>\n\t\t\t\t\t\t\t\t\t\t<value><string>"""+hash_file+"""</string></value>\n\t\t\t\t\t\t\t\t</member>\n\t\t\t\t\t\t\t</struct>\n\t\t\t\t\t\t</value>\n\t\t\t\t\t</data>\n\t\t\t\t</array>\n\t\t\t</value>\n\t\t</param>\n\t</params>\n</methodCall>"""
	headers = {'Content-Type': 'text/xml'}
	answer = urllib2.Request('http://api.opensubtitles.org/xml-rpc', data=xml, headers=headers)
	i=0
	while i<3:
		try:
			answer = urllib2.urlopen(answer).read()
			break
		except urllib2.URLError:
			i+=1
			log("{0}\tdownload: Erro ao buscar legenda {1} de 3. Tentando novamente em 2 segundos...".format(str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second), i))
			time.sleep(2)
			continue
	new_answer = answer
	i=0
	exit=0
	root = ET.fromstring(new_answer)
	for n in root.iter('member'):
		if n.find('name').text == 'SubDownloadLink':
			url = n.find('value').find('string').text
			file_name = name[:-4]
			i=0			
			while i<3:
				try:			
					download = urllib2.urlopen(url)
					break
				except urllib2.URLError:
					i+=1
					log("{0}\tdownload: Erro ao baixar legenda. Tentativa {1} de 3".format(str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second), i))
					time.sleep(1)
					continue
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
		log("{0}\tdownload: Legenda salva como: {1}.srt".format(str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second), file_name))
	else:
		log("{0}\tdownload: Não foi possível baixar legenda para: {1}".format(str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second), name))
