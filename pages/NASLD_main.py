# -*- coding: utf-8 -*-
"""
Created on Fri Aug 11 16:11:18 2023

@author: User
"""


import nasld_function as nf
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
    st.title('NASLD分析/Nes活性指標')
    
    uploaded_file3 = st.sidebar.file_uploader("請上傳您的檔案", type=["csv"]) #,accept_multiple_files=True
    if uploaded_file3 is not None : #or st.session_state['btn_clicked']
        @st.cache_data(show_spinner=False) ##不要顯示涵式名稱
        def read_df(uploaded_file):
            Transaction_dict = pd.read_csv(uploaded_file,low_memory= False)
            return Transaction_dict #,product_df
        # 抓資料
        Transaction_df = read_df(uploaded_file3) #,product_df
    if uploaded_file3 is not None :
        with st.spinner('Wait for it...'):
            @st.cache_data(show_spinner=False) #by月份數據
            def read_df2(Transaction_df):
                nalsd_pd,percentage_df,awake_person_pd = nf.repurchase_df(Transaction_df)
                return nalsd_pd,percentage_df,awake_person_pd
            nalsd_pd,percentage_df,awake_person_pd = read_df2(Transaction_df)
            sleep_customer = nf.sleep_new_customer(nalsd_pd)
            final_nes = nf.concat_to_newpd(sleep_customer,awake_person_pd)
            
            #圖表區
            fig_customer,fig_percent = nf.make_plot(nalsd_pd)
            
        tab1, tab2 = st.tabs(["🗃數據", "📈圖表"])
        with tab1:
            st.subheader("NASLD各月份數")
            st.dataframe(nalsd_pd)
            st.subheader("NASLD各月份占比")
            st.dataframe(percentage_df)
            st.subheader("Nes活性指標數據")
            st.dataframe(final_nes)
        with tab2:
            tab2.plotly_chart(fig_customer)
            tab2.plotly_chart(fig_percent) #, theme=None
            
            

if __name__ == '__main__':
    main()  
            