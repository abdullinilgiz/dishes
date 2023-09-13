# Food and dishes
### Project description
With the help of the service, users can publish recipes, subscribe to the publications of other users, add favorite recipes to the list of favorites, and before going to the store to download a list of products needed to prepare the selected dishes.

### Main features
* Work with recipes. View, publish, add to favorites, download.
* Administration panel for site management.
* Data retrieval via API.

### Tech stack
  
 - Python  
 - Django, DRF, ORM
 - Docker
 - PostgreSQL


### Running the project on a Linux server
* Install Docker:
```
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
sudo systemctl status docker
```
* Install and configure nginx on a free port (see nginx.default.example):
```
sudo apt install nginx -y
sudo systemctl start nginx
sudo nano /etc/nginx/sites-enabled/default
sudo nginx -t
sudo service nginx reload
```
* Create a folder foodgram and copy the file docker-compose.production.yml and the data folder into it
* In the foodgram folder, create and populate the .env environment variables file (see env.example)
* Start docker compose:
```
sudo docker compose -f docker-compose.production.yml up -d
```
* Perform migrations, build backend static files and copy them to /backend_static/static/:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/dishes/collected_static/. /backend_static/static/
```
* Load data into the database:
```
docker compose exec -it backend python manage.py import_ingredients
```
* Create a superuser for admin:
```
docker compose exec -it backend python manage.py createsuperuser
```

### API request examples:
* Create new user (POST):
  
  - api/users/
```
{
  "email": "donald@email.com",
  "username": "vasya.pupkin",
  "first_name": "Donald",
  "last_name": "Brew",
  "password": "11111one"
}

``` 
* Receive a token for authentication (POST): 

  - api/token/login/
```
{
  "password": "11111one",
  "email": "donald@email.com"
}

```
* Create recipe (POST)
  - api/recipes/
```
{
  "image": "data:image/png;base64,",
  "name": "string",
  "text": "string",
  "cooking_time": 1,
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ]
}
```
* List recipes (GET)
  - api/recipes/
  - query_params:
```
page	- integer.  Page number.
limit	- integer. Number of objects on the page.
is_favorited - integer Enum: 0 1. Recipes from the favorite list.
is_in_shopping_cart	- integer Enum: 0 1. Reciepes from shopping cart.
author - integer. Recipes of the author with the given id.
tags	Array of strings. Recipes with the following tags (slug).
```
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
* List ingredients (GET):
  - api/ingredients/
  - query_param:
```
name - string. Search by partial occurrence at the beginning of the ingredient name.
```
```
[
  {
    "id": 0,
    "name": "Cucumber",
    "measurement_unit": "kg"
  }
]
```
* List tags (GET):
  - api/tags/
```
[
  {
    "id": 0,
    "name": "Breakfast",
    "color": "#00FF00",
    "slug": "breakfast"
  }
]
```
* Get ingredient (GET):
```
api/ingredients/{id}/
```
* Get tag (GET):
```
api/tags/{id}/
```
* Get a recipe (GET), edit (PATCH) and delete (DELETE) your recipe:
  - api/recipes/{id)
* Add (POST) or remove (DELETE) a recipe from your shopping cart:
  - api/recipes/{id}/shopping_cart/
* Download shopping list (GET):
  - api/recipes/download_shopping_cart/
* Add (POST) or remove (DELETE) a recipe from favorites:
  - api/recipes/{id}/favorite/.
* Subscribe (POST) and unsubscribe (DELETE) to an author:
  - api/users/{id}/subscribe/
* View all subscriptions:
  - api/users/subscriptions/

### Author:
Abdullin Ilgiz (backend, API)


