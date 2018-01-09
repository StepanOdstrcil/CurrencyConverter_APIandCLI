# Basic libraries
# App libraries
from API import exchange_rates
# Third party libraries
from flask import request, jsonify, Blueprint


# Config
currency_converter_blueprint = Blueprint(
    "currency_converter", __name__
)


# -------------------------
# HELPFUL FUNCTIONS
# -------------------------

def convert_symbol_to_currency(symbol):
    """
    Converts *symbol* to the code of the country
    :param symbol: <string> Symbol of currency
    :return: <string> Code of country
    """
    return {"€": "EUR", "$": "USD", "£": "GBP", "¥": "CNY"}.get(symbol, symbol)


def convert_currencies(amount, input_currency, output_currencies, all_exchange_rates):
    """
    Converts *amount* of currency by code and dictionary of exchange rates
    :param amount: <float> Amount of money to exchange
    :param input_currency: <string> Code of country to exchange from
    :param output_currencies: <list:string> Code of country(s) to get
    :param all_exchange_rates: <dictionary> Dictionary of exchange rates to CZK
    :return: <dictionary> Result(s) of the exchange of all currencies in list *output_currencies*
    """
    if not (type(amount) == float or type(amount) == int):
        raise ValueError("'Amount' has to be <float> or <int>")

    if input_currency not in all_exchange_rates:
        raise ValueError(f"{input_currency} currency is not in exchange rates")
    if len(output_currencies) == 1 and output_currencies[0] not in all_exchange_rates:
        raise ValueError(f"{output_currencies[0]} currency is not in exchange rates")

    return {key: amount * all_exchange_rates[input_currency] / all_exchange_rates[key] for key in output_currencies}


def create_json(input_currency, amount, output, error_message=None):
    """
    Creates json output for output of the API
    :param input_currency: <str> Code of the country to exchange from
    :param amount: <str/float> Amount of *input_currency*
    :param output: <dictionary> Dictionary of all currencies exchanged to from input
    :param error_message: (optional) <str> Error message to write to *error* key
    :return: <json> JSON file (optional: with error message)
    """
    if not input_currency:
        input_currency = "unknown"

    d = {"input": {"amount": amount, "currency": input_currency}, "output": output}
    if error_message:
        d["error"] = error_message

    return jsonify(d)


# -------------------------
# API FUNCTIONS
# -------------------------

@currency_converter_blueprint.route("/currency_converter", methods=["GET"])
def currency_converter():
    """
    API endpoint to convert currency. Data are in parameters:
    * amount: <float> Amount of money to exchange
    * input_currency: <string> Code of country to exchange from
    * output_currency: <string> Code of country to get
    :return: <JSON> File of conversion or in case of error JSON file with message in 'error'
    """
    if request.method != "GET":
        return jsonify({"error": "Only GET method is allowed."})

    # Get params
    amount = request.args.get("amount", type=float)
    input_currency = request.args.get("input_currency", type=str)
    output_currency = request.args.get("output_currency", type=str)

    if not all((amount, input_currency)):
        return create_json(input_currency, amount, None,
                           "One or more of the arguments are missing and/or "
                           "one or more arguments are in wrong format. "
                           "Arguments: 'amount'<float> Quantity of currency to change from, "
                           "'input_currency'<str> Shortcut of currency to change, "
                           "'output_currency'(optional) <str> Shortcut of currency to get.")

    all_exchange_rates = exchange_rates.get_exchange_rates()

    # Check output, if None - fill output with all codes
    input_currency = convert_symbol_to_currency(input_currency).upper()
    if output_currency:
        output_currency = [convert_symbol_to_currency(output_currency).upper()]
    else:
        output_currency = [key for key in all_exchange_rates]
        output_currency.remove(input_currency)

    # Conversion
    try:
        output = convert_currencies(amount, input_currency, output_currency, all_exchange_rates)
    except ValueError as e:
        return create_json(input_currency, amount, None, f"{e}")

    return create_json(input_currency, amount, output)
