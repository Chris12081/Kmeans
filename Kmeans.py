'''
簡要敘述:
將資料進行Kmeans 分群
先進行  Kmeans 多群分析 找到 收斂群數目
在進行 Kmeans 分群 存入 CSV檔

'''

import pandas as pd
from sklearn.cluster import KMeans
import pymongo
pd.set_option('display.max_columns', 110)
# pd.set_option('display.max_rows', 110)
import matplotlib.pyplot as plt
import pprint
# Create connnect 建立與mongoDB連線
client = pymongo.MongoClient(host='192.168.158.128', port=27017)

# assign database 選擇資料庫
db = client.tibame
# assign colection 選擇collection
collection = db.recipe_vector_w2vm2

# Query specific column from all recipe_raw 選擇要讀取的資料欄位
queryArgs = {}
projectField = {'_id':False,'recipe_id' : True,'vector' : True}
search_response = db.recipe_vector_w2vm2.find(queryArgs, projection=projectField)
recipe_list = []
for item in search_response:
    recipe_list.append(item)
# 將 150個向量轉換成可以單獨顯示欄位的資料
def sav_colvec_mongo(data_list,collect):
    k = []
    for n,i in enumerate(data_list):
        km = {}
        km['recipe_id'] = i['recipe_id']
        for z in range(150):
            kmz = {}
            kmz['vector'+ str(z)] = i['vector'][0][z]
            km.update(kmz)
        k.append(km)
        # save back to mongoDB
        # print(km)
        pprint.pprint(km)
        db = client.tibame
        collection = collect
        insert_item = km
        insert_result = db.recipe_vector_w2vm3.insert_one(insert_item)
        print(insert_result)
# 開啟sav_colvec_mongo,存入mongo之資料,以利進行 Kmeans !
def open_data(collect):
    # assign database 選擇資料庫
    db = client.tibame
    # assign colection 選擇collection
    collection = collect
    df= pd.json_normalize(list(collection.find()))
    df2 = df.iloc[:,1:]
    return df2
# 利用1到多群 判斷最好的分群數 x 請填入最大群數
def find_Clustering(x):

    # Kmeans
    # 給出中心數範圍(1, x)
    cluster_range = range( 1, x)
    cluster_errors = []

    # 做x次, 把誤差結果放進cluster_errors list裡
    for num_clusters in cluster_range:
        clusters = KMeans( num_clusters )
        clusters.fit(df2)
        cluster_errors.append( clusters.inertia_ )

    # 畫出'X=kmeans中心數, Y=誤差'的圖
    clusters_df = pd.DataFrame( { "num_clusters":cluster_range, "cluster_errors": cluster_errors } )
    plt.figure(figsize=(12,6))
    plt.plot( clusters_df.num_clusters, clusters_df.cluster_errors, marker='*')
    plt.show()
# 分群 括號填入 Kmeans 分群的數目
def kmeans(x,save_csv):
    kMeans_x = KMeans(x)
    kMeans_x.fit(df2.iloc[:,1:])
    df2['label'] = kMeans_x.labels_
    df3 = df2.loc[:,['recipe_id','label']]
    df3.to_csv(save_csv,encoding='utf-8')


if __name__ == '__main__':
    # sav_colvec_mongo(recipe_list,db.recipe_vector_w2vm3) # 將資料存為可進 kmeans 之資料格式
    open_data(db.recipe_vector_w2vm3) # 開啟準備要進行 Kmeans 之 資料
    df2 = open_data(db.recipe_vector_w2vm3)
    find_Clustering(5) # 用於找到最好的分群數目會產生Plot(括號數字請填入最大分群數目)
    kmeans(6,'./kmeans/kmeans_1027_6.csv')  # 跑完 Kmeans 後會存入csv  (左邊設定分群數,右邊設定CSV存取名稱及路徑)