# Risk by Strategy Dashboard

A real-time dashboard that visualizes risk by trading strategy. Your real-time portfolio is pulled from Interactive Brokers' (IBKR) using the IBKR API. An interactive dashboard allows you to subset your holdings by strategy, and computes an immediate overview of the risks associated with each strategy.

### IBKR API Integration:

The project integrates with the IBKR API to fetch real-time stock data. Ensure that you have the required subscription permissions (a Professional account with real-time stream permissions in the assets you trade) set up. The IBKR Workstation or Gateway must be running, with the relevant port open.

### Containerization with Docker:

The application is containerized. Build and run the container using docker-compose. 

