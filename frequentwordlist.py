import csv
def write_word_list(top=20000):

    wordlist=[]
        
    with open('unigram_freq.csv','r') as f:
        x=0
        r=csv.reader(f)
        y=0
        for row in r:
            if y==0:
                y+=1
                continue
            if x==top:                #20000 most used english words i took 
                break
            
            if (len(row[0])<2 and row[0].lower() not in 'ai') or not row[0].isalpha():
                continue
            x+=1
            wordlist.append([row[0].lower()])
    
    with open("top_{}.csv".format(str(top)),'w',newline='') as f:
        wr= csv.writer(f)
        wr.writerows(wordlist)

def get_word_list(top=20000):
    listofwords=[]
    with open('top_{}.csv'.format(str(top)),'r', newline='') as f:
        r=csv.reader(f)
        listofwords=[row[0] for row in r]
    return listofwords
            

if __name__ =="__main__":
    #write_word_list()
    print(get_word_list())
    