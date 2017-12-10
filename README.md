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
    $ pip install -r requirements.txt
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
![](https://github.com/sgatana/ShoppingListAPI/blob/develop/docs/API.png)

## Endpoints

 | URL | Methods | Description | Authentication |
 | ----| ---- | --- | --- |
 | /register | POST | Allow users to register | False
 | /login | POST | Allow registered users to login and generate token | False |
 | /Shoppinglist | POST | Allow user to create a new shopping list | True |
 | /Shoppinglist | GET | Allow users to get list of shopping lists | True |
 | /user | GET | Get the current user | True |
 | /Shoppinglist/{id} | GET | Get a shoppinglist by using unique id | True |
 | /Shoppinglist/{id} | PUT | Update a shopping list given the id of the shopping list | True |
 | /Shoppinglist{id} | DELETE | Delete shopping list given the unique id | True |
 | /Shoppinglist/{id}/Items | POST | Create an item to specific shoppinglist | True |
 | /Shoppinglist/{id}/Items | GET | GET items of specific shoppinglist | True |
 | /Shoppinglist/{list_id}/item/{id} | PUT | Update an item given unique id | True |
 | /Shoppinglist/{list_id}/item/{id} | GET | Get an item given unique id | True |
 | /Shoppinglist/{list_id}/item/{id} | DELETE | Delete an item given unique id | True |



 
 
 
 
 
 
 


## Deployment

Deloy the application to heroku.

```
   Read the doc on how to deploy the application to heroku on:
   
    https://www.heroku.com/python 
```

