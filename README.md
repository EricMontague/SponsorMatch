# SponsorMatch
After reading Miguel Grinberg's Flask: Web Development, I wanted to build off of the concepts from his book and build my own Flask application. After reading about how it can be difficult for event organizers to find sponsors for their events, I decided to create a small project whose goal was to solve this problem. As the short description at the top says, SponsorMatch is an application that connects event organizers with companies who are looking to sponsor events. Building this application has been a great learning experience and my goal is to continue to polish it and possibly add new features in the future.

### Using the application on Heroku: 
If testing the application out as an event organizer, you will be asked to provide a credit card number to complete your registration. Use 4242 4242 4242 4242 as the credit card number as this is one of Stripe's test credit card numbers. Also, the application will send real emails, so be sure to type in your email and not someone else's upon registering.

<br>

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
 - SQLite3

<br>

## Todo
 - Deploy to Heroku
 - Find a different fake package that supports accurate city, state combinations.
 - Upgrade the version of Elasticsearch to the latest version
 - Refactor the backend, specifically splitting up the main blueprint.
 - Refactor the HTML to look more structured and easy to follow
 - Refactor the frontend(clean up the CSS) to make the application responsive for mobile and fix the issues with image resizing
 - Add a feature for discovering nearby events
 - Add tests for the Stripe API

