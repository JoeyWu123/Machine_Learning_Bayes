import urllib.request
from bs4 import BeautifulSoup
import json
import re
import pymongo
import time

def movie_list_crawler():
    # database part
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient.get_database('IMDb')
    all_tables = mydb.list_collection_names()  # collection in mongodb means table
    if ('movie_list' in all_tables):
        while (1):
            choice = eval(
                input("The table movie_list already exists, input 0 to quit, or input 1 to refresh the database: "))
            if (choice == 0 or choice == 1):
                break
            else:
                print("Invalid input, try again")
        if (choice == 0):
            return
        else:
            mydb.movie_list.delete_many({})  # before refreshing the collection, clear it
    # crawler part
    base_url = "https://www.imdb.com"
    _header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0"}
    for _url in ['https://www.imdb.com/chart/top?ref_=nv_wl_img_3', 'https://www.imdb.com/chart/bottom']:

        req = urllib.request.Request(url=_url, headers=_header)
        try:
            page = urllib.request.urlopen(req)
            html_code = page.read()
            page.close()
        except:
            print("Crawler failure,return")
            return

        # the part to process data
        data = BeautifulSoup(html_code, "html.parser")
        movie_data = data.find_all('td', attrs={'class': "titleColumn"})
        pattern = re.compile(r'/title/tt\d+/')
        all_rating_data=data.find_all('td', attrs={'class': "ratingColumn imdbRating"})
        all_ratings=[]
        for each_rating_data in all_rating_data:
            score= float(each_rating_data.find('strong').text)
            all_ratings.append(score)
        index=0
        for each_movie in movie_data:
            movie_name = each_movie.find('a').text
            movie_year = int(each_movie.find('span').text[1:5])
            movie_actor = each_movie.find('a').attrs['title']
            href = each_movie.find('a').attrs['href']
            tt_link = pattern.findall(href)[0]
            tt_start_position=tt_link.find('tt')
            _id=tt_link[tt_start_position+2:-1]
            movie_url = base_url + tt_link + 'reviews?ref_=tt_urv'
            mydb.movie_list.insert_one({"_id": _id,"movie_name":movie_name,"movie_year":movie_year,"movie_actors":movie_actor,"movie_rating":all_ratings[index],"movie_review_url":movie_url})
            index=index+1

    print("done")

