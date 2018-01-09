# App libraries
# Third-parties libraries
from flask import Flask

# Create app object
app = Flask(__name__)
app.config.from_object("config.DevelopmentConfig")

# Due to existing app in ExchangeRates, import needs to be here
from API.exchangerates import ExchangeRates

# Create class for saving the exchange rates
exchange_rates = ExchangeRates()

# Blueprints
from API.currency_converter import currency_converter_blueprint

app.register_blueprint(currency_converter_blueprint)
