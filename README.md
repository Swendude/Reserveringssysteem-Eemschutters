# Reserveringssysteem Eemschutters

De demo is [hier](https://eemschutters-reserveringen.herokuapp.com/) te vinden. De branch 'demo' wordt automatisch gedeployed op een commit.

## Lokaal installeren
We gebruiken [python@3.8.x](https://www.python.org/downloads/release/python-380/).

Om lokaal te draaien:
    
- Installeer de omgeving (het liefst in een virtualenv)
        
```bash
    $ source .venv/bin/activate
    $ pip install -r requirements.txt
```
- Maak een .env file aan (zie .example_env voor de benodigde waarden)
- Maak de database klaar 

```bash
    $ python manage.py makemigrations
    $ python manage.py migrate
```
- Maak een superuser aan voor het admin paneel
```bash
    $ python manage.py createsuperuser
```
- Draai de dev server:
```bash
    $ python manage.py runserver
```

## Todos

**Maak reservering**
- [x] Terug naar gekozen datum na toevoegen van een reservering


**Mijn reserveringen**
- [x] Reserveringen annuleren
- [x] Maximaal aantal reserveringen per week
- [x] Volgorde omdraaien (eerstvolgende reservering bovenaan)
- [x] Reserveringen van de huidige dag tonen
- [x] ~~Reserveringen maximaal een uur van te voren annuleren~~
- [x] Reserveringen annuleren tot eindtijd
- [ ] Reserveringen na vier weken verwijderen

**Opmaak**
- [x] Bestiging modal bij reserveren
- [x] Login form
- [x] Responsive maken
- [x] Error Messages

**Diverse**
- [x] Wachtwoord wijzigen
- [x] Overzicht voor baancommandant/sleutelhouder
- [x] Bij het wijzigen van een schietdag: Alle toekomstige reservaties verwijderen
- [x] 'Reserveringen' pagina een regelblokje
- [x] Eerste en laatste sloten bouwen op/af
- [x] Als een baan geen opmerking heeft, dan ook de 'Haakjes: `(` `)` niet laten zien
- [x] Sleutelhouderslot reserveren
- [ ] RIVM Gezondheidscheck bij reserveren
- [x] Reserveringen exporteren

**Datamodel/Validatie**
- [x] Geen twee slots op dezelfde avond
- [ ] X-de dag van de maand Schietdagen
- [x] Label banen naar string
- [x] Non int aantal sloten
    - [x] Resterende tijd toevoegen aan begin en eind slot
- [x] Een uur van te voren is een slot vogelvrij
    - [x] Vogelvrije sloten tellen niet mee in de weektelling
    - [x] Sloten hebben een bonusveld
- [x] Algemene instellingen in admin
- [x] Admin reserveringen verbeteren
- [x] Alleen gebruikers in de groep sleutelhouders zien overzicht

**Bug**
- [x] Na database-migratie Als je de schietdagen niet goed vult, krijg je een error over de assert functie (regel 98)
- [x] Mijn reserveringen worden niet goed gesorteerd per week.
