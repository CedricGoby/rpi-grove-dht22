#!/usr/bin/env python
# -*- coding: utf-8 -*-
# filename: rpi-grovepi-dht22.py
# Raspbian GNU/Linux 8 (Jessie)
# Python 2.7
# Matériel utilisé : Raspberry pi2 Model B, Module GrovePi+, Grove Temperature and Humidity Sensor Pro DHT22
# Description : Récupère la température et l'humidité depuis la sonde et envoie les données
# vers une base MySQL. Un email est envoyé en cas d'erreur de connexion à la base.
# Usage : python rpi-grovepi-dht22.py
# Licence : GNU General Public License, version 3 (GPL-3.0)

# Importation des modules nécessaires
import grovepi
import MySQLdb
import time
import smtplib
import email.utils
from email.mime.text import MIMEText

# Nom de la base MySQL
_db_name ="db-name"
# Nom de la table
_db_table ="db-table"
# Fichier de connexion (contient : utilisateur MySQL, mot de passe, hôte MySQL)
_db_config_file ="db-login.cnf"
# Nom de l'hôte qui envoie les emails
_hostname ="hostname"
# Destinataire des emails
_recipient ="your-address@your-provider.com"
# Serveur SMTP pour l'envoi des emails
_smtp_server ="smtp.your-provider.com"
# Date et heure
_datetime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) 

# Connecte la sonde Grove Temperature & Humidity Sensor Pro au port digital D4 # SIG,NC,VCC,GND
sensor = 4
# Lancement du processus d'acquisition
try:
	# Acquisition des données de la sonde
    # Second paramètre:  1 = Sonde de température et d'humitité DHT22
	[_temperature,_humidity] = grovepi.dht(sensor,1)
	print _datetime,_temperature,_humidity
	# Connexion à la base MySQL : Timeout en secondes, Nom de la base de données MySQL, fichier de connexion
	con = MySQLdb.connect(connect_timeout=10,db=_db_name,read_default_file=_db_config_file)
	# Création d'un "Cursor object" qui permettra d'exécuter n'importe quelle requête SQL
	cur = con.cursor()
	# Construction de la requête SQL
	sql = "INSERT INTO " + _db_table + " (date_insert, temperature, humidity) VALUES (%s, %s, %s)"
	# Exécution de la requête SQL
	cur.execute(sql, (_datetime, _temperature, _humidity))
	con.commit()
	# Fermeture de la connexion à la base MySQL
	con.close()
# En cas d'erreur MySQL
except MySQLdb.Error, e:
    try:
        # On récupère l'erreur MySQL (l'erreur est connue)
        _erreurmysql = ("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))
        print _erreurmysql
    except IndexError:
        # On récupère l'erreur MySQL (l'erreur est inconnue)
        _erreurmysql =  ("MySQL Error: %s" % str(e))
        print _erreurmysql
    # Envoi d'un email indiquant l'erreur MySQL
    # Création du message
    msg = MIMEText(_erreurmysql)
    # Destinataire
    msg['To'] = email.utils.formataddr(('Recipient', _recipient))
    # Expéditeur
    msg['From'] = email.utils.formataddr((_hostname, _recipient))
    # Sujet
    msg['Subject'] = '[Erreur MySQL]'
    # Connexion au serveur SMTP avec un timeout en secondes
    server = smtplib.SMTP(_smtp_server,timeout=60)
    # Affichage des messages de communication avec le serveur SMTP (Pour débogage)
    server.set_debuglevel(True)
    # Envoi du message (expéditeur, destinataire)
    try:
        server.sendmail(_recipient, [_recipient], msg.as_string())
    finally:
        server.quit()
