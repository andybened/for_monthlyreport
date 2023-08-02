# -*- coding: utf-8 -*-
"""
Created on Mon Jul 31 17:31:24 2023

@author: User
"""

# 計算規則
# group by 新舊客戶
# 線下 : 區域名稱 = (現場會員+電話會員) 、 類別名稱 = 會員 、 會員分類 != 非會員
# 廣告 : 區域名稱 = 非(現場會員+電話會員)  、 類別名稱 = 會員 、 會員分類 != 非會員
# KOL : 類別名稱 = 快樂益生 、 會員分類 != 非會員
import pandas as pd
import numpy as np
import setting as st
member_c = st.for_member()
def sum_purchase(Transaction_df):
    """
    # 計算規則 group by 新舊客戶
    # 線下 : 區域名稱 = (現場會員+電話會員) 、 類別名稱 = 會員 、 會員分類 != 非會員
    # 廣告 : 區域名稱 = 非(現場會員+電話會員)  、 類別名稱 = 會員 、 會員分類 != 非會員
    # KOL : 類別名稱 = 快樂益生 、 會員分類 != 非會員
    """
    # ### 客戶來的次數by年+月 
    Transaction_df['會員分類'] = Transaction_df.apply(member_c.member_class,axis = 1)
    member_filter =  (Transaction_df.會員分類 != '非會員')
    Transaction_df = Transaction_df.loc[member_filter].reset_index(drop=True)
    Transaction_df.rename(columns = {'客戶/廠商編號':'客戶廠商編號','合計':'金額'}, inplace = True)
    Transaction_df['日期'] = Transaction_df['日期'].astype('datetime64[ns]')
    Transaction_df['日期年加月'] = Transaction_df['日期'].dt.strftime('%Y-%m')
    
    #filt = (purchase_detail['客戶廠商編號'] == '915870760')
    #bbb = purchase_detail.loc[filt]
    #tr_df = Transaction_df[['客戶廠商編號','類別名稱','來源單號','日期年加月']].drop_duplicates()
    #tr_df2 = Transaction_df[['客戶廠商編號','日期年加月']].drop_duplicates()
    #抓人數 by月份
    purchase_times = Transaction_df.groupby(['客戶廠商編號','日期年加月','區域名稱','類別名稱']).客戶廠商編號.nunique()
    purchase_times = purchase_times.to_frame()
    purchase_times = purchase_times.rename(columns={"客戶廠商編號": "人數"})
    purchase_times = purchase_times.reset_index()
    # ### 客戶帶來的總額與件數by年+月
    purchase_sum = Transaction_df.groupby(['客戶廠商編號','日期年加月','區域名稱','類別名稱']).agg({'金額': sum}) #'客戶代號':len
    purchase_sum = purchase_sum.reset_index()
    #### 合併總額數量與次數
    purchase_detail = purchase_sum.merge(purchase_times,on=['客戶廠商編號','日期年加月','區域名稱','類別名稱'],how='inner')
    #篩選金額>0
    money_filter =  (purchase_detail.金額 > 0)
    purchase_detail = purchase_detail.loc[money_filter].reset_index(drop=True)
    
    #合併第一次、最後一次購買時間
    first_buy = Transaction_df.groupby("客戶廠商編號", as_index = False)['日期年加月'].min()
    first_buy.rename(columns = {'日期年加月':'第一次購買年加月'}, inplace = True)
    last_buy = Transaction_df.groupby("客戶廠商編號", as_index = False)['日期年加月'].max()
    last_buy.rename(columns = {'日期年加月':'最後一次購買年加月'}, inplace = True)
    purchase_detail =  purchase_detail.merge(first_buy[['客戶廠商編號','第一次購買年加月']]
    ,on=['客戶廠商編號'],how='left')
    purchase_detail =  purchase_detail.merge(last_buy[['客戶廠商編號','最後一次購買年加月']]
    ,on=['客戶廠商編號'],how='left')
    purchase_detail['月份新舊客戶'] = np.where((purchase_detail['日期年加月'] == purchase_detail['第一次購買年加月']), '新客戶', '舊客戶')
    purchase_detail = purchase_detail[['客戶廠商編號','日期年加月','月份新舊客戶','區域名稱','類別名稱','人數']]
    return purchase_detail

def groupby_newold(purchase_detail,year_date):
    #線下#根據條件篩選
    #offline_df = purchase_detail.query('區域名稱 =="現場會員" | 區域名稱 =="電話會員" & 類別名稱=="會員" ').groupby(["日期年加月",'月份新舊客戶'])["人數"].sum().reset_index()
    offline_df = purchase_detail.query('區域名稱 in ("現場會員","電話會員") & 類別名稱=="會員" ').groupby(["日期年加月",'月份新舊客戶'])["人數"].sum().reset_index()
    #offline_df2 = purchase_detail.query('來源單號 == "非Shopline訂單" & 類別名稱=="會員" ').groupby(["日期年加月",'月份新舊客戶'])["客戶廠商編號"].nunique().reset_index()
    #廣告 in ('Spark','PySpark')
    ad_df = purchase_detail.query('區域名稱 not in ("現場會員","電話會員") & 類別名稱=="會員" ').groupby(["日期年加月",'月份新舊客戶'])["人數"].sum().reset_index()
    #KOL
    kol_df = purchase_detail.query('類別名稱 == "快樂益生" ').groupby(["日期年加月",'月份新舊客戶'])["人數"].sum().reset_index()
    
    new_final_df =  offline_df.merge(ad_df,on=['日期年加月','月份新舊客戶'],how='left')
    new_final_df = new_final_df.merge(kol_df,on=['日期年加月','月份新舊客戶'],how='left')
    new_final_df.rename(columns = {'人數_x':'線下','人數_y':'廣告','人數':'KOL'}, inplace = True)
    new_final_df.fillna(value=0, inplace=True)
    new_final_df['會員總數'] = new_final_df['線下'] + new_final_df['廣告'] + new_final_df['KOL']
    new_filter =  (new_final_df.月份新舊客戶 == '新客戶') & (new_final_df['日期年加月'].apply(lambda x: str(x)[0:4]) == year_date)
    new_df = new_final_df.loc[new_filter].reset_index(drop=True)
    new_df.drop('月份新舊客戶', inplace=True, axis=1)
    old_filter =  (new_final_df.月份新舊客戶 == '舊客戶') & (new_final_df['日期年加月'].apply(lambda x: str(x)[0:4]) == year_date)
    old_df = new_final_df.loc[old_filter].reset_index(drop=True)
    old_df.drop('月份新舊客戶', inplace=True, axis=1)
    return new_df,old_df