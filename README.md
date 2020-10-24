# Project 1

Web Programming with Python and JavaScript

# About Site

This is a site for project1 from CS50W on EDX. This is site is for book review. The site has 5000 books for review.
People can search the site only if they are logged in. People can delete the account if they don't want to use the site anymore. Users can logout there session will be cleared when the logout. Users cannot login multiple times in a 
session as the index page cleares the session when reloaded. Users can submit reviews for book and rate it out of 5.
Users are restricted to submit blank review and also restricted to review multiple times per book. Api can be called using /api/+<isbn> but the isbn with no reviews or no book at all will return an error .No review book error is  because rowproxy don't allow value assigning using python code.  Requirements are freezed into requirements.txt. Site is hosted on heroku's free tier plan.
The site link: https://book-flask-project.herokuapp.com/

# What's included?

* Users can register and will be automatically returned to login page.
* Users can Login.
* Search page has delete and logout button. Users an search from a library of 5000 books.
* Results page shows all the books that matches the search but limits to 10 books.
* Book page contains book cover on top and a link to goodreads page of the book.
* Two blocks in books page shows the info in database and ratings from goodreads API.
* Has a review box and shows reviews.
