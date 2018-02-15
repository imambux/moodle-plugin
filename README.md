# A Python built Middleware for Moodle Web services
>Lightweight client for Moodle REST web services

[![Moodle Plugin Directory](http://img.shields.io/badge/moodle-plugin-orange.svg)](https://localhost:5001)

## Requirements

- Linux/Windows
- Python 3.6
- MySQL

## Enable Webservices
Login to your moodle, go to `Site administration -> Plugins -> Web services -> Overview` and follow the instructions to enable web services and generate authorization token. Make sure to check the following while going through this process:

- Activate REST protocol
- Assign a service to the token which has all the functions. *So that, call of any capability can get response from your moodle.*

## Run Middleware
1. Clone the git repository.
2. Install the dependent libraries (packages) from [requirements.txt](requirements.txt).
3. Make sure that MySQL Server is up and running with the following credentials:
*If you want the plugin to adapt MySQL server settings of your own then setup your credentials in moodle-middleware/local_settings.py*

        host = "127.0.0.1"
        database = "moodle-middleware"
        user = "root"
        pass = ""
        
4. Deploy the sql file moodle-middleware/database/moodle-middleware.sql on MySQL Server to create moodle table in the database.
5. Run the plugin:
    - Windows

            python main.py
        - App runs on Flask Server at "http://localhost:5000"
        - For Development Puspose only!        
    - Linux
    
            ./start.sh
        - App runs on Gunicorn Server at "http://localhost:5001"*

## Usage
Refer to this [documentation](documentation/API%20Documentation.odt) for api calls.
