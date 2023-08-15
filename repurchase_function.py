# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 09:17:38 2023

@author: User
"""

import pandas as pd
import numpy as np
import setting as st

member_c = st.for_member()
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

    people_bill = Transaction_df.groupby(['客戶廠商編號','日期年加月']).agg({'單據號碼': pd.Series.nunique
                                                ,'金額': sum})
    people_bill = people_bill.reset_index()
    people_bill_fil =  (people_bill.金額 > 0)
    bill_detail = people_bill.loc[people_bill_fil].reset_index(drop=True)
    purchase_detail = purchase_detail.merge(bill_detail[['客戶廠商編號','日期年加月','單據號碼']]
                                      ,on=['客戶廠商編號','日期年加月'],how='inner')
    purchase_detail['日期年'] = purchase_detail['日期年加月'].apply(lambda x: str(x)[0:4])
    #### 合併後累加
    customer = purchase_detail.groupby(['客戶廠商編號'])
    purchase_detail['cumsum_times'] = customer['次數'].cumsum() #次數
    purchase_detail['cumsum_money'] = customer['金額'].cumsum() #總額
    def cumsum_times(x): 
        if x['cumsum_times'] == 1:
            return '1次'
        elif x['cumsum_times'] == 2:
            return '2次' 
        elif x['cumsum_times'] == 3:
            return '3次' 
        elif x['cumsum_times'] == 4:
            return '4次'
        elif x['cumsum_times'] >= 5:
            return '5次以上'
    purchase_detail['回購分類'] = purchase_detail.apply(cumsum_times,axis=1)
    purchase_detail['cumsum_bill'] = customer['單據號碼'].cumsum() #單據數
    purchase_detail['最後一次購買年加月整數'] = purchase_detail['最後一次購買年加月'].apply(lambda x: int(x.replace("-",'')))
    purchase_detail['第一次購買年'] = purchase_detail['第一次購買年加月'].apply(lambda x: str(x)[0:4])
    #purchase_detail['客戶數'] = 1
    
    purchase_detail2 =  purchase_detail2.merge(first_buy[['客戶廠商編號','第一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    purchase_detail2 =  purchase_detail2.merge(last_buy[['客戶廠商編號','最後一次購買年加月']]
    ,on=['客戶廠商編號'],how='inner')
    purchase_detail2['月份新舊客戶'] = np.where((purchase_detail2['日期年加月'] == purchase_detail2['第一次購買年加月']), '新客戶', '舊客戶')
    purchase_detail2['日期年'] = purchase_detail2['日期年加月'].apply(lambda x: str(x)[0:4])
    customer2 = purchase_detail2.groupby(['客戶廠商編號'])
    purchase_detail2['cumsum_times'] = customer2['次數'].cumsum() #次數
    purchase_detail2['cumsum_money'] = customer2['金額'].cumsum() #總額
    purchase_detail2['回購分類'] = purchase_detail2.apply(cumsum_times,axis=1)
    return purchase_detail ,purchase_detail2


def get_new_first(purchase_detail,year):
    first_filter =  (purchase_detail['月份新舊客戶'] == '新客戶') & (purchase_detail['日期年'] == year)
    purchase_detail = purchase_detail.loc[first_filter].reset_index(drop=True)
    year_month_list = purchase_detail['日期年加月'].unique()
    year_month_list.sort()
    sum_by_month = []
    sum_by_monthpeople = [] #各月份只抓人數
    for ym in year_month_list:
        newold_filter = (purchase_detail['日期年加月'] == ym)
        purchase_new_month = purchase_detail.loc[newold_filter].reset_index(drop=True)
        sumbymonth_df = purchase_new_month.groupby(['日期年加月']).agg({'客戶廠商編號': len,'金額':sum,'單據號碼':sum}) #當月總數    
        sumbymonth_df.insert(0, '回購分類', '1總')
        sumbymonth_df = sumbymonth_df.reset_index()
        sumbymonth_df.set_index('回購分類', inplace = True)
        sumbymonth_df.drop(['日期年加月'], axis=1, inplace = True)
        sumbymonth_df.rename(columns = {'客戶廠商編號':f'{ym}人數','金額':f'{ym}金額'
                             ,'單據號碼':f'{ym}單據數'}, inplace = True)
        sum_by_month.append(sumbymonth_df)
        sum_by_monthpeople.append(sumbymonth_df[f'{ym}人數'])
    merge_df = sum_by_month[0]
    for i in range(1,len(sum_by_month)):
        merge_df = merge_df.merge(sum_by_month[i],on=['回購分類'],how='inner')
        
    # sum_people_all = sum_by_monthpeople[0].to_frame()
    # for j in range(1,len(sum_by_monthpeople)):
    #     sum_people_all = pd.concat([sum_people_all,sum_by_monthpeople[j].to_frame()],axis= 1)
    return merge_df,sum_by_monthpeople

def newoldcustomer_data(purchase_detail,purchase_detail2,year,merge_df,sum_by_monthpeople):
    year_with_month = member_c.month_year(year)
    #sum_by_month2 = [] # 各月份新客df
    total_month = purchase_detail['日期年加月'].unique()
    even_numbers = [x for x in total_month if x[0:4] == year]
    even_numbers.sort()
    #ym = '2023-01'
    #ym2 = '2023-12'
    #將所有的新客戶資料抓出並逐月處理回購狀況 #982124861 來的次數與單據數不符
    sum_by_month_total = {} # 各月份、回購新客df
    purchase_object_cumsum_dict = {}
    for ym in year_with_month:
        sum_by_month = [] # 各月份、回購新客df
        purchase_object_cumsum_list = []
        first_filter =  (purchase_detail['月份新舊客戶'] == '新客戶') & (purchase_detail['日期年加月'] == ym) #"2023-01" 
        purchase_new_month = purchase_detail.loc[first_filter].reset_index(drop=True) 
        member = purchase_new_month['客戶廠商編號'].unique()
        if purchase_new_month.empty == False:      
            for ym2 in even_numbers:
                if ym <= ym2: 
                    member_filter = (purchase_detail['客戶廠商編號'].isin(member)) & (purchase_detail['日期年加月'] <= ym2) #year_with_month[-1]
                    purchase_object = purchase_detail.loc[member_filter].reset_index(drop=True) #loc[~filter2] 非isin
                    member_filter2 = (purchase_detail2['客戶廠商編號'].isin(member)) & (purchase_detail2['日期年加月'] <= ym2) #year_with_month[-1]
                    purchase_money = purchase_detail2.loc[member_filter2].reset_index(drop=True) #loc[~filter2] 非isin
                    
                    purchase_object2 = purchase_object.query("cumsum_times != 1").groupby(['客戶廠商編號']).agg({'回購分類':max
                                                        ,'cumsum_money':max,'cumsum_bill':max})
                    
                    purchase_money2 = purchase_money.query("cumsum_times != 1").groupby(['客戶廠商編號']).agg({'回購分類':max
                                                        ,'cumsum_money':max})
                    
                    purchase_object2.reset_index(inplace = True)
                    purchase_object2["月份"] = ym2 #"2022-01"
                    purchase_object3 = purchase_object2.groupby(['月份','回購分類']).agg({'客戶廠商編號':len,'cumsum_bill':sum})
                    
                    purchase_money2.reset_index(inplace = True)
                    purchase_money2["月份"] = ym2 #"2022-01"
                    purchase_money3 = purchase_money2.groupby(['月份','回購分類']).agg({'cumsum_money':sum})
                    purchase_object3 = purchase_object3.merge(purchase_money3,on=['月份','回購分類'],how='inner')
                    
                    purchase_object3.rename(columns = {'客戶廠商編號':f'{ym}人數','cumsum_money':f'{ym}金額'
                                         ,'cumsum_bill':f'{ym}單據數'}, inplace = True)
                    sum_by_month.append(purchase_object3)
                    sum_by_month_total[f"{ym}"] = sum_by_month
                    purchase_object_cumsum = purchase_object2.groupby(['月份']).agg({'客戶廠商編號':len,'cumsum_money':sum,'cumsum_bill':sum})
                    purchase_object_cumsum.rename(columns = {'客戶廠商編號':f'{ym}人數','cumsum_money':f'{ym}金額'
                                         ,'cumsum_bill':f'{ym}單據數'}, inplace = True)
                    purchase_object_cumsum_list.append(purchase_object_cumsum[f'{ym}人數'])
                    purchase_object_cumsum_dict[f"{ym}"] = purchase_object_cumsum_list
        else:
            break   
        
    #key = '2023-01'
    #values = sum_by_month_total[key]
    #將dict的各個key的value合併
    total_pd_list = [] #看各個重構次數人數
    mm_merge_list = [] #看重構總人數
    for key,values in  sum_by_month_total.items():
        pd_merge = sum_by_month_total[key][0]
        mm_merge = purchase_object_cumsum_dict[key][0]
        for j in range(1,len(values)):
            pd_merge = pd.concat([pd_merge,sum_by_month_total[key][j]])
            mm_merge = pd.concat([mm_merge,purchase_object_cumsum_dict[key][j]])
        total_pd_list.append(pd_merge)   
        mm_merge_list.append(mm_merge)
    
    #合併成每月大表    
    month_merge_df = total_pd_list[0] 
    for i in range(1,len(total_pd_list)): ##組合起來
        month_merge_df = month_merge_df.merge(total_pd_list[i],on=['月份','回購分類'],how='outer')
    final_merge = pd.concat([month_merge_df.iloc[:0], merge_df, month_merge_df.iloc[0:]]) #,ignore_index=True    
    final_merge.fillna(0,inplace = True)  
    #各月份總計與後續回購狀況之數量與百分比
    merge_total_list = []
    sum_merge_df2 = mm_merge_list[0].to_frame()
    c_name = sum_merge_df2.columns[0]
    sum_people_df2 = sum_by_monthpeople[0].to_frame()
    merge_total = pd.concat([sum_merge_df2.iloc[:0], sum_people_df2, sum_merge_df2.iloc[0:]]) #,ignore_index=True
    per_list = []
    for j in range(len(merge_total)):
        percent_value = merge_total[f'{c_name}'][j]/merge_total[f'{c_name}'][0]
        per_list.append(percent_value)
    merge_total.insert(1, f'{c_name}占比', per_list) #指定要插入的索引位置
    merge_total[f'{c_name}占比'] = merge_total[f'{c_name}占比'].apply(lambda x: format(x,'.0%')) 
    merge_total_list.append(merge_total)
    
    for k in range(1,len(mm_merge_list)):
        sum_merge_df2 = mm_merge_list[k].to_frame()
        c_name = sum_merge_df2.columns[0]
        sum_people_df2 = sum_by_monthpeople[k].to_frame()
        merge_total = pd.concat([sum_merge_df2.iloc[:0], sum_people_df2, sum_merge_df2.iloc[0:]]) #,ignore_index=True
        per_list = []
        for j in range(len(merge_total)):
            percent_value = merge_total[f'{c_name}'][j]/merge_total[f'{c_name}'][0]
            per_list.append(percent_value)
        merge_total.insert(1, f'{c_name}占比', per_list) #指定要插入的索引位置
        merge_total[f'{c_name}占比'] = merge_total[f'{c_name}占比'].apply(lambda x: format(x,'.0%')) 
        merge_total_list.append(merge_total)
    
    aa_df = merge_total_list[0]   
    merge_to_df2 = aa_df
    for x in range(1,len(merge_total_list)):
        merge_to_df2 = pd.concat([merge_to_df2,merge_total_list[x]], axis= 1)
    merge_to_df2.fillna(0,inplace = True)   
    
    return final_merge,merge_to_df2
    
# year = '2022'
# member_c = st.for_member()

# Transaction_df = pd.read_csv("2015-20230630_Transcationdata.csv",low_memory=False)
# product_df = pd.read_csv("產品分類.csv",low_memory=False).dropna()
# purchase_detail = repurchase_df(Transaction_df)
# merge_df, sum_by_monthpeople = get_new_first(purchase_detail,year)
# final_merge, merge_to_df2 = newoldcustomer_data(purchase_detail,year,merge_df,sum_by_monthpeople)

