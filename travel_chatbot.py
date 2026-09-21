import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import webbrowser
import os
import re
import time
import math
import sqlite3
import difflib
from datetime import datetime


# ============================================================
# API KEYS
# ============================================================
# You can add these later.
#
# OpenAI:
# OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"
#
# Google Places:
# GOOGLE_PLACES_API_KEY = "YOUR_GOOGLE_PLACES_API_KEY"
#
# The application uses live providers and shows an unavailable state when they return no data.

OPENAI_API_KEY = ""
GOOGLE_PLACES_API_KEY = ""
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_ENABLED = os.environ.get("OLLAMA_ENABLED", "1") == "1"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), "travel_chatbot.db")
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

PORT = 8000

CITY_COORDINATES = {
    "hyderabad": (17.3850, 78.4867),
    "goa": (15.4909, 73.8278),
    "ooty": (11.4102, 76.6950),
    "bangalore": (12.9716, 77.5946),
    "bengaluru": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.6139, 77.2090),
}

DESTINATION_ALIASES = {
    "otty": "ooty",
    "hyderbad": "hyderabad",
    "hydrabad": "hyderabad",
    "banglore": "bangalore",
}


# ============================================================
# LIVE DATA PROVIDERS
# ============================================================

HOTELS = {
    "hyderabad": [
        {
            "name": "Royal Residency",
            "price": 2500,
            "rating": 4.5,
            "type": "Hotel"
        },
        {
            "name": "Grand Palace",
            "price": 3800,
            "rating": 4.7,
            "type": "Hotel"
        },
        {
            "name": "Budget Inn",
            "price": 1800,
            "rating": 4.1,
            "type": "Budget Hotel"
        },
        {
            "name": "City Comfort Hotel",
            "price": 3200,
            "rating": 4.3,
            "type": "Hotel"
        }
    ],

    "goa": [
        {
            "name": "Sea View Resort",
            "price": 4200,
            "rating": 4.8,
            "type": "Resort"
        },
        {
            "name": "Palm Beach Hotel",
            "price": 3000,
            "rating": 4.4,
            "type": "Hotel"
        },
        {
            "name": "Goa Budget Stay",
            "price": 1900,
            "rating": 4.0,
            "type": "Budget Hotel"
        }
    ],

    "ooty": [
        {
            "name": "Hill Crown",
            "price": 2800,
            "rating": 4.6,
            "type": "Hotel"
        },
        {
            "name": "Lake View Hotel",
            "price": 3400,
            "rating": 4.5,
            "type": "Hotel"
        },
        {
            "name": "Green Nest",
            "price": 2100,
            "rating": 4.2,
            "type": "Hotel"
        }
    ],

    "bangalore": [
        {
            "name": "City Star Hotel",
            "price": 3000,
            "rating": 4.3,
            "type": "Hotel"
        },
        {
            "name": "Urban Comfort",
            "price": 2500,
            "rating": 4.2,
            "type": "Hotel"
        },
        {
            "name": "Royal Suites",
            "price": 4500,
            "rating": 4.7,
            "type": "Hotel"
        }
    ],

    "chennai": [
        {
            "name": "Marina Hotel",
            "price": 2800,
            "rating": 4.3,
            "type": "Hotel"
        },
        {
            "name": "Chennai Grand",
            "price": 3500,
            "rating": 4.5,
            "type": "Hotel"
        },
        {
            "name": "City Residency",
            "price": 2200,
            "rating": 4.0,
            "type": "Hotel"
        }
    ],

    "mumbai": [
        {
            "name": "Marine View Hotel",
            "price": 4500,
            "rating": 4.5,
            "type": "Hotel"
        },
        {
            "name": "Mumbai Comfort",
            "price": 3800,
            "rating": 4.2,
            "type": "Hotel"
        },
        {
            "name": "City Palace",
            "price": 5000,
            "rating": 4.7,
            "type": "Hotel"
        }
    ],

    "delhi": [
        {
            "name": "Capital Residency",
            "price": 2800,
            "rating": 4.3,
            "type": "Hotel"
        },
        {
            "name": "Delhi Grand",
            "price": 3500,
            "rating": 4.5,
            "type": "Hotel"
        },
        {
            "name": "Royal Delhi Hotel",
            "price": 4200,
            "rating": 4.6,
            "type": "Hotel"
        }
    ]
}


PLACES = {
    "hyderabad": [
        "Charminar",
        "Golconda Fort",
        "Hussain Sagar Lake",
        "Salar Jung Museum",
        "Ramoji Film City",
        "Qutb Shahi Tombs"
    ],

    "goa": [
        "Baga Beach",
        "Calangute Beach",
        "Fort Aguada",
        "Dudhsagar Falls",
        "Basilica of Bom Jesus",
        "Anjuna Beach"
    ],

    "ooty": [
        "Ooty Lake",
        "Botanical Garden",
        "Doddabetta Peak",
        "Tea Museum",
        "Rose Garden",
        "Avalanche Lake"
    ],

    "bangalore": [
        "Bangalore Palace",
        "Lalbagh Botanical Garden",
        "Cubbon Park",
        "ISKCON Temple",
        "Vidhana Soudha",
        "Wonderla"
    ],

    "chennai": [
        "Marina Beach",
        "Kapaleeshwarar Temple",
        "Fort St George",
        "Government Museum",
        "Besant Nagar Beach",
        "VGP Marine Kingdom"
    ],

    "mumbai": [
        "Gateway of India",
        "Marine Drive",
        "Elephanta Caves",
        "Colaba Causeway",
        "Juhu Beach",
        "Siddhivinayak Temple"
    ],

    "delhi": [
        "India Gate",
        "Red Fort",
        "Qutub Minar",
        "Lotus Temple",
        "Humayun's Tomb",
        "Akshardham Temple"
    ]
}


