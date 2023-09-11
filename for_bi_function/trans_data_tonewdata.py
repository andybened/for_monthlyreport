# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 10:34:30 2023

@author: User
"""

import pandas as pd
import numpy as np
import setting as st    
from collections import Counter
member_c = st.for_member()   
def Transaction_with_product(Transaction_df,product_df):
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
    people_bill_final['日期年'] = people_bill_final['日期年加月'].apply(lambda x: x[0:4])
    product_bill_final = people_bill_final
    return product_bill_final

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

def newold_forbi(product_bill_final):
    people_sum = product_bill_final.query("金額 > 0").groupby(['日期年加月','分類','月份新舊客戶']).agg({'人數': sum})
    bill_sum = product_bill_final.groupby(['日期年加月','分類','月份新舊客戶']).agg({'單據數': sum})
    money_sum = product_bill_final.groupby(['日期年加月','分類','月份新舊客戶']).agg({'金額': sum})
    total_df = people_sum.merge(bill_sum,on=['日期年加月','分類','月份新舊客戶'],how='inner')
    total_df = total_df.merge(money_sum,on=['日期年加月','分類','月份新舊客戶'],how='inner')
    total_df = total_df.reset_index()
    total_df['ASP客單'] = (total_df['金額']/total_df['單據數']).astype('int')
    total_df['ARPU人單'] = (total_df['金額']/total_df['人數']).astype('int')

    
    # df_product = purchase_product_detail.groupby(['日期年加月','分類','月份新舊客戶']).agg(
    #     {'人數':len,'單據數':sum}).reset_index()
    # df_product2 = bill_product_detail3.groupby(['日期年加月','分類','月份新舊客戶']).agg(
    #     {'金額':sum}).reset_index()
    # df_final = df_product.merge(df_product2,on=['日期年加月','分類','月份新舊客戶'],how='inner')
    
    # df_noproduct = purchase_detail.groupby(['日期年加月','月份新舊客戶']).agg(
    #     {'人數':len,'單據數':sum}).reset_index()
    # df_noproduct2 = purchase_detail2.groupby(['日期年加月','月份新舊客戶']).agg(
    #     {'金額':sum}).reset_index()
    # df_final2 = df_noproduct.merge(df_noproduct2,on=['日期年加月','月份新舊客戶'],how='inner')
    return total_df #,df_final2

def cross_item(purchase_product_detail):
    cross_item_byperson2 = purchase_product_detail.groupby(['客戶廠商編號','日期年']).apply(lambda x:'-'.join(np.unique(x['分類']))).reset_index()
    cross_item_byperson2.rename(columns={0: "購買品項"}, inplace = True)
    cross_item_byperson2["購買清單"] = cross_item_byperson2["購買品項"].apply(lambda x: len(x.split("-")))
    def good_mood(df,value): #是否購買品項 
        if df["購買品項"].find(value) != -1: 
            return "Y" #有購買回傳1
        else:
            return "N" 
    for index,value in enumerate(member_c.product): 
        cross_item_byperson2[f"{value}"] = cross_item_byperson2.apply(good_mood, args=(value,),axis = 1) #args可以給function參數

    cross_item_avgpro = cross_item_byperson2.groupby('日期年').agg(avg_product=('購買清單', 'mean'))
    cross_item_avgpro["avg_product"] = cross_item_avgpro["avg_product"].apply(lambda x: format(x,'.1f'))
    
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
    return cross_item_avgpro,cross_item_person

    

# Transaction_df = pd.read_csv("2015~20230731_AA2.csv",low_memory=False)
# product_df = pd.read_csv("產品分類.csv",low_memory=False).dropna()
#purchase_product_detail,bill_product_detail3 = Transaction_with_product(Transaction_df,product_df)
#purchase_detail,purchase_detail2 = Transaction_without_product(Transaction_df)
# df_final,df_final2 = newold_forbi(purchase_product_detail,bill_product_detail3,  purchase_detail,purchase_detail2)

# Transaction_df.to_excel('Transaction_df.xlsx',index = False)
# purchase_detail.to_excel('purchase_detail.xlsx',index = False)

# with pd.ExcelWriter('output.xlsx') as writer:  
#     purchase_money.to_excel(writer, sheet_name='purchase_money')
#     purchase_object.to_excel(writer, sheet_name='purchase_object')