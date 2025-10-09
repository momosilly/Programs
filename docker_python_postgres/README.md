# Docker images Python met Postgres

## Installatie
* Open de hoofmap van de repository in Visual Studio Code (of andere editor)
* Open een terminal-venster
* Vanuit de hoofdmap installeren met `docker-compose up`

Er worden 3 containers gestart:
* Python
* Postgres
* Adminer

## Python
* De app-map is de plek waar je de python-bestanden in opslaat.
* De modules in het bestand requirements.txt zijn al geïnstalleerd (zie Dockerfile)
* Je kunt python-scripts uitvoeren door eerst een interactieve terminal te starten:
    * Open een nieuw terminal-venster in je editor
    * `docker exec -it python-app-1 bash` (zie voor exacte naam `docker ps`)
    * Vervolgens kun je scripts starten op de gebruikelijke manier bijv. `python main.py`

## Postgres
* In de db_init map staat een init.sql script. Tijdens `docker compose up` wordt dit bestand gekopieerd naar de postgres server en uitgevoerd.
* Er worden 1 database aangemaakt en er wordt een user aangemaakt die je kunt gebruiken met Adminer. (pas eventueel passwords aan!)
* In docker-compose.yml wordt een `postgres`-user (root) met password gedefinieerd. (pas passwords hier eventueel ook aan!)
* Om er voor te zorgen dat alle data niet verloren gaat, worden de data-bestanden opgeslagen in de map db_data op het host-systeem
* LET OP: De db_data map wordt niet meegenomen in het wegschrijven naar de repository (zie .gitignore). Als je toch een backup wilt bewaren van je database, exporteer dan je databasestructuur inclusief data in een sql-bestand en plaats dat in de hoofdmap van je repository.

## Adminer
* Je kunt Adminer gebruiken om de database-server (postgres) te beheren.
* Ga met je browser naar `http://127.0.0.1:8083`
* Log in met de root-user en wachtwoord (zie docker-compose.yml)
* Je kunt ook inloggen met de speciale some_user (zie /db/init.sql)


## School database
* Met het installeren via docker-compose wordt er een database `school` aangemaakt.
* Log als superuser in op Adminer (student/student) en gebruik de database `school`
* Importeer het `school_pg.sql`-script