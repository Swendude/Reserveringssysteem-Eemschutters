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

- [ ] Reserveringen annuleren
- [ ] Maximaal aantal reserveringen per week
- [ ] Ux verbeteren
    - [ ] Bestiging modal bij reserveren
    - [ ] Login form
- [ ] Wachtwoord wijzigen
- [ ] Overzicht voor baancommandant/sleutelhouder