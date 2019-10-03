#!/usr/bin/python2
# -*- coding: utf-8 -*-
# aprs_bot.py aka elenatagrabber.py, nach einer Idee von DO7EN
# Auswerten des APRX-Log und Reaktion auf:
# - Nachrichten an 'call_msg', erstellen
#   eines Textfiles zur späteren TTS-Umwandlung
# - Mini-Bot an 'call_remote' mit erweiterbaren Funktionen
#
# V1.0	03.10.2019	DL7ATA

import os
import tailer
import requests
import time
import lib_parse
import aprslib
from libfap import *
from time import strftime

call_msg = "DL7ATA"
home = (52.5692293, 13.2312943)
call_remote = "DB0TGO"
passwd_remote = "*****"
call_remote1k2 = "DB0TGO-15"
beacon_port1k2 = "2m"
call_remote9k6 = "DB0TGO-14"
beacon_port9k6 = "70cm"
beacon_portTCP = "TCPIP"

elenata = "svxlink@Banana26"
aprsmsgziel = elenata + ":/tmp/aprsmsg.text"
logdatei = '/var/log/aprx/aprx-rf.log'
ausgabedatei = '/tmp/aprs_bot.log'
wemos_ip = "http://192.168.10.181/"
# Wenn folgender Inhalt vorhanden, dann keine Ausgabe auf Wemos
wemos_no1 = "BLN1WXBLN"
wemos_no2 = "BLN4WXTXL"
wemos_no3 = "Solarpower"
bake = '1k2 X-Band-iGate.APRX TEST'
farbe_rot = '\033[31m'
farbe_gelb = '\033[33m'
farbe_aus = '\033[0m'
counter_noparse = 0
counter_parse = 0
mheard_string = "mheard -o t | sed -n 3,5p | cut -c 1-9,17-26 | sed 's/       //' | tr '\n' ' '"
# TMP Datei hier auf dem Rechner
dateiname = "/tmp/aprsmsg.text"
last_msg = ''

# Ausgabe auf WEMOS
def wemos(von, entfernung, feld, speed):
    res = ""
    kommentar = (feld.replace(' ', '_').replace('>', '_')
                 .replace('{', '_').replace('}', '_'))
    if entfernung > 0:
        entfernung = str(entfernung)
        if speed > 0:
            entfernung += str(speed)
    else:
        entfernung = ''
    text = wemos_ip + strftime("%H:%M:%S") + "____APRS" + \
        von + "_" + entfernung + kommentar
    try:
        res = requests.get(text, timeout=2.5)
    except Exception as e:
        print "WEMOS zzt. nicht erreichbar", res, e
        pass

def senden(von, msg_string, rx_src, beacon_port):
    # Empfänger = von
    # msg_String = senden_ack/antwort
    # rx_src=TGO-14/-15 oder TCPIP
    # beacon_port = AX25-Relikt (1k2 oder 9k6, 2m/70cm)
    # ZIEL-CALL mit 9 Stellen indizieren und durch Zielcall ersetzten
    zielcall = [" "," "," "," "," "," "," "," "," "]
    for i in range(0, len(von)):
        zielcall[i] = str(von[i])
    zielcall = ''.join(zielcall)
    # Zusammensetzen der MSg
    # command = rx_src + ">TCPIP," + rx_src + "::" + zielcall + ":" + msg_string
    command = "DB0TGO>TCPIP,DB0TGO-15::" + zielcall + ":" + msg_string
    AIS = aprslib.IS(call_remote, passwd_remote, port=14580)
    AIS.connect()
    # senden
    AIS.sendall(command)
    print("Msg -> " + command + "\nan " + zielcall +
          " um " + strftime("%H:%M:%S") + " gesendet.")
    return