RESTAURANTS = {
    "hyderabad": [
        "Paradise Biryani",
        "Shah Ghouse",
        "Bawarchi",
        "Pista House"
    ],

    "goa": [
        "Fisherman's Wharf",
        "Vinayak Family Restaurant",
        "Cafe Chocolatti",
        "Thalassa"
    ],

    "ooty": [
        "Earl's Secret",
        "Place To Bee",
        "Hyderabad Biryani House"
    ],

    "bangalore": [
        "MTR",
        "Vidyarthi Bhavan",
        "Toit",
        "Truffles"
    ],

    "chennai": [
        "Murugan Idli Shop",
        "Saravana Bhavan",
        "Anjappar",
        "Dakshin"
    ],

    "mumbai": [
        "Britannia & Co.",
        "Cafe Madras",
        "Leopold Cafe",
        "Trishna"
    ],

    "delhi": [
        "Karim's",
        "Bukhara",
        "Saravana Bhavan",
        "Paranthe Wali Gali"
    ]
}


FOODS = {
    "hyderabad":
        "Hyderabadi Biryani, Haleem, Irani Chai, Osmania Biscuits and Double Ka Meetha",

    "goa":
        "Goan Fish Curry, Prawn Balchao, Bebinca and Pork Vindaloo",

    "ooty":
        "Homemade Chocolates, Ooty Tea, Varkey and fresh bakery items",

    "bangalore":
        "Masala Dosa, Idli, Vada, Bisi Bele Bath and Filter Coffee",

    "chennai":
        "Idli, Dosa, Pongal, Chettinad Cuisine and Filter Coffee",

    "mumbai":
        "Vada Pav, Pav Bhaji, Misal Pav and Bombay Sandwich",

    "delhi":
        "Butter Chicken, Chole Bhature, Paratha and Kebabs"
}


# ============================================================
# HTML USER INTERFACE
# ============================================================

HTML = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>AI Travel Assistant</title>


<style>

*{
    box-sizing:border-box;
}

body{
    margin:0;
    font-family:Inter,Segoe UI,Arial,sans-serif;
    background:#f5f7fb;
    color:#172033;
}


/* HEADER */

