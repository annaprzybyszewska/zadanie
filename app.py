# -*- coding: utf-8 -*-
import re
import urllib2

from bs4 import BeautifulSoup
from flask import Flask, render_template, request


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def main():
    """Renders proper template."""
    data = {}
    errors = ''
    if request.method =='POST':
        given_url = request.form.get('url')
        try:
            url = urllib2.urlopen(given_url).read()
        except (ValueError, urllib2.URLError, urllib2.HTTPError) as e:
            errors = e.message or e.reason
            return render_template('template.html', data=data, errors=errors)
        raw = BeautifulSoup(url.decode('utf-8', 'ignore'), 'html.parser')
        keywords = raw.find_all(attrs={"name": re.compile(r'keywords', re.I)})
        if keywords:
            kw_list = prepare_keywords(keywords)
            if kw_list:
                soup = prepare_soup(raw)
                for kw in kw_list:
                    kw_count = soup.find_all(string=re.compile(kw+'\\b', re.I))
                    data.update({kw:len(kw_count)})
            else:
                errors = u'Brak słów kluczowych'
        else:
            errors = u'Brak słów kluczowych'

    return render_template('template.html', data=data, errors=errors)

def prepare_keywords(keywords):
    """Getting keywords from meta tags."""
    kw = []
    for keyword in keywords:
        if keyword['content']:
            kw.extend(keyword['content'].split(','))
    kw_list = [i.strip() for i in kw]
    return kw_list

def prepare_soup(soup):
    """Removing unnecessary tags."""
    for tag in soup.find_all(['script', 'style', 'title']):
        tag.extract()
    return soup
