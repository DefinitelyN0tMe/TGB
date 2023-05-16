from pycoingecko import CoinGeckoAPI
from telegram import Update, BotCommand, ParseMode, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from quickchart import QuickChart
import datetime
import requests
import pandas as pd
import pandas_ta as ta
import traceback
import backoff
from binance.client import Client
import matplotlib.pyplot as plt
import os
from bs4 import BeautifulSoup
import urllib.parse
from etherscan import Etherscan
from datetime import datetime, timedelta
import time
from typing import List, Dict
import threading
from collections import defaultdict
import json
import re


TELEGRAM_BOT_TOKEN = '***************************'
cg = CoinGeckoAPI()
NEWS_API_KEY = "********************************"
api_key = "****************************************"
api_secret = "***************************************"

binance_client = Client(api_key, api_secret)
etherscan_api_key = "***************************"
etherscan_client = Etherscan(etherscan_api_key)
coingecko_client = CoinGeckoAPI()

BSCSCAN_API_KEY = "*************************************"
POLYGONSCAN_API_KEY = "***************************"

ALERTS_FILE = 'alert_data.json'

@backoff.on_exception(backoff.expo, Exception, max_tries=5)
def make_coingecko_request(url, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Hello! I am a cryptocurrency bot. Here are the available commands:\n'
        '/price [symbol] - Retrieves the current price, market capitalization, trading volume, and 24-hour price change percentage for a specified cryptocurrency.\n Example: /price BTC\n'
        '/history [symbol] [daily/weekly/monthly] - Get the price history of a cryptocurrency for the given time period (daily, weekly, or monthly).\n Example: /history ETH weekly\n'
        '/chart [symbol] - Get the 30-day and 24-hour price charts of a cryptocurrency.\n Example: /chart XMR\n'
        '/news [symbol] - Get the top 5 news articles for a given cryptocurrency.\n Example: /news DOGE\n'
        '/ta [symbol] - Get the technical analysis for a given cryptocurrency.\n Example: /ta ADA\n'
        '/top - Get the top 10 gainers and losers in the last 24 hours.\n Example /top\n'
        '/convert [amount] [from_currency] [to_currency] - Convert between two cryptocurrencies or fiat currencies.\n Example:/convert 40000 DOGE BTC\n'
        "/ob [symbol] or /ob [symbol] [symbol] - Get an order book chart for a cryptocurrency pair.\n Example: /ob BTC\n Example: /ob ETH BTC\n"
        "/oba [symbol] [symbol] - Analyze the order book for a cryptocurrency pair\n Example: /oba ETH BTC\n"
        "/ideas [symbol] - Get the top 3 TradingView ideas for a specified trading pair (e.g., BTCUSDT)\n"
        "/markets [symbol] - Get a list of all cex markets and trading pairs for a specific coin, e.g., /markets ADA\n"
        "/gasfees - Get the current gas fees for Ethereum and transaction fees for Bitcoin\n"
        "/desc [symbol] - Show the description and general information about a specific cryptocurrency.\n"
        "/dom - Shows the current Bitcoin (BTC) dominance percentage in the market.\n"
        "/halving - Shows the Bitcoin (BTC) halving date.\n"
        "/cap - Get total cryptocurrency market statistics.\n"
        "/trends - Get trending searches on CoinGecko for the last 24 hours.\n"
        "/showcoins - Get crypto holdings of a specific address.\n"
        "/whales [symbol] [interval_minutes] [min_trade_volume] - Shows the top 10 big whale orders for the specified symbol and time interval. Optionally, set a minimum trade volume to filter the results. (e.g., /whales BTC 90 500000)\n"
        "/defi - Get DeFi market statistics, including market cap, trading volume, DeFi dominance, and the top DeFi token's price.\n"
        "/nft - Top NFT Coins by 24h Volume\n"
        "/events - Get the upcoming top 20 cryptocurrency events.\n"
        "/staking - Get available Staking product list on Binance.\n"
        "/airdrop - Get the latest 6 airdrops.\n"
        "/new - Returns the top 10 recently added cryptocurrencies.\n"
        "/cex - Returns top 20 cryptocurrency exchanges ranked by trust score.\n"
        "/dex - displays the top 20 decentralized exchanges ranked by 24-hour trading volume.\n"
        "/volume - Get the top 20 cryptocurrencies by 24-hour trading volume.\n"
        "/alert [symbol] [price] - Set an alert for a cryptocurrency price. The bot will send you a message when the price reaches the specified amount.\n Example: /alert BTC 50000 or /alert LTC BTC 0.1\n"
        "/myalerts - Get a list of all your alerts.\n"
        "/delalert [alert_id] - Delete an alert by its ID. You can get the ID by using the /myalerts command.\n"
        "/info - List available bot commands\n"
    )


def info(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Hello! I am a cryptocurrency bot. Here are the available commands:\n'
        '/price [symbol] - Retrieves the current price, market capitalization, trading volume, and 24-hour price change percentage for a specified cryptocurrency.\n Example: /price BTC\n'
        '/history [symbol] [daily/weekly/monthly] - Get the price history of a cryptocurrency for the given time period (daily, weekly, or monthly).\n Example: /history ETH weekly\n'
        '/chart [symbol] - Get the 30-day and 24-hour price charts of a cryptocurrency.\n Example: /chart XMR\n'
        '/news [symbol] - Get the top 5 news articles for a given cryptocurrency.\n Example: /news DOGE\n'
        '/ta [symbol] - Get the technical analysis for a given cryptocurrency.\n Example: /ta ADA\n'
        '/top - Get the top 10 gainers or losers in the last 24 hours.\n Example /top\n'
        '/convert [amount] [from_currency] [to_currency] - Convert between two cryptocurrencies or fiat currencies.\n Example:/convert 40000 DOGE BTC\n'
        "/ob [symbol] or /ob [symbol] [symbol] - Get an order book chart for a cryptocurrency pair.\n Example: /ob BTC\n Example: /ob ETH BTC\n"
        "/oba [symbol] [symbol] - Analyze the order book for a cryptocurrency pair\n Example: /oba ETH BTC\n"
        "/ideas [symbol] - Get the top 3 TradingView ideas for a specified trading pair (e.g., BTCUSDT)\n"
        "/markets [symbol] - Get a list of all markets and trading pairs for a specific coin, e.g., /markets ADA\n"
        "/gasfees - Get the current gas fees for Ethereum and transaction fees for Bitcoin\n"
        "/desc [symbol] - Show the description and general information about a specific cryptocurrency.\n"
        "/dom - Shows the current Bitcoin (BTC) dominance percentage in the market.\n"
        "/halving - Shows the Bitcoin (BTC) halving date.\n"
        "/cap - Get total cryptocurrency market statistics.\n"
        "/trends - Get trending searches on CoinGecko for the last 24 hours.\n"
        "/showcoins - Get crypto holdings of a specific address.\n"
        "/whales [symbol] [interval_minutes] [min_trade_volume] - Shows the top 10 big whale orders for the specified symbol and time interval. Optionally, set a minimum trade volume to filter the results. (e.g., /whales BTC 90 500000)\n"
        "/defi - Get DeFi market statistics, including market cap, trading volume, DeFi dominance, and the top DeFi token's price.\n"
        "/nft-Top NFT Coins by 24h Volume\n"
        "/events - Get the upcoming top 20 cryptocurrency events.\n"
        "/staking - Get available Staking product list on Binance.\n"
        "/airdrop - Get the latest 6 airdrops.\n"
        "/new - Returns the top 10 recently added cryptocurrencies.\n"
        "/cex - Returns top 20 cryptocurrency exchanges ranked by trust score.\n"
        "/dex - displays the top 20 decentralized exchanges ranked by 24-hour trading volume.\n"
        "/volume - Get the top 20 cryptocurrencies by 24-hour trading volume.\n"
        "/alert [symbol] [price] - Set an alert for a cryptocurrency price. The bot will send you a message when the price reaches the specified amount.\n Example: /alert BTC 50000 or /alert LTC BTC 0.1\n"
        "/myalerts - Get a list of all your alerts.\n"
        "/delalert [alert_id] - Delete an alert by its ID. You can get the ID by using the /myalerts command.\n"
        "/info - List available bot commands\n"
    )


