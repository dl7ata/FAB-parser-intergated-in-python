#!/bin/bash
# Starten aprs_bot.py
# Wird aus Cronjob gestartet.

id_file='/var/tmp/aprs_bot.pid'

if [ -f "$id_file" ];then
  id=$(cat ${id_file})
  echo "Beende  $id ..."
  /bin/kill -HUP $id

  if [ $? -eq 0 ]
  then
	echo "Warte jetzt 4 Sek. um $(date +%T)"
	sleep 4
  fi
fi

exec python2 -u ./aprs_bot.py > /tmp/aprs_bot.log &
echo $! > /var/tmp/aprs_bot.pid
idn=$(echo $!)
echo "Starte $idn,   $(date +%d-%m-%y.%H:%M:%S)"
echo -e "\n"

exit 0
