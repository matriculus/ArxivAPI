import urllib.request as libreq
from bs4 import BeautifulSoup
import inspect
import json

class AuthorTags:
    name = "name"
    affiliation = "arxiv:affiliation"

class Tags:
    id = "id"
    title = "title"
    updated = "updated"
    published = "published"
    summary = "summary"
    doi = "arxiv:doi"
    journal = "arxiv:journal_ref"
    comment = "arxiv:comment"
    primaryCategory = "arxiv:primary_category"
    category = "category"
    authors = "author", AuthorTags

class Author:
    def __init__(self):
        self.name = None
        self.affiliation = None
    
    def __str__(self):
        return f"Name:\t{self.name}\nAffiliation:\t{self.affiliation}"
    
    # def __repr__(self):
    #     return self.__str__()
    
    def __iter__(self):
        yield("Name", self.name)
        yield("Affiliation", self.affiliation)

class Article:
    def __init__(self):
        self.id = None
        self.title = None
        self.updated = None
        self.published = None
        self.summary = None
        self.authors = dict()
        self.doi = None
        self.journal = None
        self.comment = None
        self.primaryCategory = None
        self.category = None
        self.authorCount = 0
    
    def setAuthor(self, author):
        self.authors[f"author{self.authorCount}"] = dict(author)
        self.authorCount += 1
    
    def __str__(self):
        output = ""
        for tag, val in inspect.getmembers(self):
            if tag.startswith("__") or callable(val):
                continue
            output += f"{tag}:\t{val}\n"
        return output
    
    # def __repr__(self):
    #     return self.__str__()
    
    def __iter__(self):
        for tag, val in inspect.getmembers(self):
            if tag.startswith("__") or callable(val):
                continue
            yield(tag, val)
        

def get_article(entry):
    article = Article()
    for tag, val in inspect.getmembers(Tags):
        if tag.startswith("__"):
            continue
        if "author" in tag:
            authors = entry.find_all(Tags.authors[0])
            for author in authors:
                ath = Author()
                for atag, aval in inspect.getmembers(AuthorTags):
                    if atag.startswith("__"):
                        continue
                    atval = author.find(aval)
                    if atval:
                        setattr(ath,atag, atval.text)
                article.setAuthor(ath)
            continue
                
        tagvalue = entry.find(val)
        if tagvalue:
            setattr(article, tag, tagvalue.text.replace('\n', " "))
    return article

def search_all(query=None, max_results=3):
    if not query:
        return
    articles = list()
    query = query.replace(" ","%20")
    with libreq.urlopen(f'http://export.arxiv.org/api/query?search_query=all:{query}&start=0&max_results={max_results}') as url:
        results = url.read()
        soup = BeautifulSoup(results, "html.parser")
        totalResults = soup.find("opensearch:totalresults")
        entries = soup.find_all("entry") 
        for entry in entries:
            article = get_article(entry)
            articles.append(article)
    return {"total results": int(totalResults.text), "articles": articles}

def save_articles(filename="data.json", articleList=None):
    data = dict()
    filename = filename.replace(" ", "_")
    data["Total Results"] = articleList["total results"]
    for i, article in enumerate(articleList["articles"]):
        data[f"Article{i}"] = dict(article)
    
    # print(data)
    with open(filename, 'w+') as f:
        json.dump(data, f, sort_keys=True, indent=4, separators=(',', ': '))

def main():
    query = "morphing wings"
    result = search_all(query=query, max_results=3)
    save_articles(filename=f"{query}.json", articleList=result)

if __name__=="__main__":
    main()