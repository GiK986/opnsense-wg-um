# OPNsense WireGuard User Management with Django 

This project provides a user management interface for OPNsense WireGuard VPN using Django.  
It allows you to easily create, update and delete WireGuard VPN users in OPNsense through a web interface, using OPNsense API client.

## Getting Started

To get started with this project, follow the steps below:

### Installation

First, install the required dependencies by running:

> pip install -r requirements.txt

### Secret Key using *openssl*

Generate a secret key and save it to `secret_key.txt` by running:

> openssl rand -hex 32 >> secret_key.txt

### Database Migration

Migrate the database by running:

> python manage.py migrate

### Super User

Create a superuser account by running:

> python manage.py createsuperuser

### Run Server

Finally, run the development server using:

> python manage.py runserver 0.0.0.0:8000

You can then access the application by navigating to `http://localhost:8000` in your web browser.


## Docker Image Build  

### Build for ARM64 

> docker build --platform=linux/arm64 -t gik986/opnsense-wg-um:latest-arm64 .

### Build for AMD64

> docker build --platform=linux/amd64 -t gik986/opnsense-wg-um:latest-amd64 .

## Contributing

If you would like to contribute to this project, please follow the guidelines in CONTRIBUTING.md.

## License

This project is licensed under the MIT License.
