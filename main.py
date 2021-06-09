import requests
from bs4 import BeautifulSoup
import pymongo
from etherscan import Etherscan
import time
from datetime import datetime

# Enter your etherscan API
eth = Etherscan('xxx')


# start： starting block  end: end block  upperlimit: upperlimmit of contracts  col: database column
def CollectContractAddress(start, end, upperlimmit, col):
    _list = []
    for i in range(end, start, -1):
        a = datetime.now()  # Get current time
        print('-----------------CURRENT PROGRESS %d-------------------'% i)
        url = 'https://etherchain.org/block/' + str(i) + '#pills-txs'
        strhtml = requests.get(url)
        soup = BeautifulSoup(strhtml.text, 'html.parser')
        soup.prettify()

        stop_flag = False
        index_in_block = 0
        for tr in soup.find_all('tr', ):
            for td in tr.find_all('td', ):
                try:
                    # find the cell with contract icon
                    icon_find = td.find_all('i', )
                    if icon_find:
                        # contract index
                        index_in_block += 1
                        # get contract ID
                        contract_id = td.find('a', ).get('href')[-42:]
                        # find whether the contract is repeat
                        if col.count_documents({"contract": contract_id}) != 0:
                            print("Find duplicate:%s; Current Index In Block:%d" % (contract_id, index_in_block))
                            break

                        # Limit the speed of accessing
                        time.sleep(0.1)
                        # get contract code and store it into MongoDB
                        contract_code = eth.get_contract_source_code(contract_id)[0]['SourceCode']
                        if contract_code == '':
                            print("Push Empty Contract: %s; Current index in block:%d" % (contract_id, index_in_block))
                            mydict = {"contract": contract_id, 'contract_code': ''}
                            col.insert_one(mydict)
                            break

                        mydict = {"contract": contract_id, 'contract_code': contract_code}
                        print("Successfully push data into database:%s; Current index in block:%d" % (contract_id, index_in_block))
                        col.insert_one(mydict)
                        _list = []
                        if col.estimated_document_count() >= upperlimmit:
                            stop_flag = True
                except:
                    print("Exception Detected")
                if stop_flag:
                    break
            if stop_flag:
                break

        b = datetime.now()  # get current time
        durn = (b-a).seconds
        print("we spend %d seconds in this block" % durn)
    return _list


def initMongo(host, dbname, col):
    myclient = pymongo.MongoClient(host)
    mydb = myclient[dbname]
    mycol = mydb[col]
    return mycol


if __name__ == '__main__':
    # initialize MongoDB
    col = initMongo('mongodb://localhost:27017/', 'contractCollector', 'contractAddress')
    contractAddress = CollectContractAddress(12597000,12597923, 100000, col)
