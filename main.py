from naive_bayes import*

def main():
    model=naive_bayes()
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient.get_database('IMDb')
    my_table=mydb['movie_reviews']
    train_data=my_table.aggregate([{ '$sample': {'size': 8000}}])
    train_data_id=[]
    model = naive_bayes()
    for i in train_data:
        model.train( i['review_titles']+i['comment'] , i['scores'])
        train_data_id.append(i['review_id'])
    test_data=my_table.find({ "review_id": { '$nin' : train_data_id } } )
    correct_count=0
    incorrect_count=0
    false_negative=0
    false_positive=0
    negative_count=0
    positive_count=0
    print("Test begin")
    for i in test_data:
        prediction=model.predict(i['review_titles']+i['comment'] )
        label=0
        if(i['scores']>=6.5):
            label=1
            positive_count=positive_count+1
        else:
            negative_count=negative_count+1
        if(prediction==label):
            correct_count=correct_count+1
        else:
            incorrect_count=incorrect_count+1
            if(prediction==0):
                false_negative=false_negative+1
            else:
                false_positive=false_positive+1
    print("Correct count: ",correct_count)
    print("Incorrect count: ",incorrect_count)
    print("Accuracy: ",correct_count/(correct_count+incorrect_count))
    print("False positive: ",false_positive)
    print("False negative: ", false_negative)
    print("Positive count: ", positive_count)
    print("Negative count: ",negative_count)

    #model.save_model()
def test():
    model = naive_bayes('model.txt')

if __name__=='__main__':
    main()
