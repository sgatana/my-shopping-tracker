[![Build Status](https://travis-ci.org/sgatana/ShoppingListAPI.svg?branch=develop)](https://travis-ci.org/sgatana/ShoppingListAPI)
[![Coverage Status](https://coveralls.io/repos/github/sgatana/ShoppingListAPI/badge.svg?branch=develop)](https://coveralls.io/github/sgatana/ShoppingListAPI?branch=develop)
[![Code Health](https://landscape.io/github/sgatana/ShoppingListAPI/develop/landscape.svg?style=flat)](https://landscape.io/github/sgatana/ShoppingListAPI/develop)

# ShoppingListAPI
An API developed in flask restful that allows you to create a shopping list and add items on different shopping lists.
It is using token based auth to enhance security on users' lists

## Getting Started
### Prerequisites
You need to have the following installed in you PC
````
1. Python 2.7+ (preferably python 3.4 and above)
2. Flask
3. PostgreSQL
4. Flask SQL Alchemy
install them using pip command (i.e pip install flask)
````
### Installing
To install the project to your local PC, clone the repo by running

``
git clone  https://github.com/sgatana/ShoppingListAPI.git
``

Once you have cloned the project, navigate to the directory and install the requirements.

```
    $ cd ShoppingListAPI
    $ pip install -r requirequirements.txt
```
## Database Setup
Create the database for the API project, for this project we are using postgresql database.

```
$ psql:
# create database API;
```
## Running Tests
Prepare the environment for running test by running the following commands on your terminal
```
export DB_URL='postgresql://postgres@username:password/-databasenname-'
export SECRET_KEY = 'this-should-be-very-secret'
```
* if you are using windows, user **_set_** instead of _**export**_

Run the tests using nose
``
    nosetests -v --with-coverage
``
## Running the Application
Set the environment to run your application
```
export FLASK_CONFIG=development
export SECRET_KEY='this-is-very-secret'
export DB_URL='postgresql://postgres@username:password/-databasenname-'
```
* Run the application using:

```
python run.py runserver
```

Access the application on your browser using :


```
    127.0.0.1:5000
```
![](.README_images/c2c95f56.png)


## Endpoints
```
/regiter
/login
/ShoppingList
/ShoppingList/{id}/items
/shoppinglist/{id}
/item{id}
```



## Deployment

Deloy the application to heroku.

```
   Read the doc on how to deploy the application to heroku on:
   
    https://www.heroku.com/python 
```

