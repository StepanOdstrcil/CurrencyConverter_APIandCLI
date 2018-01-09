# Basic libraries
import json
# Third party libraries
import click
import requests

BANK_API_URL = r"http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.txt"


# -------------------------
# HELPFUL FUNCTIONS
# -------------------------

def create_json(input_currency, amount, output, error_message=None):
    """
    Creates json output for output of the CLI
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

    return json.dumps(d, sort_keys=True, indent=4, separators=(',', ': '))


def load_exchange_rates(url):
    """
    Loads exchange rates from bank API
    :param url: <string> Url of bank API (www.cnb.cz) that send back string of exchange rates separated by '|'
    :return: <dictionary> Dictionary of exchange rates
    """
    string = requests.get(url).text.strip("\n")
    rows = [s.split("|") for s in string.split("\n")[2:]]

    exchange_rates = {code: float(rates.replace(",", ".")) / float(czk.replace(",", "."))
                      for _, _, czk, code, rates in rows}

    exchange_rates["CZK"] = 1

    return exchange_rates


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


def currency_converter(amount, input_currency, output_currency):
    """
    CLI endpoint for conversion
    :param amount: <float> Amount of money to exchange
    :param input_currency: <string> Code of country to exchange from
    :param output_currency: <string> Code of country to get
    :return: <JSON> File of conversion or in case of error JSON file with message in 'error'
    """
    if not all((amount, input_currency)):
        return create_json(input_currency, amount, None,
                           "One or more of the arguments are missing and/or "
                           "one or more arguments are in wrong format. "
                           "'input_currency'<str> Shortcut of currency to change, "
                           "'output_currency'(optional) <str> Shortcut of currency to get.")

    # Loads exchange rates dictionary
    try:
        all_exchange_rates = load_exchange_rates(BANK_API_URL)
    except Exception:
        return create_json(input_currency, amount, None, "Could not connect to the bank API for exchange rates.")

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


# -------------------------
# CLI FUNCTIONS
# -------------------------

@click.command()
@click.option("--amount", default=None, type=float, help="Amount of currency to exchange.")
@click.option("--input_currency", default=None, help="Code of the country to exchange from.")
@click.option("--output_currency", default=None, help="(optional) Code of the country to exchange.")
def run(amount, input_currency, output_currency):
    json_file = currency_converter(amount, input_currency, output_currency)
    click.echo(json_file)


if __name__ == "__main__":
    run()
