# SponsorMatch

> SponsorMatch is a Flask application that connects event organizers with companies who are looking to sponsor events.

![code-coverage](https://img.shields.io/badge/coverage-66%25-yellowgreen)
![last-commit](https://img.shields.io/badge/last%20commit-Nov%202020-blue)

<br>


![Image of Homepage](https://github.com/EricMontague/SponsorMatch/blob/master/app/static/images/SponsorMatch_Screenshot.png)

<br>
After reading Miguel Grinberg's Flask: Web Development, I wanted to build off of the concepts from his book and build my own Flask application. While looking for ideas, I stumbled upon an old post on Quora where the founder of Eventbrite mentioned how it can be difficult for event organizers to find sponsors for their events. This inspired me to build, [SponsorMatch](https://sponsormatch.herokuapp.com/), a web application dedicated to solving this problem. 
<br>
<br>

## Using the live application: 
- If you're using the live application and you choose to register as a sponsor, use **4242 4242 4242 4242** as the credit card number when purchasing packages as this is one of Stripe's test credit card numbers. The rest of the purchase form can be filled in with whatever numbers you wish to complete your purchase.
<br>

## Development:
- First you need to [register with Stripe](https://stripe.com/) and then [obtain your API keys](https://stripe.com/docs/keys) from your Stripe dashboard
- Next you will need to [download Elasticsearch](https://www.elastic.co/downloads/elasticsearch) if you don't have it installed on your computer already. I built this application using version 7.6, but I believe that any subversion of version 7 should work
- If you choose to run the application using Docker, it will be running at http://localhost:8000. If you run it with the werkzeug development server, it will be available at http://localhost:5000
<br>



### Running with Docker
```sh
➜ git clone https://github.com/EricMontague/SponsorMatch.git
➜ cd Sponsormatch
➜ touch .docker-env (add environment variables here)
➜ docker-compose up
```


`.docker-env`

```sh
FLASK_APP=sponsormatch.py
FLASK_CONFIG=docker
MAIL_USERNAME=(optional) - Use if you want to utilize email functionality
MAIL_PASSWORD=(optional) - Use if you want to utilize email functionality
ADMIN_EMAIL=(optional)
SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
DATABASE_URL= postgresql://sponsormatch:password@database:5432/sponsormatch_db
POSTGRES_USER=sponsormatch
POSTGRES_PASSWORD=password
POSTGRES_DB=sponsormatch_db
ELASTICSEARCH_URL=http://elasticsearch:9200 

```
<br>

### Running with the Werkzeug development server
- Open a tab in your terminal, navigate to the directory that contains Elasticsearch and run ```elasticsearch-7.6.0/bin/elasticsearch``` in order to start
up Elasticsearch
- Then, in a new tab, sequentially enter the commands below 

```sh
➜ git clone https://github.com/EricMontague/SponsorMatch.git
➜ cd Sponsormatch
➜ python3 -m venv venv
➜ source venv/bin/activate
➜ pip install --upgrade pip && pip install -r requirements.txt
➜ touch .env (add environment variables here)
➜ flask setup-environment --fake-data (optional flag if you want to insert fake data into the database)
➜ flask run
```


`.env`

```sh
FLASK_APP=sponsormatch.py
FLASK_ENV=development
FLASK_DEBUG=1
MAIL_USERNAME=(optional) - Use if you want to utilize email functionality
MAIL_PASSWORD=(optional) - Use if you want to utilize email functionality
ADMIN_EMAIL=(optional)
SECRET_KEY=
STRIPE_PUBLISHABLE_KEY=
STRIPE_SECRET_KEY=
DATABASE_URL= (optional)
ELASTICSEARCH_URL=http://localhost:9200

```
<br>

## Testing
```sh
➜ python run-tests.py
```
<br>
<br>

## Core Features
 - Organizers can create events as well as sponsorship packages that can be purchased in the app by potential sponsors through the Stripe API
 - Organizers have an area where they can manage their events, make changes, and see what purchases have been made
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


