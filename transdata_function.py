# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 16:34:52 2023

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
    #抓單據 by月份
    people_bill = Transaction_df.groupby(['單據號碼','日期年加月','分類']).單據號碼.nunique()
    people_bill = people_bill.to_frame()
    people_bill = people_bill.rename(columns={"單據號碼": "單據數"})
    people_bill = people_bill.reset_index()
    bill_compare = Transaction_df[['單據號碼','客戶廠商編號','分類']]
    bill_compare = bill_compare.drop_duplicates()
    # ### 單據帶來的總額與by年+月
    bill_sum = Transaction_df.groupby(['單據號碼','日期年加月','分類']).agg({'金額': sum}) #'客戶代號':len
    bill_sum = bill_sum.reset_index()
    #### 合併總額數量與次數
    bill_detail = bill_sum.merge(people_bill,on=['單據號碼','日期年加月','分類'],how='inner')
    bill_filter =  (bill_detail.金額 > 0)
    bill_detail = bill_detail.loc[bill_filter].reset_index(drop=True)
    bill_detail2 = bill_detail.merge(bill_compare,on=['單據號碼','分類'],how='inner')
    bill_detail3 = bill_detail2.merge(purchase_detail[['客戶廠商編號','日期年加月','分類','月份新舊客戶']]
                                      ,on=['客戶廠商編號','日期年加月','分類'],how='left')
    return purchase_detail,bill_detail3

def makedf_with_product(purchase_product_detail,bill_product_detail3):
    """人數(當月多次也只算1) 排掉客戶當月金額加總為負或是0
    最後會有 人數 金額總額 單據數"""
    # money_filter =  (purchase_product_detail.金額 > 0)
    # df_money_filter = purchase_product_detail.loc[money_filter].reset_index(drop=True)
    # 人數+金額
    df_sumpeople = purchase_product_detail.groupby(['日期年加月','分類']).agg({'人數':len,'金額':sum}).reset_index()
    #df_summoney = df_money_filter.groupby('日期年加月').agg({'金額':sum}).reset_index()
    # 單據
    # bill_filter =  (bill_product_detail3.金額 > 0)
    # bill_money_filter = bill_product_detail3.loc[bill_filter].reset_index(drop=True)
    df_sumbill = bill_product_detail3.groupby(['日期年加月','分類']).agg({'單據數':sum}).reset_index()
    df_product = df_sumpeople.merge(df_sumbill,on=['日期年加月','分類'],how='inner')
    
    ############### 新客 #######
    newmoney_filter =  (purchase_product_detail.月份新舊客戶 == '新客戶')
    df_newmoney_filter = purchase_product_detail.loc[newmoney_filter].reset_index(drop=True)
    # 人數+金額
    df_sumnewpeople = df_newmoney_filter.groupby(['日期年加月','分類']).agg({'人數':len,'金額':sum}).reset_index()
    #df_sumnewmoney = df_newmoney_filter.groupby('日期年加月').agg({'金額':sum}).reset_index()
    # 單據
    newbill_filter =   (bill_product_detail3.月份新舊客戶 == '新客戶')
    bill_newmoney_filter = bill_product_detail3.loc[newbill_filter].reset_index(drop=True)
    df_new_sumbill = bill_newmoney_filter.groupby(['日期年加月','分類']).agg({'單據數':sum}).reset_index()
    df_new_product = df_sumnewpeople.merge(df_new_sumbill,on=['日期年加月','分類'],how='inner')
    
    ############### 舊客 ####### 
    oldmoney_filter =  (purchase_product_detail.月份新舊客戶 == '舊客戶')
    df_oldmoney_filter = purchase_product_detail.loc[oldmoney_filter].reset_index(drop=True)
    # 人數+金額
    df_sumoldpeople = df_oldmoney_filter.groupby(['日期年加月','分類']).agg({'人數':len,'金額':sum}).reset_index()
    # 單據
    oldbill_filter =  (bill_product_detail3.月份新舊客戶 == '舊客戶')
    bill_oldmoney_filter = bill_product_detail3.loc[oldbill_filter].reset_index(drop=True)
    df_old_sumbill = bill_oldmoney_filter.groupby(['日期年加月','分類']).agg({'單據數':sum}).reset_index()
    df_old_product = df_sumoldpeople.merge(df_old_sumbill,on=['日期年加月','分類'],how='inner')
    
    df_product['ATV'] = (df_product['金額']/df_product['單據數']).astype('int')
    df_product['ATV人'] = (df_product['金額']/df_product['人數']).astype('int')
    df_new_product['ATV'] = (df_new_product['金額']/df_new_product['單據數']).astype('int')
    df_new_product['ATV人'] = (df_new_product['金額']/df_new_product['人數']).astype('int')
    df_old_product['ATV'] = (df_old_product['金額']/df_old_product['單據數']).astype('int')
    df_old_product['ATV人'] = (df_old_product['金額']/df_old_product['人數']).astype('int')
    
    return df_product,df_new_product,df_old_product

