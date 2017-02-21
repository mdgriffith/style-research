
from bs4 import BeautifulSoup
import requests
import json
import pprint
import time


mdn_base = "https://developer.mozilla.org"
index_url = mdn_base + "/en-US/docs/Web/CSS/Reference"



def get(url, wait=None):
    if wait is not None:
        time.sleep(wait)
    response = requests.get(url)
    if response.status_code >= 300:
        raise Exception("Bad Request")

    return BeautifulSoup(response.content, 'html.parser')


def retrieve_mdn_css_spec():
    
    html = get(index_url)
    links = html.find('div', { "class" : "index" }).find_all('a')
    cssSpec = []
    for link in links:

        documented = True
        if 'class' in link and 'new' in link['class']:
            documented = False

        text = link.get_text()

        typeOf = 'property'
        if text.startswith('<') and text.endswith('>'):
            typeOf = 'unit'
        elif text.startswith('::'):
            typeOf = 'pseudo-element'
        elif text.startswith(':'):
            typeOf = 'pseudo-class'
        elif text.startswith('@'):
            typeOf = 'at-rule'
        elif text.endswith('()'):
            typeOf = 'function'

        found = {}
        found['url'] = mdn_base + link.get('href')
        found['name'] = text
        found['documented'] = documented
        found['type'] = typeOf
        cssSpec.append(found)
    return cssSpec


def read_compatability_table(table):
    """
    Returns data in the following format:
        [{ "level": "Basic support"
        , "support":
            { "chrome": {"prefix": None, "support": True}
    
            }
    
        }]
    """

    compatibility = []
    headers = []
    rows = table.find_all('tr')
    for i, row in enumerate(rows):
        if i == 0:
            for column in row.find_all('th'):
                headers.append(column.get_text())
        else:
            level = {"support":{}}
            for c, column in enumerate(row.find_all('td')):
                if c == 0:
                    level["level"] = column.get_text()
                else:
                    supported = True
                    prefix = None
                    if "No Support" in column.get_text():
                        supported = False

                    maybe_prefix = column.find("span", {"title": "prefix"})
                    if maybe_prefix is not None:
                        prefix = maybe_prefix.get_text()

                    level["support"][headers[c]] = {"support": supported, "prefix":prefix }
            compatibility.append(level)
    return compatibility




def inspect_linked_documents(cssSpec):


    for element in cssSpec:

        if element['documented'] and element['type'] == 'property' and element['name'] == "position":
            html = get(element["url"] , wait=0.3)
            syntaxbox = html.find('pre', {'class':'syntaxbox'})
            element['syntax'] = syntaxbox.get_text()


            compat_desktop = read_compatability_table(html.find('div', {'id':'compat-desktop'}).find('table'))
            pprint.pprint(compat_desktop)
            # compat_mobile = read_compatability_table(html.find('div', {'id':'compat-mobile'}).find('table'))

            return element


def summarize(cssSpec):
    summary = {
        "counts":{}
        }

    for element in cssSpec:
        if element["type"] in summary["counts"]:
            summary["counts"][element["type"]] = summary["counts"][element["type"]] + 1
        else:
            summary["counts"][element["type"]] = 0

    return summary



if __name__ == "__main__":
    cssSpec = retrieve_mdn_css_spec()
    pprint.pprint(inspect_linked_documents(cssSpec))
    pprint.pprint(summarize(cssSpec))
    with open('data/css-spec.json', 'w') as RESULTS:
        RESULTS.write(json.dumps(cssSpec, indent=2))
