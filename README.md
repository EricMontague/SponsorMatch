# SponsorMatch
After reading Miguel Grinberg's Flask: Web Development, I wanted to build off of the concepts from his book and build my own Flask application. After reading about how it can be difficult for event organizers to find sponsors for their events, I decided to create a small project whose goal was to solve this problem. As the short description at the top says, SponsorMatch is an application that connects event organizers with companies who are looking to sponsor events. Building this application has been a great learning experience and my goal is to continue to polish it and possibly add new features in the future.
<br>
<br>
<br>
### Features:
 - Organizers can create events as well as sponsorship packages that can be purchased in the app by potential sponsors through the Stripe API. 
 - Organizers have an area where they can manage their events, make changes, and see what purchases have been made.
 - Sponsors have an area where they can review past purchases
 - Sponsors can save events they're interested in to a personalized list
 - Basic search functionality for finding events, powered by Elasticsearch


## Technologies
 - Flask
 - Bootstrap
 - Elasticsearch
 - jQuery
 - Stripe API
 - SQLite3


## Todo
 - Deploy to Heroku
 - Upgrade the version of Elasticsearch to the latest version
 - Refactor the backend, specfically splitting up the main blueprint.
 - Refactor the frontend to make the application responsive for mobile and fix the issues with image resizing
 - Add a feature for discovering nearby events
 - Add tests for the Stripe API

