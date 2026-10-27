# Forslagskasse

En enkel, nettbasert forslagskasse der brukere kan sende inn forslag med vedlegg. Innsendte forslag kan leses av administratorer.

## Krav

For å installere og kjøre forslagskassen trenger du:

- [Python](https://www.python.org/downloads/) 3.12 eller høyere.
- [uv](https://docs.astral.sh/uv/) for installasjon og håndtering av prosjektets avhengigheter.

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

## Installer prosjektet

Åpne en terminal i prosjektmappen, altså mappen som inneholder `manage.py`.

Kjør deretter oppsettskriptet som passer til operativsystemet ditt.

**Linux og macOS**

```bash
chmod +x setup.sh
./setup.sh
```

**Windows**

Kjør følgende i en kommandoprompt i prosjektmappen:

```bat
setup.bat
```

Oppsettskriptet installerer prosjektets avhengigheter, kjører databasemigreringer og tester forslagskassen. Hvis et trinn mislykkes, stopper kjøringen.

## Start forslagskassen

Når oppsettet er fullført, starter du applikasjonen med:

**Linux og macOS**

```bash
./start.sh
```

**Windows**

```bat
start.bat
```

Åpne deretter følgende adresse i nettleseren:

`http://127.0.0.1:8000/`

## Administrasjon

Administrasjonssiden er tilgjengelig på:

`http://127.0.0.1:8000/admin/`

Administratorer må logge inn for å lese innsendte forslag og laste ned vedlegg. Tilgang og rettigheter administreres gjennom Django.

## Opprett administratorkonto

Før du kan logge inn på administrasjonssiden, må du opprette en administratorkonto.

Åpne en terminal i prosjektmappen og kjør:

```bash
uv run manage.py createsuperuser
```

Følg instruksjonene i terminalen for å angi brukernavn, e-postadresse og passord. E-postadressen kan være valgfri, avhengig av konfigurasjonen.

Når kontoen er opprettet, starter du forslagskassen og åpner administrasjonssiden:

`http://127.0.0.1:8000/admin/`

Logg inn med brukernavnet og passordet du nettopp opprettet.

Ta vare på innloggingsopplysningene. Superbrukeren har omfattende rettigheter i applikasjonen.

## Opprett brukerkontoer

En superbruker kan opprette kontoer for andre som skal administrere forslagskassen, uten å gi dem full tilgang til systemet.

1. Logg inn på administrasjonssiden med superbrukerkontoen din: `http://127.0.0.1:8000/admin/`
2. Gå til **Brukere** og velg **Legg til ny bruker**.
3. Opprett brukeren med brukernavn og passord.
4. Åpne den nye brukeren og aktiver **Administrasjonsstatus**.
5. Under **Brukerrettigheter** gir du brukeren følgende rettigheter:
   - `Forslagskasse | Forslag | Can view Forslag`
   - `Forslagskasse | Vedlegg | Can view Vedlegg`
6. Lagre brukeren.

Brukeren kan nå logge inn på administrasjonssiden, lese innsendte forslag og laste ned vedlegg. Brukeren trenger ikke ha **Superbruker status** eller rettighetene **Add**, **Change** og **Delete** for disse modellene.

**Merk:** Brukeren må ha **Administrasjonsstatus** for å få tilgang til administrasjonssiden og laste ned vedlegg. Det er ikke nødvendig å gi brukeren flere rettigheter enn de som er angitt ovenfor.

## Vedlegg

Forslagskassen støtter vedlegg i følgende formater:

- Bilder: JPG, PNG og SVG
- Dokumenter: DOC, DOCX, PDF og ODT
- Regneark: XLS, XLSX og ODS
- Tekstfiler: TXT

Hvert forslag kan ha maksimalt fem vedlegg, med en maksimal filstørrelse på 5 MB per vedlegg.

## Feilsøking

Hvis installasjonen eller oppstarten mislykkes:

1. Kontroller at Python og `uv` er installert.
2. Kontroller at du kjører kommandoene fra prosjektmappen.
3. Les feilmeldingen i terminalen. Den kan inneholde informasjon om hva som gikk galt.
4. Kontroller at nødvendige avhengigheter er installert, og at databasemigreringene er gjennomført.

Hvis problemet vedvarer, kan du rapportere det på prosjektets GitHub-side.

## Videre informasjon

Dette prosjektet er utviklet med Django. Mer informasjon om rammeverket finnes i [Djangos dokumentasjon](https://docs.djangoproject.com/).
