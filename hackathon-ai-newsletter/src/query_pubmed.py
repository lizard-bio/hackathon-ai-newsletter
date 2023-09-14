from pymed import PubMed
from datetime import date
import time
import yaml


def get_recent_articles(topic, email, outfile=None, timeframe=7):
    """
    A function to query PubMed for articles published within a given timeframe.
    Input: 
        - topic: str, the topic you want to search for
        - email: str, your email address to supply to the PubMed API
        - outfile: str, if provided, the output will be written to a yaml file
        - timeframe: int, the number of days to search back in time
    Output:
        - articleInfo: list of dicts, each dict contains title, authors, abstract, 
        journal, keywords, publication date, and doi of an article.
        - a yaml file containing the articleInfo if outfile is provided
    Example: `get_recent_articles("metagenomics", "add.your@e.mail", outfile="pubmed-metagenomics-5days.yaml", timeframe=5)`
    """
    # get today's date in datetime format
    today = date.today()

    # define pubmed query
    pubmed = PubMed(tool="PubMedSearcher", email=email)

    # query pubmed until we have all articles within the timeframe
    print("Querying PubMed...")
    articleList = []
    searched_full_timeframe = False #(API only allows < 100 results at a time)
    while not searched_full_timeframe:
        # query pubmed
        results = pubmed.query(topic, max_results=99) 
        for article in results:
            articleDict = article.toDict()
            article_age = today - articleDict['publication_date']
            if article_age.days <= timeframe:
                articleList.append(articleDict)
                time.sleep(0.5) # to avoid overloading the API
            else:
                searched_full_timeframe = True
                break

    # extract relevant info from articles
    articleInfo = []
    for article in articleList:
        articleInfo.append({
            'title': article['title'],
            'authors': article['authors'],
            'journal': article['journal'],
            'publication_date': article['publication_date'],
            'keywords': article['keywords'],
            'abstract': article['abstract'],
            'doi': article['doi']
        })
    print("Found {} articles!".format(len(articleList)))
    if outfile is None:
        return articleInfo
    else:
        with open(outfile, "w") as f:
            yaml.dump(articleInfo, f)
        return "Output written to {}".format(outfile)