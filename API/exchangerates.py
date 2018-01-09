# File for class ExchangeRates
# Basic libraries
from datetime import datetime
import requests
# App libraries
from API import app


class ExchangeRates:
    """
    Class for saving and retrieving exchange rates during live of API
    """
    def __init__(self,
                 url=r"http://www.cnb.cz/cs/financni_trhy/devizovy_trh/kurzy_devizoveho_trhu/denni_kurz.txt"):
        """
        :param url:(optional) <string> Url of bank API (www.cnb.cz) that send back string of exchange rates
        separated by '|' at each row
        """
        self._url = url
        self._exchange_rates = None
        self._last_loaded_date = datetime.fromordinal(1)
        self.load_new_rates()

    @property
    def exchange_rates_date(self):
        """
        Date of exchange rates
        :return: <string> Date of the exchange rates
        """
        return self._last_loaded_date

    def get_exchange_rates(self):
        """
        Gets exchange rates. Updates them if its day or more old
        :return: <dictionary> Dictionary {code: rate_to_czk}
        """
        if datetime.today() > self._last_loaded_date:
            self.load_new_rates()
        return self._exchange_rates

    def load_new_rates(self):
        """
        Load exchange rates from bank and save it to dictionary that represents 'file with last exchange rates'
        """
        try:
            string = requests.get(self._url).text.strip("\n")
        except Exception:
            app.logger.info("Failed to load exchange rates string from url")
        else:
            exchange_rows = string.split("\n")
            date_string = exchange_rows[0].split()[0]
            date_exchange_rates = datetime.strptime(date_string, "%d.%m.%Y")

            # If bank has old data (date of data are the same as saved), no update is needed
            if date_exchange_rates > self._last_loaded_date:
                lst = [s.split("|") for s in exchange_rows[2:]]
                d = {code: float(rates.replace(",", ".")) / float(czk.replace(",", "."))
                     for _, _, czk, code, rates in lst}
                d["CZK"] = 1
                self._exchange_rates = d
                self._last_loaded_date = date_exchange_rates
                app.logger.info("Loaded new exchange rates from the bank url")
