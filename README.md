
# market simulator

This is a web application that lets users buy and sell resources in a market. 

## Usage

Access the web app with this site <br>
https://mariusfacktor.github.io/market_simulator/

1) Type in a Session key at the top. This creates a new session with that unique key or joins an existing one. 
2) In the left box, create a new person or select an existing person. 
3) Enable admin mode to create a new resource. You can also deposit or withdraw resources or money. 
4) In the center box you can see your person's resources and sell them. When you sell a resource it will be placed on the market as a listing, and you can cancel this listing if you want to. 
5) In the right box you can buy resources. The market simply sorts the sale listings by the lowest price. 

<div float="left">
    <img src="./images/example.png" alt="example" height="400">
</div>
<br>

## Tech stack

Here I'll list the tools and components I used to build and host this web app. 

<ins>Backend</ins>

Sqlite <br>
SQLAlchemy ORM <br>
Flask <br>
Postman for testing HTTP API calls <br>
Gunicorn <br>
Nginx <br>
Google Cloud VM to host the backend server <br>
Duck DNS to map the VM's external IP address to a domain name <br>
Let's Encrypt to create an SSL Certificate <br>

<ins>Frontend</ins>

Node.js <br>
Vue.js <br>
Axios to make HTTPS requests <br>
PrimeVue UI Component Library <br>
GitHub Pages to deploy the frontend <br>
