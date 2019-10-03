#!/usr/bin/python2
# -*- coding: utf-8 -*-
import settings
from libfap import *
from time import strftime

RED = '\033[31m'
LYELLOW = '\033[93m'
BLUE = '\033[34m'
NORMAL = '\033[0m'
LIGHTGREEN = '\033[92m'
GREEN = '\033[32m'
UNDERL_ON = '\033[4m'
UNDERL_OFF = '\033[24m'
DARKGREY = '\033[90m'
BOLD = '\033[1m'
pak = settings.PAK
error_datei = '/tmp/fabparse_error.tmp'

def parse(packet_str, counter_parse, counter_noparse, rx_src):
    try:
        druck = NORMAL
        distanz = 0
        speed = 0
        msg = ''
        msg_ack = ''
        msg_id = 0
        feld = ''
        dst = ''
        dst_callsign = ''
        typ = ''
        index = 0
        p_end = 0

        # Vor Parsen fehlerhafte 0x1$ Pakete filtern bzw. umwandeln
        line = packet_str.strip()
        while index < len(line):
            p_start = line.find("<0x")
            if p_start > 0:
                p_end = line[p_start:].find('>')
                if p_end > 0:
                    zeichen = str(int(line[p_start+1:p_start+p_end], 16))
                    line = line[:p_start] + \
                                 "%c" % int(line[p_start+1:p_start+p_end], 16) + \
                                 line[p_start + p_end + 1:]
            else:
                break
            index += 1

        libfap.fap_init()
        packet = libfap.fap_parseaprs(line, len(line), 0)
        von = packet[0].src_callsign
        length_src = len(rx_src)
        druck +=  DARKGREY + rx_src[length_src-2:length_src] + NORMAL + " " + str(von).ljust(10, ' ')

        if packet[0].latitude and packet[0].longitude:
            lat = packet[0].latitude[0]
            lon = packet[0].longitude[0]
            my_lat = settings.MY_LAT
            my_lon = settings.MY_LON
            entfernung = libfap.fap_distance(settings.MY_LON,
                                             settings.MY_LAT, lon, lat)
            richtung = libfap.fap_direction(settings.MY_LON,
                                            settings.MY_LAT, lon, lat)
            distanz = str(round(entfernung, 1)) + "km"
            richtung = str(int(round(richtung))) + "° "
            di_ri = " " + distanz + " " + richtung
            if packet[0].speed:
                if  packet[0].speed[0] > 0:
                    speed = str(int(round(packet[0].speed[0]))) + "km/h "
                    di_ri += speed
            else:
                if packet[0].altitude:
                    if  packet[0].altitude[0] > 0:
                        alti = str(int(round(packet[0].altitude[0]))) + "m "
                        di_ri += alti

            druck += di_ri.ljust(22, ' ')
        else:
            druck += "\t\t\t"

        if packet[0].error_code:
            error = ' '*60
            error_code = packet[0].error_code[0]
            libfap.fap_explain_error(error_code, error)
            druck += RED + error.strip() + NORMAL + " "
            druck += str(packet[0].body)
            counter_noparse += 1
            druck_parse = "  {0:.0%}"\
                          .format(float(counter_noparse)/counter_parse) + \
                          ' Error #'
            druck += druck_parse
            file_output = strftime("%H:%M:%S") + druck + " " + str(counter_noparse) + "\n"
            # TEST
            with open(error_datei, 'a') as output:
                output.write(file_output)
                output.close()

        if packet[0].object_or_item_name:
            druck += LYELLOW + packet[0].object_or_item_name + NORMAL + " "

        if packet[0].type and not packet[0].error_code:
            typ = packet[0].type[0]
            type_txt = pak[typ]
            pak_typ = LIGHTGREEN + type_txt + NORMAL + " "
            druck += pak_typ.ljust(19, " ")

        if packet[0].comment:
            feld = str(packet[0].comment).strip()
            if packet[0].wx_report:
                druck += LYELLOW + feld + NORMAL + " "
                # Wetter
                druck += GREEN
                if packet[0].wx_report[0].temp:
                    druck += " " + str(int(packet[0].wx_report[0].temp[0])) + "°C"
                if packet[0].wx_report[0].humidity:
                    druck += ", " + str(int(packet[0].wx_report[0].humidity[0])) + "%"
                if packet[0].wx_report[0].pressure:
                    if int(packet[0].wx_report[0].pressure[0]) > 0:
                        druck += ", " + str(int(packet[0].wx_report[0].pressure[0])) + "hPa"
                if packet[0].wx_report[0].wind_speed:
                    if int(packet[0].wx_report[0].wind_speed[0]) > 0:
                        druck += ", Wind " + str(int(packet[0].wx_report[0].wind_speed[0])) + "m/s"
                if packet[0].wx_report[0].wind_gust:
                    if int(packet[0].wx_report[0].wind_gust[0]) > 0:
                        druck += " max " + str(int(packet[0].wx_report[0].wind_gust[0])) + "m/s"
                if packet[0].wx_report[0].wind_dir:
                    druck += " aus " + str(int(packet[0].wx_report[0].wind_dir[0])) + "°"
                if packet[0].wx_report[0].soft:
                    druck += "/SW " + packet[0].wx_report[0].soft + " "
                druck += NORMAL
            else:
                druck += LYELLOW + feld.ljust(65, " ") + NORMAL + " "

        if packet[0].status:
            feld = str(packet[0].status).strip()
            druck += LYELLOW + packet[0].status + NORMAL + " "

        if packet[0].destination:
            dst = packet[0].destination
            druck += dst + " "

        if packet[0].message:
            msg = packet[0].message
            dst_callsign = packet[0].dst_callsign
            feld = msg + " An: " + packet[0].destination
            druck += "\t" + msg
            if packet[0].message_id:
                msg_id = str(packet[0].message_id)
                druck += " msg_id: " + msg_id
            if packet[0].message_ack:
                msg_ack = str(packet[0].message_ack)
                druck += " ack: " + str(msg_id)
            # TEST
            if typ == 6:
                file_output = strftime("%H:%M:%S") + ": Msg von " + von + " an " + packet[0].destination + ":" + msg + "\n"
                with open(error_datei, 'a') as output:
                    output.write(file_output)
                    output.close()

        pfad = []
        if packet[0].path_len:
            i = 0
            while i < packet[0].path_len:
                pfad.append(packet[0].path[i])
                i += 1
            druck += BOLD + "\t" + ', '.join(pfad) + NORMAL + " "

        druck += NORMAL + str(counter_noparse) + "/" +  str(counter_parse)

        print strftime("%H:%M:%S"), druck

        libfap.fap_free(packet)
        return(von, feld, distanz, speed, typ, msg, dst, msg_id, msg_ack, counter_noparse)
    except():
        pass