def Transaction_without_product(Transaction_df):
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
    first_buy = Transaction_df.groupby("客戶廠商編號", as_index = False)['日期年加月'].min()
    first_buy.rename(columns = {'日期年加月':'第一次購買年加月'}, inplace = True)
    last_buy = Transaction_df.groupby("客戶廠商編號", as_index = False)['日期年加月'].max()
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
    #purchase_detail['cumsum_count'] = customer['數量'].cumsum() #購買件數
    #抓單據 by月份
    people_bill = Transaction_df.groupby(['單據號碼','日期年加月']).單據號碼.nunique()
    people_bill = people_bill.to_frame()
    people_bill = people_bill.rename(columns={"單據號碼": "單據數"})
    people_bill = people_bill.reset_index()
    bill_compare = Transaction_df[['單據號碼','客戶廠商編號']]
    bill_compare = bill_compare.drop_duplicates()
    # ### 單據帶來的總額與by年+月
    bill_sum = Transaction_df.groupby(['單據號碼','日期年加月']).agg({'金額': sum}) #'客戶代號':len
    bill_sum = bill_sum.reset_index()
    #### 合併總額數量與次數
    bill_detail = bill_sum.merge(people_bill,on=['單據號碼','日期年加月'],how='inner')
    bill_filter =  (bill_detail.金額 > 0)
    bill_detail = bill_detail.loc[bill_filter].reset_index(drop=True)
    bill_detail2 = bill_detail.merge(bill_compare,on=['單據號碼'],how='inner')
    bill_detail3 = bill_detail2.merge(purchase_detail[['客戶廠商編號','日期年加月','月份新舊客戶']]
                                      ,on=['客戶廠商編號','日期年加月'],how='left')
    return purchase_detail,bill_detail3

