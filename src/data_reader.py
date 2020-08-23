import functools
import re

from bs4 import BeautifulSoup, NavigableString

from .protocol import Protocol

def optional(function):
    """ Return a default value if an exception is raised.

    This decorator wraps the passed in function and
    returns an empty string if either an AttributeError
    or KeyError is raised.
    """
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except (AttributeError, KeyError) as e:
            return ""
    return wrapper

def _find_element(protocol_soup, text):
    return protocol_soup.find('p', text = re.compile(f"\s*{text}\s*"),
                              attrs= {'class': 'pptt'})

def parse_title(protocol_soup):
    return protocol_soup.find('div', {'class': 'topbar'}) \
                        .find('h1').text.strip()

@optional
def parse_abstract(protocol_soup):
    abstract_element = protocol_soup.find('p', {'id': 'biaoti0'})
    assert "Abstract" == abstract_element.text
    return abstract_element.find_next('p').text.strip()

def parse_authors(protocol_soup):
    return [author.text.strip()
            for author in protocol_soup.find('div', {'class': 'authordiv'}).find_all('a')
            if not isinstance(author, NavigableString)]

@optional
def parse_background(protocol_soup):
    background_element = protocol_soup.find('p', text = "Background")
    return background_element.find_next('p').text.strip()

def parse_categories(protocol_soup):
    return [category.text.strip()
            for category in protocol_soup.find('div', {'class': 'categories_a'}).find_all('a')
            if not isinstance(category, NavigableString)]

@optional
def parse_materials(protocol_soup):
    materials_element = _find_element(protocol_soup, "Materials")
    return [material.text.strip()
            for material in materials_element.find_next('ol').find_all('li')]

def parse_equipment(protocol_soup):
    equipment_element = _find_element(protocol_soup, "Equipment")
    return [equipment.text.strip()
            for equipment in equipment_element.find_next('ol').find_all('li')]

def parse_procedure(protocol_soup):
    procedure_element = _find_element(protocol_soup, "Procedure")
    return [procedure.text.strip()
            for procedure in procedure_element.find_next('ol').find_all('li', recursive=False)]

def parse_protocol(protocol_html, protocol_id):
    soup = BeautifulSoup(protocol_html, 'lxml') # use lxml parser to fix some broken tags
    return Protocol(protocol_id, parse_title(soup), parse_abstract(soup),
                    parse_materials(soup), parse_procedure(soup),
                    parse_equipment(soup), parse_background(soup),
                    parse_categories(soup), parse_authors(soup))
