## IBKR Risk Dashboard

### Overview
A live dashboard for Interactive Brokers (IBKR) portfolios. Interactively subset holdings by strategy and the dashboard displays the volatility and beta of each strategy.

### Features
- **Live Holdings**: Retrieves live holdings using the IBKR API.
- **User Interaction**: Allows users to subset their holdings by strategy.
- **Strategy Metrics**: Displays the volatility and beta of each selected strategy.
- **Dockerized**: The application is containerized and can be run using Docker.

### Prerequisites
- Users need to have the necessary permissions on IBKR, including market data subscription for receiving streaming top-of-book live data.
- Docker installed on your machine.
