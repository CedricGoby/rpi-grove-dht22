#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Description : Récupère la température et l'humidité depuis la sonde et envoie les données
# vers une base MySQL. Un email est envoyé en cas d'erreur.
# Langage : Python 2
# Licence : GPL-3+
# Auteur : Cédric Goby
# Versioning : https://github.com/CedricGoby/rpi-grove-dht22

# Importation des modules nécessaires
import sys
import os
import grovepi
import MySQLdb
import time
# Importation de la fonction SendError depuis le fichier send__error.py
from send_error import SendError

# Nom de la base MySQL
__db_name ="db-name"
# Nom de la table
__db_table ="db-table"
# Fichier de connexion (contient : utilisateur MySQL, mot de passe, hôte MySQL)
__db_login_file = os.path.join(sys.path[0], 'db-login.cnf')
# Nom de l'hôte qui envoie les emails
__hostname ="hostname"
# Expéditeur des emails
__sender ="sender@provider.com"
# Destinataire des emails
__recipient ="recipient@provider.com"
# Serveur SMTP pour l'envoi des emails
__smtp_server ="smtp.provider.com"
# Nom du scipt
__file_name = os.path.basename(__file__)
# Date et heure
__datetime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) 
# La sonde Grove Temperature & Humidity sensor Pro est connectée au port digital D4 du module GrovePi+ # SIG,NC,VCC,GND
__sensor = 4

# Lancement du processus d'acquisition des données de la sonde
try:
	# Acquisition de la température et de l'humidité
	# Second paramètre: 1 = Modèle de sonde de température et d'humitité DHT22
	[__temperature,__humidity] = grovepi.dht(__sensor,1)
	# Affichage de la date et de l'heure, de la température et de l'humidité
	print __datetime,__temperature,__humidity
	# Connexion à la base MySQL : Timeout en secondes, Nom de la base de données MySQL, fichier de connexion
	con = MySQLdb.connect(connect_timeout=10,db=__db_name,read_default_file=__db_login_file)
	# Création d'un "Cursor object" qui permettra d'exécuter la requête SQL
	cur = con.cursor()
	# Construction de la requête SQL
	sql = "INSERT INTO " + __db_table + " (date_insert, temperature, humidity) VALUES (%s, %s, %s)"
	# Exécution de la requête SQL
	cur.execute(sql, (__datetime, __temperature, __humidity))
	con.commit()
	# Fermeture de la connexion à la base MySQL
	con.close()

# Dans le cas d'une erreur MySQL
except MySQLdb.Error, e:
	try:
		# Récupération de l'erreur MySQL (l'erreur est connue)
		__error = ("Erreur MySQL [%d]: %s" % (e.args[0], e.args[1]))
		# Affichage de l'erreur
		print __error
	except IndexError:
		# Récupération de l'erreur MySQL (l'erreur est inconnue)
		__error =  ("Erreur MySQL: %s" % str(e))
		# Affichage de l'erreur
		print __error
	# Envoi de l'erreur par email avec la fonction SendError
	SendError(__error, __sender, __recipient, __hostname, __file_name, __smtp_server)

# Dans le cas d'une erreur autre qu'une erreur MySQL
except:
	__error = ("Erreur: %s" % sys.exc_info()[0])
	# Affichage de l'erreur
	print __error
	# Envoi de l'erreur par email avec la fonction SendError
	SendError(__error, __sender, __recipient, __hostname, __file_name, __smtp_server)
