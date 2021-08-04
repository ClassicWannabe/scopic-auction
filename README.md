# Auction application

## Tech

Auction application uses a number of open source projects to work properly:

- [ReactJS] - a JavaScript library for building user interfaces
- [Material UI] - component library to build faster, beautiful, and more accessible React applications
- [Django] - a high-level Python Web framework
- [Django REST] - a powerful and flexible toolkit for building Web APIs
- [PostgreSQL] - a powerful, open source object-relational database

## Installation
Auction application requires [Node.js](https://nodejs.org/) and [PostgreSQL](https://www.postgresql.org/) to run.
* Go to the project folder:  
```sh
$ cd <project_folder>
```
Backend:  
* Go to backend application:  
```
$ cd <project_folder>/backend
```
* Create virtual environment for the project using virtualenvwrapper or other:  
```sh
$ mkvirtualenv env
```
* Install packages listed in requirements.txt:  
```sh
$ pip install -r requirements.txt
```
* Create .env file in the backend folder listing following variables:
```sh
SECRET_KEY=...
DEBUG=...
DB_HOST=...
DB_NAME=...
DB_USER=...
DB_PASS=...
```
* Create admin user to log in to the admin panel:  
```
$ python manage.py createsuperuser
```
Frontend:
* Go to frontend application:
```
$ cd <project_folder>/frontend
```
* Install packages from package.json:  
```
$ npm install
```
* Create production build:  
```
$ npm run build
```
Run local server from the backend folder application:  
```
$ python manage.py runserver
```
Open http://127.0.0.1:8000/ in the browser of your choice. To access the admin panel go to http://127.0.0.1:8000/trYmXDMI9XA7G9ce6wD4Su+yFfTDET1p8QW46hCyYTI=/

To populate fake data in DB you can run the following command:  
```
$ python populate.py
```
This command creates 5 users with 1 superuser (username: 'user1', password: '123456789') and by default 20 auction items with random fake data.
