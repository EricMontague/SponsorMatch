# SponsorMatch

> SponsorMatch is a Flask application that connects event organizers with companies who are looking to sponsor events.
![Coveralls github](https://img.shields.io/coveralls/github/EricMontague/SponsorMatch)

[Live Application Here](https://sponsormatch.herokuapp.com/)

After reading Miguel Grinberg's Flask: Web Development, I wanted to build off of the concepts from his book and build my own Flask application. While looking for ideas about what type of application to build, I stumbled upon an old post on Quora where the founder of Eventbrite was talking about how it can be difficult for event organizers to find sponsors for their events. This inspired me to build a web application dedicated to solving this problem. 
<br>

# Production: 
If you're using the live application and you choose to register as a sponsor, use **4242 4242 4242 4242** as the credit card number when purchasing packages as this is one of Stripe's test credit card numbers. The rest of the purchase form can be filled in with whatever numbers you wish to complete your purchase.
<br>


# Development:
- First you need to [register with Stripe](https://stripe.com/) and then [obtain your API keys](https://stripe.com/docs/keys) from your Stripe dashboard
- Next you will need [download Elasticsearch](https://www.elastic.co/downloads/elasticsearch) if you don't have it installed on your computer already. I built this application using version 7.6, but I believe that any subversion of version 7 should work


### Environment Variables:
- Regardless of how you choose to run the application, you will need to setup some environment variables
- If choosing to run the application using Docker, these will be held in a file named .docker-env
- If choosing to run the application using the Werkzeug development server, I recommend storing these in a .flask-env file
- Note that designating a database url is optional since the application will default to using a SQLite database if no database url is provided
- The variables you will need to setup are as follows:




### Running with Docker (Preferred)
```sh
&#8594; git clone https://github.com/EricMontague/SponsorMatch.git
&#8594; touch .docker-env
&#8594; docker-compose up
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
DATABASE_URL= (optional)
ELASTICSEARCH_URL=

```

### Running with the Werkzeug development server

```sh
&#8594; git clone https://github.com/EricMontague/SponsorMatch.git
&#8594; touch .flask-env
&#8594; [insert command to start up Elasticsearch]
&#8594; flask setup-environment --fake-data (optional flag if you want to insert fake data into the database)
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

### Features:
 - Organizers can create events as well as sponsorship packages that can be purchased in the app by potential sponsors through the Stripe API. 
 - Organizers have an area where they can manage their events, make changes, and see what purchases have been made.
 - Sponsors have an area where they can review past purchases
 - Sponsors can save events they're interested in to a personalized list
 - The app offers basic search functionality for finding events, powered by Elasticsearch
 
<br>

## Technologies
 - Flask
 - Bootstrap
 - Elasticsearch
 - jQuery
 - Stripe API
 - Postgresql

<br>

