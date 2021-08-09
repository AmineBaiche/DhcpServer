#!/usr/bin/python
#-*-coding:Latin-1 -*

import sys, getopt
import fileinput
import os
from socket import *
import yaml
import os.path
import configparser # Permet de parser le fichier de paramètres


###########	remplace des éléments	###########
def replaceAll(file,searchExp,replaceExp):
    for line in fileinput.input(file, inplace=1):
        if searchExp in line:
            line = line.replace(searchExp,replaceExp)
        sys.stdout.write(line)

###########	DHCP	###########
		
def dhcp_conf(server_name,subnet_mask,domain,option_dns,sous_res,interfaces,leasetime,Deny_unknown,dhcp_ip):
	os.system("apt-get install isc-dhcp-server")

	fichier = open("/etc/dhcp/dhcpd.conf","w")
	fichier.write("##### Option générale par défaut #####\n")
	fichier.write("\n### RÉSEAU #####\n")
	fichier.write("\nserver-name \""+server_name+"\";") #nom du serveur dns
	fichier.write("\nauthoritative;")
	fichier.write("\noption subnet-mask "+subnet_mask+";")
	fichier.write("\noption domain-name \""+ domain +"\";")
	fichier.write("\noption domain-name-servers "+ option_dns +";")
	fichier.write("\nddns-update-style none;")
	fichier.write("\ndefault-lease-time 3600;")
	fichier.write("\nmax-lease-time "+ leasetime + ";")
	fichier.write("\nlog-facility local7;\n")
	if Deny_unknown == "yes" :
		fichier.write("deny unknown-clients ;")
		print ( "seul les clients dans le fichier de configuration se verront attribuer une addresse " )
	
	

 
	
###########	sous reseaux	###########
	
	def Mac_filter(client ,mac, ip):
		fichier.write("\nhost "+client+" {")
		fichier.write("\n  hardware ethernet " +mac+";")
		fichier.write("\n  fixed-address " +ip+";")
		fichier.write("\n}\n")
		print ( " client1 configure")
	
		
	fichier.write("\n##### RÉSEAUX #####\n")
	fichier.write("\n## Déclaration sous réseaux")


	config = configparser.RawConfigParser() # On créé un nouvel objet "config"
	config.read('config.ini')

	i=0
	for i in range(0,sous_res):

		reseau = str("reseau"+str(i))
		subnet = config.get(reseau,'subnet')
		netmask = config.get(reseau,'netmask')
		broadcast = config.get(reseau,'broadcast')
		ntp = config.get(reseau,'ntp')
		routers = config.get(reseau,'routers')
		pool = config.get(reseau,'pool')
		client1 = config.get(reseau,'client1')
		client1_mac = config.get(reseau,'client1_mac')
		client1_ip = config.get(reseau,'client1_ip')
		client2 = config.get(reseau,'client2')
		client2_mac = config.get(reseau,'client2_mac')
		client2_ip = config.get(reseau,'client2_ip')
		client3 = config.get(reseau,'client3')
		client3_mac = config.get(reseau,'client3_mac')
		client3_ip = config.get(reseau,'client3_ip')
		fichier.write("\nsubnet "+subnet+" netmask "+netmask+" {")		
		fichier.write("\n  option domain-name \""+domain+"\";")
		fichier.write("\n  option broadcast-address "+broadcast+";")
		fichier.write("\n  option ntp-servers "+ntp+";")
		fichier.write("\n  option routers "+routers+";")
		fichier.write("\n  range "+pool+";")
		fichier.write("\n  ping-check = 1;")
		

        
		if not client1 :
			print (" aucun filtrage mac saisie" )
		else : 
			s=Mac_filter(client1,client1_mac,client1_ip)
			print (" le client",client1,"va recevoir l' adresse ip suivante :",client1_ip )       
		if not client2 :
			print (" pas de filtrage mac saisie pour client2" )
		else : 
			print (" le client",client2,"va recevoir l' adresse ip suivante :",client2_ip )  			
			s=Mac_filter(client2,client2_mac,client2_ip) 
		if not client3 :
			print (" pas de filtrage mac saisie pour client3" )
		else :
			print (" le client",client3,"va recevoir l' adresse ip suivante :",client3_ip )  
			s=Mac_filter(client3,client3_mac,client3_ip) 
	
		fichier.write("\n}\n")
	
	fichier.close()

	replaceAll("/etc/default/isc-dhcp-server","INTERFACESv4=\"\"","INTERFACESv4=\""+interfaces+"\"")
	os.system("ifconfig "+interfaces +" inet "+ dhcp_ip+" netmask "+subnet_mask)
	os.system("service isc-dhcp-server restart")
	os.system("service isc-dhcp-server status | grep 'Active'" )
	os.system("watch -n 1 dhcp-lease-list") 


###########	main	###########
def main(argv):

   ip = ''
   server_name = ''
   subnet_mask = ''
   option_dns = ''
   sous_res = ''
   interfaces = ''
   leasetime = ''
   Deny_unknown = ''
   dhcp_ip = ''
  		
    

   try:
      opts, args = getopt.getopt(argv,"hid:a:n:m:o:r:f:",["domain=","addr=","name=","mask=","optdns=","reseau=","interfaces="])
   except getopt.GetoptError:
      print ('dhcp_dns.py -i pour le mode interactif ou dhcp_dns.py -d <domain> -a <addr ip> -n <server name> -m <subnet mask> -o <option dns> -r <nb sous res> --interfaces="interface1 interface2 or_more"')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('dhcp_dns.py -i mode interactif ou dhcp_dns.py -d <domain> -a <addr ip> -n <server name> -l <maxleasetime> -b <ipdhcp> -m <subnet mask> -o <option dns> -r <nb sous res> --interfaces="interface1 interface2 or_more"')
         sys.exit()
      elif opt in ("-d", "--domain"):
         domain = arg
      elif opt in ("-a", "--addr"):
         ip = arg
      elif opt in ("-n", "--name"):
         server_name = arg
      elif opt in ("-l", "--maxleasetime"):
         leasetime = arg
      elif opt in ("-m", "--mask"):
         subnet_mask = arg
      elif opt in ("-o", "--optdns"):
         option_dns = arg
      elif opt in ("-r", "--reseau"):
         sous_res = int(arg)
      elif opt in ("-f", "--interfaces"):
         interfaces = arg
      elif opt in ("-b", "ipdhcp"):
         dhcp_ip = arg

      elif opt in ("-i", "--i"):
         domain = input("Entrez le nom de domaine : ")
         ip = input("Entrez l'ip du serveur dns : ")
         server_name = input("Entrez le nom du serveur DHCP (ex : dns.ubuntu-fr.lan) : ") 
         dhcp_ip = input("Entrez l'adresse ip du dhcp : ")
         subnet_mask = input("Entrez le masque : ")
         option_dns = input("Entrez les options dns (si plusieurs mettez ceci ', ' entre les ip, ex : 1.1.1.1, 2.2.2.2) : ")
         sous_res=int(input("Entrez le nombre de sous réseaux : "))
         interfaces=input("Entrez les interfaces d'écoute (ex si plusieurs ens33 ens34) : ")
         leasetime=input("Entrez le lease time maximum : ")
         Deny_unknown = input ("Voulez-vous autoriser seulement les clients configurer ? yes/no ")

   
   dhcp_conf(server_name,subnet_mask,domain,option_dns,sous_res,interfaces,leasetime,Deny_unknown,dhcp_ip)


if __name__ == "__main__":
   main(sys.argv[1:])
