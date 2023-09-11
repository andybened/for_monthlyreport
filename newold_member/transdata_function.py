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
    
    people_bill = Transaction_df.groupby(['客戶廠商編號','單據號碼','分類','日期年加月']).agg({'單據號碼': pd.Series.nunique,'金額': sum})
    def change_neg(x):
        if x['金額'] == 0:
            return 0
        elif x['金額'] < 0:
            return -x['單據號碼']
        elif x['金額'] > 0:
            return x['單據號碼'] 
    people_bill['單據數'] = people_bill.apply(change_neg,axis = 1)
    people_bill.drop('單據號碼', inplace=True, axis=1)
    people_bill = people_bill.reset_index()
    people_bill_final = people_bill.groupby(['客戶廠商編號','日期年加月','分類']).agg({'客戶廠商編號':pd.Series.nunique
                                                                     ,'單據數': sum,'金額': sum})
    people_bill_final = people_bill_final.rename(columns={"客戶廠商編號": "人數"})
    people_bill_final = people_bill_final.reset_index()
    
    #合併第一次、最後一次購買時間
    first_buy = people_bill.groupby("客戶廠商編號", as_index = False)['日期年加月'].min()
    first_buy.rename(columns = {'日期年加月':'第一次購買年加月'}, inplace = True)
    last_buy = people_bill.groupby("客戶廠商編號", as_index = False)['日期年加月'].max()
    last_buy.rename(columns = {'日期年加月':'最後一次購買年加月'}, inplace = True)
    people_bill_final =  people_bill_final.merge(first_buy[['客戶廠商編號','第一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    people_bill_final =  people_bill_final.merge(last_buy[['客戶廠商編號','最後一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    people_bill_final['月份新舊客戶'] = np.where((people_bill_final['日期年加月'] == people_bill_final['第一次購買年加月']), '新客戶', '舊客戶')
    product_bill_final = people_bill_final
    return product_bill_final

def makedf_with_product(product_bill_final):
    """人數(當月多次也只算1) 排掉客戶當月金額加總為負或是0
    最後會有 人數 金額總額 單據數"""
    final_list = []
    new_old_list = ['總','新客戶','舊客戶']
    for person in new_old_list:
        if person == '總':
            people_sum = product_bill_final.query("金額 > 0").groupby(['日期年加月','分類']).agg({'人數': sum})
            bill_sum = product_bill_final.groupby(['日期年加月','分類']).agg({'單據數': sum})
            money_sum = product_bill_final.groupby(['日期年加月','分類']).agg({'金額': sum})
            total_df = people_sum.merge(bill_sum,on=['日期年加月','分類'],how='inner')
            total_df = total_df.merge(money_sum,on=['日期年加月','分類'],how='inner')
            total_df = total_df.reset_index()
        else:
            newmoney_filter =  (product_bill_final.月份新舊客戶 == person)
            people_bill_type = product_bill_final.loc[newmoney_filter].reset_index(drop=True)
            people_sum = people_bill_type.query("金額 > 0").groupby(['日期年加月','分類']).agg({'人數': sum})
            bill_sum = people_bill_type.groupby(['日期年加月','分類']).agg({'單據數': sum})
            money_sum = people_bill_type.groupby(['日期年加月','分類']).agg({'金額': sum})
            total_df = people_sum.merge(bill_sum,on=['日期年加月','分類'],how='inner')
            total_df = total_df.merge(money_sum,on=['日期年加月','分類'],how='inner')
            total_df = total_df.reset_index()
        total_df['ASP客單'] = (total_df['金額']/total_df['單據數']).astype('int')
        total_df['ARPU人單'] = (total_df['金額']/total_df['人數']).astype('int')
        final_list.append(total_df)     
    
    return final_list[0],final_list[1],final_list[2]

def Transaction_without_product(Transaction_df):
    """人數(當月多次也只算1) 客戶當月金額加總>0"""
    # ### 客戶來的次數by年+月
    Transaction_df['會員分類'] = Transaction_df.apply(member_c.member_class,axis = 1)
    member_filter =  (Transaction_df.會員分類 != '非會員') # & (Transaction_df.訂單總金額 != 0)
    Transaction_df = Transaction_df.loc[member_filter].reset_index(drop=True)
    Transaction_df.rename(columns = {'客戶/廠商編號':'客戶廠商編號','合計':'金額'}, inplace = True)
    Transaction_df['日期'] = Transaction_df['日期'].astype('datetime64[ns]')
    Transaction_df['日期年加月'] = Transaction_df['日期'].dt.strftime('%Y-%m')
    #抓單據 by月份
    #people_bill = Transaction_df.groupby(['客戶廠商編號','日期年加月']).單據號碼.nunique()
    people_bill = Transaction_df.groupby(['客戶廠商編號','單據號碼','日期年加月']).agg({'單據號碼': pd.Series.nunique,'金額': sum})
    def change_neg(x):
        if x['金額'] == 0:
            return 0
        elif x['金額'] < 0:
            return -x['單據號碼']
        elif x['金額'] > 0:
            return x['單據號碼'] 
    people_bill['單據數'] = people_bill.apply(change_neg,axis = 1)
    people_bill.drop('單據號碼', inplace=True, axis=1)
    people_bill = people_bill.reset_index()
    people_bill_final = people_bill.groupby(['客戶廠商編號','日期年加月']).agg({'客戶廠商編號':pd.Series.nunique
                                                                     ,'單據數': sum,'金額': sum})
    people_bill_final = people_bill_final.rename(columns={"客戶廠商編號": "人數"})
    people_bill_final = people_bill_final.reset_index()
    # test_filter =  (Transaction_df.客戶廠商編號 == '0962098225') # & (Transaction_df.訂單總金額 != 0)
    # Transaction_df = Transaction_df.loc[test_filter].reset_index(drop=True)
    #合併第一次、最後一次購買時間
    first_buy = people_bill.groupby("客戶廠商編號", as_index = False)['日期年加月'].min()
    first_buy.rename(columns = {'日期年加月':'第一次購買年加月'}, inplace = True)
    last_buy = people_bill.groupby("客戶廠商編號", as_index = False)['日期年加月'].max()
    last_buy.rename(columns = {'日期年加月':'最後一次購買年加月'}, inplace = True)
    people_bill_final =  people_bill_final.merge(first_buy[['客戶廠商編號','第一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    people_bill_final =  people_bill_final.merge(last_buy[['客戶廠商編號','最後一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    people_bill_final['月份新舊客戶'] = np.where((people_bill_final['日期年加月'] == people_bill_final['第一次購買年加月']), '新客戶', '舊客戶')
    
    return people_bill_final

def makedf_without_product(people_bill_final):
    """最後會有 人數 金額總額 單據數"""
    final_list = []
    new_old_list = ['總','新客戶','舊客戶']
    for person in new_old_list:
        if person == '總':
            people_sum = people_bill_final.query("金額 > 0").groupby(['日期年加月']).agg({'人數': sum})
            bill_sum = people_bill_final.groupby(['日期年加月']).agg({'單據數': sum})
            money_sum = people_bill_final.groupby(['日期年加月']).agg({'金額': sum})
            total_df = people_sum.merge(bill_sum,on=['日期年加月'],how='inner')
            total_df = total_df.merge(money_sum,on=['日期年加月'],how='inner')
            total_df = total_df.reset_index()
        else:
            newmoney_filter =  (people_bill_final.月份新舊客戶 == person)
            people_bill_type = people_bill_final.loc[newmoney_filter].reset_index(drop=True)
            people_sum = people_bill_type.query("金額 > 0").groupby(['日期年加月']).agg({'人數': sum})
            bill_sum = people_bill_type.groupby(['日期年加月']).agg({'單據數': sum})
            money_sum = people_bill_type.groupby(['日期年加月']).agg({'金額': sum})
            total_df = people_sum.merge(bill_sum,on=['日期年加月'],how='inner')
            total_df = total_df.merge(money_sum,on=['日期年加月'],how='inner')
            total_df = total_df.reset_index()
        total_df['ASP客單'] = (total_df['金額']/total_df['單據數']).astype('int')
        total_df['ARPU人單'] = (total_df['金額']/total_df['人數']).astype('int')
        final_list.append(total_df)     
    return final_list[0],final_list[1],final_list[2]

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
        new_df.drop('分類', inplace=True, axis=1)
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

# Transaction_df = pd.read_csv("20150101-20230831_AA.csv",low_memory=False)
# product_df = pd.read_csv("產品分類.csv",low_memory=False).dropna()
#Transaction_df.to_excel('Transaction_df.xlsx',index = False)
