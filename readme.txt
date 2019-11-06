Tutorial
https://buildmedia.readthedocs.org/media/pdf/pyro4/stable/pyro4.pdf

---
Untuk menjalankan, name server harus dinyalakan dulu
harus di start dulu dengan  pyro4-ns -n localhost -p 7777
gunakan URI untuk referensi name server yang akan digunakan

----
Untuk aktifasi virtualenv
jika menggunakan ubuntu
install python3-venv
apt-get install python3-venv

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

---
menjalankan program
cd c0
python greet_server.py

client:
python greet_client.py
---

menjalankan file server
cd c1
python server.py

client:
python client.py


