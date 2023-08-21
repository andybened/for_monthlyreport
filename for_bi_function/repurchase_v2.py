# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 09:17:38 2023

@author: User
"""

import pandas as pd
import numpy as np
import setting as st

def repurchase_df(Transaction_df):
    Transaction_df['會員分類'] = Transaction_df.apply(member_c.member_class,axis = 1)
    member_filter =  (Transaction_df.會員分類 != '非會員')
    Transaction_df = Transaction_df.loc[member_filter].reset_index(drop=True)
    Transaction_df.rename(columns = {'客戶/廠商編號':'客戶廠商編號','合計':'金額'}, inplace = True)
    Transaction_df['日期'] = Transaction_df['日期'].astype('datetime64[ns]')
    Transaction_df['日期年加月'] = Transaction_df['日期'].dt.strftime('%Y-%m')
    #抓人次 by月份   
    purchase_times = Transaction_df.groupby(['客戶廠商編號','日期']).客戶廠商編號.nunique()
    purchase_times = purchase_times.to_frame()
    purchase_times = purchase_times.rename(columns={"客戶廠商編號": "次數"})
    purchase_times = purchase_times.reset_index()
    purchase_times['日期年加月'] = purchase_times['日期'].apply(lambda x: str(x)[0:7])
    purchase_times['日期年'] = purchase_times['日期年加月'].apply(lambda x: str(x)[0:4])
    purchase_times_final = purchase_times.groupby(['客戶廠商編號','日期年加月']).agg({'次數': sum}) #'客戶代號':len
    purchase_times_final = purchase_times_final.reset_index()
    # ### 客戶帶來的總額與件數by年+月
    purchase_sum = Transaction_df.groupby(['客戶廠商編號','日期年加月']).agg({'金額': sum}) #'客戶代號':len
    purchase_sum = purchase_sum.reset_index()
    #### 合併總額數量與次數
    purchase_detail = purchase_sum.merge(purchase_times_final,on=['客戶廠商編號','日期年加月'],how='inner')
    purchase_detail2 = purchase_detail
    money_filter =  (purchase_detail.金額 > 0)
    purchase_detail = purchase_detail.loc[money_filter].reset_index(drop=True)

    def cumsum_times(x): 
        if x['次數'] == 1:
            return '1次'
        elif x['次數'] == 2:
            return '2次' 
        elif x['次數'] == 3:
            return '3次' 
        elif x['次數'] == 4:
            return '4次'
        elif x['次數'] >= 5:
            return '5次以上'
    purchase_detail['日期年'] = purchase_detail['日期年加月'].apply(lambda x: str(x)[0:4])
    purchase_detail = purchase_detail.groupby(['客戶廠商編號','日期年']).agg({'次數': sum}) #'客戶代號':len
    purchase_detail = purchase_detail.reset_index()
    purchase_detail['回購分類'] = purchase_detail.apply(cumsum_times,axis=1)
    
    purchase_avgday = purchase_times.groupby(['客戶廠商編號','日期年'])['日期'].apply(lambda x: x.diff().mean().days)
    purchase_avgday = purchase_avgday.reset_index()
    purchase_avgday.fillna(0,inplace = True)
    day_filter =  (purchase_avgday.日期 != 0)
    purchase_avgday = purchase_avgday.loc[day_filter].reset_index(drop=True)
    ####計算平均時間
    #purchase_avgday_df = purchase_avgday.groupby(['日期年']).agg({'客戶廠商編號': len})
    purchase_avgday_df = purchase_avgday.groupby('日期年').agg(avg_days=('日期', 'mean'),
    customer_count=('客戶廠商編號', len))
    purchase_avgday_df["avg_days"] = purchase_avgday_df["avg_days"].apply(lambda x: format(x,'.1f'))
    ####計算當年買家一次購
    sumbymonth_df = purchase_detail.groupby(['日期年','回購分類']).agg({'客戶廠商編號': len})  
    sumbymonth_df = sumbymonth_df.reset_index()
    return purchase_avgday_df ,sumbymonth_df

member_c = st.for_member()
# Transaction_df = pd.read_csv("2015~20230731_AA2.csv",low_memory=False)
# product_df = pd.read_csv("產品分類.csv",low_memory=False).dropna()
# purchase_avgday_df ,sumbymonth_df = repurchase_df(Transaction_df)