# Fernsteuerbefehle
def remote(p_msg):
    if p_msg[0:2] == '/?':
        antwort = "Willkommen bei bot.py, '/h' for help."
    elif p_msg[0:2] == '/h':
        antwort = "Befehle beginnen mit '/' -  ?,h,t,a,b,c,e,m,p,q"
    elif p_msg[0:2] == '/t':
        antwort = "Zeit in TgO: " + (strftime("%H:%M") + " Uhr")
    elif p_msg[0:2] == '/q':
        antwort = "Du weisst schon, was ein '/Q' bedeutet?"
    elif p_msg[0:2] == '/a':
        antwort = "Das ist der Beginn des kleinen A,B,C ..... 😁"
    elif p_msg[0:2] == '/b':
        antwort = "... und mit b, bist Du mitten drinnen ..."
    elif p_msg[0:2] == '/c':
        antwort = ("Aber bei 'c' endet meine Intellejentz leider,"
                   " wohl doch keine KI?")
    elif p_msg[0:2] == '/m':
        mheard = os.popen(mheard_string).readlines()
        antwort = "MHEARD:" + ''.join(mheard).rstrip()
    elif p_msg[0:2] == '/e':
        antwort = p_msg[2:].lstrip()
    elif p_msg[0:2] == '/p':
        command = "wget -q -O /tmp/PV_Ertrag.txt http://banana26/PV_Ertrag.txt"
        os.system(command)
        pv_string = open("/tmp/PV_Ertrag.txt").read()
        a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, \
            a15, a16, a17, a18, a18 = pv_string.split(' ')
        antwort = ("Solarpower  A=" + a1 + " V=" + a10 + " " + a4 + "Wh")
    elif p_msg[0:2] == '/w':
        command = "~/APRSMsg/wx_eddt.sh > /tmp/wx_eddt.tmp &"
        os.system(command)
        time.sleep(2.0)
        try:
            wx_string = open("/tmp/wx_eddt.tmp").read()
            antwort = strftime("%H:%M:%S") + wx_string
        except:
            antwort = "Errorhandling 0xff"
            pass
    else:
        antwort = p_msg[0:2] + " ist kein gueltiges Kommando."
    return(antwort)

print("Starte REMOTE als " + call_remote9k6 + " auf 70cm und " +
      call_remote1k2 + " auf 2m als bot" + "\n" +
      "...und MESSAGE als " + call_msg + " TTS um " +
      strftime("%H:%M:%S") + "\n")

while True:
    for line in tailer.follow(open(logdatei)):
        rx_src = line[24:33].rstrip()
        if rx_src == call_remote9k6:
            beacon_port = beacon_port9k6
        elif rx_src == call_remote1k2:
            beacon_port = beacon_port1k2
        else:
            beacon_port = beacon_port9k6    # TCP
        text = ""
        for i in range(36, len(line)):
            text += str(line[i])
        if text[0] == "*":
            text = text[1:].rstrip()

        # weiter mit passendem string und parsen
        counter_parse += 1
        von, feld, entfernung, speed, typ, msg, dst, msg_id, msg_ack,\
            counter_noparse = \
            lib_parse.parse(text, counter_parse, counter_noparse, rx_src)
        # print von, feld, entfernung, typ, msg, dst, msg_id, counter_noparse
        # Ausgabe auf Wemos wenn Traffic auf 70cm
        # Keine Ausgabe wennn ...
        # 	- Bake in text
        # 	- BLN (wemos_no1 + wemos_no2) in dst
        # 	- Solar-msg (wemos_no3) in text
        if (typ == 6 or call_remote9k6 == von) and not \
           (bake in text or wemos_no1 == dst or wemos_no2
           == dst or wemos_no3 in text):
            wemos(von, entfernung, feld, speed)

        if typ == 6 and not msg_ack:    # 6 = message und kein ack
            p_msg = msg
            # auf msg - Inhalt abfragen und mit ack quittieren.
            if dst == call_remote:
                print "Msg an ", dst, " von ", von, " um ", \
                      strftime("%H:%M:%S"), "-->", farbe_rot, \
                      p_msg, farbe_aus, "<--"
                # Aussenden "ACK"
                senden_ack = "ack" + msg_id
                senden(von, senden_ack, rx_src,
                       beacon_port)
                # prüfen auf Remote-Befehl
                if p_msg[0:1] == '/':
                    antwort = remote(p_msg)
                    time.sleep(2.0)
                    senden(von, antwort, rx_src,
                           beacon_port)
                    last_msg = antwort
            elif dst == call_msg and wemos_no3 not in text and not last_msg in p_msg:
                print strftime("%H:%M:%S"), "-->", farbe_rot, msg, farbe_aus
                senden_ack = "ack" + str(msg_id)
                senden(von, senden_ack, call_msg,
                       beacon_port)
                # Temp Datei für svxlink erstellen und kopieren
                with open(dateiname, 'w+') as output:
                    zusendentext = "#" + von + "#" +\
                                    dst + "#" +\
                                    msg.replace(":", "") + "#" +\
                                    str(msg_id)
                    output.write(zusendentext)
                    output.close()
                print "svxlink-file: ", zusendentext
                action_msg = "scp " + dateiname + " " + aprsmsgziel
                os .system(action_msg)
libfap.fap_cleanup()
