# -*- coding: utf-8 -*-
"""
Created on Thu Jul 27 17:24:49 2023

@author: User
"""
import transdata_function as tf
import sum_purchase_fun as sf
import streamlit as st
import io
import streamlit_ext as ste
import pandas as pd

def main():
    buffer = io.BytesIO()
    st.set_page_config(
        #page_title="新舊客戶相關分析",
        page_icon="random",
        layout='wide',
        #initial_sidebar_state="collapsed",
    )
    product_df = pd.read_csv("產品分類.csv",low_memory=False).dropna()
    st.title('新舊客戶搭配產品別相關分析')
    
    
    # 上傳資料集
    uploaded_file = st.sidebar.file_uploader("請上傳您的檔案", type=["csv"]) #,accept_multiple_files=True
    if uploaded_file is not None : #or st.session_state['btn_clicked']
        
        @st.cache_data(show_spinner=False) ##不要顯示涵式名稱
        def read_df(uploaded_file):
            Transaction_dict = pd.read_csv(uploaded_file,low_memory= False)
            return Transaction_dict #,product_df
        # 抓資料
        Transaction_df = read_df(uploaded_file) #,product_df
    if uploaded_file is not None :
        with st.spinner('Wait for it...'):
            @st.cache_data(show_spinner=False) #by月份數據
            def read_df2(Transaction_df):
                purchase_detail,bill_detail3 = tf.Transaction_without_product(Transaction_df)
                total_df,total_new_df,total_old_df = tf.makedf_without_product(purchase_detail,bill_detail3)
                return total_df,total_new_df,total_old_df
            total_df,total_new_df,total_old_df = read_df2(Transaction_df)
                
            @st.cache_data(show_spinner=False) # by商品數據
            def read_df3(Transaction_df,product_df):    
                purchase_product_detail,bill_product_detail3 = tf.Transaction_with_product(Transaction_df,product_df)
                df_product,df_new_product,df_old_product = tf.makedf_with_product(purchase_product_detail,bill_product_detail3)
                return df_product,df_new_product,df_old_product
            df_product,df_new_product,df_old_product =  read_df3(Transaction_df,product_df)
            
            @st.cache_data(show_spinner=False) # by商品數據
            def read_df4(df_new_product,df_old_product): 
                new_product_list = tf.sep_product(df_new_product)
                old_product_list = tf.sep_product(df_old_product)
                newold_p = tf.newold_sep_product(df_new_product, df_old_product)
                return new_product_list,old_product_list,newold_p
            new_product_list,old_product_list,newold_p = read_df4(df_new_product,df_old_product)       
            
            @st.cache_data(show_spinner=False) # by商品數據
            def read_df5(Transaction_df): 
                purchase_detail = sf.sum_purchase(Transaction_df)
                return purchase_detail
            purchase_df = read_df5(Transaction_df)
            # 資料下載 
            # st.subheader('資料集')
            # with pd.ExcelWriter(buffer,engine='xlsxwriter') as writer:   #下載EXCEL資料
            #     total_df.to_excel(writer, index = False, sheet_name='總人數')
            #     total_new_df.to_excel(writer, index = False, sheet_name='新客人數')
            #     total_old_df.to_excel(writer, index = False, sheet_name='舊客人數')
            #     #writer.close()
            # ste.download_button('下載excel檔',data = buffer,file_name='表格下載.xlsx')
            
            st.subheader("各月分資料by新舊客戶")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader('總人數')
                st.dataframe(total_df)
            with col2:
                st.subheader('新客人數')
                st.dataframe(total_new_df)
            with col3:
                st.subheader('舊客人數')
                st.dataframe(total_old_df)
                
            st.subheader("各月分資料by新客戶、商品")    
            tab_all = st.tabs(tf.member_c.product)        
            with tab_all[0]: # 好欣情
                col1_good,col2_good = st.columns(2)
                with col1_good:
                    st.subheader("新客戶")
                    st.dataframe(new_product_list[0])
                with col2_good:
                    st.subheader("舊客戶")
                    st.dataframe(old_product_list[0])
                st.subheader("新舊客戶人數佔比")
                st.dataframe(newold_p[0])
            with tab_all[1]: # 益菌寶
                col1_germ,col2_germ = st.columns(2)
                with col1_germ:
                    st.subheader("新客戶")
                    st.dataframe(new_product_list[1])
                with col2_germ:
                    st.subheader("舊客戶")
                    st.dataframe(old_product_list[1])
                st.subheader("新舊客戶人數佔比")
                st.dataframe(newold_p[1])
            with tab_all[2]: # 好益活
                col1_happy,col2_happy = st.columns(2)
                with col1_happy:
                    st.subheader("新客戶")
                    st.dataframe(new_product_list[2])
                with col2_happy:
                    st.subheader("舊客戶")
                    st.dataframe(old_product_list[2])
                st.subheader("新舊客戶人數佔比")
                st.dataframe(newold_p[2])
            with tab_all[3]: # 淨美莓
                col1_beauty,col2_beauty = st.columns(2)
                with col1_beauty:
                    st.subheader("新客戶")
                    st.dataframe(new_product_list[3])
                with col2_beauty:
                    st.subheader("舊客戶")
                    st.dataframe(old_product_list[3])
                st.subheader("新舊客戶人數佔比")
                st.dataframe(newold_p[3])
            with tab_all[4]: # 益菌優
                col1_goodgerm,col2_goodgerm = st.columns(2)
                with col1_goodgerm:
                    st.subheader("新客戶")
                    st.dataframe(new_product_list[4])
                with col2_goodgerm:
                    st.subheader("舊客戶")
                    st.dataframe(old_product_list[4])
                st.subheader("新舊客戶人數佔比")
                st.dataframe(newold_p[4])
            with tab_all[5]: # 益伏敏
                col1_allergy,col2_allergy = st.columns(2)
                with col1_allergy:
                    st.subheader("新客戶")
                    st.dataframe(new_product_list[5])
                with col2_allergy:
                    st.subheader("舊客戶")
                    st.dataframe(old_product_list[5])
                st.subheader("新舊客戶人數佔比")
                st.dataframe(newold_p[5])
            with tab_all[6]: # 好益思
                col1_think,col2_think = st.columns(2)
                with col1_think:
                    st.subheader("新客戶")
                    st.dataframe(new_product_list[6])
                with col2_think:
                    st.subheader("舊客戶")
                    st.dataframe(old_product_list[6])
                st.subheader("新舊客戶人數佔比")
                st.dataframe(newold_p[6])
            with tab_all[7]: # 激耐益
                col1_sport,col2_sport = st.columns(2)
                with col1_sport:
                    st.subheader("新客戶")
                    st.dataframe(new_product_list[7])
                with col2_sport:
                    st.subheader("舊客戶")
                    st.dataframe(old_product_list[7])
                st.subheader("新舊客戶人數佔比")
                st.dataframe(newold_p[7])
            with tab_all[8]: # 套組
                col1_set,col2_set = st.columns(2)
                with col1_set:
                    st.subheader("新客戶")
                    st.dataframe(new_product_list[8])
                with col2_set:
                    st.subheader("舊客戶")
                    st.dataframe(old_product_list[8])
                st.subheader("新舊客戶人數佔比")
                st.dataframe(newold_p[8])
            with tab_all[9]: # 奇毛子
                col1_pet,col2_pet = st.columns(2)
                with col1_pet:
                    st.subheader("新客戶")
                    st.dataframe(new_product_list[9])
                with col2_pet:
                    st.subheader("舊客戶")
                    st.dataframe(old_product_list[9])
                st.subheader("新舊客戶人數佔比")
                st.dataframe(newold_p[9])
            with tab_all[10]: # 銀養奇毛子
                col1_pet1,col2_pet2 = st.columns(2)
                with col1_pet1:
                    st.subheader("新客戶")
                    st.dataframe(new_product_list[10])
                with col2_pet2:
                    st.subheader("舊客戶")
                    st.dataframe(old_product_list[10])
                st.subheader("新舊客戶人數佔比")
                st.dataframe(newold_p[10])
            with tab_all[11]: # 定期購
                col1_regular1,col2_regular2 = st.columns(2)
                with col1_regular1:
                    st.subheader("新客戶")
                    st.dataframe(new_product_list[11])
                with col2_regular2:
                    st.subheader("舊客戶")
                    st.dataframe(old_product_list[11])
                st.subheader("新舊客戶人數佔比")
                st.dataframe(newold_p[11])
            
            st.subheader("年度資料by新舊客戶、商品")
            df_product['年份'] = df_product['日期年加月'].apply(lambda x: str(x)[0:4])
            year_list = df_product['年份'].unique()
            year_list = sorted(year_list, reverse = True)
            
            year_date = st.selectbox("選擇年分", year_list ,index = 0)
            col4, col5 = st.columns(2)
            with col4:
                st.subheader("年度新客戶")
                newyear_df = tf.year_product(df_new_product,year_date)
                st.dataframe(newyear_df)
            with col5:
                st.subheader("年度舊客戶")
                oldyear_df = tf.year_product(df_old_product,year_date)
                st.dataframe(oldyear_df)
                
            st.subheader("年度資料by會員分類")
            new_mem_df,old_mem_df = sf.groupby_newold(purchase_df, year_date)
            col6, col7 = st.columns(2)
            with col6:
                st.subheader("新客戶")
                st.dataframe(new_mem_df)
            with col7:
                st.subheader("舊客戶")
                st.dataframe(old_mem_df)
        # with st.form("my_form"):
        #     year_date = st.selectbox("選擇年分", year_list ,index = 0)
        #     submitted = st.form_submit_button("Submit")
        # if submitted:
        #     newyear_df = tf.year_product(df_product,year_date)
        #     st.dataframe(newyear_df)
if __name__ == '__main__':
    main()  