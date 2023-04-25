# Animal_crossing_wiki_webscrapping

Hi,
Welcome to my repository. 

## File explanation: 
1) animal_wiki_scrapping_mainscript.py - Main driver script.
2) Web_page_documents - Consists of webpage contents as documents(json).

## Task brief :

Main aim of this reporsitory is to create a python script that will scrape all the contents from all the webpages from the URL and store it in DB. Also, we need to 
ensure that the code is scheduled to run on weekly basis and will record only changes made in document. 

## Libraries used :

1) Time
2) requests
3) pymongo
4) hashlib
5) beautifulsoup4
6) urllib

## Code walkthrough :

--> For the purpose of storing the output documents as collection we are going with mongoDB database, since we aren't sure about the data entity and structure of parsing data. we are going with NoSQL databse of mongoDB and it helps with storing contents as documents.

--> We are connecting to our local DB using pymongo connector through local port 27017 and creating database and collection as well.

--> Function "Url_scrapping" takes the parent URL as input and extracts all the web page links. Later we loop through the parent URL and join the href link with main parent URL.

--> Function "get_webcontents" takes URL as input and returns the page hash value, title, summary and content. We hashed the html content in order to compare later whether any changes made into code. 
for title we are scrapping from the tag 'title', for summary we can see almost all the page has a description which summarizes the page content with tag value 'meta', property="og:description". For the content we are scrapping with the tag 'p' .

-->Now individual scrapped contents are stored as a key value pair in dictionary within a loop and passed as output.

--> This function "db_store" takes a document as an input and pass it to query, which will compare it with existing collections and if not exists it will insert the document into collections. If it exists and hash values of previously entered document and now differs then it sense a tampering of data and updates the new content to existing document.

--> In the main function, we are passing through the URL and running loop with the list of URL's to insert/update scrapped documents in our webpage.

