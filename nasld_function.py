# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 11:15:32 2023

@author: User
"""
import pandas as pd
import numpy as np
import setting as st
from plotly.subplots import make_subplots
import plotly.graph_objs as go
import plotly.express as px
from datetime import datetime

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
    #yy = "2022"
    nalsd_list = []
    for_repurchase = {}
    for yy in for_year:
       if int(yy) >= 2021:
           for ym in year_month: 
               if ym[0:4] == yy:
                   member_filter =  (Transaction_df.會員分類 != '非會員') & (Transaction_df.日期年加月 <= ym)
                   ym_choose_df = Transaction_df.loc[member_filter].reset_index(drop=True)
                   
                   #新增判斷當月金額>0 start
                   purchase_times = ym_choose_df.groupby(['客戶廠商編號','日期年加月']).客戶廠商編號.nunique()
                   purchase_times = purchase_times.to_frame()
                   purchase_times = purchase_times.rename(columns={"客戶廠商編號": "人數"})
                   purchase_times = purchase_times.reset_index()
                   # ### 客戶帶來的總額與件數by年+月
                   purchase_sum = ym_choose_df.groupby(['客戶廠商編號','日期年加月']).agg({'金額': sum}) #'客戶代號':len
                   purchase_sum = purchase_sum.reset_index()
                   #### 合併總額數量與次數
                   purchase_detail = purchase_sum.merge(purchase_times,on=['客戶廠商編號','日期年加月'],how='inner')
                   money_filter =  (purchase_detail.金額 > 0)
                   purchase_detail = purchase_detail.loc[money_filter].reset_index(drop=True)
                   ym_choose_df2 = ym_choose_df.merge(purchase_detail[['客戶廠商編號','日期年加月','人數']],on=['客戶廠商編號','日期年加月'],how='right')
                   #test2 = ym_choose_df2.groupby(['客戶廠商編號','日期年加月']).agg({'金額': sum}) #'客戶代號':len
                   #新增判斷當月金額>0 end 
                   
                   first_buy = ym_choose_df2.groupby("客戶廠商編號", as_index = False)['日期'].min() #ym_choose_df
                   first_buy.rename(columns = {'日期':'第一次購買日'}, inplace = True)
                   last_buy = ym_choose_df2.groupby("客戶廠商編號", as_index = False)['日期'].max() #ym_choose_df
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
                   ###將封存客的客戶ID存起來
                   sleep_filter = (first_last["NASLD"] == "D(封存客)")
                   sleep_pd = first_last.loc[sleep_filter].reset_index(drop=True)
                   sleep_c = sleep_pd["客戶廠商編號"].to_list()
                   for_repurchase[f"{ym}"] = sleep_c
                   
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
    percentage_df = percentage_df.applymap(lambda x: format(x,'.1%'))
    
    selected_keys = [key for key, value in for_repurchase.items() if key >= "2021-12"]
    # 創建新的字典，僅包含key>=2021-12
    selected_dict = {key: for_repurchase[key] for key in selected_keys}
    #key = "2022-12"
    #member_awake = selected_dict["2022-12"]
    awake_person_pd = pd.DataFrame(index=["喚醒客"])
    for key,values in selected_dict.items():
        member_awake = values
        date_object = datetime.strptime(key, '%Y-%m').date()
        date_object = date_object + pd.DateOffset(months=1) #pandas內日期相加
        next_month = date_object.strftime("%Y-%m")
        repur_filter = (Transaction_df['客戶廠商編號'].isin(member_awake)) & (Transaction_df['日期年加月'] == next_month) #year_with_month[-1]
        repur_nextmonth = Transaction_df.loc[repur_filter].reset_index(drop=True)
        repur_cus = repur_nextmonth.groupby(['客戶廠商編號']).agg({'金額': sum})
        awake_person_pd[f"{next_month}"] = [len(repur_cus)]
    return nalsd_pd,percentage_df,awake_person_pd

#計算封存客跟新客
def sleep_new_customer(nalsd_pd):
    sleep_pd = nalsd_pd.iloc[:, 11:]
    column_list = sleep_pd.columns
    column_list = column_list.to_list()
    test_pd = pd.DataFrame()
    for i in range(1, len(column_list)):
        col_name = f'{column_list[i]}'
        test_pd[col_name] = sleep_pd.iloc[:, i] - sleep_pd.iloc[:, i-1]
    sleep_customer = test_pd.loc["D(封存客)":]  #test_pd.iloc[4]
    sleep_customer = sleep_customer.rename(index={'總計': '新客'})
    return sleep_customer

def concat_to_newpd(sleep_customer,awake_person_pd):
    nes_pd = pd.concat([sleep_customer,awake_person_pd])
    nes_pd.drop(nes_pd.columns[-1], axis=1, inplace=True)
    
    # 選擇特定的兩個行
    water_rows = ['喚醒客', '新客']
    selected_data = nes_pd.loc[water_rows]
    # 計算活水
    new_row = pd.DataFrame(selected_data.sum()).T
    new_row.index = ['活水客']
    final_pd = pd.concat([nes_pd, new_row])
    
    selected_rows = [ 'D(封存客)','活水客']
    selected_data2 = final_pd.loc[selected_rows]
    # 計算差異
    new_row2 = pd.DataFrame(selected_data2.diff().iloc[-1]).T
    new_row2.index = ['活水-封存']
    final_pd = pd.concat([final_pd, new_row2])
    return final_pd

def make_plot(nalsd_pd):
#nalsd_pd2 = nalsd_pd.drop(nalsd_pd.index[-1])
    nalsd_pd2 = nalsd_pd.reset_index()
    nalsd_pd2 = nalsd_pd2.melt(id_vars='NASLD',var_name='Date',
        value_name='value')
    fig_customer = px.line(nalsd_pd2, x="Date", y="value", color='NASLD',markers=True)
    fig_customer.update_yaxes(title_text="客戶數",tickformat=',.0f')
    
    percentage_df = (nalsd_pd / nalsd_pd.loc["總計"])
    nalsd_percent = percentage_df.drop(percentage_df.index[-1])
    nalsd_percent = nalsd_percent.reset_index()
    nalsd_percent2 = nalsd_percent.melt(id_vars='NASLD',var_name='Date',
        value_name='value')
    fig_percent = px.line(nalsd_percent2, x="Date", y="value", color='NASLD' ,markers=True)   
    fig_percent.update_yaxes(title_text="百分比",tickformat=',.1%')
    
    #fig_customer.update_xaxes(tickformat='%Y/%b')
    fig_customer.update_layout(title={'text': "NASLD數量(by月)",
    'y':0.95,
    'x':0.5,
    'xanchor': 'center',
    'yanchor': 'top',},
    title_font_family = "Times New Roman" ,
    title_font_color = "red",  
    title_font_size = 25,  
    width=1500, height=600) # width=2000,Times New Roman
    
    fig_percent.update_layout(title={'text': "NASLD占比(by月)",
    'y':0.95,
    'x':0.5,
    'xanchor': 'center',
    'yanchor': 'top',},
    title_font_family = "Times New Roman" ,
    title_font_color = "red",  
    title_font_size = 25,  
    width=1500, height=600) # width=2000,Times New Roman
    return fig_customer,fig_percent
