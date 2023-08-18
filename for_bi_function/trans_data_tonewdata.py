# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 10:34:30 2023

@author: User
"""

import pandas as pd
import numpy as np
import setting as st    
member_c = st.for_member()   
def Transaction_with_product(Transaction_df,product_df):
    # ### 客戶來的次數by年+月
    Transaction_df['會員分類'] = Transaction_df.apply(member_c.member_class,axis = 1)
    member_filter =  (Transaction_df.會員分類 != '非會員')
    Transaction_df = Transaction_df.loc[member_filter].reset_index(drop=True)
    Transaction_df.rename(columns = {'客戶/廠商編號':'客戶廠商編號','合計':'金額'}, inplace = True)
    Transaction_df['日期'] = Transaction_df['日期'].astype('datetime64[ns]')
    Transaction_df['日期年加月'] = Transaction_df['日期'].dt.strftime('%Y-%m')
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
    
    #只抓金額
    purchase_detail2 = purchase_sum.merge(purchase_times,on=['客戶廠商編號','日期年加月','分類'],how='inner')
    purchase_detail2 =  purchase_detail2.merge(first_buy[['客戶廠商編號','第一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    purchase_detail2 =  purchase_detail2.merge(last_buy[['客戶廠商編號','最後一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    purchase_detail2['月份新舊客戶'] = np.where((purchase_detail2['日期年加月'] == purchase_detail2['第一次購買年加月']), '新客戶', '舊客戶')
    
    #抓單據 by月份
    #people_bill = Transaction_df.groupby(['客戶廠商編號','日期年加月','分類']).單據號碼.nunique()
    people_bill = Transaction_df.groupby(['客戶廠商編號','日期年加月','分類']).agg({'單據號碼': pd.Series.nunique
                                                ,'金額': sum})
    people_bill = people_bill.reset_index()
    people_bill_fil =  (people_bill.金額 > 0)
    bill_detail = people_bill.loc[people_bill_fil].reset_index(drop=True)
    purchase_detail = purchase_detail.merge(bill_detail[['客戶廠商編號','日期年加月','分類','單據號碼']]
                                      ,on=['客戶廠商編號','日期年加月','分類'],how='inner')
    
    purchase_detail.rename(columns = {'單據號碼':'單據數'}, inplace = True)
    return purchase_detail, purchase_detail2

def Transaction_without_product(Transaction_df):
    """人數(當月多次也只算1) 客戶當月金額加總>0"""
    # ### 客戶來的次數by年+月
    Transaction_df['會員分類'] = Transaction_df.apply(member_c.member_class,axis = 1)
    member_filter =  (Transaction_df.會員分類 != '非會員')
    Transaction_df = Transaction_df.loc[member_filter].reset_index(drop=True)
    Transaction_df.rename(columns = {'客戶/廠商編號':'客戶廠商編號','合計':'金額'}, inplace = True)
    Transaction_df['日期'] = Transaction_df['日期'].astype('datetime64[ns]')
    Transaction_df['日期年加月'] = Transaction_df['日期'].dt.strftime('%Y-%m')
    #Transaction_df['日期年加月'] = Transaction_df['日期'].apply(lambda x: str(x)[0:6])
    #抓人數 by月份
    purchase_times = Transaction_df.groupby(['客戶廠商編號','日期年加月']).客戶廠商編號.nunique()
    purchase_times = purchase_times.to_frame()
    purchase_times = purchase_times.rename(columns={"客戶廠商編號": "人數"})
    purchase_times = purchase_times.reset_index()
    # ### 客戶帶來的總額與件數by年+月
    purchase_sum = Transaction_df.groupby(['客戶廠商編號','日期年加月']).agg({'金額': sum}) #'客戶代號':len
    purchase_sum = purchase_sum.reset_index()
    #### 合併總額數量與次數
    purchase_detail = purchase_sum.merge(purchase_times,on=['客戶廠商編號','日期年加月'],how='inner')
    money_filter =  (purchase_detail.金額 > 0)
    purchase_detail = purchase_detail.loc[money_filter].reset_index(drop=True)
    #合併第一次、最後一次購買時間
    first_buy = purchase_detail.groupby("客戶廠商編號", as_index = False)['日期年加月'].min()
    first_buy.rename(columns = {'日期年加月':'第一次購買年加月'}, inplace = True)
    last_buy = purchase_detail.groupby("客戶廠商編號", as_index = False)['日期年加月'].max()
    last_buy.rename(columns = {'日期年加月':'最後一次購買年加月'}, inplace = True)
    purchase_detail =  purchase_detail.merge(first_buy[['客戶廠商編號','第一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    purchase_detail =  purchase_detail.merge(last_buy[['客戶廠商編號','最後一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    purchase_detail['月份新舊客戶'] = np.where((purchase_detail['日期年加月'] == purchase_detail['第一次購買年加月']), '新客戶', '舊客戶')
    #### 合併後累加
    customer = purchase_detail.groupby(['客戶廠商編號'])
    purchase_detail['cumsum_times'] = customer['人數'].cumsum() #人數
    purchase_detail['cumsum_money'] = customer['金額'].cumsum() #總額
    #只抓金額
    purchase_detail2 = purchase_sum.merge(purchase_times,on=['客戶廠商編號','日期年加月'],how='inner')
    purchase_detail2 =  purchase_detail2.merge(first_buy[['客戶廠商編號','第一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    purchase_detail2 =  purchase_detail2.merge(last_buy[['客戶廠商編號','最後一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    purchase_detail2['月份新舊客戶'] = np.where((purchase_detail2['日期年加月'] == purchase_detail2['第一次購買年加月']), '新客戶', '舊客戶')
    
    #抓單據 by月份
    #people_bill = Transaction_df.groupby(['客戶廠商編號','日期年加月']).單據號碼.nunique()
    people_bill = Transaction_df.groupby(['客戶廠商編號','日期年加月']).agg({'單據號碼': pd.Series.nunique
                                                ,'金額': sum})
    people_bill = people_bill.reset_index()
    people_bill_fil =  (people_bill.金額 > 0)
    bill_detail = people_bill.loc[people_bill_fil].reset_index(drop=True)
    purchase_detail = purchase_detail.merge(bill_detail[['客戶廠商編號','日期年加月','單據號碼']]
                                      ,on=['客戶廠商編號','日期年加月'],how='inner')
    
    purchase_detail.rename(columns = {'單據號碼':'單據數'}, inplace = True)
    return purchase_detail,purchase_detail2


def newold_forbi(purchase_product_detail,bill_product_detail3,  purchase_detail,purchase_detail2):
    df_product = purchase_product_detail.groupby(['日期年加月','分類','月份新舊客戶']).agg(
        {'人數':len,'單據數':sum}).reset_index()
    df_product2 = bill_product_detail3.groupby(['日期年加月','分類','月份新舊客戶']).agg(
        {'金額':sum}).reset_index()
    df_final = df_product.merge(df_product2,on=['日期年加月','分類','月份新舊客戶'],how='inner')
    
    df_noproduct = purchase_detail.groupby(['日期年加月','月份新舊客戶']).agg(
        {'人數':len,'單據數':sum}).reset_index()
    df_noproduct2 = purchase_detail2.groupby(['日期年加月','月份新舊客戶']).agg(
        {'金額':sum}).reset_index()
    df_final2 = df_noproduct.merge(df_noproduct2,on=['日期年加月','月份新舊客戶'],how='inner')
    return df_final,df_final2

# Transaction_df = pd.read_csv("20150101-20230731_AA.csv",low_memory=False)
# product_df = pd.read_csv("產品分類.csv",low_memory=False).dropna()
# purchase_product_detail,bill_product_detail3 = Transaction_with_product(Transaction_df,product_df)
# purchase_detail,purchase_detail2 = Transaction_without_product(Transaction_df)
# df_final,df_final2 = newold_forbi(purchase_product_detail,bill_product_detail3,  purchase_detail,purchase_detail2)

# df_final.to_excel('purchase_detail.xlsx',index = False)
# purchase_product_detail.to_excel('商品人數計算用.xlsx',index = False)

# with pd.ExcelWriter('output.xlsx') as writer:  
#     purchase_money.to_excel(writer, sheet_name='purchase_money')
#     purchase_object.to_excel(writer, sheet_name='purchase_object')