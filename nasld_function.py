# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 11:15:32 2023

@author: User
"""
import pandas as pd
import numpy as np
import setting as st

member_c = st.for_member()
def repurchase_df(Transaction_df):
    Transaction_df['會員分類'] = Transaction_df.apply(member_c.member_class,axis = 1)
    Transaction_df.rename(columns = {'客戶/廠商編號':'客戶廠商編號','合計':'金額'}, inplace = True)
    Transaction_df['日期'] = Transaction_df['日期'].astype('datetime64[ns]')
    Transaction_df['日期年加月'] = Transaction_df['日期'].dt.strftime('%Y-%m')
    Transaction_df['日期年'] = Transaction_df['日期'].dt.strftime('%Y')
    year_month = Transaction_df['日期年加月'].unique()
    year_month = year_month.tolist()
    year_month.sort()
    for_year = Transaction_df['日期年'].unique()
    for_year = for_year.tolist()
    for_year.sort()
    #ym = "2022-04"
    nalsd_list = []
    for yy in for_year:
       if int(yy) >= 2022:
           for ym in year_month: 
               if ym[0:4] == yy:
                   member_filter =  (Transaction_df.會員分類 != '非會員') & (Transaction_df.日期年加月 <= ym)
                   ym_choose_df = Transaction_df.loc[member_filter].reset_index(drop=True)
        
                   first_buy = ym_choose_df.groupby("客戶廠商編號", as_index = False)['日期'].min()
                   first_buy.rename(columns = {'日期':'第一次購買日'}, inplace = True)
                   last_buy = ym_choose_df.groupby("客戶廠商編號", as_index = False)['日期'].max()
                   last_buy.rename(columns = {'日期':'最後一次購買日'}, inplace = True)
                   first_last = first_buy.merge(last_buy,on=['客戶廠商編號'],how='inner')
                   first_last['第一次購買日期年加月'] = first_last['第一次購買日'].dt.strftime('%Y-%m')
                   
                   first_last["新客卡點"]  = ym
                   first_last["新客卡點"] = pd.to_datetime(first_last["新客卡點"], format='%Y-%m')
                   first_last["新客卡點年加月"] = first_last['新客卡點'].dt.strftime('%Y-%m')
                   first_last['月份新舊客戶'] = np.where((first_last['第一次購買日期年加月'] == first_last['新客卡點年加月']), '新客戶', '舊客戶')
                   
                   first_last["日期卡點"] = first_last["新客卡點"]  + pd.DateOffset(months=1) #pandas內日期相加
                   #first_last["日期卡點"] = str(ym[0:5]) + str(int(ym[5:7])+1) + "-01"
                   #first_last["日期卡點"] = pd.to_datetime(first_last["日期卡點"], format='%Y-%m-%d')
                   first_last['date_diff'] = first_last['日期卡點'] - first_last['最後一次購買日']
                   first_last['date_diff'] = first_last['date_diff'].dt.days
                   first_last['NASLD'] = first_last.apply(member_c.Repurchase_range,axis=1)
                   
                   first_last_group = first_last.groupby(['NASLD']).agg({'客戶廠商編號': len})
                   first_last_group.rename(columns={'客戶廠商編號': f'{ym}'},inplace = True)
                   first_last_group.loc['總計'] = first_last_group.sum(axis = 0) #最後插入總計 #[f'{ym}'] 必要再放入欄位
                   nalsd_list.append(first_last_group)
    
    nalsd_pd = nalsd_list[0]
    for i in range(1,len(nalsd_list)):
        nalsd_pd = nalsd_pd.merge(nalsd_list[i],on=['NASLD'],how='outer')
    nalsd_pd.fillna(0,inplace = True)    
    list_nasld_sort = ["N(新客)","A(活耀客)","S(沉睡)","L(鬆動)","D(封存客)","總計"]
    nalsd_pd = nalsd_pd.reindex(list_nasld_sort)
    #透過各產品總計 產生占比
    percentage_df = (nalsd_pd / nalsd_pd.loc["總計"])
    #percentage_df = percentage_df.applymap(format_percentage)
    percentage_df = percentage_df.applymap(lambda x: format(x,'.1%'))

    return nalsd_pd,percentage_df
# Transaction_df = pd.read_csv("2015-20230630_Transcationdata.csv",low_memory=False)