def price(update: Update, context: CallbackContext):
    if len(context.args) < 1 or len(context.args) > 2:
        update.message.reply_text('Please provide a valid cryptocurrency symbol and optionally a currency, e.g., /price BTC EUR')
        return

    symbol = context.args[0].lower()
    currency = 'usd'

    if len(context.args) == 2:
        currency = context.args[1].lower()

    try:
        search_result = cg.search(symbol)
        if len(search_result['coins']) > 0:
            coin_id = search_result['coins'][0]['id']
            coin_symbol = search_result['coins'][0]['symbol'].upper()
            coin_name = search_result['coins'][0]['name']
            coin_data = cg.get_coin_by_id(coin_id)

            price_in_usd = coin_data['market_data']['current_price']['usd']
            price_in_eur = coin_data['market_data']['current_price']['eur']
            price_in_btc = coin_data['market_data']['current_price']['btc']
            price_in_eth = coin_data['market_data']['current_price']['eth']
            market_cap_in_currency = coin_data['market_data']['market_cap'][currency]
            total_volume_in_currency = coin_data['market_data']['total_volume'][currency]
            price_change_percentage_24h = coin_data['market_data']['price_change_percentage_24h']
            rank = coin_data['market_data']['market_cap_rank']

            update.message.reply_text(
                f"{coin_name} ({coin_symbol})\n"
                f"Price:\n"
                f"  USD: {price_in_usd:.8f}\n"
                f"  EUR: {price_in_eur:.8f}\n"
                f"  BTC: {price_in_btc:.8f}\n"
                f"  ETH: {price_in_eth:.8f}\n"
                f"Market Cap: {market_cap_in_currency:,.0f} {currency.upper()}\n"
                f"24h Trading Volume: {total_volume_in_currency:,.0f} {currency.upper()}\n"
                f"24h Price Change: {price_change_percentage_24h:.2f}%\n"
                f"Rank: {rank}"
            )
        else:
            update.message.reply_text(
                f"Couldn't find the cryptocurrency with symbol {symbol.upper()}. Please check your input and try again.")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def history(update: Update, context: CallbackContext):
    if len(context.args) < 2 or len(context.args) > 3:
        update.message.reply_text('Please provide a valid cryptocurrency symbol and a time period (daily, weekly, or monthly), e.g., /history BTC weekly')
        return

    symbol = context.args[0].lower()
    time_period = context.args[1].lower()

    if time_period not in ['daily', 'weekly', 'monthly']:
        update.message.reply_text('Please provide a valid time period (daily, weekly, or monthly), e.g., /history BTC weekly')
        return

    if len(context.args) == 3:
        try:
            data_points = int(context.args[2])
        except ValueError:
            update.message.reply_text('Please provide a valid number of data points, e.g., /history BTC weekly 5')
            return
    else:
        data_points = None

    try:
        search_result = cg.search(symbol)
        if len(search_result['coins']) > 0:
            coin_id = search_result['coins'][0]['id']
            coin_symbol = search_result['coins'][0]['symbol'].upper()
            coin_name = search_result['coins'][0]['name']

            if time_period == 'daily':
                days = '1'
            elif time_period == 'weekly':
                days = '7'
            else:
                days = '30'

            coin_data = cg.get_coin_market_chart_by_id(coin_id, vs_currency='usd', days=days)
            prices = coin_data['prices']

            if data_points:
                prices = prices[-data_points:]

            price_data = ''
            for price in prices:
                timestamp, price_usd = price
                price_date = datetime.fromtimestamp(timestamp // 1000).strftime('%Y-%m-%d %H:%M:%S')
                price_data += f"{price_date}: ${price_usd:.8f}\n"

            # Split the message into smaller parts
            message_parts = []
            current_message = f"Price history for {coin_name} ({coin_symbol}) ({time_period}):\n"
            for line in price_data.splitlines():
                if len(current_message + line + "\n") > 4096:
                    message_parts.append(current_message)
                    current_message = ""
                current_message += line + "\n"

            if current_message:
                message_parts.append(current_message)

            # Send each part separately
            for message in message_parts:
                update.message.reply_text(message)
        else:
            update.message.reply_text(
                f"Couldn't find the cryptocurrency with symbol {symbol.upper()}. Please check your input and try again.")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def chart(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text('Please provide a valid cryptocurrency symbol, e.g., /chart BTC')
        return

    symbol = context.args[0].lower()

    def send_chart(days, interval):
        market_chart = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days=days, interval=interval)
        prices = market_chart['prices']
        timestamps = [price[0] for price in prices]
        price_values = [price[1] for price in prices]

        qc = QuickChart()
        qc.width = 800
        qc.height = 400
        qc.config = {
            "type": "line",
            "data": {
                "labels": timestamps,
                "datasets": [{
                    "label": f'{coin_name} ({coin_symbol}) Price',
                    "data": price_values,
                    "fill": False,
                    "borderColor": "rgb(75, 192, 192)",
                    "tension": 0.1
                }]
            },
            "options": {
                "scales": {
                    "xAxes": [{
                        "type": "time",
                        "time": {
                            "unit": "day" if days != '1' else "hour"
                        }
                    }]
                }
            }
        }

        chart_url = qc.get_url()
        response = requests.get(chart_url, stream=True)
        response.raise_for_status()
        update.message.reply_photo(photo=response.raw)

    try:
        search_result = cg.search(symbol)
        if len(search_result['coins']) > 0:
            coin_id = search_result['coins'][0]['id']
            coin_symbol = search_result['coins'][0]['symbol'].upper()
            coin_name = search_result['coins'][0]['name']

            # Send 30-day chart
            update.message.reply_text("Here is the 30-day chart:")
            send_chart(days='30', interval='daily')

            # Send 24-hour chart with hourly intervals
            update.message.reply_text("Here is the 24-hour chart with hourly intervals:")
            send_chart(days='1', interval='hourly')

        else:
            update.message.reply_text(
                f"Couldn't find the cryptocurrency with symbol {symbol.upper()}. Please check your input and try again.")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def news(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text('Please provide a valid cryptocurrency symbol, e.g., /news BTC')
        return

    symbol = context.args[0].lower()

    try:
        search_result = cg.search(symbol)
        if len(search_result['coins']) > 0:
            coin_id = search_result['coins'][0]['id']
            coin_symbol = search_result['coins'][0]['symbol'].upper()
            coin_name = search_result['coins'][0]['name']

            url = f"https://newsapi.org/v2/everything?q={coin_name}&apiKey={NEWS_API_KEY}"
            response = requests.get(url)
            news_data = response.json()

            if news_data['status'] == 'ok' and len(news_data['articles']) > 0:
                for article in news_data['articles'][:5]:  # Display top 5 news articles
                    title = article['title']
                    url = article['url']
                    update.message.reply_text(f"{title}\n{url}")
            else:
                update.message.reply_text(f"No news found for {coin_name} ({coin_symbol}).")
        else:
            update.message.reply_text(
                f"Couldn't find the cryptocurrency with symbol {symbol.upper()}. Please check your input and try again.")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def technical_analysis(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text('Please provide a valid cryptocurrency symbol, e.g., /ta BTC')
        return

    symbol = context.args[0].lower()

    try:
        search_result = cg.search(symbol)
        if len(search_result['coins']) > 0:
            coin_id = search_result['coins'][0]['id']
            coin_symbol = search_result['coins'][0]['symbol'].upper()
            coin_name = search_result['coins'][0]['name']

            market_chart = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days='90', interval='daily')
            prices = market_chart['prices']

            timestamps = [price[0] for price in prices]
            price_values = [price[1] for price in prices]

            data = pd.DataFrame({'timestamp': timestamps, 'price': price_values})
            data['date'] = pd.to_datetime(data['timestamp'], unit='ms')
            data.set_index('date', inplace=True)
            data.drop(columns=['timestamp'], inplace=True)

            sma_short = ta.sma(data["price"], 20).iloc[-1]
            sma_long = ta.sma(data["price"], 50).iloc[-1]
            rsi = ta.rsi(data["price"]).iloc[-1]
            macd = ta.macd(data["price"]).iloc[-1]['MACD_12_26_9']
            macd_signal = ta.macd(data["price"]).iloc[-1]['MACDh_12_26_9']

            update.message.reply_text(
                f"Technical Analysis for {coin_name} ({coin_symbol}):\n"
                f"SMA (short-term): {sma_short:.8f}\n"
                f"SMA (long-term): {sma_long:.8f}\n"
                f"RSI: {rsi:.2f}\n"
                f"MACD: {macd:.8f}\n"
                f"MACD Signal: {macd_signal:.8f}\n"
            )

        else:
            update.message.reply_text(
                f"Couldn't find the cryptocurrency with symbol {symbol.upper()}. Please check your input and try again.")
    except Exception as e:
        tb_str = traceback.format_exception_only(type(e), e)
        update.message.reply_text(f"An error occurred: {str(e)}\n{''.join(tb_str)}")

def top_gainers_losers(update: Update, context: CallbackContext):
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false"
        response = requests.get(url)
        coins_data = response.json()

        # Filter out coins with None price_change_percentage
        coins_data = [coin for coin in coins_data if coin['price_change_percentage_24h'] is not None]

        top_gainers = sorted(coins_data, key=lambda x: x['price_change_percentage_24h'], reverse=True)[:10]
        top_losers = sorted(coins_data, key=lambda x: x['price_change_percentage_24h'])[:10]

        reply_text = "🚀 Top 10 Gainers (24h):\n\n"
        for index, coin in enumerate(top_gainers):
            coin_name = coin['name']
            coin_symbol = coin['symbol'].upper()
            coin_pct_change = coin['price_change_percentage_24h']
            reply_text += f"{index + 1}. {coin_name} ({coin_symbol}) - {coin_pct_change:.2f}%\n"

        reply_text += "\n💩 Top 10 Losers (24h):\n\n"
        for index, coin in enumerate(top_losers):
            coin_name = coin['name']
            coin_symbol = coin['symbol'].upper()
            coin_pct_change = coin['price_change_percentage_24h']
            reply_text += f"{index + 1}. {coin_name} ({coin_symbol}) - {coin_pct_change:.2f}%\n"

        update.message.reply_text(reply_text)
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")


def crypto_conversion(update: Update, context: CallbackContext):
    if len(context.args) != 3:
        update.message.reply_text('Please provide the correct format: /convert [amount] [from_currency] [to_currency]. E.g., /convert 1 BTC ETH')
        return

    try:
        amount, from_currency, to_currency = context.args
        amount = float(amount)
        from_currency = from_currency.lower()
        to_currency = to_currency.lower()

        market_url = f"https://api.coingecko.com/api/v3/coins/list"
        coins_list = make_coingecko_request(market_url)

        from_coin_id = next((coin['id'] for coin in coins_list if coin['symbol'].lower() == from_currency), None)
        to_coin_id = next((coin['id'] for coin in coins_list if coin['symbol'].lower() == to_currency), None)

        if from_coin_id is None or to_coin_id is None:
            update.message.reply_text('Invalid currency symbols. Please try again with valid symbols.')
            return

        market_url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={from_coin_id},{to_coin_id}"
        market_data = make_coingecko_request(market_url)

        from_coin = next((coin for coin in market_data if coin['id'] == from_coin_id), None)
        to_coin = next((coin for coin in market_data if coin['id'] == to_coin_id), None)

        from_usd_price = from_coin['current_price']
        to_usd_price = to_coin['current_price']
        result_amount = (amount * from_usd_price) / to_usd_price

        if to_currency == 'usd':
            result_amount = round(result_amount, 2)
        else:
            result_amount = round(result_amount, 8)

        reply_text = f"{amount} {from_currency.upper()} is equivalent to {result_amount} {to_currency.upper()}."
        update.message.reply_text(reply_text)

    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def order_book_chart(update: Update, context: CallbackContext):
    if len(context.args) == 0 or len(context.args) > 2:
        update.message.reply_text('Please provide a valid cryptocurrency symbol, e.g., /ob BTC, or two symbols for a custom pair, e.g., /ob BTC ETH')
        return

    base_symbol = context.args[0].upper()

    if len(context.args) == 1:
        quote_symbols = ['USD', 'USDT', 'BUSD']
    else:
        quote_symbols = [context.args[1].upper()]

    for quote_symbol in quote_symbols:
        trading_pair_symbol = f"{base_symbol}{quote_symbol}"

        try:
            order_book = binance_client.get_order_book(symbol=trading_pair_symbol, limit=150)
            bids = order_book['bids']
            asks = order_book['asks']

            bid_prices = [float(bid[0]) for bid in bids]
            bid_volumes = [float(bid[1]) for bid in bids]
            ask_prices = [float(ask[0]) for ask in asks]
            ask_volumes = [float(ask[1]) for ask in asks]

            plt.plot(bid_prices, bid_volumes, label='Bids', color='g')
            plt.plot(ask_prices, ask_volumes, label='Asks', color='r')
            plt.xlabel('Price')
            plt.ylabel('Volume')
            plt.legend()
            plt.title(f'{trading_pair_symbol} Order Book')

            chart_filename = f'order_book_{trading_pair_symbol}.png'
            plt.savefig(chart_filename)
            plt.clf()

            with open(chart_filename, 'rb') as chart_file:
                update.message.reply_photo(photo=chart_file)

            # Clean up the saved PNG file
            os.remove(chart_filename)

            break

        except Exception as e:
            if quote_symbol == quote_symbols[-1]:
                update.message.reply_text(f"An error occurred: {str(e)}")


def order_book_analysis(update: Update, context: CallbackContext):
    if len(context.args) != 2:
        update.message.reply_text('Please provide two valid cryptocurrency symbols, e.g., /oba BTC ETH')
        return

    base_symbol = context.args[0].upper()
    quote_symbol = context.args[1].upper()

    trading_pair_symbol = f"{base_symbol}{quote_symbol}"
    trading_pair_symbol_reversed = f"{quote_symbol}{base_symbol}"

    try:
        order_book = None
        try:
            order_book = binance_client.get_order_book(symbol=trading_pair_symbol, limit=50)
        except Exception as e:
            if 'Invalid symbol' in str(e):
                order_book = binance_client.get_order_book(symbol=trading_pair_symbol_reversed, limit=50)
                trading_pair_symbol, trading_pair_symbol_reversed = trading_pair_symbol_reversed, trading_pair_symbol
            else:
                raise

        bids = order_book['bids']
        asks = order_book['asks']

        bid_prices = [float(bid[0]) for bid in bids]
        bid_volumes = [float(bid[1]) for bid in bids]
        ask_prices = [float(ask[0]) for ask in asks]
        ask_volumes = [float(ask[1]) for ask in asks]

        highest_bid = bid_prices[0]
        lowest_ask = ask_prices[0]
        spread = lowest_ask - highest_bid
        spread_percentage = (spread / highest_bid) * 100

        reply_text = f"Order Book Analysis for {trading_pair_symbol}:\n"
        reply_text += f"Highest Bid: {highest_bid:.8f} {quote_symbol}\n"
        reply_text += f"Lowest Ask: {lowest_ask:.8f} {quote_symbol}\n"
        reply_text += f"Spread: {spread:.8f} {quote_symbol}\n"
        reply_text += f"Spread Percentage: {spread_percentage:.2f}%\n"

        update.message.reply_text(reply_text)

    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def tradingview_ideas(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text('Please provide a valid trading pair, e.g., /ideas BTCUSDT')
        return

    trading_pair = context.args[0].upper()

    try:
        url = f'https://www.tradingview.com/symbols/{trading_pair}/ideas/'
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        ideas = soup.find_all('a', class_='tv-widget-idea__title')

        if len(ideas) > 0:
            update.message.reply_text(f"TradingView Ideas for {trading_pair}:\n")
            for idea in ideas[:3]:  # Display top 3 ideas
                idea_title = idea.text
                idea_url = f"https://www.tradingview.com{idea['href']}"
                update.message.reply_text(f"{idea_title}\n{idea_url}")
        else:
            update.message.reply_text(f"No ideas found for {trading_pair}.")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def markets(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text('Please provide a valid cryptocurrency symbol, e.g., /markets BTC')
        return

    symbol = context.args[0].lower()

    try:
        search_result = cg.search(symbol)
        if len(search_result['coins']) > 0:
            coin_id = search_result['coins'][0]['id']
            coin_symbol = search_result['coins'][0]['symbol'].upper()
            coin_name = search_result['coins'][0]['name']

            tickers_data = cg.get_coin_ticker_by_id(coin_id)

            if tickers_data and tickers_data['tickers']:
                reply_text = f"Markets for {coin_name} ({coin_symbol}):\n"
                for ticker in tickers_data['tickers'][:10]:  # Display top 10 markets
                    base = ticker['base']
                    target = ticker['target']
                    platform_name = ticker['market']['name']
                    market_url = ticker['trade_url']
                    if market_url is None:
                        market_url = f"URL not provided by {platform_name}"
                    reply_text += f"{base}/{target} on {platform_name}: {market_url}\n"
                update.message.reply_text(reply_text)
            else:
                update.message.reply_text(f"No markets found for {coin_name} ({coin_symbol}).")
        else:
            update.message.reply_text(
                f"Couldn't find the cryptocurrency with symbol {symbol.upper()}. Please check your input and try again.")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def get_btc_fees():
    url = 'https://mempool.space/api/v1/fees/recommended'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def gas_fees(update: Update, context: CallbackContext):
    try:
        eth_gas_price = etherscan_client.get_gas_oracle()
        eth_fast_gas_price_gwei = eth_gas_price['SafeGasPrice']
        eth_medium_gas_price_gwei = eth_gas_price['ProposeGasPrice']

        btc_fees = get_btc_fees()
        btc_fast_fee_per_kb = btc_fees['halfHourFee']
        btc_medium_fee_per_kb = btc_fees['hourFee']

        eth_price_data = coingecko_client.get_price(ids='ethereum', vs_currencies='usd')
        eth_price = eth_price_data['ethereum']['usd']

        btc_price_data = coingecko_client.get_price(ids='bitcoin', vs_currencies='usd')
        btc_price = btc_price_data['bitcoin']['usd']

        eth_fast_fee_usd = (float(eth_fast_gas_price_gwei) * 1e-9) * eth_price
        eth_medium_fee_usd = (float(eth_medium_gas_price_gwei) * 1e-9) * eth_price

        btc_fast_fee_usd = (float(btc_fast_fee_per_kb) * 1e-8) * btc_price
        btc_medium_fee_usd = (float(btc_medium_fee_per_kb) * 1e-8) * btc_price

        update.message.reply_text(
            f"Fast Ethereum gas price: {eth_fast_gas_price_gwei} Gwei (${eth_fast_fee_usd:.6f})\n"
            f"Medium Ethereum gas price: {eth_medium_gas_price_gwei} Gwei (${eth_medium_fee_usd:.6f})\n"
            f"Fast Bitcoin transaction fee: {btc_fast_fee_per_kb} sat/byte (${btc_fast_fee_usd:.6f})\n"
            f"Medium Bitcoin transaction fee: {btc_medium_fee_per_kb} sat/byte (${btc_medium_fee_usd:.6f})"
        )
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def coin_info(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text('Please provide a valid cryptocurrency symbol, e.g., /desc BTC')
        return

    coin_symbol = context.args[0].lower()

    try:
        # Search for the coin ID using the symbol
        search_result = coingecko_client.search(coin_symbol)
        coins_list = search_result['coins']
        coin_id = None
        for coin in coins_list:
            if coin['symbol'].lower() == coin_symbol:
                coin_id = coin['id']
                break

        if coin_id is None:
            update.message.reply_text(f"Coin with symbol '{coin_symbol.upper()}' not found.")
            return

        # Get coin information using the coin ID
        coin_data = coingecko_client.get_coin_by_id(id=coin_id, localization='false')
        coin_name = coin_data['name']
        coin_symbol = coin_data['symbol'].upper()
        coin_description = coin_data['description']['en']

        update.message.reply_text(
            f"Name: {coin_name}\n"
            f"Symbol: {coin_symbol}\n"
            f"Description:\n{coin_description}"
        )
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def btc_dominance(update: Update, context: CallbackContext):
    try:
        global_data = coingecko_client.get_global()
        btc_dominance = global_data['market_cap_percentage']['btc']

        update.message.reply_text(
            f"The current BTC dominance is {btc_dominance:.2f}%."
        )

    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def market_cap(update: Update, context: CallbackContext):
    try:
        global_data = coingecko_client.get_global()
        total_market_cap = global_data['total_market_cap']['usd']
        total_volume_24h = global_data['total_volume']['usd']
        market_cap_change_24h = global_data['market_cap_change_percentage_24h_usd']
        active_cryptocurrencies = global_data['active_cryptocurrencies']

        update.message.reply_text(
            f"Total Market Cap: ${total_market_cap:,.0f}\n"
            f"24h Volume: ${total_volume_24h:,.0f}\n"
            f"Market Cap Change (24h): {market_cap_change_24h:.2f}%\n"
            f"Active Cryptocurrencies: {active_cryptocurrencies}"
        )
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def trends(update: Update, context: CallbackContext):
    try:
        trending_searches = coingecko_client.get_search_trending()
        reply_text = "Trending searches on CoinGecko:\n"

        if len(trending_searches['coins']) > 0:
            for index, coin in enumerate(trending_searches['coins']):
                coin_name = coin['item']['name']
                coin_symbol = coin['item']['symbol'].upper()
                reply_text += f"{index + 1}. {coin_name} ({coin_symbol})\n"
        else:
            reply_text = "No trending searches found."

        update.message.reply_text(reply_text)
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")


def get_big_whale_trades(symbol: str, interval_minutes: int, min_trade_volume: float) -> List[Dict]:
    end_time = int(time.time() * 1000)
    start_time = end_time - (interval_minutes * 60 * 1000)
    trades = binance_client.get_aggregate_trades(symbol=symbol, startTime=start_time, endTime=end_time)

    # Print the raw trades data for verification
    print("Raw trades data:")
    print(trades)

    big_trades = [trade for trade in trades if float(trade['q']) >= min_trade_volume]
    big_trades.sort(key=lambda x: x['q'], reverse=True)
    return big_trades[:10]


def send_large_message(chat_id, text, bot, max_length=4096):
    if len(text) <= max_length:
        bot.send_message(chat_id, text)
    else:
        parts = []
        while len(text) > 0:
            if len(text) > max_length:
                part = text[:max_length]
                last_newline = part.rfind('\n')
                if last_newline != -1:
                    part = part[:last_newline]
                parts.append(part)
                text = text[len(part):]
            else:
                parts.append(text)
                break

        for part in parts:
            bot.send_message(chat_id, part)


def whales_command_handler(update: Update, context: CallbackContext):
    args = context.args
    if len(args) < 2:
        update.message.reply_text('Please provide the symbol and interval in minutes (e.g., /whales BTC 90) and trade volume minimum limit optionaly (e.g., /whales DOGE 90 500000).')
        return

    symbol = args[0].upper() + 'USDT'
    interval_minutes = int(args[1])

    # Set a default min_trade_volume value
    min_trade_volume = 0.1  # Change this to your desired default value

    # Check if a min_trade_volume argument was provided
    if len(args) > 2:
        try:
            min_trade_volume = float(args[2])
        except ValueError:
            update.message.reply_text("Invalid min_trade_volume value. Using default value.")

    big_trades = get_big_whale_trades(symbol, interval_minutes, min_trade_volume)

    # Limit the number of trades displayed
    max_trades = 10  # Change this to your desired maximum number of trades to display
    big_trades = sorted(big_trades, key=lambda x: x['q'], reverse=True)[:max_trades]

    if not big_trades:
        response = f"No big whale orders found for {symbol} in the past {interval_minutes} minutes."
    else:
        response = f"Big whale orders for {symbol} in the past {interval_minutes} minutes (Top {max_trades} by volume):\n\n"
        for trade in big_trades:
            timestamp = datetime.fromtimestamp(trade['T'] // 1000).strftime('%Y-%m-%d %H:%M:%S')
            response += f"Price: {trade['p']} | Volume: {trade['q']} | Time: {timestamp}\n"

    send_large_message(update.message.chat_id, response, update.message.bot)

def get_defi_data():
    url = 'https://api.coingecko.com/api/v3/global/decentralized_finance_defi'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None

def defi(update: Update, context: CallbackContext):
    try:
        defi_data = get_defi_data()

        if defi_data is not None:
            defi_market_cap = defi_data['data']['defi_market_cap']
            eth_market_cap = defi_data['data']['eth_market_cap']
            defi_to_eth_ratio = defi_data['data']['defi_to_eth_ratio']
            trading_volume_24h = defi_data['data']['trading_volume_24h']
            defi_dominance = defi_data['data']['defi_dominance']
            top_coin_name = defi_data['data']['top_coin_name']
            top_coin_defi_dominance = defi_data['data']['top_coin_defi_dominance']

            update.message.reply_text(
                f"Defi Market Cap: ${float(defi_market_cap):,.2f}\n"
                f"ETH Market Cap: ${float(eth_market_cap):,.2f}\n"
                f"Defi to ETH Ratio: {float(defi_to_eth_ratio):.2f}%\n"
                f"Trading Volume 24h: ${float(trading_volume_24h):,.2f}\n"
                f"Defi Dominance: {float(defi_dominance):.2f}%\n"
                f"Top Coin: {top_coin_name}\n"
                f"Top Coin Defi Dominance: {float(top_coin_defi_dominance):.2f}%"
            )
        else:
            update.message.reply_text("Error fetching Defi data.")

    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")


def nft_coins(update: Update, context: CallbackContext):
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=non-fungible-tokens-nft&order=volume_desc&per_page=10&page=1&sparkline=false"
        response = requests.get(url)
        nft_coins_data = response.json()

        reply_text = "Top NFT Coins by 24h Volume:\n"

        for index, coin in enumerate(nft_coins_data):
            coin_name = coin['name']
            coin_symbol = coin['symbol'].upper()
            coin_volume = coin['total_volume']
            reply_text += f"{index + 1}. {coin_name} ({coin_symbol}) - 24h Volume: ${coin_volume:,.2f}\n"

        update.message.reply_text(reply_text)
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")


def new_coins(update, context):
    url = "https://coinmarketcap.com/new/"

    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    table = soup.find("table", class_="cmc-table")

    if not table:
        update.message.reply_text("Could not find the recently added coins table")
        return

    recently_added_coins = []

    rows = table.tbody.find_all("tr")
    for row in rows:
        columns = row.find_all("td")
        coin_name_and_symbol = columns[1].find_all("p")
        if len(coin_name_and_symbol) < 2:
            continue
        coin_name = coin_name_and_symbol[0].text.strip()
        coin_symbol = coin_name_and_symbol[1].text.strip()
        recently_added_coins.append({"name": coin_name, "symbol": coin_symbol})

    if not recently_added_coins:
        update.message.reply_text("No recently added coins found.")
        return

    response_text = "Recently Added Coins:\n"
    for i, coin in enumerate(recently_added_coins, start=1):
        response_text += f"{i}. {coin['name']} ({coin['symbol']})\n"

    update.message.reply_text(response_text)


def exchanges(update: Update, context: CallbackContext):
    try:
        url = "https://api.coingecko.com/api/v3/exchanges"
        response = requests.get(url)
        exchanges_data = response.json()

        # Filter out exchanges without trust score
        exchanges_data = [exchange for exchange in exchanges_data if exchange['trust_score'] is not None]

        # Sort exchanges by trust score
        exchanges_data = sorted(exchanges_data, key=lambda exchange: exchange['trust_score'], reverse=True)

        reply_text = "Top 10 Crypto Exchanges by Trust Score:\n"

        for index, exchange_data in enumerate(exchanges_data[:20]):
            exchange_name = exchange_data['name']
            exchange_country = exchange_data['country']
            exchange_trust_score = exchange_data['trust_score']
            reply_text += f"{index + 1}. {exchange_name} ({exchange_country}) - Trust Score: {exchange_trust_score}\n"

        update.message.reply_text(reply_text)
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

def dex(update: Update, context: CallbackContext):
    try:
        url = "https://www.coingecko.com/en/exchanges/decentralized"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find_all('table')[0]
        rows = table.find_all('tr')[1:21]

        reply_text = "Top 20 Decentralized Exchanges Ranked by 24H Trading Volume:\n\n"

        for index, row in enumerate(rows):
            cols = row.find_all('td')
            exchange_name = cols[1].text.strip()
            token_name = cols[2].text.strip()
            token_price = float(cols[3].text.strip().replace(',', '').replace('$', ''))
            trading_volume = cols[-1].text.strip()
            if trading_volume.endswith("%"):
                trading_volume = float(trading_volume[:-1]) / 100
            else:
                trading_volume = float(trading_volume.replace(',', '')) / token_price
            reply_text += f"{index + 1}. {exchange_name}\nDecentralized\nDecentralized volume - {trading_volume:.2%} {token_name}\n\n"

        update.message.reply_text(reply_text)

    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")


def top_defi(update: Update, context: CallbackContext):
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=decentralized_finance_defi&order=market_cap_desc&per_page=20&page=1&sparkline=false"
        response = requests.get(url)
        coins_data = response.json()

        reply_text = "Top 20 Defi Coins by Market Cap:\n"

        for index, coin in enumerate(coins_data):
            coin_name = coin['name']
            coin_symbol = coin['symbol'].upper()
            coin_market_cap = coin['market_cap']
            reply_text += f"{index + 1}. {coin_name} ({coin_symbol}) - Market Cap: ${coin_market_cap:,.2f}\n"

        update.message.reply_text(reply_text)
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")


def top_volume(update: Update, context: CallbackContext):
    try:
        url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=volume_desc&per_page=20&page=1&sparkline=false"
        response = requests.get(url)
        coins_data = response.json()

        reply_text = "Top 20 Coins by Trading Volume:\n"

        for index, coin in enumerate(coins_data):
            coin_name = coin['name']
            coin_symbol = coin['symbol'].upper()
            coin_volume = coin['total_volume']
            reply_text += f"{index + 1}. {coin_name} ({coin_symbol}) - 24h Volume: ${coin_volume:,.2f}\n"

        update.message.reply_text(reply_text)
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")


user_set_price = {}
user_alerts = defaultdict(list)

def save_alert_data(user_set_price, user_alerts):
    data = {'user_set_price': user_set_price, 'user_alerts': user_alerts}
    with open('alert_data.json', 'w') as f:
        json.dump(data, f)
    print("Saved alert data:", data)

def load_alert_data():
    if os.path.isfile(ALERTS_FILE):
        with open(ALERTS_FILE, 'r') as file:
            data = json.load(file)
            # Convert chat IDs to integers
            data['user_set_price'] = {int(k): v for k, v in data['user_set_price'].items()}
            data['user_alerts'] = {int(k): v for k, v in data['user_alerts'].items()}
            return data
    else:
        return {'user_set_price': {}, 'user_alerts': {}}


def alert(update: Update, context: CallbackContext):
    if len(context.args) < 2 or len(context.args) > 3:
        update.message.reply_text("Usage: /alert SYMBOL TARGET_PRICE [REFERENCE_SYMBOL]")
        return

    if len(context.args) == 2:
        symbol = context.args[0].upper() + 'USDT'
        reference_symbol = 'USDT'
    elif len(context.args) == 3:
        symbol = context.args[0].upper() + context.args[1].upper()
        reference_symbol = context.args[1].upper()

    try:
        target_price = float(context.args[-1])
    except ValueError:
        update.message.reply_text("Invalid target price. Please provide a valid number.")
        return

    chat_id = update.message.chat_id

    try:
        ticker = binance_client.get_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
    except Exception as e:
        update.message.reply_text(f"Error fetching the current price for {symbol}: {e}")
        return

    if chat_id not in user_set_price:
        user_set_price[chat_id] = {}

    user_set_price[chat_id][symbol] = current_price

    if chat_id not in user_alerts:
        user_alerts[chat_id] = []

    user_alerts[chat_id].append((symbol, target_price))
    update.message.reply_text(f"Alert set for {symbol[:-len(reference_symbol)]}/{reference_symbol} at {target_price}.")

    # Save the alert data after setting a new alert
    save_alert_data(user_set_price, user_alerts)

def check_price_alerts(bot: Bot):
    while True:
        for chat_id, alerts in list(user_alerts.items()):
            for alert in alerts:
                symbol, target_price = alert
                try:
                    ticker = binance_client.get_symbol_ticker(symbol=symbol)
                    current_price = float(ticker['price'])
                    set_price = user_set_price[chat_id][symbol]

                    if (set_price > target_price and current_price <= target_price) or \
                            (set_price < target_price and current_price >= target_price):
                        message = f"{symbol} has reached your target price of {target_price}! The current price is {current_price}."
                        bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)
                        user_alerts[chat_id].remove(alert)

                except Exception as e:
                    print(f"Error checking price for {symbol}: {e}")

        time.sleep(1) # sleep for 1 seconds


def myalerts(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    if chat_id not in user_alerts or not user_alerts[chat_id]:
        update.message.reply_text("You have no alerts set.")
        return

    alerts_message = "Your alerts:\n"
    for i, (symbol, target_price) in enumerate(user_alerts[chat_id], start=1):
        alerts_message += f"{i}. {symbol}: {target_price}\n"

    update.message.reply_text(alerts_message)

def delalert(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        update.message.reply_text("Usage: /delalert ALERT_ID")
        return

    try:
        alert_id = int(context.args[0])
    except ValueError:
        update.message.reply_text("Invalid alert ID. Please provide a valid number.")
        return

    chat_id = update.message.chat_id

    if chat_id not in user_alerts:
        update.message.reply_text("You have no alerts set.")
        return

    if 0 < alert_id <= len(user_alerts[chat_id]):
        symbol, target_price = user_alerts[chat_id].pop(alert_id - 1)
        update.message.reply_text(f"Alert removed for {symbol} at {target_price}.")
        save_alert_data(user_set_price, user_alerts)
    else:
        update.message.reply_text(f"No alert found with ID {alert_id}.")
        return


def events(update: Update, context: CallbackContext):
    api_key = "xDqEzwHByP6V2jazhapf39xJ3sQfuLcq5jDEP8u3"
    url = "https://developers.coinmarketcal.com/v1/events"
    headers = {
        'x-api-key': api_key,
        'Accept-Encoding': "deflate, gzip",
        'Accept': "application/json"
    }

    querystring = {"max": "20"}

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        events_data = response.json()['body']
    except Exception as e:
        update.message.reply_text(f"Error fetching events: {e}")
        return

    if not events_data:
        update.message.reply_text("No upcoming events found.")
        return

    events_message = f"Top 20 upcoming events:\n"
    for event in events_data[:20]:
        event_name = event['title']['en']
        event_symbol = event['coins'][0]['symbol'] if event['coins'] else 'Unknown'
        events_message += f"{event['date_event']} - {event_name} ({event_symbol})\n"
        if 'link' in event:
            events_message += f"{event['link']}\n"

    update.message.reply_text(events_message)

def get_balance(network, address, api_key):
    base_url = ""
    if network == "ethereum":
        base_url = "https://api.etherscan.io/api"
    elif network == "bsc":
        base_url = "https://api.bscscan.com/api"
    elif network == "matic":
        base_url = "https://api.polygonscan.com/api"

    querystring = {
        "module": "account",
        "action": "tokentx",
        "address": address,
        "startblock": 0,
        "endblock": 999999999,
        "sort": "asc",
        "apikey": api_key,
    }

    response = requests.get(base_url, params=querystring)
    if response.status_code != 200:
        return []

    transactions = response.json().get("result", [])
    balances = {}

    # Calculate balances based on transactions
    for tx in transactions:
        if not isinstance(tx, dict):
            continue
        token_symbol = tx.get("tokenSymbol", "Unknown")
        if not token_symbol:
            token_symbol = "Unknown"

        value = int(tx.get("value", 0)) / (10 ** int(tx.get("tokenDecimal", 18)))
        if token_symbol not in balances:
            balances[token_symbol] = 0

        if tx["from"].lower() == address.lower():
            balances[token_symbol] -= value
        elif tx["to"].lower() == address.lower():
            balances[token_symbol] += value

    return balances

def is_ethereum_address(address: str) -> bool:
    return bool(re.match(r"^0x[a-fA-F0-9]{40}$", address))


COINGECKO_IDS = {
    'ETH': 'ethereum',
    'BNB': 'binancecoin',
    'MATIC': 'matic-network',
    # Add more tokens as needed
}

def get_native_balance(network, address, api_key):
    base_url = ""
    if network == "ethereum":
        base_url = "https://api.etherscan.io/api"
    elif network == "bsc":
        base_url = "https://api.bscscan.com/api"
    elif network == "matic":
        base_url = "https://api.polygonscan.com/api"

    querystring = {
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest",
        "apikey": api_key,
    }

    response = requests.get(base_url, params=querystring)
    if response.status_code != 200:
        return 0

    balance = int(response.json().get("result", 0))
    return balance / (10 ** 18)

def showcoins(update: Update, context: CallbackContext):
    if not context.args or not is_ethereum_address(context.args[0]):
        update.message.reply_text("Please provide a valid Ethereum address.")
        return

    eth_address = context.args[0].lower()

    eth_balances = get_balance("ethereum", eth_address, etherscan_api_key)
    bsc_balances = get_balance("bsc", eth_address, BSCSCAN_API_KEY)
    matic_balances = get_balance("matic", eth_address, POLYGONSCAN_API_KEY)

    eth_native_balance = get_native_balance("ethereum", eth_address, etherscan_api_key)
    bsc_native_balance = get_native_balance("bsc", eth_address, BSCSCAN_API_KEY)
    matic_native_balance = get_native_balance("matic", eth_address, POLYGONSCAN_API_KEY)

    response_message = "The crypto holdings of addy:\n\n"

    response_message += "\nEthereum Network:\n"
    response_message += f"ETH: {eth_native_balance}\n"
    for symbol, balance in eth_balances.items():
        response_message += f"{symbol}: {balance}\n"

    response_message += "\nBSC chain:\n"
    response_message += f"BNB: {bsc_native_balance}\n"
    for symbol, balance in bsc_balances.items():
        response_message += f"{symbol}: {balance}\n"

    response_message += "\nPolygon (Matic) Network:\n"
    response_message += f"Matic: {matic_native_balance}\n"
    for symbol, balance in matic_balances.items():
        response_message += f"{symbol}: {balance}\n"

    update.message.reply_text(response_message)


def staking(update: Update, context: CallbackContext):
    staking_products = binance_client.get_staking_product_list(product='STAKING')

    response_message = ""
    messages = []
    for product in staking_products:
        asset = product['detail']['asset']
        reward_asset = product['detail']['rewardAsset']
        duration = product['detail']['duration']
        renewable = product['detail']['renewable']
        apy = product['detail']['apy']
        total_personal_quota = product['quota']['totalPersonalQuota']
        minimum = product['quota']['minimum']

        new_message = f"Staking info for {asset}:\n"
        new_message += f"Reward asset: {reward_asset}\n"
        new_message += f"Lock period (days): {duration}\n"
        new_message += f"Renewable: {renewable}\n"
        new_message += f"Annual percentage yield (APY): {apy}\n"
        new_message += f"Total personal quota: {total_personal_quota}\n"
        new_message += f"Minimum amount per order: {minimum}\n\n"

        if len(response_message) + len(new_message) > 4096:
            messages.append(response_message)
            response_message = new_message
        else:
            response_message += new_message

    if response_message:
        messages.append(response_message)

    for message in messages:
        update.message.reply_text(message)

def halving(update: Update, context: CallbackContext):
    genesis_block_date = datetime(2009, 1, 3)
    block_time = timedelta(minutes=10)
    blocks_per_halving = 210000

    def estimate_halving_date(halving_number):
        total_blocks = blocks_per_halving * halving_number
        total_time = block_time * total_blocks
        return genesis_block_date + total_time

    next_halving = 0
    current_date = datetime.now()
    while estimate_halving_date(next_halving) < current_date:
        next_halving += 1

    previous_halving = next_halving - 1
    next_halving_date = estimate_halving_date(next_halving)
    previous_halving_date = estimate_halving_date(previous_halving)

    update.message.reply_text(
        f"The next Bitcoin halving is estimated to occur around {next_halving_date.date()}\n"
        f"The previous Bitcoin halving occurred on {previous_halving_date.date()}")


def airdrops(update: Update, context: CallbackContext):
    url = "https://api.airdropking.io/airdrops/?order=latest&amount=20"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(f"Number of airdrops returned: {len(data)}")  # Print the number of airdrops

        message = ""
        counter = 0

        # Format the response
        for airdrop in data:
            message += (
                f"Token Name: {airdrop['name']}\n"
                f"Symbol: {airdrop['token']}\n"
                f"About: {airdrop['about']}\n"
                f"Days left for airdrop: {airdrop['days_left']}\n\n"
            )

            counter += 1

            # After every 6 airdrops, or if we are at the last airdrop, send the message
            if counter % 6 == 0 or counter == len(data):
                # Send the message
                update.message.reply_text(message)
                message = ""  # Reset the message
    else:
        update.message.reply_text(
            "Sorry, I was unable to retrieve the airdrops information at this time. Please try again later.")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Define bot commands
    bot_commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("price", "Get price information"),
        BotCommand("cap", "Get market cap information"),
        BotCommand("markets", "Get market information for a cryptocurrency"),
        BotCommand("chart", "Get chart for a cryptocurrency"),
        BotCommand("volume", "Get top 20 coins by trading volume"),
        BotCommand("history", "Get historical price information"),
        BotCommand("ob", "Get order book chart"),
        BotCommand("oba", "Get order book aggregated data"),
        BotCommand("ta", "Get technical analysis indicators"),
        BotCommand("top", "Get top gainers and losers"),
        BotCommand("convert", "Convert between cryptocurrencies"),
        BotCommand("trends", "Get top trending cryptocurrencies"),
        BotCommand("showcoins", "Get crypto holdings of a specific address"),
        BotCommand("dex", "Get top 20 decentralized exchanges by trading volume"),
        BotCommand("cex", "Get top 20 centralized exchanges by trading volume"),
        BotCommand("news", "Get latest 5 cryptocurrency news"),
        BotCommand("ideas", "Get top crypto ideas from TradingView"),
        BotCommand("gasfees", "Get current gas fees statistics"),
        BotCommand("desc", "Get description of a cryptocurrency"),
        BotCommand("dom", "Get market dominance of a BTC"),
        BotCommand("halving", "Get information about the Bitcoin halving"),
        BotCommand("defi", "Get defi statistics"),
        BotCommand("nft", "Get NFT related coins stats"),
        BotCommand("events", "Get top 20 upcoming cryptocurrency events"),
        BotCommand("staking", "Get available Staking product list on Binance"),
        BotCommand("airdrops", "Get latest 6 airdrops"),
        BotCommand("whales", "Get top 10 whales orders"),
        BotCommand("new", "Get recently added cryptocurrencies"),
        BotCommand("info", "Get information about a bot commands"),
        BotCommand("help", "Get help"),
        BotCommand("alert", "Set price alert for a cryptocurrency"),
        BotCommand("myalerts", "Get your price alerts"),
        BotCommand("delalert", "Delete a price alert"),
        # Add more commands here
    ]

    # Set bot commands
    updater.bot.set_my_commands(bot_commands)

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('price', price))
    dp.add_handler(CommandHandler('history', history))
    dp.add_handler(CommandHandler('chart', chart))
    dp.add_handler(CommandHandler('news', news))
    dp.add_handler(CommandHandler('ta', technical_analysis))
    dp.add_handler(CommandHandler('top', top_gainers_losers))
    dp.add_handler(CommandHandler("convert", crypto_conversion, pass_args=True))
    dp.add_handler(CommandHandler('info', info))
    dp.add_handler(CommandHandler("help", info))
    dp.add_handler(CommandHandler('ob', order_book_chart))
    dp.add_handler(CommandHandler('oba', order_book_analysis))
    dp.add_handler(CommandHandler('ideas', tradingview_ideas))
    dp.add_handler(CommandHandler("markets", markets))
    dp.add_handler(CommandHandler("gasfees", gas_fees))
    dp.add_handler(CommandHandler("desc", coin_info))
    dp.add_handler(CommandHandler("dom", btc_dominance))
    dp.add_handler(CommandHandler('halving', halving))
    dp.add_handler(CommandHandler("cap", market_cap))
    dp.add_handler(CommandHandler("trends", trends))
    dp.add_handler(CommandHandler("showcoins", showcoins))
    dp.add_handler(CommandHandler('whales', whales_command_handler, pass_args=True))
    dp.add_handler(CommandHandler('defi', defi))
    dp.add_handler(CommandHandler('nft', nft_coins))
    dp.add_handler(CommandHandler('events', events))
    dp.add_handler(CommandHandler('staking', staking))
    dp.add_handler(CommandHandler('airdrops', airdrops))
    dp.add_handler(CommandHandler('new', new_coins))
    dp.add_handler(CommandHandler('cex', exchanges))
    dp.add_handler(CommandHandler('dex', dex))
    dp.add_handler(CommandHandler('volume', top_volume))
    dp.add_handler(CommandHandler('top_defi', top_defi))
    dp.add_handler(CommandHandler('alert', alert, pass_args=True))
    dp.add_handler(CommandHandler('myalerts', myalerts))
    dp.add_handler(CommandHandler('delalert', delalert, pass_args=True))

    price_check_thread = threading.Thread(target=check_price_alerts, args=(updater.bot,), daemon=True)
    price_check_thread.start()

    # Load the alert data
    alert_data = load_alert_data()
    print("Loaded alert data:", alert_data)

    global user_set_price, user_alerts
    user_set_price = alert_data.get("user_set_price", {})
    user_alerts = defaultdict(list, alert_data.get("user_alerts", {}))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
