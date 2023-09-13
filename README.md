# Foodgram
site: foodanddishes.sytes.net
### About the project
Platform where people can share their recipes.
### What have been done
Backend was written using Django, DRF, see /docs/ to see specification.
### Tech stack
```
Python

Django (ORM + PostgreSQL, DRF + Djoser)

Docker

JavaScript(React)
```

### Requests example
```json
POST /api/recipes/:

{
  "ingredients": [
    {
      "id": 1,
      "amount": 1
    },
    {
      "id": 2,
      "amount": 1
    }
  ],
  "tags": [
    1,
    2
  ],
  "name": "string",
  "text": "string",
  "cooking_time": 12
}
```

`
GET /api/users/?limit=1&page=1:
`

`
GET /api/users/me/
`

`
GET /api/recipes/
`

### Author
Abdullin Ilgiz 

`
abdyllin-ilgiz@mail.ru
`

