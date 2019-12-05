The crawler part is done in crawler.py. Make sure to run movie_list_crawler() first to get movie lists, then run crawler_get_reviews() to crawl all reviews and save data into MongoDB (you are expected to get about 9900 reviews from 250 IMDb top-rating movies and 100 bottom movies. About 4400 reviews are negative. 

naive_bayes.py defines class naive_bayes. There are 3 public functions. train() takes one movie review (text) as input at each iteration. predict() takes one review (text) as input and outputs 0(negative) or 1(positive).save_model saves the current trained model into local txt file, so that the trained model can be directly used at next time.

main.py provides example to run the model. It takes 8000  movie reviews at random to train the model, and uses the remaining 1900+ movie reviews as test data. The accuracy rate is about 85%. 

Author: Zhuoyi Wu, Ziyao Sun, Yue Rong, Jack Lavin
