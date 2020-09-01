import requests
from bs4 import BeautifulSoup
import mechanize
import time
import validators
import streamlit as st


def get_the_link_from_aiddata(num, base_url='http://admin.china.aiddata.org/resources/'):
    """get the link from Aiddata's resources website"""

    url = base_url + str(num)
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')

    # Find all attributes in site with "a"
    tags = soup.find_all('a')

    sites = []

    # Extracting URLs from the attribute href in the <a> tags.
    for tag in tags:
        link = tag.get('href')
        if 'http' in link:
            if 'aiddata' not in link:
                sites.append(link)

    # Isolate link we want to save
    try:
        link = sites[1]
        return link

    except IndexError:
        st.write(f'There is an error. Check the link http://admin.china.aiddata.org/resources/{num}')
        return []


def save_to_wayback(link, start):
    """Enter the url into the Web Archive's save form and submit"""

    try:
        br = mechanize.Browser()
        br.open("https://web.archive.org/save")
        br.select_form('wwmform_save')
        br.form['url'] = link
        br.find_control("capture_all").disabled = True
        br.submit()
    except:
        st.write(f"Something went wrong with resource {start}")
    finally:
        st.write(f"Resource {start} has been saved to the Wayback Machine")


def SourceSaver(start, end):
    while start < end + 1:
        # Get the link we want to save
        link = get_the_link_from_aiddata(start)

        # Make sure it's not a Factiva link
        if 'factiva' not in link and link != []:

            # Make sure the URL is valid
            if validators.url(link):
                save_to_wayback(link, start)

        # Wait five seconds before making next request to avoid angering the Internet Archive's server
        time.sleep(5)

        # Iterate by one to next resource ID
        start += 1


def save_source():
    st.header('Scrap Source')

    st.write("Sources come from: http://admin.china.aiddata.org/resources/")

    start = st.number_input("Enter starting resource", value=0, min_value=0)
    end = st.number_input("Enter ending resource:", value=1, min_value=1)

    if st.button('Start Scraping Source'):
        SourceSaver(start, end)
