# Theatre API service

_Django REST Framework  API project for theatre service_


## ___Instalation___

_Python3 must be already installed_

```shell
git clone https://github.com/Vitalii-Khmura/theatre-APi-service.git
cd theatre_api_service
python -m venv venv
venv/Scripts/activate
pip innstall requirements.txt

python manage.py runserver
```

Then you should create an ```.env``` file and enter in this file ```SECRET_KEY```
and your POSTGRES DB 

```shell
    POSTGRES_HOST=<your_postgres_host>
    POSTGRES_USER=<your_postgres_user>
    POSTGRES_NAME=<your_postgres_name>
    POSTGRES_PASSWORD=<your_postgres_password>
    
    
    SECRET_KEY=<your_secret_key>
```

All Environment variables that should be in .env file are specified in the .env_sample file

Finally, perform the migration, write next command in terminal:

```shell
    python manage.py makemigrations
    python manage.py migrate
```

After loading data from fixture you can use following superuser (or create another one by yourself):
* Login: ```test_user```
* Password:```admin```


## ___Run with docker___

_Docker should be installed_

```shell
    docker-compose build
    docker-compose up
```

## ___Feauteres___

- JWT authentication
- Admin panel /admin/
- Documentation is located at /api/doc/swagger/
- Managing actors & genres
- Creating performance
- Creating plays with actor and genres
- Creating Theatre Hall
- Make a reservation




