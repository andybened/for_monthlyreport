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
                        ,"好益思","激耐益","套組","奇毛子","銀養奇毛子","定期購")
    def member_class(self,df): #區分會員組合
        if df["區域名稱"] in self.normal_member:
            return "一般會員"
        elif df["區域名稱"] in self.platinum_member:
            return "白金會員"
        elif df["區域名稱"] in self.VIP_member:   
            return "尊爵會員"
        else:
            return "非會員"