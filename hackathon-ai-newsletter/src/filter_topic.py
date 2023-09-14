from datetime import date
import openai
import os
from pymed import PubMed
import time
import yaml

from dotenv import load_dotenv

# Make sure to add your OpenAI API key to the .env file!
BROAD_TOPIC = "single cell genomics"
NARROW_TOPIC = "spatial single cell genomics"
MODEL = "gpt-3.5-turbo"
EMAIL = "add.your@e.mail"
OUTFILE = "filtered-sc-genomics-7days.yaml"
load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY") # or openai.api_key = "sk-xxx"


### query pubmed for articles
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
                #print("Found more than 99, this might take a while...")
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
            'doi': article['doi'].split('\n')[0]
        })
    print("Found {} articles!".format(len(articleList)))
    if outfile is None:
        return articleInfo
    else:
        with open(outfile, "w") as f:
            yaml.dump(articleInfo, f)
        return "Output written to {}".format(outfile)

article_info = get_recent_articles(BROAD_TOPIC, EMAIL, timeframe=7)
article_info = [i for i in article_info if i['abstract'] is not None]
# load abstracts
abstracts = []
for article in article_info:
    if article['abstract'] is not None:
        abstracts.append(article['abstract'])


# filter abstracts by topic
classifications = []
for i in abstracts:
    prompt = "Below is an academic abstract, enclosed by triple backticks. Based on the asbtract, please type 'yes' or 'no' indicating whether the abstract is relevant to the topic of "
    prompt += NARROW_TOPIC + ".\n\n```" + i + "```"

    response = openai.ChatCompletion.create(
        model=MODEL,
        top_p=0,
        presence_penalty=-2,
        messages=[
            {'role': 'system', 'content': 'Your job is to distinguish whether a number of paragraphs of text belong to a given topic.'},
            {'role': 'user', 'content': prompt}
        ]
    )
    classifications.append(response['choices'][0]['message']['content'])

article_info = [i for (idx, i) in enumerate(article_info) if classifications[idx]=="Yes"]

### output to YAML file
with open(OUTFILE, "w") as f:
    yaml.dump(article_info, f)

print("Output written to {}".format(OUTFILE))