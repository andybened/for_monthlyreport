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

member_c = st.for_member()
def Transaction_with_product(Transaction_df,product_df,year):
    # ### 客戶來的次數by年+月
    Transaction_df['會員分類'] = Transaction_df.apply(member_c.member_class,axis = 1)
    Transaction_df.rename(columns = {'客戶/廠商編號':'客戶廠商編號','合計':'金額'}, inplace = True)
    Transaction_df['日期'] = Transaction_df['日期'].astype('datetime64[ns]')
    Transaction_df['日期年加月'] = Transaction_df['日期'].dt.strftime('%Y-%m')
    Transaction_df['日期年'] = Transaction_df['日期'].dt.strftime('%Y')
    member_filter =  (Transaction_df.會員分類 != '非會員') & (Transaction_df.日期年 == year)
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
    #合併第一次、最後一次購買時間
    first_buy = Transaction_df.groupby("客戶廠商編號", as_index = False)['日期年加月'].min()
    first_buy.rename(columns = {'日期年加月':'第一次購買年加月'}, inplace = True)
    last_buy = Transaction_df.groupby("客戶廠商編號", as_index = False)['日期年加月'].max()
    last_buy.rename(columns = {'日期年加月':'最後一次購買年加月'}, inplace = True)
    purchase_detail =  purchase_detail.merge(first_buy[['客戶廠商編號','第一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    purchase_detail =  purchase_detail.merge(last_buy[['客戶廠商編號','最後一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    purchase_detail['月份新舊客戶'] = np.where((purchase_detail['日期年加月'] == purchase_detail['第一次購買年加月']), '新客戶', '舊客戶')
    #抓單據 by月份
    people_bill = Transaction_df.groupby(['客戶廠商編號','日期年加月','分類']).agg({'單據號碼': pd.Series.nunique
                                                ,'金額': sum})
    people_bill = people_bill.reset_index()
    people_bill_fil =  (people_bill.金額 > 0)
    bill_detail = people_bill.loc[people_bill_fil].reset_index(drop=True)
    purchase_detail = purchase_detail.merge(bill_detail[['客戶廠商編號','日期年加月','分類','單據號碼']]
                                      ,on=['客戶廠商編號','日期年加月','分類'],how='inner')
    purchase_detail.rename(columns = {'單據號碼':'單據數'}, inplace = True)
    ###客戶groupby商品 去重複商品
    
    cross_item_byperson2 = purchase_detail.groupby(['客戶廠商編號']).apply(lambda x:'-'.join(np.unique(x['分類']))).reset_index()
    cross_item_byperson2.rename(columns={0: "購買品項"}, inplace = True)
    cross_item_byperson2["購買清單"] = cross_item_byperson2["購買品項"].apply(lambda x: len(x.split("-")))
    def good_mood(df,value): #是否購買品項 
        if df["購買品項"].find(value) != -1: 
            return "Y" #有購買回傳1
        else:
            return "N" 
    for index,value in enumerate(member_c.product): 
        cross_item_byperson2[f"{value}"] = cross_item_byperson2.apply(good_mood, args=(value,),axis = 1) #args可以給function參數

    cross_item_bytimes = purchase_detail.groupby(['客戶廠商編號']).apply(lambda x:'-'.join((x['分類']))).reset_index()    
    cross_item_bytimes.rename(columns={0: "購買品項"}, inplace = True)
    #cross_item_bytimes["購買清單"] = cross_item_bytimes["購買品項"].apply(lambda x: len(x.split("-")))
    def good_times(df,value): #是否購買品項 
        count =df["購買品項"].count(value) #count抓出產品數量 
        if count == 1:
            return "1次"
        elif count == 2:
            return "2次"
        elif count == 3:
            return "3次"
        elif count == 4:
            return "4次"
        elif count == 5:
            return "5次"
        elif count > 5 :
            return "5次以上"

    for index,value in enumerate(member_c.product): 
        cross_item_bytimes[f"{value}"] = cross_item_bytimes.apply(good_times, args=(value,),axis = 1)
        
    return cross_item_byperson2,cross_item_bytimes

def product_amount(cross_item_byperson2):
    one_product = {}
    moreone_product = {}
    for i in member_c.product:
        filter_onegood =  (cross_item_byperson2[f'{i}'] == "Y") & (cross_item_byperson2["購買清單"] == 1) 
        good_1 = cross_item_byperson2['客戶廠商編號'].loc[filter_onegood].reset_index(drop=True).value_counts()
        one_product[f'{i}'] = len(good_1)
       
        filter_multigood =  (cross_item_byperson2[f'{i}'] == "Y") & (cross_item_byperson2["購買清單"] > 1) 
        good_2 = cross_item_byperson2['客戶廠商編號'].loc[filter_multigood].reset_index(drop=True).value_counts()
        moreone_product[f'{i}'] = len(good_2)
        
    one_product_pd = pd.DataFrame.from_dict(one_product,orient='index')
    one_product_pd.rename(columns={0: "僅單品項"}, inplace = True)
    moreone_product_pd = pd.DataFrame.from_dict(moreone_product,orient='index')
    moreone_product_pd.rename(columns={0: "跨品項"}, inplace = True)
    total_df = pd.concat([one_product_pd,moreone_product_pd],axis= 1)
    total_df['總人數'] = total_df["僅單品項"] + total_df["跨品項"]
    total_df['單品項(%)'] = (total_df["僅單品項"] / total_df["總人數"]).apply(lambda x: format(x,'.0%')) 
    total_df['跨品項(%)'] = (total_df["跨品項"] / total_df["總人數"]).apply(lambda x: format(x,'.0%')) 

    multi_product = {}
    for index,value in enumerate(member_c.product):
        counts = index+1
        multi_good = []
        for j in member_c.product:
            filter1 =  (cross_item_byperson2[f'{value}'] == "Y") & (cross_item_byperson2[f'{j}'] == "Y")
            good_1 = cross_item_byperson2['客戶廠商編號'].loc[filter1].reset_index(drop=True).value_counts()
            multi_good.append(len(good_1))
        multi_product[f'{counts}.{value}'] = multi_good
            #multi_product[f'{counts}.{value}-{j}'] = len(good_1)
    new_index = list(member_c.product)
    final_pd = pd.DataFrame.from_dict(multi_product)
    final_pd.index = new_index
    return final_pd,total_df
   
def product_repurchase(cross_item_bytimes):
    product_list_df = []
    for product in member_c.product:
        cr_repurchase_df = cross_item_bytimes.groupby([f'{product}']).agg({'客戶廠商編號': len})
        cr_repurchase_df.reset_index(inplace = True)
        cr_repurchase_df.rename(columns={'客戶廠商編號': f'{product}',f'{product}': '重購次數'},inplace = True)
        cr_repurchase_df.set_index("重購次數",inplace = True)
        cr_repurchase_df.loc['總計'] = cr_repurchase_df[f'{product}'].sum(axis = 0)
        product_list_df.append(cr_repurchase_df)   
    #合併各產品
    product_df = product_list_df[0]
    for i in range(1,len(product_list_df)):
        product_df = product_df.merge(product_list_df[i],on=['重購次數'],how='outer')
    product_df.fillna(0,inplace = True)  
    
    #透過各產品總計 產生占比
    percentage_df = (product_df / product_df.loc["總計"])
    #percentage_df = percentage_df.applymap(format_percentage)
    percentage_df = percentage_df.applymap(lambda x: format(x,'.1%')) 
    return product_df,percentage_df