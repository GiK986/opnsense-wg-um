# OPNsense WireGuard User Management with Django 

This project provides a user management interface for OPNsense WireGuard VPN using Django.  
It allows you to easily create, update, delete and generate .conf file for WireGuard VPN users in OPNsense through a web interface, using [OPNsense API Reference](https://docs.opnsense.org/development/api.html#introduction).

# Getting Started

 To get started with this project, follow the steps below:

 ## Prerequisites

 Before installing this project, you must have the following installed:

 - Python 3
 - pip
 - openssl
 - WireGuard tools
 - OPNsense with WireGuard plugin installed
 - OPNsense API key and secret

 ### Generating an API Key and Secret in OPNsense
 
 To generate an API key and secret in OPNsense, follow the steps below:
 1. Navigate to **System > Access > Users**.
 2. Click on the **Edit** button next to the user for whom you want to generate an API key.
 3. Scroll down to the **API Keys** section and click on the "+" icon to create a new API key.  
 
 When the key is created, you will receive a (single download) with the credentials in one text file (ini formatted).  
 Copy the contents of the file to a safe location.
 The contents of this file look like this:

 > key=w86XNZob/8Oq8aC5r0kbNarNtdpoQU781fyoeaOBQsBwkXUt  
 > secret=XeD26XVrJ5ilAc/EmglCRC+0j2e57tRsjHwFepOseySWLM53pJASeTA3
 
 The `key` is the API key and the `secret` is the API secret needed to create a new OPNsense API client.
 
 ### Installing WireGuard Tools
 
 #### Linux
 
 On Ubuntu or Debian-based systems, you can install the WireGuard tools by running:
 
 ``` bash
 sudo apt-get update  
 sudo apt-get install wireguard-tools
 ```
 
 For other Linux distributions, please see the [WireGuard installation instructions](https://www.wireguard.com/install/).
 
 #### Windows
 
 You can download and install the WireGuard tools for Windows from the [WireGuard website](https://www.wireguard.com/install/).  
 Follow the instructions on the website to download and install the software.
 
 #### macOS
 
 You can install the WireGuard tools on macOS using [Homebrew](https://brew.sh/).  
 First, install Homebrew by running:
 
 ``` bash
 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
 ```

 Then, install the WireGuard tools by running:
 
 ``` bash
 brew install wireguard-tools
 ```

 For more information on installing the WireGuard tools on macOS, please see the [WireGuard installation instructions](https://www.wireguard.com/install/).

 ## Installation locally

 To install this project, follow the steps below:

 1. Clone this repository to your local machine.

    ```bash
    git clone https://github.com/GiK986/opnsense-wg-um.git
    ```
2. Navigate to the cloned repository:
    
    ```bash
    cd opnsense-wg-um
    ```

3. Create a virtual environment for the project by running:
    
    ``` bash
    python -m venv venv
    ```
    
4. Install the required dependencies:  
 
     ``` bash
     pip install -r ./src/requirements.txt
     ```

5. Rename .env.dev-sample to .env.dev and .env.dev.db-sample to .env.dev.db. Update the environment variables.
    - generate a secret key by running:
     ``` bash
     sed -i "" "s/^DJANGO_SECRET_KEY=.*$/DJANGO_SECRET_KEY=$(openssl rand -hex 32)/" .env.dev
     ```
 
6. Migrate the database by running:  

     ``` bash
     cd ./src
     python manage.py migrate
     ```

7. Create a superuser account by running:

     ``` bash
     python manage.py createsuperuser
     ```
 
8. Finally, run the development server using:
 
     ``` bash
     python manage.py runserver 0.0.0.0:8000
     ```
 
 You can then access the application by navigating to [`http://localhost:8000`](http://localhost:8000) in your web browser.

 ## Docker Image Build  
 
 ### Build for ARM64 
 
 ```bash
 docker build --platform=linux/arm64 -t gik986/opnsense-wg-um:latest-arm64 .
 ```
 
 ### Build for AMD64
 
 ```bash
 docker build --platform=linux/amd64 -t gik986/opnsense-wg-um:latest-amd64 .
 ```

## Using docker-compose (recommended)

### Development

Uses the default Django development server.

1. Rename *.env.dev-sample* to *.env.dev*.
2. Update the environment variables in the *docker-compose.yml* and *.env.dev* files.
3. Build the images and run the containers:

    ```sh
    docker-compose up -d --build
    ```

    Test it out at [http://localhost:8000](http://localhost:8000). The "src" folder is mounted into the container and your code changes apply automatically.

### Production

Uses gunicorn + nginx.

1. Rename *.env.prod-sample* to *.env.prod* and *.env.prod.db-sample* to *.env.prod.db*. Update the environment variables.
2. Build the images and run the containers:

    ```sh
    docker-compose -f docker-compose.prod-nginx.yml up -d --build
    ```

    Test it out at [http://localhost](http://localhost). No mounted folders. To apply changes, the image must be re-built.


## License

This project is licensed under the Apache-2.0 license.
