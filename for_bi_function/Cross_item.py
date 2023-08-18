# -*- coding: utf-8 -*-
"""
Created on Thu Aug 10 13:42:03 2023

@author: User
"""
import pandas as pd
import numpy as np
import setting as st
import numpy as np
from collections import Counter

def Transaction_with_product(Transaction_df,product_df):
    # ### 客戶來的次數by年+月
    Transaction_df['會員分類'] = Transaction_df.apply(member_c.member_class,axis = 1)
    Transaction_df.rename(columns = {'客戶/廠商編號':'客戶廠商編號','合計':'金額'}, inplace = True)
    Transaction_df['日期'] = Transaction_df['日期'].astype('datetime64[ns]')
    Transaction_df['日期年加月'] = Transaction_df['日期'].dt.strftime('%Y-%m')
    Transaction_df['日期年'] = Transaction_df['日期'].dt.strftime('%Y')
    member_filter =  (Transaction_df.會員分類 != '非會員')
    Transaction_df = Transaction_df.loc[member_filter].reset_index(drop=True)
    
    Transaction_df = Transaction_df.merge(product_df[['產品編號','分類']],on=['產品編號'],how='left')
    Transaction_df = Transaction_df[Transaction_df['分類'].isin(member_c.product)]
    #抓人數 by月份
    purchase_times = Transaction_df.groupby(['客戶廠商編號','日期年加月','分類']).客戶廠商編號.nunique()
    purchase_times = purchase_times.to_frame()
    purchase_times = purchase_times.rename(columns={"客戶廠商編號": "人數"})
    purchase_times = purchase_times.reset_index()
    # ### 客戶帶來的總額與件數by年+月
    purchase_sum = Transaction_df.groupby(['客戶廠商編號','日期年加月','分類']).agg({'金額': sum}) #'客戶代號':len
    purchase_sum = purchase_sum.reset_index()
    #### 合併總額數量與次數
    purchase_detail = purchase_sum.merge(purchase_times,on=['客戶廠商編號','日期年加月','分類'],how='inner')
    money_filter =  (purchase_detail.金額 > 0)
    purchase_detail = purchase_detail.loc[money_filter].reset_index(drop=True)
    purchase_detail['日期年'] = purchase_detail['日期年加月'].apply(lambda x: str(x)[0:4])
    #合併第一次、最後一次購買時間
    # first_buy = purchase_detail.groupby("客戶廠商編號", as_index = False)['日期年加月'].min()
    # first_buy.rename(columns = {'日期年加月':'第一次購買年加月'}, inplace = True)
    # last_buy = purchase_detail.groupby("客戶廠商編號", as_index = False)['日期年加月'].max()
    # last_buy.rename(columns = {'日期年加月':'最後一次購買年加月'}, inplace = True)
    # purchase_detail =  purchase_detail.merge(first_buy[['客戶廠商編號','第一次購買年加月']]
    # ,on=['客戶廠商編號'],how='inner')
    # purchase_detail =  purchase_detail.merge(last_buy[['客戶廠商編號','最後一次購買年加月']]
    # ,on=['客戶廠商編號'],how='inner')
    # purchase_detail['月份新舊客戶'] = np.where((purchase_detail['日期年加月'] == purchase_detail['第一次購買年加月']), '新客戶', '舊客戶')
    
    ###客戶groupby商品 去重複商品
    cross_item_byperson2 = purchase_detail.groupby(['客戶廠商編號','日期年']).apply(lambda x:'-'.join(np.unique(x['分類']))).reset_index()
    cross_item_byperson2.rename(columns={0: "購買品項"}, inplace = True)
    cross_item_byperson2["購買清單"] = cross_item_byperson2["購買品項"].apply(lambda x: len(x.split("-")))
    def good_mood(df,value): #是否購買品項 
        if df["購買品項"].find(value) != -1: 
            return "Y" #有購買回傳1
        else:
            return "N" 
    for index,value in enumerate(member_c.product): 
        cross_item_byperson2[f"{value}"] = cross_item_byperson2.apply(good_mood, args=(value,),axis = 1) #args可以給function參數

    # cross_item_bytimes = purchase_detail.groupby(['客戶廠商編號']).apply(lambda x:'-'.join((x['分類']))).reset_index()    
    # cross_item_bytimes.rename(columns={0: "購買品項"}, inplace = True)
    # #cross_item_bytimes["購買清單"] = cross_item_bytimes["購買品項"].apply(lambda x: len(x.split("-")))
    # def good_times(df,value): #是否購買品項 
    #     count =df["購買品項"].count(value) #count抓出產品數量 
    #     if count == 1:
    #         return "1次"
    #     elif count == 2:
    #         return "2次"
    #     elif count == 3:
    #         return "3次"
    #     elif count == 4:
    #         return "4次"
    #     elif count == 5:
    #         return "5次"
    #     elif count > 5 :
    #         return "5次以上"

    # for index,value in enumerate(member_c.product): 
    #     cross_item_bytimes[f"{value}"] = cross_item_bytimes.apply(good_times, args=(value,),axis = 1)
    cross_item_avgpro = cross_item_byperson2.groupby('日期年').agg(avg_product=('購買清單', 'mean'))
    
    cross_item_person = cross_item_byperson2.groupby(['日期年','購買清單']).agg(customer_count=('客戶廠商編號', len))
    cross_item_person = cross_item_person.reset_index()
    def cumsum_times(x): 
        if x['購買清單'] == 1:
            return '1類'
        elif x['購買清單'] == 2:
            return '2類' 
        elif x['購買清單'] == 3:
            return '3類' 
        elif x['購買清單'] == 4:
            return '4類'
        elif x['購買清單'] >= 5:
            return '5類以上'
    cross_item_person['回購分類'] = cross_item_person.apply(cumsum_times,axis=1)
    return cross_item_avgpro,cross_item_person#,cross_item_bytimes

member_c = st.for_member()
# Transaction_df = pd.read_csv("20150101-20230731_AA.csv",low_memory=False)
# product_df = pd.read_csv("產品分類.csv",low_memory=False).dropna()
# cross_item_byperson2 = Transaction_with_product(Transaction_df,product_df)
#member_filter =  (cross_item_byperson2['益菌寶'] == 'N')
#cross_item_byperson2 = cross_item_byperson2.loc[member_filter].reset_index(drop=True)
