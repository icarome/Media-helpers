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


def log(message):
	home= os.getenv('HOME')
	arquivo=home+"/tvrenamer.log"
	logfile = open(arquivo, 'r')
	oldlog = logfile.read()
	newlog = oldlog + "-----------------------------------------------\n" + str(datetime.today().day) +"-"+ str(datetime.today().month)+"-"+ str(datetime.today().year)+"\t"+ str(datetime.today().hour) +":" + str(datetime.today().minute) +":" + str(datetime.today().second) +"\n" + message + "\n"
	logfile = open(arquivo, 'w')
	logfile.write(newlog)
	logfile.close()

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
   <value><string>pob</string></value>
  </param>
  <param>
   <value><string>SolEol 0.0.8</string></value>
  </param>
 </params>
</methodCall>"""
	headers = {'Content-Type': 'text/xml'}
	res = requests.post('http://api.opensubtitles.org/xml-rpc', data=xml, headers=headers).text
	#print res
	nres = res.split("\n")
	cont=0
	for var in nres:
		if '<name>status</name>' in var:
			op=nres[cont+2].replace('      <string>', '')
			status=op.replace('</string>', '')
			if status == '200 OK':
				tk=nres[cont-4].replace('      <string>', '')
				tk=tk.replace('</string>', '')
				return tk
				break
		cont=cont+1
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
	res = requests.post('http://api.opensubtitles.org/xml-rpc', data=xml, headers=headers).text
	#print res
	nres = res.split("\n")
	cont=0
	exit=0
	for var in nres:
		if '<name>SubDownloadLink</name>' in var:
			op=nres[cont+2].replace('            <string>', '')
			url=op.replace('</string>', '')
			file_name = name.replace('.mp4', '')
			u = urllib2.urlopen(url)
			f = open(file_name, 'wb')
			f.write(u.read())
			f.close()
			with gzip.open(file_name, 'rb') as f:
	   			srt = open(file_name+".srt", 'wb')
				srt.write(f.read())
				srt.close()
			os.remove(file_name)
			exit=1
			break
		cont=cont+1
	if exit==1:
		log("legenda salva como: " + file_name + ".srt")
	else:
		log("legenda não encontrada para " + name)

os.chdir("/media/Arquivos/Episódios")
address=os.listdir("/media/Arquivos/Episódios")
lugar="/media/Arquivos/Episódios"
while True:
	time.sleep(1)
	if len(address) == 0 and os.getcwd()!="/media/Arquivos/Episódios":
		torem=os.getcwd()
		#print "AquiQ"
		os.chdir("/media/Arquivos/Episódios")
		os.rmdir(torem)
		address=os.listdir("/media/Arquivos/Episódios")
		continue
	for arquivo in address:
		if os.path.isdir(arquivo):
			lugar=arquivo
			continue
		if not arquivo.lower().endswith(('.mp4', '.mkv', '.avi')):
			os.remove(arquivo)
			continue
		#if arquivo.count('/') > 1:
		arquivo=arquivo.split('/')
		dirw=arquivo[:len(arquivo)-1]
		dirw = str(dirw)
		dirw = dirw.replace("[\'", "/")
		dirw = dirw.replace("\', \'", "/")
		dirw = dirw.replace("\']", "/")
		dirw = dirw.replace("[]", "")
		arquivo=arquivo[len(arquivo)-1]
		if arquivo.count('.') > 1:
			string = arquivo.split('.')
		else:
			string = arquivo.split()
			aux=string[len(string)-1]
			string.pop(len(string)-1)
			string.extend(aux.split('.'))
		tam=len(string)
		codex=0
		if string[tam-1] == "mp4" or string[tam-1] == "mkv" or string[tam-1] == "avi" :
			codex=1
		if codex==0:
			continue
		if not os.path.exists(dirw + arquivo):
			log(arquivo + " não existe!\nVerifique a localização do arquivo e tente novamente.")
			continue
		path = "/media/Arquivos/icaronascimento/Series/"
		cont=0
		conttt=0
		flag=0
		seriename = []
		for var in string:
			##print var + " nada"
			if re.match("[a-zA-Z0-9]+$", var):
				seriename.append(string[conttt])
				##print seriename
			conttt=conttt+1
		for var in seriename:
			cont=cont+1
			if re.match("[A-z][0-9]", var):
				##print var
				break
			if re.match("[0-9]", var):
				flag=1		
				##print var
				break
		##print seriename[:cont-1]
		if flag==1:
			if len(string[cont-1][1:])>2:
				epi="E"+seriename[cont-1][2:]
				temp=" S"+seriename[cont-1][:2]
			else:
				epi="E"+seriename[cont-1][1:]
				temp=" S0"+seriename[cont-1][:1]
		else:
			epi=seriename[cont-1][3:].title()
			temp=" " +seriename[cont-1][:3].title()
		##print epi
		##print temp	
		t=Tvdb()
		oc=0
		h1 = str(seriename[:cont-1])
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
			##print arquivo
			shutil.move(arquivo, fl)
			download(fl)
			#sendmessage("TV Renamer", "Arquivo movido para " + fl)
			log("Arquivo movido para " + fl)
		else:
			log("Série não encontrada" + h1)
	#print os.getcwd()
	if os.path.isdir(lugar):
		os.chdir(lugar)
	address=os.listdir(os.getcwd())
