# Forslagskasse

[English](README.en.md) | [Norsk](README.md)

A simple, web-based suggestions box where users can submit suggestions with attachments. Submitted suggestions can be read by administrators.

## Requirements

To install and run Forslagskasse, you need:

- [Docker](https://docs.docker.com/get-docker/) with Docker Compose.

You also need access to the project files.

## Get the project

You can obtain the project in either of the following ways.

**Option 1: Download from GitHub**

1. Open the project's GitHub page.
2. Click **Code**, then **Download ZIP**.
3. Extract the ZIP file to a folder on your computer.

**Option 2: Use Git**

If you have Git installed, you can clone the project from the command line:

```bash
git clone https://github.com/Auxiguilar/forslagskasse
```

## Configure the project

Open a terminal in the project directory, i.e. the folder containing `compose.yaml`.

Create a local environment file by copying `.env.example`:

**Linux and macOS**

```bash
cp .env.example .env
```

**Windows**

```bat
copy .env.example .env
```

Open `.env` and configure the values as needed. Among other things, you must provide a secret key (`DJANGO_SECRET_KEY`), a database password, and the allowed host names (`DJANGO_ALLOWED_HOSTS`).

The environment file contains configuration and secrets and should not be shared.

If the default ports are already in use, you can change `DJANGO_HOST_PORT` and `POSTGRES_HOST_PORT` in `.env`. For example, setting `DJANGO_HOST_PORT=8080` makes the website available on port `8080`.

On Linux, set `APP_UID` and `APP_GID` to your user IDs so that the application has write access to `media/`. The default value is `1000`; if your IDs are different, find them using `id -u` and `id -g` and update the values in `.env`.

## Start Forslagskasse

Run the following command in the project directory:

```bash
docker compose up --build -d
```

Docker builds the application image and starts the services in the background.

Uploaded files are stored in the project directory `media/`, and PostgreSQL data is stored in `postgres_data/`.

The first time you start the project, you must also create the database tables:

```bash
docker compose exec django-web python manage.py migrate
```

Forslagskasse is now available on the port specified by `DJANGO_HOST_PORT` (default `8000`):

`http://localhost:8000/`

## Administration

The administration site is available on the port specified by `DJANGO_HOST_PORT` (default `8000`):

`http://localhost:8000/admin/`

Administrators must log in to read submitted suggestions and download attachments. Access and permissions are managed through Django.

### Create an administrator account

Before you can log in to the administration site, you must create an administrator account.

Run the following command in the project directory:

```bash
docker compose exec django-web python manage.py createsuperuser
```

Follow the instructions in the terminal to enter a username, email address, and password. The email address may be optional, depending on the configuration.

Once the account has been created, open the administration site:

`http://localhost:8000/admin/`

Log in using the username and password you just created.

Keep your login credentials safe. The superuser has extensive permissions within the application.

### Create user accounts

A superuser can create accounts for others who need to administer Forslagskasse, without giving them full access to the system.

1. Log in to the administration site using your superuser account: `http://localhost:8000/admin/`
2. Go to **Brukere** (users) and select **Legg til ny bruker** (add user).
3. Create the user with a username and password.
4. Open the new user and enable **Administrasjonsstatus** (staff status).
5. Under **Brukerrettigheter** (user permissions), grant the user the following permissions:
   - `Forslagskasse | Forslag | Can view Forslag`
   - `Forslagskasse | Vedlegg | Can view Vedlegg`
   - `Forslagskasse | Vedlegg | Can download Vedlegg`
6. Save the user.

`Can view Forslag` (suggestion) allows the user to read suggestions. `Can view Vedlegg` (attachment) allows the user to see attachment entries in the administration site, and `Can download Vedlegg` allows the user to download the files.

The user does not need **Superbruker status** or the **Add**, **Change**, and **Delete** permissions for these models.

**Note:** The user must have **Administrasjonsstatus** enabled to access the administration site and download attachments.

## Attachments

Forslagskasse supports attachments in the following formats:

- Images: JPG, PNG, and SVG
- Documents: DOC, DOCX, PDF, and ODT
- Spreadsheets: XLS, XLSX, and ODS
- Text files: TXT

Each suggestion can have a maximum of five attachments, with a maximum file size of 5 MB per attachment.

## Stop and restart Forslagskasse

To stop the services, run:

```bash
docker compose down
```

To start them again without rebuilding the image:

```bash
docker compose up -d
```

The database and uploaded files are stored in the project directories `postgres_data/` and `media/`. The data therefore remains in place when the containers are stopped or replaced. Back up these directories to preserve your data.

## Troubleshooting

If installation or startup fails:

1. Check that Docker is running.
2. Make sure you are running the commands from the project directory.
3. Read the error messages in the terminal.
4. Check that `.env` has been created and contains valid values.

You can inspect the Django service logs with:

```bash
docker compose logs django-web
```

If the problem persists, you can report it on the project's GitHub page.

## Further information

This project is built with Django. More information about the framework is available in [the Django documentation](https://docs.djangoproject.com/).