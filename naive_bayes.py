import re

from pattern.en import lemma

from nltk.corpus import stopwords
import math
import pymongo
import langid
import json
#due to the bug of pattern in python3.7, running lemma at the first time will raise error, then running it again will be ok
#so I add try:except here
try:
    lemma("hello")
except:
    pass

class naive_bayes:
    def __init__(self,load_data=None,threshold=6.5):
        if(load_data==None):
            self._positive_reviews_words_frequency={}
            self._negative_reviews_words_frequency={}
            self._total_train_reviews=0
            self._positive_train_reviews=0
            self._threshold=threshold
            self._stop_words=set(stopwords.words('english'))
        else:
            file=open(load_data,'r',encoding='utf-8')
            js=file.read()
            file.close()
            dic=json.loads(js)
            self._positive_reviews_words_frequency = dic['_positive_reviews_words_frequency']
            self._negative_reviews_words_frequency = dic['_negative_reviews_words_frequency']
            self._total_train_reviews = dic['_total_train_reviews']
            self._positive_train_reviews = dic['_positive_train_reviews']
            self._threshold = dic['_threshold']
            self._stop_words = set(stopwords.words('english'))
    def _textParse(self,bigString):
        Tokens = re.split(r'\W+', bigString)
        list_of_tokens=[]
        for each_token in Tokens:

            processed_each_token=lemma(each_token)
            if processed_each_token not in self._stop_words and len(processed_each_token)>1:
                #list_of_tokens.append(porter_stemmer.stem(each_token))
                list_of_tokens.append(processed_each_token)

        return list_of_tokens
            
    def _bag_of_words_2_dic(self,vocab_list):
        return_dic={}
        for word in vocab_list:
            if word in return_dic:
                return_dic[word]= return_dic[word]+1
            else:
                return_dic[word]=1
        return return_dic
    def train(self,input_text,score):
        if(langid.classify("input_text")[0]!='en'):
            print("Not English Content, abort")
            return
        vocab_list=self._textParse(input_text)
        review_words_dic = self._bag_of_words_2_dic(vocab_list)
        if(score>=self._threshold):
            self._positive_train_reviews=self._positive_train_reviews+1
            for each_word in review_words_dic.keys():
                if(each_word in self._positive_reviews_words_frequency):
                    self._positive_reviews_words_frequency[each_word]=self._positive_reviews_words_frequency[each_word]+review_words_dic[each_word]
                else:
                    self._positive_reviews_words_frequency[each_word] =1

        else:
            for each_word in review_words_dic.keys():
                if(each_word in self._negative_reviews_words_frequency):
                    self._negative_reviews_words_frequency[each_word]=self._negative_reviews_words_frequency[each_word]+review_words_dic[each_word]
                else:
                    self._negative_reviews_words_frequency[each_word] =1
        self._total_train_reviews = self._total_train_reviews + 1
    def predict(self,input_text):
        if (langid.classify("input_text")[0] != 'en'):
            print("Not English Content, abort")
            return None
        vocab_list=self._textParse(input_text)
        p_positive=0
        p_negative=0
        total_positive_review_words=max(sum(self._positive_reviews_words_frequency.values()),2)
        total_negative_review_words = max(sum(self._negative_reviews_words_frequency.values()), 2)
        for each_word in vocab_list:
            p_positive=p_positive+math.log(self._positive_reviews_words_frequency.get(each_word,1)/total_positive_review_words)
            #print(self._positive_reviews_words_frequency.get(each_word,1)/total_positive_review_words)
            p_negative= p_negative + math.log(self._negative_reviews_words_frequency.get(each_word, 1)/total_negative_review_words)
        #print("done")
        p_class_positive=max(self._positive_train_reviews/self._total_train_reviews,0.000001)
        p_class_negative=max(1-p_class_positive,0.000001)
        p_positive=p_positive+math.log(p_class_positive)
        p_negative=p_negative+math.log(p_class_negative)
        if(p_positive>p_negative):
            return 1
        else:
            return 0

    def save_model(self,file_name="model.txt"):
        model_data={'_positive_reviews_words_frequency': self._positive_reviews_words_frequency, '_negative_reviews_words_frequency': self._negative_reviews_words_frequency,
         '_total_train_reviews': self._total_train_reviews, '_positive_train_reviews': self._positive_train_reviews, '_threshold': self._threshold}
        js = json.dumps(model_data, ensure_ascii=False)
        file=open(file_name,'w',encoding='utf-8')
        file.write(js)
        file.close

if __name__=="__main__":
    pass

        
            
    
        
