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
- [x] Reserveringen maximaal een uur van te voren annuleren

**Opmaak**
- [x] Bestiging modal bij reserveren
- [x] Login form
- [x] Responsive maken
- [x] Error Messages

**Diverse**
- [x] Wachtwoord wijzigen
- [x] Overzicht voor baancommandant/sleutelhouder
- [x] Bij het wijzigen van een schietdag: Alle toekomstige reservaties verwijderen
- [ ] 'Reserveringen' pagina een nieuwsblokje
- [ ] Eerste en laatste sloten bouwen op/af

**Datamodel/Validatie**
- [x] Geen twee slots op dezelfde avond
- [ ] X-de dag van de maand Schietdagen
- [ ] Label banen naar string
- [ ] Non int aantal sloten
    - [ ] Tijd tussen slots
    - [ ] Tijd begin avond
    - [ ] Tijd eind avond
- [ ] Een uur van te voren is een slot vogelvrij
    - [ ] Vogelvrije sloten tellen niet mee in de weektelling
    - [ ] Sloten hebben een status: reserveringstype (Normaal, Laat)
- [ ] Algemene instellingen in admin
- [x] Admin reserveringen verbeteren
- [x] Alleen gebruikers in de groep sleutelhouders zien overzicht