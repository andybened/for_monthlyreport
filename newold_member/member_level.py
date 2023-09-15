# -*- coding: utf-8 -*-
"""
Created on Mon Aug 28 16:24:18 2023

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
    Transaction_df['日期年加月'] = Transaction_df['日期'].dt.strftime('%Y%m')
    year_filter =  (Transaction_df.日期年加月 >= '202101') #& (Transaction_df.訂單總金額 > 0) #& (Transaction_df.合計 != 0)
    Transaction_df = Transaction_df.loc[year_filter].reset_index(drop=True)

    Transaction_df = Transaction_df.merge(product_df[['產品編號','分類']],on=['產品編號'],how='left')
    Transaction_df = Transaction_df[Transaction_df['分類'].isin(member_c.product)]
    people_bill = Transaction_df.groupby(['客戶廠商編號','單據號碼','會員分類','分類','日期年加月']).agg({'單據號碼': pd.Series.nunique,'金額': sum})
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
    people_bill_final = people_bill.groupby(['客戶廠商編號','日期年加月','會員分類','分類']).agg({'客戶廠商編號':pd.Series.nunique
                                                                     ,'單據數': sum,'金額': sum})
    people_bill_final = people_bill_final.rename(columns={"客戶廠商編號": "人數"})
    product_bill_final = people_bill_final.reset_index()

    return product_bill_final

def makedf_with_product(product_bill_final): #要用另一個檔案
    """合併人數、訂單數、金額"""
    product_bill_final['日期年'] = product_bill_final['日期年加月'].apply(lambda x: x[0:4])
    max_time = product_bill_final['日期年加月'].max()
    final_list = {}
    #new_old_list = ['總','一般會員','白金會員','尊爵會員']
    for product in member_c.product:
            # people_sum = product_bill_final.query("金額 > 0").groupby(['日期年加月','分類']).agg({'人數': sum})
            # bill_sum = product_bill_final.groupby(['日期年加月','分類']).agg({'單據數': sum})
            # money_sum = product_bill_final.groupby(['日期年加月','分類']).agg({'金額': sum})
            # total_df = people_sum.merge(bill_sum,on=['日期年加月','分類'],how='inner')
            # total_df = total_df.merge(money_sum,on=['日期年加月','分類'],how='inner')
            # total_df = total_df.reset_index()
        newmoney_filter =  (product_bill_final.分類 == product)
        people_bill_type = product_bill_final.loc[newmoney_filter].reset_index(drop=True)
        people_sum = people_bill_type.query("金額 > 0").groupby(['日期年','會員分類']).agg({'客戶廠商編號': pd.Series.nunique})
        #people_sum = people_bill_type.groupby(['日期年','會員分類']).agg({'客戶廠商編號': pd.Series.nunique})
        bill_sum = people_bill_type.groupby(['日期年','會員分類']).agg({'單據數': sum})
        money_sum = people_bill_type.groupby(['日期年','會員分類']).agg({'金額': sum})
        total_df = people_sum.merge(bill_sum,on=['日期年','會員分類'],how='inner')
        total_df = total_df.merge(money_sum,on=['日期年','會員分類'],how='inner')
        total_df = total_df.reset_index()
        total_df = total_df.rename(columns={"客戶廠商編號": "人數"})
        total_df['ASP客單'] = (total_df['金額']/total_df['單據數']).astype('int')
        total_df['ARPU人單'] = (total_df['金額']/total_df['人數']).astype('int')
        total_df.iloc[3:, :1] = max_time[0:4] + '/01~' + max_time[4:]
        final_list[f'{product}'] = total_df    
    
    return final_list

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
    people_bill = Transaction_df.groupby(['客戶廠商編號','單據號碼','會員分類','日期年加月']).agg({'單據號碼': pd.Series.nunique,'金額': sum})
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
    people_bill_final = people_bill.groupby(['客戶廠商編號','會員分類','日期年加月']).agg({'客戶廠商編號':pd.Series.nunique
                                                                     ,'單據數': sum,'金額': sum})
    people_bill_final = people_bill_final.rename(columns={"客戶廠商編號": "人數"})
    people_bill_final = people_bill_final.reset_index()

    return people_bill_final

def makedf_without_product(people_bill_final):
    """最後會有 人數 金額總額 單據數"""
    final_list = []
    new_old_list = ['總','一般會員','白金會員','尊爵會員']
    for person in new_old_list:
        if person == '總':
            people_sum = people_bill_final.query("金額 > 0").groupby(['日期年加月']).agg({'人數': sum})
            bill_sum = people_bill_final.groupby(['日期年加月']).agg({'單據數': sum})
            money_sum = people_bill_final.groupby(['日期年加月']).agg({'金額': sum})
            total_df = people_sum.merge(bill_sum,on=['日期年加月'],how='inner')
            total_df = total_df.merge(money_sum,on=['日期年加月'],how='inner')
            total_df = total_df.reset_index()
        else:
            newmoney_filter =  (people_bill_final.會員分類 == person)
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
    return final_list[1],final_list[2],final_list[3]

def repurchase_nowyear(people_bill_final): #只能先看2022以後是否前年有購買(忠誠客)
    people_bill_final['日期年'] = people_bill_final['日期年加月'].apply(lambda x: x[0:4])
    # people_bill_final['2021購買'] = np.where((people_bill_final['日期年'] == '2021'), 'Y', 'N')
    # people_bill_final['2022購買'] = np.where((people_bill_final['日期年'] == '2022'), 'Y', 'N')
    # people_bill_final['2023購買'] = np.where((people_bill_final['日期年'] == '2023'), 'Y', 'N')
    
    # 使用groupby按客户ID分组并应用筛选条件
    year_list = people_bill_final['日期年'].unique().tolist()
    year_list.sort()
    result_list = []
    member_final_pd = {} #忠誠客戶
    for i,value in enumerate(year_list):
        if i > 0:
            pre_value = str(int(value)-1)
            result_value = people_bill_final.groupby('客戶廠商編號').filter(lambda x: 
            (x['日期年'] == pre_value).any() and (x['日期年'] == value).any())
            filterbyyear =  (result_value.日期年 == value)
            result_pd = result_value.loc[filterbyyear].reset_index(drop=True)
            result_list.append(result_pd)
        
            people_sum = result_pd.query("金額 > 0").groupby(['日期年加月']).agg({'客戶廠商編號': pd.Series.nunique})
            people_sum = people_sum.rename(columns={"客戶廠商編號": "人數"})
            bill_sum = result_pd.groupby(['日期年加月']).agg({'單據數': sum})
            money_sum = result_pd.groupby(['日期年加月']).agg({'金額': sum})
            total_df = people_sum.merge(bill_sum,on=['日期年加月'],how='inner')
            total_df = total_df.merge(money_sum,on=['日期年加月'],how='inner')
            total_df = total_df.reset_index()
            total_df['ASP客單'] = (total_df['金額']/total_df['單據數']).astype('int')
            total_df['ARPU人單'] = (total_df['金額']/total_df['人數']).astype('int')
            member_final_pd[f'{value}'] = total_df
    
    return member_final_pd

# Transaction_df = pd.read_csv("2022_202308_AA.csv",low_memory=False)
# Transaction_df = pd.read_csv("202101-202308每月交易資料.csv",low_memory=False)
# product_df = pd.read_csv("產品分類.csv",low_memory=False).dropna()
# #member_level_df = pd.read_csv("會籍專用.csv",low_memory=False).dropna()
# product_bill_final = Transaction_with_product(Transaction_df,product_df)
# final_list = makedf_with_product(product_bill_final)
# people_bill_final = Transaction_without_product(Transaction_df)
# normal_df,platinum_df,VIP_df= makedf_without_product(people_bill_final)
# member_final_pd = repurchase_nowyear(people_bill_final)

