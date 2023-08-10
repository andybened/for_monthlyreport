# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 15:35:30 2023

@author: User
"""

import repurchase_function as rf
import streamlit as st
import io
import streamlit_ext as ste
import pandas as pd

def main():
    #buffer = io.BytesIO()
    st.set_page_config(
        #page_title="新舊客戶相關分析",
        page_icon="random",
        layout='wide',
        #initial_sidebar_state="collapsed",
    )
    product_df = pd.read_csv("產品分類.csv",low_memory=False).dropna()
    st.title('新客戶回購相關分析')
    
    # 上傳資料集
    with st.form("my_form"):
        with st.sidebar:
            uploaded_file = st.sidebar.file_uploader("請上傳您的檔案", type=["csv"]) #,accept_multiple_files=True
            year = st.sidebar.text_input('輸入年分', '2023')
            submitted = st.form_submit_button("Submit")
    if submitted:
        with st.spinner('Wait for it...'):
            @st.cache_data(show_spinner=False) ##不要顯示涵式名稱
            def read_df(uploaded_file):
                Transaction_dict = pd.read_csv(uploaded_file,low_memory= False)
                return Transaction_dict #,product_df
            # 抓資料
            Transaction_df = read_df(uploaded_file) #,product_df
            @st.cache_data(show_spinner=False) ##不要顯示涵式名稱
            def read_df2(Transaction_df):
                purchase_detail = rf.repurchase_df(Transaction_df)
                return purchase_detail
            purchase_detail = read_df2(Transaction_df)
            merge_df, sum_by_monthpeople = rf.get_new_first(purchase_detail,year)
            final_merge, merge_to_df2 = rf.newoldcustomer_data(purchase_detail,year,merge_df,sum_by_monthpeople)
            #merge_df, sum_by_monthpeople = rf.get_new_first(purchase_detail,year)
            #final_merge, merge_to_df2 = rf.newoldcustomer_data(purchase_detail,year,merge_df,sum_by_monthpeople)
            
            st.subheader("新客回購大表")
            st.dataframe(final_merge)
            st.subheader("新客回購人數占比總表")
            st.dataframe(merge_to_df2)        
                
            
if __name__ == '__main__':
    main()  