def crawler_get_reviews():
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient.get_database('IMDb')
    all_tables = mydb.list_collection_names()
    if ('movie_list' not in all_tables):
        print("Movie list doesn't exist in databse, using crawlers to get movie list first")
    if ('movie_reviews' in all_tables):
        while (1):
            choice = eval(input("The table movie_reviews already exists, input 0 to quit, or input 1 to refresh the database: "))
            if (choice == 0):
                return
            if (choice==1):
                while(1):
                    choice2=eval((input("Warning: this operation will erase all original data in movie_reviews, and getting new data may take hours; input 0 to abort, or input 1 to refresh the database: ")))
                    if(choice2==0):
                        return
                    if(choice2==1):
                        break
                    else:
                        print("Invalid input, try again")
                break
            else:
                print("Invalid input, try again")
    mydb.movie_reviews.delete_many({})  # before refreshing the collection, clear it
    movie_list=mydb['movie_list']
    movie_review_links=[]
    movie_overall_ratings=[]
    movie_id=[]

    #myquery = {"movie_rating": {"$lt":6.5}}
    #get all info we need from movie_list first
    for i in movie_list.find({},{"_id":1,"movie_review_url":1,"movie_rating":1}):
        movie_review_links.append(i['movie_review_url'])
        movie_overall_ratings.append(i["movie_rating"])
        movie_id.append(i["_id"])

    _header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0"}
    failed_url=[]
    index=0
    for each_movie_url in movie_review_links:
        req = urllib.request.Request(url=each_movie_url, headers=_header)
        print(index+1," Send crawler to: ",each_movie_url)
        try:
            page = urllib.request.urlopen(req)
            html_code = page.read()
            page.close()
        except:
            failed_url.append(each_movie_url)
            print("crawler fails at: ",each_movie_url)
            index=index+1
            continue
        data = BeautifulSoup(html_code, "html.parser")
        reviews_data=data.find_all('div', attrs={"class":("lister-item mode-detail imdb-user-review collapsable","lister-item mode-detail imdb-user-review with-spoiler")})
        reviews_id=[]
        titles=[]
        comments=[]
        scores=[]
        pattern = re.compile(r'\d+')
        for each_review in reviews_data:

            if(each_review.find('span',attrs={"class","point-scale"})==None): #some people just gave reviews but didn't gave score, filter these reviews
                continue
            title = each_review.find('a', attrs={"class": 'title'})
            comment = each_review.find('div', attrs={'class': "text show-more__control"})
            if(title==None or comment==None):  #filter the data without title or comment
                continue
            review_id=each_review.attrs['data-review-id']
            reviews_id.append(review_id.strip())
            titles.append(title.text.strip())
            comments.append(comment.text.strip())
            score = each_review.find('span', attrs={"class": None})
            scores.append(int(pattern.findall(score.text.strip())[0]))
        for i in range(len(scores)):#insert all the data we got just now, into the database
            mydb.movie_reviews.insert_one({"movie_id": movie_id[index], "review_id":reviews_id[i],"review_titles": titles[i], "comment": comments[i],"scores":scores[i]})

        #if this is a bad movie, we should get more comments by clicking "load more" to balance dataset, remember we crawl 100 bad movies and 250 good movies
        if(movie_overall_ratings[index]<6.5):
            # bad, the crawler should click "load more" on web page and catch more comments
            time.sleep(5) #don't send crawlers too frequently, be more friendly to the website
            try:
                key=data.find('div', attrs={'class': "load-more-data"}).attrs['data-key']
            except:
                index=index+1
                continue
            key=key.strip()
            new_url="https://www.imdb.com/title/tt"+movie_id[index]+"/reviews/_ajax?paginationKey="+key
            #constrcut a new_url to get data in "load more" page
            req = urllib.request.Request(url=new_url, headers=_header)
            #the following code is the same as above
            try:
                new_page = urllib.request.urlopen(req)
                html_code = new_page.read()
                new_page.close()
            except:
                failed_url.append(new_url)
                print("crawler fails at: ", new_url)
                index=index+1
                continue
            data = BeautifulSoup(html_code, "html.parser")
            reviews_data = data.find_all('div', attrs={"class": ("lister-item mode-detail imdb-user-review collapsable",
                                                                 "lister-item mode-detail imdb-user-review with-spoiler")})
            reviews_id = []
            titles = []
            comments = []
            scores = []
            pattern = re.compile(r'\d+')
            for each_review in reviews_data:

                if (each_review.find('span', attrs={"class",
                                                    "point-scale"}) == None):  # some people just gave reviews but didn't gave score, filter these reviews
                    continue
                title = each_review.find('a', attrs={"class": 'title'})
                comment = each_review.find('div', attrs={'class': "text show-more__control"})
                if (title == None or comment == None):  # filter the data without title or comment
                    continue
                review_id = each_review.attrs['data-review-id']
                reviews_id.append(review_id.strip())
                titles.append(title.text.strip())
                comments.append(comment.text.strip())
                score = each_review.find('span', attrs={"class": None})
                scores.append(int(pattern.findall(score.text.strip())[0]))
            for i in range(len(scores)):  # insert all the data we got just now, into the database
                mydb.movie_reviews.insert_one(
                    {"movie_id": movie_id[index], "review_id": reviews_id[i], "review_titles": titles[i],
                     "comment": comments[i], "scores": scores[i]})

        index=index+1
        time.sleep(60) #don't send crawlers too frequently, be more friendly to the website
    file=open('log.txt','w')
    for each_url in failed_url:
        file.write(each_url)
        file.write('\n')
    file.close()
    print("done")

if __name__ == "__main__":
    #movie_list_crawler()
    crawler_get_reviews()
