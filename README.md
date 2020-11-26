# SponsorMatch

> SponsorMatch is a Flask application that connects event organizers with companies who are looking to sponsor events.

![code-coverage](https://img.shields.io/badge/coverage-66%25-yellowgreen)
![last-commit](https://img.shields.io/badge/last%20commit-November%202020-blue)

<br>

After reading Miguel Grinberg's Flask: Web Development, I wanted to build off of the concepts from his book and build my own Flask application. While looking ideas, I stumbled upon an old post on Quora where the founder of Eventbrite mentioned how it can be difficult for event organizers to find sponsors for their events. This inspired me to build, [SponsorMatch](https://sponsormatch.herokuapp.com/), a web application dedicated to solving this problem. 
<br>
<br>

## Using the live application: 
- If you're using the live application and you choose to register as a sponsor, use **4242 4242 4242 4242** as the credit card number when purchasing packages as this is one of Stripe's test credit card numbers. The rest of the purchase form can be filled in with whatever numbers you wish to complete your purchase.
<br>

## Development:
- First you need to [register with Stripe](https://stripe.com/) and then [obtain your API keys](https://stripe.com/docs/keys) from your Stripe dashboard
- Next you will need [download Elasticsearch](https://www.elastic.co/downloads/elasticsearch) if you don't have it installed on your computer already. I built this application using version 7.6, but I believe that any subversion of version 7 should work
<br>



### Running with Docker (Preferred)
```sh
➜ git clone https://github.com/EricMontague/SponsorMatch.git
➜ touch .docker-env
➜ docker-compose up
```


`.docker-env`

```sh
FLASK_APP=
FLASK_CONFIG=
MAIL_USERNAME=(optional) - Use if you want to utilize email functionality
MAIL_PASSWORD=(optional) - Use if you want to utilize email functionality
ADMIN_EMAIL=(optional)
SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
DATABASE_URL= postgresql://sponsormatch:password@database:5432/sponsormatch_db
ELASTICSEARCH_URL=http://elasticsearch:9200 (Elasticsearch defaults to listening on port 9200, but adjust this to your needs)

```
<br>

### Running with the Werkzeug development server

```sh
➜ git clone https://github.com/EricMontague/SponsorMatch.git
➜ touch .flask-env
➜ [insert command to start up Elasticsearch]
➜ flask setup-environment --fake-data (optional flag if you want to insert fake data into the database)
```


`.flask-env`

```sh
FLASK_APP=
FLASK_CONFIG=
MAIL_USERNAME=(optional) - Use if you want to utilize email functionality
MAIL_PASSWORD=(optional) - Use if you want to utilize email functionality
ADMIN_EMAIL=(optional)
SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
DATABASE_URL= (optional)
ELASTICSEARCH_URL=

```
<br>

## Testing
```sh
➜ flask run-tests
```
<br>
<br>

## Core Features
 - Organizers can create events as well as sponsorship packages that can be purchased in the app by potential sponsors through the Stripe API. 
 - Organizers have an area where they can manage their events, make changes, and see what purchases have been made.
 - Sponsors have an area where they can review past purchases
 - Sponsors can save events they're interested in to a personalized list
 - The app offers basic search functionality for finding events, powered by Elasticsearch
 
<br>

## Technologies Used
 - Flask
 - Bootstrap
 - Elasticsearch
 - jQuery
 - Stripe API
 - SQLite/Postgresql


