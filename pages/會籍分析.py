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

def main():
    #buffer = io.BytesIO()
    st.set_page_config(
        #page_title="新舊客戶相關分析",
        page_icon="random",
        layout='wide',
        #initial_sidebar_state="collapsed",
    )
    product_df = pd.read_csv("產品分類.csv",low_memory=False).dropna()
    st.title('會籍搭配產品別相關分析')
    uploaded_file = st.sidebar.file_uploader("請上傳您的檔案", type=["csv"]) #,accept_multiple_files=True
    # 上傳資料集
    if uploaded_file is not None :
        @st.cache_data(show_spinner=False) 
        def read_df(uploaded_file):
            member_level_df = pd.read_csv(uploaded_file,low_memory=False)
            return member_level_df
        Transaction_df = read_df(uploaded_file)
        with st.spinner('Wait for it...'):
            @st.cache_data(show_spinner=False) #商品by會籍
            def read_df2(Transaction_df,product_df):
                product_bill_final = mem.Transaction_with_product(Transaction_df,product_df)
                final_list = mem.makedf_with_product(product_bill_final)
                return final_list
            final_list= read_df2(Transaction_df,product_df) #dict key商品別
                
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
                
            st.subheader("各月分資料by會籍、商品")    
            tab_all = st.tabs(mem.member_c.product)        
            with tab_all[0]: # 好欣情
                st.dataframe(final_list['好欣情'])
            with tab_all[1]: # 益菌寶
                st.dataframe(final_list['益菌寶'])
            with tab_all[2]: # 好益活
                st.dataframe(final_list['好益活'])
            with tab_all[3]: # 淨美莓
                st.dataframe(final_list['淨美莓'])
            with tab_all[4]: # 益菌優
                st.dataframe(final_list['益菌優'])
            with tab_all[5]: # 益伏敏
                st.dataframe(final_list['益伏敏'])
            with tab_all[6]: # 好益思
                st.dataframe(final_list['好益思'])    
            with tab_all[7]: # 激耐益
                st.dataframe(final_list['激耐益'])    
            with tab_all[8]: # 套組
                st.dataframe(final_list['套組'])    
            with tab_all[9]: # 奇毛子
                st.dataframe(final_list['奇毛子'])    
            with tab_all[10]: # 銀養奇毛子
                st.dataframe(final_list['銀養奇毛子'])    
            with tab_all[11]: # 定期購
                st.dataframe(final_list['定期購'])   
            
            st.subheader("忠誠客重購by月份")
            tab_all = st.tabs(['2022','2023'])        
            with tab_all[0]: # 好欣情
                st.dataframe(member_final_pd['2022'])
            with tab_all[1]: # 益菌寶
                st.dataframe(member_final_pd['2023'])

if __name__ == '__main__':
    main()  