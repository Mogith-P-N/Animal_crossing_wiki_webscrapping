# -*- coding: utf-8 -*-
"""
Created on Sat Apr 22 16:56:55 2023

@author: mogit
"""
import time #to record the time of our script
import requests
import pymongo #to connect with our local mongoDB 
import hashlib #importing hashlib to get the hash of our webpage
from bs4 import BeautifulSoup #using bs4 for our web scrapping
from urllib.parse import urljoin #using urljoin to join the scrapped page links from parent URL

start_time = time.time()

#we are using local MongoDB database to store the web page contents as documents.
mongo=pymongo.MongoClient("mongodb://127.0.0.1:27017/") #calling mongodb local instance DB , if needed we can add mongo atlas link with credentials to store it in cloud.
mydb=mongo['Animal_crossing_wiki_DB1'] #database name
mycollection=mydb['webpages_content'] #collection 

#Function takes url as input and gives list of all page url's as output
def url_scrapping(url):

    try:
        request=requests.get(url,timeout=5)
    except requests.exceptions.RequestException as e:
        print("We are facing issue connecting to this URL {}:{}".format(url,e))
        
    bsoup=BeautifulSoup(request.text,'html.parser') #parsing the URL 
    all_links=bsoup.findAll('a')  #will return URLs of all the pages inside the website
    url_lists=[]
    
    # To get the full proper link
    for link in all_links:
        href=link.get('href') #scrapping using tag 'href' which returns all subpage URLs
        full_url=urljoin(url,href)
        if full_url not in url_lists:
            url_lists.append(full_url)
        
    print(len(url_lists))    
    return url_lists #function returns the fully joined URLs of all pages


#This function is to parse the each and every webpage and to scrape the title, summary and contents from it.
def get_webcontents(url):
    document={} #declaring empty dictionary to store as a documents
    try:
        r=requests.get(url)
        try:
            bsoup=BeautifulSoup(r.content,'html.parser',from_encoding="iso-8859-1") #uses html parser for page with html compatible structure.
        except:
            bsoup=BeautifulSoup(r.content,'lxml')  #uses xml parser for the page with XML structure
       
        webpage_hash=bsoup.find('html')
        webpage_title=bsoup.find('title') #scrapping the title of website using title tag
        webpage_summary=bsoup.find('meta', property="og:description") #Almost all webpage has the description of the page in the tag 'meta', property="og:description" hence we used to get summary.
        webpage_contents=bsoup.findAll('p') #to extract the contents from the page we used the 'p' tag. 
        
        #now we will have a seperate field called web hash in order to hash our content then compare it while running the script again to check if any changes made to page.
        document['web_hash']= hashlib.sha256(webpage_hash.encode('utf-8')).hexdigest()
        
        #Appending all the entries into document with respective keys
        try:
            document['title']= str(webpage_title.text)
        except AttributeError: #we'll get attribute error for some titles where it can't be encoded so we making an exception block.
            print('This type is not supported for title')
            document['title']=url
            
        try:
            document['page_summary']=str(webpage_summary)
        except AttributeError:
            print('This type is not supported for summary')
            document['page_summary']='null'
        
        try:    
            document['page_content']=str(webpage_contents)
        except AttributeError:
            print('This type is not supported for webcontent')
            document['page_content']='null'
            
    #Displays the error when the website is not allowing to scrape the contents and showing max retries exceeded error. we'll record just that.
    except : 
        print('Max retries exceeded with url')
        document['web_hash']='null'
        document['title']=url
        document['page_summary']='null'
        document['page_content']='null'
    
    return document

#function to insert new document into local mongodb databse or to check if already document exists and to update if changes were made.
def db_store(doc):
    #to  create a filter that facilitates our query
    #searching with page title which will be identifier in our case and masking ID and to get hash value.
    query= mycollection.find_one({'title': doc['title']}, {'_id':0,'web_hash':1}) 
    
    #if query returns a none value, then there is exsisting document present in our DB so it'll insert one document in the collection.
    if query is None:
        mycollection.insert_one(doc)
    else:
        #if we find a document but our previous hash value is not matching with new one means we'll proceed with updating the existing entry.
        if query['web_hash'] !=doc['web_hash']: 
            mycollection.update_one({'title':doc['title']},
                                    {'$set':{'page_summary':doc['page_summary'],
                                             'web_hash':doc['web_hash']}})
            print("{} page has been changed".format(doc['title']))
   
    
#Main program
if __name__=="__main__":
    website="https://animalcrossing.fandom.com/wiki/Animal_Crossing_Wiki" 
    list_of_urls=url_scrapping(website) #function produces a list of URLs 
   
    counter=0
    #looping through the list of URL's
    for link in list_of_urls:
        doc=get_webcontents(link) 
       #print("for link {} web content scrapped into dict".format(counter))
        db_store(doc)
        print("URL {} is done".format(counter))
        counter+=1 #counter to keep track on how many documents inserted.
        
    print("Web page was successfully scrapped and stored in Database")
    print("--- %s seconds ---" % (time.time() - start_time))
    
       
        
        
        
        
        
        
        
        