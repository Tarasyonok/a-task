from requests import Session

url_for_price = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
url_for_name = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'

CMC_API_KEY = "9f5ec4c7-8bc4-4a89-89dc-af533821bb5d"

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': CMC_API_KEY,
}

session = Session()
session.headers.update(headers)


def get_crypto_name(crypto_slug: str):
    parameters = {
        'slug': crypto_slug,
    }
    response = session.get(url_for_name, params=parameters)
    data = response.json()

    try:
        name = next(iter(data["data"].values()))["name"]
        return name
    except KeyError:
        raise Exception(data["status"]["error_message"])


def get_crypto_price(crypto_slug: str):
    parameters = {
        'slug': crypto_slug,
        'convert': 'USD',
    }
    response = session.get(url_for_price, params=parameters)
    data = response.json()
    # return data

    try:
        price = next(iter(data["data"].values()))["quote"]["USD"]["price"]
        if price is None:
            raise Exception("Не получилось подсчитать стоимость этой криптовалюты")
        return float(price)
    except KeyError:
        raise Exception(data["status"]["error_message"])


def get_cryptos_list():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?start=1&limit=10&convert=USD"
    response = session.get(url)
    data = response.json()

    result = []

    for c in data["data"]:
        result.append((c["name"], c["slug"], str(round(c["quote"]["USD"]["price"], 3))))

    return result
