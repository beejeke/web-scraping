"""
            Práctica 1 - Web Scraping

    Desarrollo de una herramienta para aplicar herramientas
    de web scraping sobre un sitio web, con el fin de extraer
    datos de interés y generar un dataset con dicha información.

    ==> Autores
        * Omar Mendo Mesa <@beejeke>
        * Guzmán Manuel Gómez Pérez <@GGP00>

    ==> Fichero
        * src/methods.py

    ==> Descripción
        Fichero principal donde se desarrollan los métodos necesarios para
        la extracción de datos a partir de un sitio web.
"""

import requests
import re
import pandas as pd
import time
import random
import csv
from bs4 import BeautifulSoup
from tqdm import tqdm

Y = '\033[1;33m'
B = '\033[1;36m'
G = '\033[1;32m'
P = '\033[1;35m'
W = '\033[1;37m'
NC = '\033[0m'

nanosats_n = int(input(f"\n{Y}Input the number of nanosats do you want to scrape{NC} {W}[1-2780]{NC}: "))


class SatelliteScraper:

    def __init__(self):
        self.url = 'https://www.nanosats.eu'
        self.subdomain = '/database'
        self.headers = []
        self.data = []
        self.df = pd.DataFrame()

    def get_html(self, url):
        """
        Método para obtener la URL a scrapear y parsearla a HTML.
        :param url: URL a scrapear.
        :return: Contenido de la respuesta en HTML.
        """
        response = requests.get(url)
        html = BeautifulSoup(response.content, 'html.parser')

        return html

    def get_nanosats_database_links(self, html):
        """
        Método para obtener la información detallada de cada nanosatélite mediante su link correspondiente.
        :param html: Estructura HTML de la página previamente recogida.
        :return: Lista con los links que contienen los datos de cada nanosatélite.
        """
        td_tags = html.find_all('td')

        nanosats_links = []
        for td in td_tags:
            a = td.next_element
            if a.name == 'a':
                href = a['href']
                if re.match('sat', href):
                    nanosats_links.append(href)

        print(nanosats_links)

        return nanosats_links

    def get_nanosats_names_links(self, html):
        """
        Método para obtener el nombre de cada nanosatélite mediante su link correspondiente.
        :param html: Estructura HTML de la página previamente recogida.
        :return: Lista con los nombres de cada nanosatélite.
        """
        td_tags = html.find_all('td')

        nanosats_names = []
        for td in td_tags:
            a = td.next_element
            if a.name == 'a':
                href = a['href']
                if re.match('sat', href):
                    href = href[3:]
                    nanosats_names.append(href)

        return nanosats_names

    def get_headers(self, html):
        """
        Método para obtener las cabeceras para el fichero CSV y determinar la estructura que deseamos.
        :param html: Estructura HTML de la página previamente recogida.
        :return: Lista con los nombres de las columnas que queremos tener en el dataset.
        """
        b_tags = html.find_all('b')

        hdrs = []
        for b in b_tags:
            hdrs.append(b.text)
        return hdrs

    def data_scraper(self, html):
        """
        Método que obtiene los datos de cada nanosatélite.
        :param html: Estructura HTML de la página previamente recogida.
        """
        td_tags = html.find_all('td')

        extracted_data = []
        for td in td_tags:
            extracted_data.append(td.text)

        self.data.append(extracted_data)

    def scraper(self):
        """
        Método principal donde se ejecutarán los métodos desarrollados previamente para scrapear los datos.
        """
        print(f"\n===> 🚀 {P}Web Scraping of nanosatellites launch missions data from{NC} " + "'" +
              f'{B}{self.url}{NC}' + f"' 🚀 <===\n\n")

        html = self.get_html(self.url + self.subdomain)
        nanosats_names = self.get_nanosats_names_links(html)

        html = self.get_html(self.url + '/sat/tubsat-n')
        hdrs = self.get_headers(html)
        self.headers.append(hdrs)

        cnt = 0
        for i, name in zip(range(nanosats_n), tqdm(nanosats_names, total=nanosats_n)):
            tqdm.write("==> Adding nanosatellite name to his link: " + f'{W}{self.url}' + '/sat' + f'{name}{NC}')
            html = self.get_html(self.url + '/sat' + name)
            time.sleep(random.randint(0, 3))
            hdrs_ = self.get_headers(html)

            if self.headers == [hdrs_]:
                tqdm.write(f'==> {G}Scraping data{NC} for ' + name + ' nanosatellite...')
                self.data_scraper(html)
                tqdm.write(f'==> {G}Data scraped:{NC} {W}{self.data[cnt]}{NC}\n')
                cnt += 1
            else:
                tqdm.write(f'{B}[INFO]{NC} Invalid headers, discarding data [...]\n')

        self.df = pd.DataFrame(self.data, columns=self.headers)
        self.df = self.df.drop(labels='Sources', axis=1)

    def save_data_csv(self):
        self.df.to_csv(f'../datasets/nanosat_info-{nanosats_n}.csv', header=True, sep=';',
                       index=False, quoting=csv.QUOTE_NONE, escapechar=' ', encoding='utf-8')
        print(f'{G}Datos descargados con éxito:{NC}', '\n', f'{W}{self.df.head()}{NC}', '\n', f'{G}Guardados en:{NC} {W}/datasets{NC}\n')