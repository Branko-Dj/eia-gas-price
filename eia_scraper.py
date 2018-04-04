# The script scrapes natural gas prices from https://www.eia.gov/dnav/ng/hist/rngwhhdm.htm

from bs4 import BeautifulSoup
from urllib.request import urlopen
from dateutil import rrule
from datetime import datetime
import pandas


def convertToDates(string):
    strdate = string.replace(' to', '')
    strdate = strdate.replace('- ', '-')
    year, first_date, last_date = strdate.split(' ')
    first_date = year + '-' + first_date
    last_date = year + '-' + last_date
    dates = []

    for dt in rrule.rrule(rrule.DAILY,
        dtstart = datetime.strptime(first_date, '%Y-%b-%d'),
        until = datetime.strptime(last_date, '%Y-%b-%d')):
        dates.append(dt.strftime('%Y-%b-%d'))

    return dates


def scrapeDaily():

    records = []
    url = "https://www.eia.gov/dnav/ng/hist/rngwhhdD.htm"
    html = urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.findAll("table")
    gas_table = tables[5]

    rows = gas_table.findAll("tr")
    for row in rows[1:]:
        cells = row.findAll("td")
        date_string = cells[0].text.strip()
        try:
            dates = convertToDates(date_string)
        except ValueError:
            continue
        prices = list(map(lambda x: x.text, cells[1:]))
        for date, price in zip(dates, prices):
            records.append((date, price))

    return records


daily_records = scrapeDaily()
df_daily = pandas.DataFrame.from_records(daily_records, columns = ['Date', 'Price'])
df_daily.to_csv("daily_prices.csv", index=False)