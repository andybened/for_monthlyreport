# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 17:24:49 2023

@author: User
"""
from newold_member import member_level  as mem
#from newold_member import sum_purchase_fun as sf
import streamlit as st
#import io
import streamlit_ext as ste
import pandas as pd
#from st_aggrid import AgGrid
def for_member():
    #buffer = io.BytesIO()
    st.set_page_config(
        #page_title="新舊客戶相關分析",
        page_icon="random",
        layout='wide',
        #initial_sidebar_state="collapsed",
    )
    product_df = pd.read_csv("產品分類.csv",low_memory=False).dropna()
    st.title('會籍搭配產品別相關分析')
    
    with st.form("my_form"):
        with st.sidebar:
            uploaded_file_person = st.sidebar.file_uploader("請上傳您的檔案", type=["csv"])
            submitted = st.form_submit_button("上傳檔案")
    # 上傳資料集
    if submitted:
        @st.cache_data(show_spinner=False) 
        def read_df(uploaded_file_person):
            member_level_df = pd.read_csv(uploaded_file_person,low_memory=False)
            return member_level_df
        Transaction_df = read_df(uploaded_file_person)
        with st.spinner('Wait for it...'):
                
            @st.cache_data(show_spinner=False) #by會籍
            def read_df3(Transaction_df):    
                people_bill_final = mem.Transaction_without_product(Transaction_df)
                member_final_pd = mem.repurchase_nowyear(people_bill_final) ##去年跟今年都有買重購
                normal_df,platinum_df,VIP_df= mem.makedf_without_product(people_bill_final)
                return normal_df,platinum_df,VIP_df,member_final_pd
            normal_df,platinum_df,VIP_df,member_final_pd =  read_df3(Transaction_df)
            
            # 資料下載 
            # st.subheader('資料集')
            # with pd.ExcelWriter(buffer,engine='xlsxwriter') as writer:   #下載EXCEL資料
            #     total_df.to_excel(writer, index = False, sheet_name='總人數')
            #     total_new_df.to_excel(writer, index = False, sheet_name='新客人數')
            #     total_old_df.to_excel(writer, index = False, sheet_name='舊客人數')
            #     #writer.close()
            # ste.download_button('下載excel檔',data = buffer,file_name='表格下載.xlsx')
            
            st.subheader("各月分資料by會籍")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader('一般會員')
                st.dataframe(normal_df)
            with col2:
                st.subheader('白金會員')
                st.dataframe(platinum_df)
            with col3:
                st.subheader('尊爵會員')
                st.dataframe(VIP_df)
            
            st.subheader("忠誠客重購by月份")
            tab_all = st.tabs(['2022','2023'])        
            with tab_all[0]: # 好欣情
                st.dataframe(member_final_pd['2022'])
            with tab_all[1]: # 益菌寶
                st.dataframe(member_final_pd['2023'])

for_member()