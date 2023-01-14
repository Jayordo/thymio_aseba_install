git pull &
wait

# asebamedulla "ser:device=/dev/ttyACM0"
# asebamedulla "ser:device=/dev/ttyAMA0"
# sudo service dbus restart
asebamedulla "ser:name=Thymio-II" &
python controller.py
kill $!
