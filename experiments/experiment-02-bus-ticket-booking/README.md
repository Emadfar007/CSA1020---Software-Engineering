# Experiment 02 — Bus Ticket Booking System Prototype

## Aim

To design a simple desktop prototype of a bus ticket booking system using Figma and demonstrate its booking workflow through a local testing website.

## Tools Required

- Figma account.
- Web browser.
- Internet connection for Figma.
- HTML, CSS, and JavaScript for the local website.
- Python, optionally, to run a local testing server.

## Algorithm

1. Create a Figma design file and add four desktop frames of **1440 × 960 pixels**.
2. Design a search screen with departure city, destination, travel date, passenger count, and a **Search buses** button.
3. Design a bus selection screen with operator details, travel times, fares, ratings, filters, and seat availability.
4. Design a seat selection screen with available, selected, and booked seats, plus a booking summary and total fare.
5. Design a confirmation screen displaying the route, date, operator, selected seats, amount, and sample PNR.
6. Connect the primary buttons to simulate **Search → Choose bus → Select seats → Confirmation**.
7. Implement the same flow using HTML, CSS, and JavaScript in the [website folder](website/).
8. Open `website/index.html` in a browser, or run the following command from this experiment's folder and open **http://127.0.0.1:4817/**:

   ```powershell
   python -m http.server 4817 --bind 127.0.0.1 --directory website
   ```

9. Test bus search, filters, seat selection, fare calculation, and simulated booking confirmation.

## Output Screenshots

**Trip Search — Figma**

![Desktop trip search screen](screenshots/01-search-figma.png)

**Bus Selection — Figma**

![Desktop bus results and filters](screenshots/02-results-figma.png)

**Seat Selection — Figma**

![Desktop seat map and booking summary](screenshots/03-seats-figma.png)

**Booking Confirmation — Figma**

![Desktop booking confirmation and ticket details](screenshots/04-confirmed-figma.png)

**Local Testing Website**

![Local SwiftBus website search screen](screenshots/05-local-website.png)

[Open the Figma prototype](https://www.figma.com/design/1Y71bhdPTjVX7d3ubsW6LV/Bus-Ticket-Booking-System---Prototype?node-id=11-177&p=f).

## Result

A four-screen desktop Figma prototype and a local interactive website were created to demonstrate the bus ticket booking workflow. Bookings use sample data and simulated confirmation. The website remains for local testing, with no live reservation or payment service connected.
