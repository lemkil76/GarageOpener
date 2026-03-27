# Garage Door Controller – Hörmann Supra Matic E

Webbaserad garageportsstyrning med Raspberry Pi. Ett relä kopplat till motorns
impulsplint simulerar ett knapptryck. Åtkomst via PIN-skyddat webbgränssnitt.

---

## 1. Hårdvarukoppling

```
Raspberry Pi           Relämodul
─────────────          ─────────
Pin 2  (5V)    ──────→ VCC
Pin 6  (GND)   ──────→ GND
Pin 11 (GPIO17)──────→ IN

Relämodul              Hörmann Supra Matic E (innanför kåpan)
─────────              ─────────────────────
COM            ──────→ Impulsplint T (eller märkt "Taster")
NO             ──────→ Impulsplint T (andra terminalen)
```

> Hörmanns impulsplint är potentialfri – ingen extern spänning ska appliceras.
> Dubbelkolla i manualen vilka terminaler som är märkta för extern knapp.
> Vanligen finns plintlisten längst fram/ned på motorenheten.

---

## 2. Raspberry Pi – flasha OS

**OS:** Raspberry Pi OS Lite (32-bit) – ingen skrivbordsmiljö behövs.
Ladda ner Raspberry Pi Imager från raspberrypi.com/software

**Viktigt i Imager innan du skriver – klicka "Edit Settings":**
- Hostname: `garage`
- Aktivera SSH: ja
- Användarnamn/lösenord: välj eget
- WiFi: fyll i ditt nätverks SSID och lösenord redan nu
  → Sparas i imagen och aktiveras automatiskt när WiFi-dongeln pluggas in senare

**Anslutning under installation:**
Pi 2 Model B har ett RJ45 ethernet-uttag – koppla en nätverkskabel direkt
till routern tills WiFi-dongeln är på plats. Ethernet och WiFi fungerar
omväxlande utan några ändringar i mjukvaran.

SSH in när Pi:n startat:
```bash
ssh pi@garage.local
# eller om garage.local inte fungerar:
ssh pi@<ip-adress>   # hitta IP i routerns admingränssnitt
```

---

## 3. Installera projektet

```bash
# Uppdatera systemet
sudo apt update && sudo apt upgrade -y

# Installera Python venv
sudo apt install python3-venv python3-pip -y

# Kopiera projektet
cd ~
mkdir garage-controller && cd garage-controller
# (kopiera filerna hit, t.ex. via scp eller git)

# Skapa virtuell miljö
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 4. Konfigurera

```bash
# Redigera config.py – byt PIN och SECRET_KEY
nano config.py
```

Generera ett slumpmässigt SECRET_KEY:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 5. Testa manuellt

```bash
source venv/bin/activate
python app.py
# Öppna http://<pi-ip>:5000 i webbläsaren
```

Hitta Pi:ns IP-adress:
```bash
hostname -I
```

På Mac/Windows utan Raspberry Pi startar appen i **simulation mode** –
GPIO-anrop loggas men inget relä aktiveras.

---

## 6. Aktivera autostart med systemd

```bash
sudo cp garage.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable garage
sudo systemctl start garage

# Kontrollera status
sudo systemctl status garage
```

---

## 7. Nå appen från mobilen

Surfa till `http://<pi-ip>:5000` på samma WiFi. Bokmärk sidan på hemskärmen:
- **iOS:** Dela → Lägg till på hemskärm
- **Android:** Meny → Lägg till på startskärmen

---

## 8. Valfritt: Tillgång utanför hemmet

**Alternativ A – Tailscale (rekommenderat, gratis, enkelt):**
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```
Installera Tailscale-appen på din mobil. Du når Pi:n via dess Tailscale-IP
även utanför hemmet, utan öppna portar i routern.

**Alternativ B – ngrok (snabb test):**
```bash
# Installera ngrok, skapa gratis-konto på ngrok.com
ngrok http 5000
```

---

## 9. Lägga till statussensor senare (TODO)

Koppla en reed switch/magnetkontakt:
```
Reed switch    Raspberry Pi
───────────    ────────────
Ledare 1  ──→ Pin 9  (GND)
Ledare 2  ──→ Pin 13 (GPIO27, med intern pull-up)
```

Lägg till i `relay.py`:
```python
GPIO_SENSOR_PIN = 27
GPIO.setup(GPIO_SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def get_door_status():
    # LOW = magnet nära = porten stängd
    return "closed" if GPIO.input(GPIO_SENSOR_PIN) == GPIO.LOW else "open"
```

Lägg till route i `app.py`:
```python
@app.route("/status")
def status():
    return jsonify({"status": relay.get_door_status()})
```

---

## Projektstruktur

```
garage-controller/
├── app.py           # Flask-backend med PIN-auth och relay-styrning
├── relay.py         # GPIO-abstraktionslager
├── config.py        # Konfiguration: PIN, GPIO-pin, tidsinställningar
├── templates/
│   ├── login.html   # PIN-inmatningssida
│   └── index.html   # Huvudgränssnitt med öppna-knapp
├── static/
│   └── style.css    # Mobilanpassad CSS
├── requirements.txt
├── garage.service   # Systemd-enhetsfil för autostart
└── README.md
```
