The crawler part is done in crawler.py. Make sure to run movie_list_crawler() first to get movie lists, then run crawler_get_reviews() to creaw all reviews and save data into MongoDB

naive_bayes.py defines class naive_bayes. There are 3 public functions, train(), which take one movie review (text) as input at each iteration. predict() takes one review (text) as input and output 0(negative) and 1(positive)
save_model save the currently trained model into local txt file, so that the trained model can be directly used at next time.

main.py provides example to run the model. It takes 8000 pieces of movie reviews at random to train the model, and use the remaining 1900+ movie reviews as test data.

Author: Zhuoyi Wu, Ziyao Sun, Yue Rong, Jack Lavin