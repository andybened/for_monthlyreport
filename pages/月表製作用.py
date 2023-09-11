# -*- coding: utf-8 -*-
"""
Created on Fri Aug 18 16:13:34 2023

@author: User
"""
from  for_bi_function import nasld_df as nf
#from  for_bi_function import Cross_item as ci
from  for_bi_function import repurchase_v2 as repur
from  for_bi_function import trans_data_tonewdata as trans
import streamlit as st
#import io
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
    st.title('月報用數據')
    
    uploaded_file3 = st.sidebar.file_uploader("請上傳您的檔案", type=["csv"]) #,accept_multiple_files=True
    if uploaded_file3 is not None : #or st.session_state['btn_clicked']
        @st.cache_data(show_spinner=False) ##不要顯示涵式名稱
        def read_df(uploaded_file):
            Transaction_dict = pd.read_csv(uploaded_file,low_memory= False)
            return Transaction_dict #,product_df
        # 抓資料
        Transaction_df = read_df(uploaded_file3) #,product_df
    if uploaded_file3 is not None :
        with st.spinner('資料處理中...'):
            @st.cache_data(show_spinner=False) #by月份數據
            def read_df2(Transaction_df):
                product_bill_final = trans.Transaction_with_product(Transaction_df,product_df)
                people_bill_final = trans.Transaction_without_product(Transaction_df)
                df_final = trans.newold_forbi(product_bill_final)
                total_df,total_new_df,total_old_df = trans.makedf_without_product(people_bill_final)
                return product_bill_final,df_final,total_df,total_new_df,total_old_df
            product_bill_final,df_final,total_df,total_new_df,total_old_df = read_df2(Transaction_df) ###
            
            purchase_avgday_df ,sumbymonth_df = repur.repurchase_df(Transaction_df) ###
            cross_item_avgpro,cross_item_person = trans.cross_item(product_bill_final)###
            #cross_item_avgpro,cross_item_person = ci.Transaction_with_product(Transaction_df,product_df)###
            
            nalsd_pd,percentage_df,awake_person_pd = nf.repurchase_df(Transaction_df)
            sleep_customer = nf.sleep_new_customer(nalsd_pd)
            final_nes = nf.concat_to_newpd(sleep_customer,awake_person_pd) ###
            #圖表區
            st.subheader("新舊客戶相關數據")
            col1, col2,col2_1,col2_2 = st.columns(4)
            with col1:
               st.dataframe(df_final)
            with col2:   
               st.dataframe(total_df)
            with col2_1:   
               st.dataframe(total_new_df)
            with col2_2:   
               st.dataframe(total_old_df)
               
            st.subheader("回購相關數據")
            col3, col4 = st.columns(2)
            with col3:
               st.dataframe(purchase_avgday_df)
            with col4:   
               st.dataframe(sumbymonth_df)
            
            st.subheader("跨品商品")
            col5, col6 = st.columns(2)
            with col5:
                st.dataframe(cross_item_avgpro)
            with col6:    
                st.dataframe(cross_item_person)
            st.subheader("NES活性數據")   
            st.dataframe(final_nes.T)

if __name__ == '__main__':
    main()  