.header{
    background:linear-gradient(135deg,#102a56 0%,#126e8c 54%,#24a7a0 100%);
    color:white;
    padding:42px 20px 48px;
    text-align:center;
    box-shadow:0 10px 30px rgba(15,42,82,.18);
}

.header-nav{
    max-width:1150px;
    margin:0 auto 48px;
    display:flex;
    align-items:center;
    justify-content:space-between;
    text-align:left;
}

.brand{
    font-size:18px;
    font-weight:800;
    letter-spacing:.4px;
}

.nav-note{
    font-size:12px;
    opacity:.75;
    letter-spacing:1.3px;
    text-transform:uppercase;
}

.header h1{
    margin:0;
    font-size:clamp(32px,5vw,54px);
    letter-spacing:-1.5px;
}

.header p{
    max-width:680px;
    margin:16px auto 0;
    font-size:17px;
    opacity:.88;
    line-height:1.55;
}

.header h1 em{color:#8de4da;font-style:normal;}

.topic-chips{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:25px;}
.topic-chip{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.24);border-radius:999px;padding:8px 13px;font-size:12px;color:white;cursor:pointer;}
.topic-chip:hover,.topic-chip.active{background:#79b900;border-color:#a6df35;color:#102a56;}


/* MAIN */

.container{
    max-width:1150px;
    margin:30px auto 50px;
    padding:0 18px;
}


.grid{
    display:grid;
    grid-template-columns:360px 1fr;
    gap:20px;
}


/* LEFT PANEL */

.panel{
    background:white;
    border-radius:18px;
    padding:25px;
    box-shadow:0 12px 30px rgba(25,42,70,.08);
    border:1px solid #e7ebf2;
}

.panel h2{
    margin-top:0;
}

.panel-intro{color:#657083;font-size:14px;line-height:1.5;margin:-8px 0 18px;}

.quick-prompts{display:flex;flex-wrap:wrap;gap:7px;margin:8px 0 4px;}
.quick-prompts button{background:#eef6f6;color:#126e8c;padding:8px 10px;font-size:12px;border:1px solid #d9ecec;}
.quick-prompts button:hover{background:#dff2ef;color:#102a56;}


label{
    display:block;
    margin-top:13px;
    margin-bottom:5px;
    font-weight:bold;
    font-size:14px;
}


input,
textarea,
select{

    width:100%;

    border:1px solid #d5dce5;

    border-radius:8px;

    padding:12px;

    font-size:14px;

}


textarea{
    min-height:80px;
    resize:vertical;
}


button{

    border:none;

    background:#0866d8;

    color:white;

    padding:12px 16px;

    border-radius:8px;

    cursor:pointer;

    font-size:14px;

    font-weight:bold;

}


button:hover{
    background:#0d5269;
}


.primary{
    width:100%;
    margin-top:18px;
    font-size:16px;
}


.clear{
    background:#e9eef5;
    color:#333;
    margin-top:8px;
    width:100%;
}


/* CHAT */

.chat-panel{
    background:white;
    border-radius:18px;
    min-height:650px;
    box-shadow:0 12px 30px rgba(25,42,70,.08);
    border:1px solid #e7ebf2;
    display:flex;
    flex-direction:column;
}


.chat-header{
    padding:20px 22px;
    border-bottom:1px solid #e7ebf2;
    font-weight:bold;
    color:#102a56;
    font-size:17px;
}


.chat{
    flex:1;
    padding:20px;
    overflow-y:auto;
    max-height:550px;
}


.message{
    margin-bottom:18px;
    display:flex;
}


.message.user{
    justify-content:flex-end;
}


.bubble{
    max-width:80%;
    padding:13px 16px;
    border-radius:12px;
    line-height:1.5;
}


.user .bubble{
    background:#126e8c;
    color:white;
    border-bottom-right-radius:3px;
}


.bot .bubble{
    background:#eef5f6;
    border-bottom-left-radius:3px;
}


/* RESULTS */

.results{
    margin-top:15px;
}


.summary{
    background:linear-gradient(135deg,#e7f6f4,#edf4fc);
    border-radius:14px;
    padding:16px;
    margin-bottom:15px;
    border:1px solid #d9ecec;
}


.cards{
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:12px;
}

.travel-map{
    width:100%;
    height:280px;
    border:0;
    border-radius:10px;
    margin-bottom:15px;
}


.card{
    background:white;
    border:1px solid #e1e6ec;
    border-radius:14px;
    padding:15px;
    box-shadow:0 5px 15px rgba(25,42,70,.05);
}


.card h3{
    margin-top:0;
    color:#126e8c;
}


.price{
    font-size:19px;
    font-weight:bold;
    color:#138a46;
}


.rating{
    color:#df9200;
    margin-top:5px;
}


.small-button{
    margin-top:10px;
    padding:8px 11px;
    font-size:12px;
}


.section{
    margin-top:20px;
}

.section.tab-hidden{display:none;}


.section h3{
    color:#126e8c;
}


.list{
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:8px;
}


.item{
    background:#f8fafc;
    padding:10px;
    border-radius:10px;
    border:1px solid #edf0f4;
}

.nearest{
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:16px;
    background:#102a56;
    color:white;
    border-radius:14px;
    padding:18px 20px;
    margin:0 0 18px;
}

.nearest strong{display:block;font-size:18px;margin-top:4px;}
.nearest small{color:#bcd5e2;text-transform:uppercase;letter-spacing:1px;font-weight:bold;}
.nearest .small-button{background:#24a7a0;margin-top:0;white-space:nowrap;}


.status{
    font-size:12px;
    color:#666;
    margin-top:10px;
}


.typing{
    color:#777;
    font-style:italic;
}


/* RESPONSIVE */

@media(max-width:850px){

    .grid{
        grid-template-columns:1fr;
    }

    .cards{
        grid-template-columns:1fr;
    }

}


@media(max-width:550px){

    .list{
        grid-template-columns:1fr;
    }

    .header h1{
        font-size:25px;
    }

    .header-nav{margin-bottom:30px;}
    .nav-note{display:none;}

}

</style>

</head>


<body>


<div class="header">

<div class="header-nav">
<div class="brand">TRAVEL CHATBOT</div>
<div class="nav-note">Personal travel planning, made simple</div>
</div>

<h1>Plan a trip that feels <em>like you.</em></h1>

<p>
Tell us where you want to go, what you love, and how you want to feel. We will shape the route, stays, food, and nearby places around you.
</p>

<div class="topic-chips">
<button type="button" class="topic-chip" onclick="showTab('hotels-section', this)">Hotels</button>
<button type="button" class="topic-chip" onclick="showTab('food-section', this)">Local food</button>
<button type="button" class="topic-chip" onclick="showTab('places-section', this)">Nearby places</button>
<button type="button" class="topic-chip" onclick="showTab('itinerary-section', this)">Day-by-day itinerary</button>
</div>

</div>


<div class="container">


<div class="grid">


<!-- LEFT SIDE -->

<div class="panel">

<h2>Start with a feeling</h2>

<div class="panel-intro">A few details help us make the recommendations feel personal. You can keep it loose.</div>


<label>Destination</label>

<input
id="destination"
placeholder="Hyderabad, Goa, Ooty...">


<label>Budget Per Night</label>

<input
id="budget"
type="number"
placeholder="₹4000">


<label>Guests</label>

<input
id="guests"
type="number"
value="2">


<label>Number of Days</label>

<input
id="days"
type="number"
value=""
readonly>


<label>Check-in</label>

<input
id="checkin"
type="date">


<label>Check-out</label>

<input
id="checkout"
type="date">


<label>Preferences</label>

<textarea
id="preferences"
placeholder="Family, food, beaches, adventure, luxury..."></textarea>

<div class="quick-prompts">
<button type="button" onclick="setPreference('slow mornings and local food')">Slow & local</button>
<button type="button" onclick="setPreference('beaches and outdoor adventure')">Beach & adventure</button>
<button type="button" onclick="setPreference('heritage, art and cafes')">Culture & cafes</button>
</div>


<button
class="primary"
onclick="generatePlan()">

🔍 Generate Travel Plan

</button>


<button
class="clear"
onclick="clearChat()">

Clear Conversation

</button>


<div class="status">

The application works with demo data now.
Live APIs can be enabled later.

</div>


</div>


<!-- RIGHT SIDE -->

<div class="chat-panel">


<div class="chat-header">

🤖 Travel Assistant

</div>


<div
id="chat"
class="chat">

<div class="message bot">

<div class="bubble">

Hello! 👋

I'm your AI Travel Assistant.

Tell me where you want to travel,
your budget and your preferences.

I can help with hotels, attractions,
restaurants, local food and itinerary planning.

</div>

</div>

</div>


</div>


</div>


</div>


<script>


let conversation = [];


function setPreference(value){

    document.getElementById("preferences").value = value;

    document.getElementById("preferences").focus();

}


function calculateTripDays(){

    const checkin = document.getElementById("checkin").value;
    const checkout = document.getElementById("checkout").value;
    const daysInput = document.getElementById("days");

    if(!checkin || !checkout){
        daysInput.value = "";
        return 0;
    }

    const start = new Date(checkin + "T00:00:00");
    const end = new Date(checkout + "T00:00:00");
    const days = Math.round((end - start) / 86400000);
    daysInput.value = days > 0 ? days : "";
    return days > 0 ? days : 0;

}


function showTab(sectionId, tab){

    const target = document.getElementById(sectionId);
    if(!target){
        document.getElementById("chat").scrollIntoView({behavior:"smooth"});
        return;
    }

    document.querySelectorAll(".results .section").forEach(function(section){
        section.classList.toggle("tab-hidden", section.id !== sectionId);
    });
    document.querySelectorAll(".topic-chip").forEach(function(item){
        item.classList.remove("active");
    });
    tab.classList.add("active");
    target.scrollIntoView({behavior:"smooth", block:"start"});

}


document.getElementById("checkin").addEventListener("change", calculateTripDays);
document.getElementById("checkout").addEventListener("change", calculateTripDays);


async function generatePlan(){

    const destination =
        document.getElementById("destination").value.trim();

    const budget =
        Number(document.getElementById("budget").value || 0);

    const guests =
        Number(document.getElementById("guests").value || 1);

    const days =
        calculateTripDays();

    const checkin =
        document.getElementById("checkin").value;

    const checkout =
        document.getElementById("checkout").value;

    const preferences =
        document.getElementById("preferences").value.trim();

    if(!days){
        alert("Please select a valid check-in and check-out range.");
        return;
    }


    if(!destination){

        alert("Please enter a destination.");

        return;

    }


    addMessage(

        "user",

        "Plan my trip to " +
        destination +
        " for " +
        days +
        " days. Budget: ₹" +
        budget +
        " per night. Preferences: " +
        preferences

    );


    addMessage(

        "bot",

        "<span class='typing'>🔄 Searching travel information...</span>"

    );


    try{

        const response = await fetch(

            "/api/travel",

            {

                method:"POST",

                headers:{
                    "Content-Type":"application/json"
                },

                body:JSON.stringify({

                    destination:destination,

                    budget:budget,

                    guests:guests,

                    days:days,

                    checkin:checkin,

                    checkout:checkout,

                    preferences:preferences,

                    conversation:conversation

                })

            }

        );


        const data = await response.json();


        removeTyping();


        if(data.error){

            addMessage(
                "bot",
                "❌ " + data.error
            );

            return;

        }


        conversation.push({

            user:
            "Plan trip to " +
            destination,

            assistant:
            data.ai_response

        });


        addMessage(

            "bot",

            formatAIResponse(data.ai_response)

        );


        showTravelResults(data);


    }

    catch(error){

        removeTyping();

        addMessage(

            "bot",

            "❌ Unable to connect to the travel server."

        );

    }

}


function formatAIResponse(text){

    if(!text){
        return "";
    }

    return text
        .replace(/\n/g,"<br>")
        .replace(/\*\*(.*?)\*\*/g,"<b>$1</b>");

}


function addMessage(role,text){

    const chat =
        document.getElementById("chat");


    const message =
        document.createElement("div");


    message.className =
        "message " + role;


    const bubble =
        document.createElement("div");


    bubble.className =
        "bubble";


    bubble.innerHTML =
        text;


    message.appendChild(bubble);

    chat.appendChild(message);

    chat.scrollTop =
        chat.scrollHeight;

}


function removeTyping(){

    const messages =
        document.querySelectorAll(".typing");

    messages.forEach(
        function(element){

            element.closest(".message").remove();

        }
    );

}


function resultName(item){

    return typeof item === "string" ? item : item.name;

}


function resultAddress(item){

    return typeof item === "string" ? "" : item.address || "";

}


function resultMapURL(item, destination){

    if(typeof item !== "string" && item.maps){
        return item.maps;
    }

    return "https://www.google.com/maps/search/?api=1&query=" +
        encodeURIComponent(resultName(item) + " " + destination);

}


function showTravelResults(data){

    let hotelHTML = "";

    const nearest = data.nearest_place;
    const nearestName = nearest ? resultName(nearest) : "No nearby attraction found";
    const nearestAddress = nearest ? resultAddress(nearest) : "Try a broader destination search";
    const nearestURL = nearest ? resultMapURL(nearest, data.destination) : resultMapURL({name: data.destination}, data.destination);


    data.hotels.forEach(

        function(hotel){

            const mapURL = resultMapURL(hotel, data.destination);


            hotelHTML += `

            <div class="card">

                <h3>🏨 ${hotel.name}</h3>

                <div>${resultAddress(hotel)}</div>

                <div class="price">
                    ₹${hotel.price}
                </div>

                <div>
                    Per night
                </div>

                <div class="rating">
                    ⭐ ${hotel.rating}
                </div>

                <button
                    class="small-button"
                    onclick="window.open('${mapURL}','_blank')">

                    📍 View on Map

                </button>

            </div>

            `;

        }

    );


    let placesHTML = "";


    data.places.forEach(

        function(place){

            const name = resultName(place);
            const url = resultMapURL(place, data.destination);


            placesHTML += `

            <div class="item">

                📍 ${name}

                <br>

                ${resultAddress(place)}

                <br>

                <button
                    class="small-button"
                    onclick="window.open('${url}','_blank')">

                    Map

                </button>

            </div>

            `;

        }

    );


    let restaurantHTML = "";

    let itineraryHTML = "";
    for(let day = 1; day <= data.days; day++){
        const place = data.places.length ? resultName(data.places[(day - 1) % data.places.length]) : data.destination;
        itineraryHTML += `<div class="item"><b>Day ${day}</b><br>${day === 1 ? "Arrival, check-in, and a relaxed walk near " + data.destination + "." : "Explore " + place + ", then leave the evening open for local food."}</div>`;
    }


    data.restaurants.forEach(

        function(restaurant){

            const name = resultName(restaurant);
            const url = resultMapURL(restaurant, data.destination);


            restaurantHTML += `

            <div class="item">

                🍴 ${name}

                <br>

                ${resultAddress(restaurant)}

                <br>

                <button
                    class="small-button"
                    onclick="window.open('${url}','_blank')">

                    Map

                </button>

            </div>

            `;

        }

    );


    const resultHTML = `

    <div class="results">


        <div class="summary">

            <b>📅 Trip Summary</b>

            <p>
                ${data.destination}
            </p>

            <p>
                ${data.days} days •
                ${data.guests} guests •
                ₹${data.budget}/night
            </p>

        </div>

        <div class="nearest">

            <div>
                <small>Nearest place to explore</small>
                <strong>📍 ${nearestName}</strong>
                <div>${nearestAddress}</div>
            </div>

            <button
                class="small-button"
                onclick="window.open('${nearestURL}','_blank')">
                Open map
            </button>

        </div>


        <iframe
            class="travel-map"
            title="Map of ${data.destination}"
            src="https://www.google.com/maps?q=${encodeURIComponent(data.destination)}&output=embed"
            loading="lazy">
        </iframe>


        <div class="section" id="hotels-section">

            <h3>🏨 Hotels</h3>

            <div class="cards">

                ${hotelHTML}

            </div>

        </div>


        <div class="section" id="places-section">

            <h3>📍 Places & Attractions</h3>

            <div class="list">

                ${placesHTML}

            </div>

        </div>


        <div class="section" id="food-section">

            <h3>🥘 Local Food</h3>

            <div class="card">
                ${data.food}
            </div>

        </div>

        <div class="section" id="itinerary-section">

            <h3>🗓 Day-by-day itinerary</h3>

            <div class="list">
                ${itineraryHTML}
            </div>

        </div>

        <div class="section">

            <h3>🍴 Restaurants</h3>

            <div class="list">

                ${restaurantHTML}

            </div>

        </div>


    </div>

    `;


    addMessage(
        "bot",
        resultHTML
    );

}


function clearChat(){

    conversation = [];


    document.getElementById("chat").innerHTML = `

    <div class="message bot">

        <div class="bubble">

        Conversation cleared. 👋

        Where would you like to travel?

        </div>

    </div>

    `;

}


</script>


</body>

</html>
"""


# ============================================================
# GOOGLE PLACES API
# ============================================================

def google_places_search(query, place_type=None):

    if not GOOGLE_PLACES_API_KEY:
        return []


_LAST_OSM_REQUEST = 0.0


def openstreetmap_search(query, limit=8, around=None):

    """Return worldwide place results without requiring an API key."""

    parameters = {
        "q": query,
        "format": "jsonv2",
        "limit": limit,
        "addressdetails": 1
    }

    if around:
        latitude, longitude = around
        parameters["viewbox"] = ",".join([
            str(longitude - 0.5),
            str(latitude + 0.5),
            str(longitude + 0.5),
            str(latitude - 0.5)
        ])
        parameters["bounded"] = 1

    params = urllib.parse.urlencode(parameters)

    global _LAST_OSM_REQUEST
    wait_seconds = 1 - (time.monotonic() - _LAST_OSM_REQUEST)
    if wait_seconds > 0:
        time.sleep(wait_seconds)
    _LAST_OSM_REQUEST = time.monotonic()

    request = urllib.request.Request(
        "https://nominatim.openstreetmap.org/search?" + params,
        headers={
            "User-Agent": "AITravelAssistant/1.0 (travel planning app)"
        }
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            results = json.loads(response.read().decode("utf-8"))

        places = []
        for result in results:
            places.append({
                "name": result.get("name") or result.get("display_name", "Unknown").split(",")[0],
                "address": result.get("display_name", ""),
                "lat": float(result["lat"]),
                "lon": float(result["lon"]),
                "rating": "N/A",
                "maps": (
                    "https://www.google.com/maps/search/?api=1&query="
                    + urllib.parse.quote(result.get("display_name", ""))
                )
            })

        return places

    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print("OpenStreetMap search error:", error)
        return []


def overpass_search(place_type, around, limit=8):
    """Find nearby OSM features using Overpass, with the same result shape as Nominatim."""
    if not around:
        return []

    latitude, longitude = around
    tag = {
        "hotel": '"tourism"="hotel"',
        "restaurant": '"amenity"="restaurant"',
        "attraction": '"tourism"="attraction"',
    }.get(place_type)
    if not tag:
        return []

    query = f"[out:json][timeout:15];(nwr[{tag}](around:12000,{latitude},{longitude}););out center {limit};"
    request = urllib.request.Request(
        OVERPASS_URL,
        data=urllib.parse.urlencode({"data": query}).encode("utf-8"),
        method="POST",
        headers={"User-Agent": "AITravelAssistant/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        places = []
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            coordinates = element.get("lat"), element.get("lon")
            if coordinates[0] is None and element.get("center"):
                coordinates = element["center"].get("lat"), element["center"].get("lon")
            if coordinates[0] is None or coordinates[1] is None:
                continue
            name = tags.get("name")
            if not name:
                continue
            places.append({
                "name": name,
                "address": tags.get("addr:street", "Nearby destination"),
                "lat": float(coordinates[0]),
                "lon": float(coordinates[1]),
                "rating": "N/A",
                "maps": "https://www.google.com/maps/search/?api=1&query=" + urllib.parse.quote(f"{name} {latitude},{longitude}"),
            })
        return places
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print("Overpass search error:", error)
        return []


def initialize_database():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination TEXT NOT NULL,
                budget INTEGER,
                guests INTEGER,
                days INTEGER,
                preferences TEXT,
                created_at TEXT NOT NULL
            )
        """)


def save_trip(data):
    initialize_database()
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            "INSERT INTO trips (destination, budget, guests, days, preferences, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (data.get("destination", ""), data.get("budget", 0), data.get("guests", 1), data.get("days", 1), data.get("preferences", ""), datetime.utcnow().isoformat()),
        )


def distance_km(first, second):
    """Calculate the straight-line distance between two latitude/longitude pairs."""
    latitude_one, longitude_one = first
    latitude_two, longitude_two = second
    earth_radius = 6371
    latitude_delta = math.radians(latitude_two - latitude_one)
    longitude_delta = math.radians(longitude_two - longitude_one)
    value = (
        math.sin(latitude_delta / 2) ** 2
        + math.cos(math.radians(latitude_one))
        * math.cos(math.radians(latitude_two))
        * math.sin(longitude_delta / 2) ** 2
    )
    return earth_radius * 2 * math.atan2(math.sqrt(value), math.sqrt(1 - value))


def rank_live_places(places, around):
    def ranking(place):
        try:
            rating = float(place.get("rating", 0))
        except (TypeError, ValueError):
            rating = 0
        distance = float("inf")
        if around and place.get("lat") is not None and place.get("lon") is not None:
            distance = distance_km(around, (place["lat"], place["lon"]))
        return (-rating, distance)

    return sorted(places, key=ranking)


def normalize_destination(destination):
    normalized = " ".join(destination.casefold().strip().split())
    if normalized in DESTINATION_ALIASES:
        return DESTINATION_ALIASES[normalized]
    match = difflib.get_close_matches(normalized, CITY_COORDINATES, n=1, cutoff=0.8)
    return match[0] if match else normalized


def destination_coordinates(destination):
    """Resolve a destination without allowing an unrelated global name match."""
    normalized = normalize_destination(destination)
    if normalized in CITY_COORDINATES:
        return CITY_COORDINATES[normalized]

    results = openstreetmap_search(destination + ", India", 1)
    if not results:
        return None

    address = results[0].get("address", "").casefold()
    if "india" not in address:
        return None

    return results[0]["lat"], results[0]["lon"]


    url = (
        "https://places.googleapis.com/v1/places:searchText"
    )


    payload = {

        "textQuery": query,

        "pageSize": 8

    }


    if place_type:

        payload["includedType"] = place_type


    data = json.dumps(payload).encode("utf-8")


    request = urllib.request.Request(

        url,

        data=data,

        method="POST",

        headers={

            "Content-Type":
            "application/json",

            "X-Goog-Api-Key":
            GOOGLE_PLACES_API_KEY,

            "X-Goog-FieldMask":
            "places.displayName,"
            "places.formattedAddress,"
            "places.rating,"
            "places.googleMapsUri,"
            "places.priceLevel"

        }

    )


    try:

        with urllib.request.urlopen(
            request,
            timeout=15
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )


            places = []


            for place in result.get(
                "places",
                []
            ):

                name = place.get(
                    "displayName",
                    {}
                ).get(
                    "text",
                    "Unknown"
                )


                places.append({

                    "name":
                    name,

                    "address":
                    place.get(
                        "formattedAddress",
                        ""
                    ),

                    "rating":
                    place.get(
                        "rating",
                        "N/A"
                    ),

                    "maps":
                    place.get(
                        "googleMapsUri",
                        ""

                    )

                })


            return places


    except Exception as error:

        print(
            "Google Places API error:",
            error
        )

        return []


# ============================================================
# OPENAI API
# ============================================================

def chroma_context(destination, preferences):
    """Return optional semantic travel context from a local Chroma collection."""
    try:
        import chromadb

        client = chromadb.PersistentClient(path=os.path.join(os.path.dirname(__file__), "chroma_data"))
        collection = client.get_or_create_collection("travel_knowledge")
        if collection.count() == 0:
            return ""
        query = f"{destination} {preferences}".strip()
        result = collection.query(query_texts=[query], n_results=3)
        documents = result.get("documents", [[]])[0]
        return "\n".join(documents)
    except Exception as error:
        print("Chroma context unavailable:", error)
        return ""


def call_ollama(user_prompt, system_prompt):
    """Use LangChain's Ollama adapter when a local model is configured."""
    if not OLLAMA_ENABLED:
        return ""
    try:
        from langchain_ollama import ChatOllama

        model = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0.7)
        response = model.invoke([
            ("system", system_prompt),
            ("human", user_prompt),
        ])
        return response.content if isinstance(response.content, str) else str(response.content)
    except Exception as error:
        print("Ollama/LangChain unavailable:", error)
        return ""

def call_openai(

    destination,

    budget,

    guests,

    days,

    preferences,

    hotels,

    places,

    restaurants,

    conversation

):


    if not OPENAI_API_KEY:

        return generate_demo_ai_response(

            destination,

            budget,

            guests,

            days,

            preferences

        )


    system_prompt = """

You are an AI Travel Assistant.

Your job is to help users plan trips.

You provide:

1. Hotel suggestions
2. Tourist attractions
3. Restaurants
4. Local food
5. Activities
6. Day-by-day itinerary
7. Travel tips

Be concise and useful.

Do not invent live hotel availability.

Clearly distinguish between
recommendations and confirmed bookings.

If real-time booking is unavailable,
tell the user that booking must be completed
through the supported booking provider.

"""


    user_prompt = f"""

Destination:
{destination}

Budget per night:
₹{budget}

Guests:
{guests}

Trip duration:
{days} days

Preferences:
{preferences}

Hotels:
{json.dumps(hotels)}

Places:
{json.dumps(places)}

Restaurants:
{json.dumps(restaurants)}

Previous conversation:
{json.dumps(conversation)}

Optional semantic travel context:
{chroma_context(destination, preferences)}

Create a personalized travel response.

Include:

- Short recommendation summary
- Hotel suggestions
- Important places
- Food recommendations
- Suggested activities
- Simple day-by-day itinerary

"""

    local_response = call_ollama(user_prompt, system_prompt)
    if local_response:
        return local_response


    payload = {

        "model":
        "gpt-4.1-mini",

        "messages":[

            {
                "role":
                "system",

                "content":
                system_prompt

            },

            {
                "role":
                "user",

                "content":
                user_prompt

            }

        ],

        "temperature":
        0.7

    }


    url = "https://api.openai.com/v1/chat/completions"


    request = urllib.request.Request(

        url,

        data=json.dumps(
            payload
        ).encode("utf-8"),

        method="POST",

        headers={

            "Content-Type":
            "application/json",

            "Authorization":
            "Bearer " +
            OPENAI_API_KEY

        }

    )


    try:

        with urllib.request.urlopen(

            request,

            timeout=30

        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )


            return (

                result
                ["choices"]
                [0]
                ["message"]
                ["content"]

            )


    except Exception as error:

        print(
            "OpenAI API error:",
            error
        )


        return generate_demo_ai_response(

            destination,

            budget,

            guests,

            days,

            preferences

        )


# ============================================================
# DEMO AI RESPONSE
# ============================================================

def generate_demo_ai_response(

    destination,

    budget,

    guests,

    days,

    preferences

):

    city = destination.lower()


    food = FOODS.get(

        city,

        "Explore the local cuisine and traditional food."

    )


    places = PLACES.get(
        city,
        []
    )


    first_places = places[:3]


    response = f"""

<b>✈ Your Travel Plan for {destination.title()}</b>

I created a {days}-day travel plan for {guests} traveller(s), with a hotel budget of ₹{budget} per night.

<b>📍 Places to Explore</b>

{", ".join(first_places)}

<b>🥘 Local Food</b>

{food}

<b>🗓 Suggested Plan</b>

Day 1:
Arrival, hotel check-in and explore nearby attractions.

Day 2:
Visit the major attractions and try local food.

Day 3:
Shopping, local experiences and relaxed sightseeing.

<b>💡 Travel Tip</b>

Keep some flexible time in your itinerary so you can explore places that interest you during the trip.

"""


    if preferences:

        response += (

            f"<br><b>❤️ Your Preferences</b><br>"
            f"I have considered your preferences: "
            f"{preferences}."

        )


    return response


# ============================================================
# TRAVEL RECOMMENDATION
# ============================================================

def create_travel_data(data):


    destination = normalize_destination(data.get(
        "destination",
        ""
    ))


    if not destination:

        return {
            "error":
            "Please enter a destination."
        }


    city = destination.lower()

    around = destination_coordinates(destination)


    budget = int(
        data.get(
            "budget",
            0
        )
        or 0
    )


    guests = int(
        data.get(
            "guests",
            1
        )
        or 1
    )


    days = int(
        data.get(
            "days",
            1
        )
        or 1
    )


    preferences = data.get(
        "preferences",
        ""
    )


    # --------------------------------------------------------
    # HOTELS
    # --------------------------------------------------------

    live_hotels = []


    if GOOGLE_PLACES_API_KEY:
        live_hotels = google_places_search(destination + " hotels")
    else:
        live_hotels = overpass_search("hotel", around) or openstreetmap_search("hotel", around=around)


    if live_hotels:
        hotels = [
            {
                "name": hotel["name"],
                "price": hotel.get("price", "Live price unavailable"),
                "rating": hotel.get("rating", "N/A"),
                "maps": hotel.get("maps", ""),
                "address": hotel.get("address", ""),
                "lat": hotel.get("lat"),
                "lon": hotel.get("lon"),
            }
            for hotel in rank_live_places(live_hotels, around)
        ]


    else:
        hotels = []


    # --------------------------------------------------------
    # PLACES
    # --------------------------------------------------------

    live_places = []


    if GOOGLE_PLACES_API_KEY:
        live_places = google_places_search(destination + " tourist attractions")
    else:
        live_places = overpass_search("attraction", around) or openstreetmap_search("attraction", around=around)


    if live_places:

        places = rank_live_places(live_places, around)

    else:
        places = []


    nearest_place = places[0] if places else None


    # --------------------------------------------------------
    # RESTAURANTS
    # --------------------------------------------------------

    live_restaurants = []


    if GOOGLE_PLACES_API_KEY:
        live_restaurants = google_places_search(destination + " restaurants")
    else:
        live_restaurants = overpass_search("restaurant", around) or openstreetmap_search("restaurant", around=around)


    if live_restaurants:

        restaurants = rank_live_places(live_restaurants, around)

    else:
        restaurants = []


    # --------------------------------------------------------
    # FOOD
    # --------------------------------------------------------

    food = "Live local food recommendations are unavailable without a connected places provider."


    # --------------------------------------------------------
    # AI RESPONSE
    # --------------------------------------------------------

    ai_response = call_openai(

        destination,

        budget,

        guests,

        days,

        preferences,

        hotels,

        places,

        restaurants,

        data.get(
            "conversation",
            []
        )

    )


    result = {

        "destination":
        destination.title(),

        "budget":
        budget,

        "guests":
        guests,

        "days":
        days,

        "preferences":
        preferences,

        "hotels":
        hotels,

        "places":
        places,

        "nearest_place":
        nearest_place,

        "restaurants":
        restaurants,

        "food":
        food,

        "ai_response":
        ai_response

    }
    save_trip(data)
    return result


# ============================================================
# HTTP SERVER
# ============================================================

try:
    from flask import Flask, Response, jsonify, request
except ImportError:
    Flask = None


flask_app = Flask(__name__) if Flask else None


if flask_app:
    @flask_app.get("/")
    def flask_home():
        return Response(HTML, mimetype="text/html")


    @flask_app.post("/api/travel")
    def flask_travel():
        try:
            return jsonify(create_travel_data(request.get_json(silent=True) or {}))
        except Exception as error:
            return jsonify({"error": str(error)}), 500

class TravelServer(
    http.server.SimpleHTTPRequestHandler
):


    def log_message(
        self,
        format,
        *args
    ):

        print(
            "[SERVER]",
            format % args
        )


    def do_GET(self):

        if self.path == "/":

            self.send_response(200)

            self.send_header(

                "Content-Type",

                "text/html; charset=utf-8"

            )

            self.end_headers()

            self.wfile.write(

                HTML.encode(
                    "utf-8"
                )

            )

        else:

            self.send_error(404)


    def do_POST(self):

        if self.path != "/api/travel":

            self.send_error(404)

            return


        try:

            content_length = int(

                self.headers.get(

                    "Content-Length",
                    0

                )

            )


            body = self.rfile.read(

                content_length

            )


            data = json.loads(

                body.decode(
                    "utf-8"
                )

            )


            result = create_travel_data(
                data
            )


            response = json.dumps(

                result,

                ensure_ascii=False

            )


            self.send_response(200)


            self.send_header(

                "Content-Type",

                "application/json; charset=utf-8"

            )


            self.send_header(

                "Content-Length",

                str(

                    len(
                        response.encode(
                            "utf-8"
                        )
                    )

                )

            )


            self.end_headers()


            self.wfile.write(

                response.encode(
                    "utf-8"
                )

            )


        except Exception as error:

            print(
                "SERVER ERROR:",
                error
            )


            response = json.dumps({

                "error":
                str(error)

            })


            self.send_response(500)


            self.send_header(

                "Content-Type",

                "application/json"

            )


            self.end_headers()


            self.wfile.write(

                response.encode(
                    "utf-8"
                )

            )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    print("")
    print("==============================================")
    print("       AI TRAVEL CHATBOT")
    print("==============================================")
    print("")
    print("Starting server...")
    print("")
    print(
        "Open: http://localhost:8000"
    )
    print("")

    if OPENAI_API_KEY:

        print(
            "OpenAI: ENABLED"
        )

    else:

        print(
            "OpenAI: DEMO MODE"
        )


    if GOOGLE_PLACES_API_KEY:

        print(
            "Google Places: ENABLED"
        )

    else:

        print(
            "Google Places: DEMO MODE"
        )


    print("")


    if flask_app:
        print("Backend: Flask")
        try:
            webbrowser.open("http://localhost:8000")
        except OSError:
            pass
        flask_app.run(host="0.0.0.0", port=PORT)
    else:
        print("Backend: built-in HTTP server (install Flask for Flask mode)")
        with socketserver.TCPServer(("", PORT), TravelServer) as server:
            try:
                webbrowser.open("http://localhost:8000")
            except OSError:
                pass
            server.serve_forever()