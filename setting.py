# -*- coding: utf-8 -*-
"""
Created on Fri Jul 28 15:05:05 2023

@author: User
"""

class for_member:
    def __init__(self): #各個會員組合細項
        self.normal_member = ('一般會員','快樂會員','國外會員','寶力健康會員'
                        ,'現場會員','惠澤之友','惠澤高階會員','港澳會員'
                        ,'電話會員','網路會員','癌症會員','官網-會員') #"一般會員"
        self.platinum_member = ("白金會員","官網-白金") # "白金會員"
        self.VIP_member = ("尊爵","官網-尊爵") #"尊爵會員"
        self.product = ("好欣情","益菌寶","好益活","淨美莓","益菌優","益伏敏"
                        ,"好益思","激耐益","套組","快樂奇毛子","銀養奇毛子","定期購")
        self.month_list = ['01','02','03','04','05','06','07','08','09','10','11','12']
    def member_class(self,df): #區分會員組合
        if df["區域名稱"] in self.normal_member:
            return "一般會員"
        elif df["區域名稱"] in self.platinum_member:
            return "白金會員"
        elif df["區域名稱"] in self.VIP_member:   
            return "尊爵會員"
        else:
            return "非會員"
    def month_year(self,year): #年月搭配
        year_with_month = []
        for i in self.month_list:
            new_map = year + "-" + i
            year_with_month.append(new_map)
        return year_with_month
    def Repurchase_range(self,x): 
        if x['月份新舊客戶'] == "新客戶":
            return 'N(新客)'
        elif x['date_diff'] <= 60:
            return 'A(活耀客)' 
        elif x['date_diff'] <= 120:
            return 'S(沉睡)' 
        elif x['date_diff'] <= 160:
            return 'L(鬆動)'
        elif x['date_diff'] > 160:
            return 'D(封存客)'
