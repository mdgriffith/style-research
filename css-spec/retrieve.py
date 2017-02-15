
from bs4 import BeautifulSoup
import requests
import json
import pprint


def retrieve_mdn_css_spec():
    indexUrl = "https://developer.mozilla.org/en-US/docs/Web/CSS/Reference"
    response = requests.get(indexUrl)
    if response.status_code >= 300:
        raise Exception("Bad Request")

    soup = BeautifulSoup(response.content, 'html.parser')
    links = soup.find('div', { "class" : "index" }).find_all('a')
    cssSpec = []
    for link in links:

        documented = True
        if 'class' in link and 'new' in link['class']:
            documented = False

        text = link.get_text()

        typeOf = 'property'
        if text.startswith('<') and text.endswith('>'):
            typeOf = 'unit'
        elif text.startswith(':'):
            typeOf = 'pseudo-element'
        elif text.startswith('@'):
            typeOf = 'at-rule'
        elif text.endswith('()'):
            typeOf = 'function'



        found = {}
        found['url'] = link.get('href')
        found['name'] = text
        found['documented'] = documented
        found['type'] = typeOf
        cssSpec.append(found)
    return cssSpec


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
    pprint.pprint(summarize(cssSpec))
    with open('data/css-spec.json', 'w') as RESULTS:
        RESULTS.write(json.dumps(cssSpec, indent=2))