def makedf_without_product(purchase_detail,bill_detail3):
    """人數(當月多次也只算1) 客戶當月金額加總>0
    最後會有 人數 金額總額 單據數"""
    # money_filter =  (purchase_detail.金額 > 0)
    # df_money_filter = purchase_detail.loc[money_filter].reset_index(drop=True)
    df_sumpeople = purchase_detail.groupby('日期年加月').agg({'人數':len}).reset_index()
    # 金額
    df_summoney = purchase_detail.groupby('日期年加月').agg({'金額':sum}).reset_index()
    # 單據
    #bill_filter =  (bill_detail3.金額 > 0)
    #bill_money_filter = bill_detail3.loc[bill_filter].reset_index(drop=True)
    df_sumbill = bill_detail3.groupby('日期年加月').agg({'單據數':sum}).reset_index()
    final_df = df_sumpeople.merge(df_summoney,on=['日期年加月'],how='inner')
    total_df = final_df.merge(df_sumbill,on=['日期年加月'],how='inner')
    
    ############### 新客 #######
    newmoney_filter =  (purchase_detail.月份新舊客戶 == '新客戶')
    df_newmoney_filter = purchase_detail.loc[newmoney_filter].reset_index(drop=True)
    df_sumnewpeople = df_newmoney_filter.groupby('日期年加月').agg({'人數':len}).reset_index()
    # 金額
    df_sumnewmoney = df_newmoney_filter.groupby('日期年加月').agg({'金額':sum}).reset_index()
    # 單據
    newbill_filter =  (bill_detail3.月份新舊客戶 == '新客戶') #(bill_detail3.金額 > 0) & 
    bill_newmoney_filter = bill_detail3.loc[newbill_filter].reset_index(drop=True)
    df_new_sumbill = bill_newmoney_filter.groupby('日期年加月').agg({'單據數':sum}).reset_index()
    new_final_df = df_sumnewpeople.merge(df_sumnewmoney,on=['日期年加月'],how='inner')
    total_new_df = new_final_df.merge(df_new_sumbill,on=['日期年加月'],how='inner')
    
    ############### 舊客 ####### 
    oldmoney_filter =  (purchase_detail.月份新舊客戶 == '舊客戶')
    df_oldmoney_filter = purchase_detail.loc[oldmoney_filter].reset_index(drop=True)
    df_sumoldpeople = df_oldmoney_filter.groupby('日期年加月').agg({'人數':len}).reset_index()
    # 金額
    df_sumoldmoney = df_oldmoney_filter.groupby('日期年加月').agg({'金額':sum}).reset_index()
    # 單據
    oldbill_filter = (bill_detail3.月份新舊客戶 == '舊客戶')
    bill_oldmoney_filter = bill_detail3.loc[oldbill_filter].reset_index(drop=True)
    df_old_sumbill = bill_oldmoney_filter.groupby('日期年加月').agg({'單據數':sum}).reset_index()
    old_final_df = df_sumoldpeople.merge(df_sumoldmoney,on=['日期年加月'],how='inner')
    total_old_df = old_final_df.merge(df_old_sumbill,on=['日期年加月'],how='inner')
    
    total_df['ATV'] = (total_df['金額']/total_df['單據數']).astype('int')
    total_df['ATV人'] = (total_df['金額']/total_df['人數']).astype('int')
    total_new_df['ATV'] = (total_new_df['金額']/total_new_df['單據數']).astype('int')
    total_new_df['ATV人'] = (total_new_df['金額']/total_new_df['人數']).astype('int')
    total_old_df['ATV'] = (total_old_df['金額']/total_old_df['單據數']).astype('int')
    total_old_df['ATV人'] = (total_old_df['金額']/total_old_df['人數']).astype('int')
    
    return total_df,total_new_df,total_old_df

def sep_product(df_product):
    product_list = []
    for product in member_c.product:
        p_filter = (df_product['分類'] == product)
        new_df = df_product.loc[p_filter].reset_index(drop=True)
        new_df.drop('分類', inplace=True, axis=1)
        product_list.append(new_df)
    return product_list
def newold_sep_product(df_new_product,df_old_product):
    newold_p = df_new_product[['日期年加月','分類','人數']].merge(df_old_product[['日期年加月','分類','人數']]
        ,on=['日期年加月','分類'],how='left')
    newold_p.fillna(value=0, inplace=True)
    newold_p.rename(columns = {'人數_x':'新客戶','人數_y':'舊客戶'}, inplace = True)
    newold_p["新客佔比"] = newold_p["新客戶"] / (newold_p["新客戶"] + newold_p["舊客戶"])
    newold_p["新客佔比"] = newold_p["新客佔比"].apply(lambda x: format(x,'.0%'))
    newold_p["舊客佔比"] = newold_p["舊客戶"] / (newold_p["新客戶"] + newold_p["舊客戶"])
    newold_p["舊客佔比"] = newold_p["舊客佔比"].apply(lambda x: format(x,'.0%'))
    product_newold = []
    for product in member_c.product:
        p_filter = (newold_p['分類'] == product)
        new_df = newold_p.loc[p_filter].reset_index(drop=True)
        product_newold.append(new_df)
    return product_newold

def year_product(df_product,year_date):
    df_product['分類'] = pd.Categorical(df_product['分類'], member_c.product)
    df_product.sort_values(['分類'])
    df_product['年份'] = df_product['日期年加月'].apply(lambda x: str(x)[0:4])
    year_df = df_product.groupby(['年份','分類']).agg({'人數':sum, '金額':sum, '單據數':sum}).reset_index()
    p_filter = (year_df['年份'] == year_date)
    newyear_df = year_df.loc[p_filter].reset_index(drop=True)
    newyear_df.drop('年份', inplace=True, axis=1)
    return newyear_df