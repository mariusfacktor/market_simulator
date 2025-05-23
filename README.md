
# market simulator

This is a web application that lets users buy and sell resources in a market. 

## Usage

Access the web app with this site <br>
https://mariusfacktor.github.io/market_simulator/

1) In the Session panel, type in a session key. This creates a new session or joins an existing one. 
2) In the Admin panel, create new people and new resources. 
3) Select a person and resource using Person and Resource panels.
4) The Assets panel shows the money and resources of the selected person. 
5) The Sell and Buy panels lets the selected person sell or buy the selected resource. Leave the price box blank to immediately sell or buy at market price, or pick your own price to create a limit order that will queue on the market. 

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
freedns.afraid.org to map the VM's external IP address to a domain name <br>
Let's Encrypt to create an SSL Certificate <br>

<ins>Frontend</ins>

Node.js <br>
Vue.js <br>
Axios to make HTTPS requests <br>
PrimeVue UI Component Library <br>
GitHub Pages to deploy the frontend <br>
