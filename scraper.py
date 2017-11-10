"""This is a module mean for webscraping Indeed.com"""

import requests
import bs4
import pprint


class Position():
    """object to contain all the position info"""
    def __init__(self, title, link, company, location):
        self.title = title
        self.company = company
        self.location = location
        self.link = link
        self.indeed = False
        self.jobText = ""

    def __str__(self):
        string = '{}, {}, {}, {}, '.format(
            self.title,
            self.company,
            self.location,
            self.link,
            self.indeed)
        return string

    def toString(self):
        string = 'Position: {}, {}\n\tLocation: {}\n\tLink: {}\n'.format(
            self.title,
            self.company,
            self.location,
            self.link)

        if self.jobText:
            string = string + "\n\tJob Description:\n"
            for line in self.jobText:
                string = string + "\t\t{}\n".format(line)

        return string


def main():
    url = "https://www.indeed.com/jobs?"
    url = url + "q=python&l=Boston,+MA&explvl=entry_level"

    positions = getPositions(url)

    for position in positions:
        queryJobLink(position)
        print(position.toString())


def getPositions(url):
    """
    takes a URL and returns a list of Position objects
    """
    page = requests.get(url)

    soup = bs4.BeautifulSoup(page.text, "html.parser")

    return extractPositions(soup)


def extractPositions(soup):
    """
    takes BeautifulSoup object returns a list of the Position objects
    """
    positions = list()
    for div in soup.find_all(
            name="div",
            attrs={"data-tn-component": "organicJob"}):

        jobTitle = getJobTitle(div)
        jobLink = getJobLink(div)
        company = getCompanyName(div)
        location = getJobLocation(div)

        positions.append(
            Position(
                jobTitle,
                jobLink,
                company,
                location))

    return positions


def queryJobLink(position):
    """
    Queries an indeed link from a position object to find the
    end destination link and replace the position link with it
    """
    page = requests.get(position.link)
    url = page.url
    if(url.startswith("https://www.indeed.com/")):
        position.link = url
        soup = bs4.BeautifulSoup(page.text, "html.parser")
        position.jobText = getJobDescription(soup)
        position.indeed = True
    else:
        position.link = url


def getJobDescription(soup):
    """
    Gets the job description from a BeautifulSoup object.
    It assumes the soup is from an Indeed job profile site
    """
    description = soup.find(name="span", attrs={"id": "job_summary"})

    jobText = list()
    for string in description.strings:
        jobText.append(string)
    return jobText


def getJobTitle(div):
    """get job title as string"""
    a = div.find(name="a", href=True, attrs={"data-tn-element": "jobTitle"})
    return a.get_text()


def getJobLink(div):
    """get link to job profile"""
    a = div.find(name="a", href=True, attrs={"data-tn-element": "jobTitle"})
    return "https://www.indeed.com" + a['href']


def getCompanyName(div):
    """get company name as string"""
    span = div.find(name="span", attrs={"class": "company"})
    return span.get_text().lstrip()


def getJobLocation(div):
    """get location as string"""
    span = div.find(name="span", attrs={"class": "location"})
    return span.get_text().lstrip()

if __name__ == '__main__':
    main()
