# Forslagskasse

En enkel, nettbasert forslagskasse der brukere kan sende inn forslag med vedlegg. Innsendte forslag kan leses av administratorer.

## Krav

For å installere og kjøre forslagskassen trenger du:

- [Docker](https://docs.docker.com/get-docker/) med Docker Compose.

Du trenger også tilgang til prosjektfilene.

## Hent prosjektet

Du kan hente prosjektet på én av følgende måter.

**Alternativ 1: Last ned fra GitHub**

1. Åpne prosjektets GitHub-side.
2. Klikk på **Code** og deretter **Download ZIP**.
3. Pakk ut ZIP-filen til en mappe på datamaskinen.

**Alternativ 2: Bruk Git**

Hvis du har Git installert, kan du klone prosjektet fra kommandolinjen:

```bash
git clone https://github.com/Auxiguilar/forslagskasse
```

## Konfigurer prosjektet

Åpne en terminal i prosjektmappen, altså mappen som inneholder `compose.yaml`.

Opprett en lokal miljøfil ved å kopiere `.env.example`:

**Linux og macOS**

```bash
cp .env.example .env
```

**Windows**

```bat
copy .env.example .env
```

Åpne `.env` og konfigurer verdiene etter behov. Du må blant annet angi en hemmelig nøkkel (`DJANGO_SECRET_KEY`), databasepassord og tillatte vertsnavn (`DJANGO_ALLOWED_HOSTS`).

Miljøfilen inneholder konfigurasjon og hemmeligheter og skal ikke deles.

## Start forslagskassen

Kjør følgende kommando i prosjektmappen:

```bash
docker compose up --build -d
```

Docker bygger applikasjonsbildet og starter tjenestene i bakgrunnen.

Første gang du starter prosjektet, må du også opprette databasetabellene:

```bash
docker compose exec django-web python manage.py migrate
```

Forslagskassen er nå tilgjengelig på:

`http://localhost:8000/`

## Administrasjon

Administrasjonssiden er tilgjengelig på:

`http://localhost:8000/admin/`

Administratorer må logge inn for å lese innsendte forslag og laste ned vedlegg. Tilgang og rettigheter administreres gjennom Django.

### Opprett administratorkonto

Før du kan logge inn på administrasjonssiden, må du opprette en administratorkonto.

Kjør følgende kommando i prosjektmappen:

```bash
docker compose exec django-web python manage.py createsuperuser
```

Følg instruksjonene i terminalen for å angi brukernavn, e-postadresse og passord. E-postadressen kan være valgfri, avhengig av konfigurasjonen.

Når kontoen er opprettet, åpner du administrasjonssiden:

`http://localhost:8000/admin/`

Logg inn med brukernavnet og passordet du nettopp opprettet.

Ta vare på innloggingsopplysningene. Superbrukeren har omfattende rettigheter i applikasjonen.

### Opprett brukerkontoer

En superbruker kan opprette kontoer for andre som skal administrere forslagskassen, uten å gi dem full tilgang til systemet.

1. Logg inn på administrasjonssiden med superbrukerkontoen din: `http://localhost:8000/admin/`
2. Gå til **Brukere** og velg **Legg til ny bruker**.
3. Opprett brukeren med brukernavn og passord.
4. Åpne den nye brukeren og aktiver **Administrasjonsstatus**.
5. Under **Brukerrettigheter** gir du brukeren følgende rettigheter:
   - `Forslagskasse | Forslag | Can view Forslag`
   - `Forslagskasse | Vedlegg | Can view Vedlegg`
   - `Forslagskasse | Vedlegg | Can download Vedlegg`
6. Lagre brukeren.

`Can view Forslag` gir tilgang til å lese forslagene. `Can view Vedlegg` gir tilgang til å se vedleggsoppføringene i administrasjonssiden, og `Can download attachment` gir tilgang til å laste ned filene.

Brukeren trenger ikke ha **Superbruker status** eller rettighetene **Add**, **Change** og **Delete** for disse modellene.

**Merk:** Brukeren må ha **Administrasjonsstatus** for å få tilgang til administrasjonssiden og laste ned vedlegg.

## Vedlegg

Forslagskassen støtter vedlegg i følgende formater:

- Bilder: JPG, PNG og SVG
- Dokumenter: DOC, DOCX, PDF og ODT
- Regneark: XLS, XLSX og ODS
- Tekstfiler: TXT

Hvert forslag kan ha maksimalt fem vedlegg, med en maksimal filstørrelse på 5 MB per vedlegg.

## Stopp og start forslagskassen

For å stoppe tjenestene kjører du:

```bash
docker compose down
```

For å starte dem igjen uten å bygge bildet på nytt:

```bash
docker compose up -d
```

Databasen lagres i et eget Docker-volum og beholdes når containerne stoppes eller erstattes.

**Merk:** Ikke bruk `docker compose down -v` med mindre du ønsker å slette de tilknyttede volumene og dermed også lagrede data.

## Feilsøking

Hvis installasjonen eller oppstarten mislykkes:

1. Kontroller at Docker kjører.
2. Kontroller at du kjører kommandoene fra prosjektmappen.
3. Les feilmeldingene i terminalen.
4. Kontroller at `.env` er opprettet og inneholder gyldige verdier.

Du kan undersøke loggene til Django-tjenesten med:

```bash
docker compose logs django-web
```

Hvis problemet vedvarer, kan du rapportere det på prosjektets GitHub-side.

## Videre informasjon

Dette prosjektet er utviklet med Django. Mer informasjon om rammeverket finnes i [Djangos dokumentasjon](https://docs.djangoproject.com/).