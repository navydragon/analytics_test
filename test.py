import streamlit as st
import numpy as np
import pandas as pd
#import matplotlib.pyplot as plt
import plotly.express as px 
import datetime
import math

#data
#read_file =  pd.read_excel('data.xlsx', sheet_name='ОБЩ')
#read_file.to_csv ('common.csv', index = None, header=True)
#read_file =  pd.read_excel('data.xlsx', sheet_name='Подразделения')
#read_file.to_csv ('divisions.csv', index = None, header=True)
#read_file =  pd.read_excel('students.xlsx', sheet_name='Лист1')
#read_file.to_csv ('students.csv', index = None, header=True)
#read_file =  pd.read_excel('data.xlsx', sheet_name='КОРПУСА')
#read_file.to_csv ('buildings.csv', index = None, header=True)

#read_file =  pd.read_excel('Содержание_имущества.xlsx', sheet_name='Все')
#read_file.to_csv ('money.csv', index = None, header=True)


divisions = pd.read_csv('https://raw.githubusercontent.com/navydragon/analytics_test/master/divisions.csv')
division_data = pd.read_csv('https://raw.githubusercontent.com/navydragon/analytics_test/master/common.csv')
students_data = pd.read_csv('https://raw.githubusercontent.com/navydragon/analytics_test/master/students.csv')
buildings_data = pd.read_csv('https://raw.githubusercontent.com/navydragon/analytics_test/master/buildings.csv')
money_data = pd.read_csv('https://raw.githubusercontent.com/navydragon/analytics_test/master/money.csv')

division_data = division_data.merge(divisions,how='inner', on='Аббревеатура')
division_data['Численность'] = division_data['Численность'].fillna(0).astype(int,errors='ignore')
division_data['Общая'] = division_data['Общая'].fillna(0).astype(int,errors='ignore')
division_data['Административная'] = division_data['Административная'].fillna(0).astype(int,errors='ignore')
division_data['Учебная'] = division_data['Учебная'].fillna(0).astype(int,errors='ignore')
division_data['Иная'] = division_data['Иная'].fillna(0).astype(int,errors='ignore')
division_data= division_data[division_data['Учит студентов'] == 1]
# полезная площадь
division_data['Полезная'] = division_data['Учебная'] + division_data['Административная']
division_data_melt = pd.melt(division_data, id_vars=['Подразделение','Аббревеатура','Объект','Общая'], value_vars=['Административная','Учебная','Иная'],var_name='Тип площади', value_name='Площадь')




id_vars = ['Наименование','Категория','Адрес','Площадь, кв.м.','Год']
value_vars = set(money_data.columns.unique()) - set(id_vars)
money_data_melt = pd.melt(money_data, id_vars=id_vars, value_vars=value_vars,var_name='Тип расходов', value_name='Расходы, руб.')
money_data_melt['Расходы, руб.'] = money_data_melt['Расходы, руб.'].fillna(0).astype('int')
money_data_melt['Год'] = money_data_melt['Год'].astype('int')
money_data_melt['Площадь, кв.м.'] = money_data_melt['Площадь, кв.м.'].astype('int')
page = st.sidebar.selectbox(
    "Страница",("Расписание РУТ","Расписание РОАТ","Структурные подразделения", "Площадь на 1 студента", "Корпуса","Содержание имущества")
)

st.header('Анализ имущественного комплекса')

if page == "Структурные подразделения":
    def filter_fig1(data,object,place_type,show_type):
        if object != 'Все':
            data = data[data['Объект'] == object]  
        if place_type == 'Полезная':
            data = data[data['Тип площади'] != 'Иная']
        elif place_type != 'Общая':
            data = data[data['Тип площади'] == place_type]
        
        data = data.groupby(by=['Подразделение','Аббревеатура','Тип площади']).sum().reset_index().sort_values(by='Общая',ascending=False)  
        data_to_top = data.groupby(by=['Подразделение'])['Площадь'].sum().sort_values(ascending=False)
        if show_type == 'TOP-5': array_in = data_to_top.head().index
        elif show_type == 'TOP-10': array_in = data_to_top.head(10).index
        elif show_type == 'BOTTOM-5': array_in = data_to_top.tail().index
        elif show_type == 'BOTTOM-10': array_in = data_to_top.tail(10).index
        else: 
            return data
        return data[data['Подразделение'].isin(array_in)]

    # division_data_pivot = division_data_melt.pivot_table(index=['Подразделение','Объект'], columns='Тип площади', values='Площадь')
    # division_data_pivot
    all = pd.Series(['Все'])
    # divisions = np.concatenate([all,division_data['Подразделение'].unique()])
    objects = np.concatenate([all,division_data['Объект'].unique()]) 
    place_types= ['Общая','Полезная','Административная','Учебная','Иная']
    show_type= ['Все','TOP-5','TOP-10','BOTTOM-5','BOTTOM-10']

    df_stacked = division_data.groupby(by='Аббревеатура').sum().reset_index().sort_values(by='Общая',ascending=False)
    df_stacked['Учебная к административной'] = (df_stacked['Учебная'] / df_stacked['Административная']).round(2)
    st.subheader('Структурные подразделения')
    
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_object = st.selectbox('Здание',objects)
    with col2:
        filter_place_type = st.selectbox('Тип площади',place_types)
    with col3:
        filter_show_type = st.selectbox('Показать подразделений',show_type)

    fig1_data = filter_fig1(division_data_melt,filter_object,filter_place_type,filter_show_type)
    fig = px.bar(fig1_data, x="Аббревеатура", y="Площадь", color="Тип площади",text_auto='.2s')
    #fig = px.bar(df_stacked, x="Подразделение", y=['Административная','Учебная','Иная'], title="Wide-Form Input")
    fig.update_layout(template = 'simple_white', xaxis_title = 'Подразделение',yaxis_title = 'Занимаемая площадь', width = 900, height = 450)
    st.plotly_chart(fig)

    #учебная к административной
    st.subheader('Отношение учебной площади к административной')
    y = 'Учебная к административной'
    df_stacked = df_stacked.sort_values(by=y,ascending=False)
    median = df_stacked[y].median()
    fig = px.bar(df_stacked, x="Аббревеатура", y=y,text_auto=True)
    fig.add_hline(y=median,line_dash="dash", line_color="green", annotation_text="Медиана = "+str(round(median,2)   ), annotation_position="top right", annotation_font_size=18, annotation_font_color="black",opacity=0.75)
    fig.update_layout(xaxis_title = 'Подразделение',yaxis_title = 'Учебная/Административноая', width = 900, height = 450)     
    fig.update_traces(textfont_size=20,textposition='outside', selector=dict(type='bar'))
    fig.update_yaxes(range=[0, df_stacked[y].max() * 1.2])
    st.plotly_chart(fig)
    if (st.checkbox('Показать таблицу')):
        df_stacked
    
    st.subheader('Данные о подразделении')
    col1, col2 = st.columns(2)
    with col1:
        division= st.selectbox('Подразделение',division_data['Аббревеатура'].unique())
    
    st.subheader(division) 
    sp_data = division_data.query("Аббревеатура == @division")
    sp_data_melt = division_data_melt.query("Аббревеатура == @division")
    st_data = students_data.query("Аббревеатура == @division")
    col1, col2, col3,col4 = st.columns(4)
    col1.metric("Общая пл.", sp_data['Общая'].sum())
    col2.metric("Административная пл.",sp_data['Административная'].sum())
    col3.metric("Учебная пл.", sp_data['Учебная'].sum())
    col4.metric("Иная пл.", sp_data['Иная'].sum())
    col1, col2, col3,col4 = st.columns(4)
    col1.metric("Общая пл. на 1 ст.", round(sp_data['Общая'].sum()/st_data['количество студентов'].sum(),2))
    col2.metric("Полезная пл. на 1 ст.", round(sp_data['Полезная'].sum()/st_data['количество студентов'].sum(),2))
    col3.metric("Учебная пл. на 1 ст.", round(sp_data['Учебная'].sum()/st_data['количество студентов'].sum(),2))
    col4.metric("Контингент", st_data['количество студентов'].sum())

    fig = px.pie(sp_data_melt, values='Площадь', names='Тип площади',title="Доля площадей разного типа")
    fig.update_traces(textinfo='percent', textfont_size=20)
    st.plotly_chart(fig)
    fig = px.pie(sp_data_melt, values='Площадь', names='Объект',title="Размещение по корпусам")
    fig.update_traces(textinfo='percent', textfont_size=20)
    st.plotly_chart(fig)

#square_students
if page == "Площадь на 1 студента":
    st.subheader('Площадь на 1 студента')
    dd_stacked = division_data.groupby(by='Аббревеатура').sum().reset_index().sort_values(by='Общая',ascending=False)
    ss_data = dd_stacked.set_index('Аббревеатура').join(students_data.set_index('Аббревеатура'))
    ss_data = ss_data.dropna(subset=['количество студентов']).drop(columns=['Наименование структурного подразделения'])
    ss_data['количество студентов'] = ss_data['количество студентов'].astype(int,errors='ignore')
    ss_data['Учебная пл. на 1 студента'] = (ss_data['Учебная'] / ss_data['количество студентов']).round(2)
    ss_data['Полезная пл. на 1 студента'] = (ss_data['Полезная'] / ss_data['количество студентов']).round(2)
    ss_data['Общая пл. на 1 студента'] = (ss_data['Общая'] / ss_data['количество студентов']).round(2)
    col1, col2 = st.columns(2)
    with col1:
        place_types= ['Общая','Полезная','Учебная']
        place_type = st.selectbox('Тип площади',place_types)
        marker_colors=dict(Общая="#9966CC",Полезная="#EF553B",Учебная="#00CC96")
        
    #place_per_student
    y = place_type+" пл. на 1 студента"
    ss_data = ss_data.sort_values(by=y,ascending=False)
    l_median = ss_data[y].median()
    fig = px.bar(ss_data, x=ss_data.index, y=y,text_auto=True)
    fig.add_hline(y=l_median,line_dash="dash", line_color="green", annotation_text="Медиана = "+str(round(l_median,2)   ), annotation_position="top right", annotation_font_size=18, annotation_font_color="black",opacity=0.75)    
    fig.update_layout(xaxis_title = 'Подразделение', width = 900, height = 450,)
    fig.update_traces(marker_color= marker_colors[place_type],textfont_size=20,textposition='outside', selector=dict(type='bar'))
    fig.update_yaxes(range=[0, ss_data[y].max() * 1.2])
    st.plotly_chart(fig)
    #scatter
    y = place_type+" пл. на 1 студента"
    fig = px.scatter(ss_data,  text=ss_data.index, x="количество студентов", y=y,size=y)
    fig.update_layout(width = 900, height = 450,)
    fig.update_traces(textposition='top center', selector=dict(type='scatter'),
        textfont=dict(size=16,color="black"),
        marker= dict(color = marker_colors[place_type]))
    fig.update_yaxes(range=[0, ss_data[y].max() * 1.2])
    st.plotly_chart(fig)
        
    if (st.checkbox('Показать таблицу')):
        ss_data

if page == "Корпуса":
    all = pd.Series(['Все'])
    places = np.concatenate([all,buildings_data['Тип помещения'].unique()])
    col1,col2 = st.columns(2)
    with col1:
        place_filter = st.selectbox('Тип помещений',places)
    with col2:
        buildings_filter = st.multiselect(
        'Корпус',
        np.concatenate([buildings_data['Корпус'].unique()]),
        ['ГУК-1','ГУК-2','ГУК-3','ГУК-4','ГУК-5','ГУК-6','ГУК-7','ГУК-12','ГУК-14','РОАТ 1 корпус','РОАТ 2 корпус','РОАТ 3 корпус','РОАТ УЛК'])
    buildings_data['Количество помещений'] = buildings_data['Количество помещений'].fillna(0).astype(int,errors='raise')
    buildings_data['Площадь'] = buildings_data['Площадь'].fillna(0).astype(int,errors='raise')
    buildings_data['Сотрудников'] = buildings_data['Сотрудников'].fillna(0).astype(int,errors='raise')
    buildings_data = buildings_data[buildings_data["Количество помещений"] > 0]
    if (len(buildings_filter) > 0):
        buildings_data = buildings_data[buildings_data["Корпус"].isin(buildings_filter)]
    stacked_data = buildings_data.groupby(by=['Корпус','Адрес','Тип помещения']).sum().reset_index()
    if place_filter != 'Все':
        filtered_data = stacked_data[stacked_data['Тип помещения'] == place_filter ]
    else:
        filtered_data = stacked_data
    filtered_data["Сотрудников на помещение"] = round(filtered_data['Сотрудников'] / filtered_data['Количество помещений'],2)
    filtered_data["Площадь на сотрудника"] = round(filtered_data['Площадь'] / filtered_data['Сотрудников'],2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Помещений", filtered_data['Количество помещений'].sum()) 
    col2.metric("Площадь", filtered_data['Площадь'].sum()) 
    col3.metric("Сотрудников", filtered_data['Сотрудников'].sum()) 
    col1, col2, col3 = st.columns(3)
    ppp_mean = round(filtered_data['Сотрудников'].sum() / filtered_data['Количество помещений'].sum(),2)
    spp_mean = round(filtered_data['Площадь'].sum() / filtered_data['Сотрудников'].sum(),2)
    p_mean = round(filtered_data['Количество помещений'].mean(),2)
    s_mean = round(filtered_data['Площадь'].mean(),2)
    col1.metric("Сотрудников на помещение", ppp_mean ) 
    col2.metric("Площадь на сотрудника", spp_mean) 
    
    filtered_data = filtered_data.groupby(by=['Корпус','Адрес']).sum().reset_index()
    
    


    st.subheader(place_filter)
    y = "Количество помещений"
    filtered_data = filtered_data.sort_values(by=y,ascending=False)  
    
    fig = px.bar(filtered_data, x="Корпус", y=y,text_auto=True)
    
    fig.add_hline(y=p_mean,line_dash="dash", line_color="black", annotation_text="Среднее = "+str(round(p_mean,2)   ), annotation_position="top right", annotation_font_size=18, annotation_font_color="black",opacity=0.75)    
    fig.update_layout(xaxis_title = 'Корпус', width = 900, height = 450)
    fig.update_traces(marker_color= "teal",textfont_size=20,textposition='outside', selector=dict(type='bar'))
    fig.update_yaxes(range=[0, filtered_data[y].max() * 1.2])
    st.plotly_chart(fig)

    y = "Площадь"
    filtered_data = filtered_data.sort_values(by=y,ascending=False)  
    
    fig = px.bar(filtered_data, x="Корпус", y=y,text_auto=True)
    
    fig.add_hline(y=s_mean,line_dash="dash", line_color="black", annotation_text="Среднее = "+str(round(s_mean,2)   ), annotation_position="top right", annotation_font_size=18, annotation_font_color="black",opacity=0.75)    
    fig.update_layout(xaxis_title = 'Корпус', width = 900, height = 450)
    fig.update_traces(marker_color= "teal",textfont_size=20,textposition='outside', selector=dict(type='bar'))
    fig.update_yaxes(range=[0, filtered_data[y].max() * 1.2])
    st.plotly_chart(fig)

    y = "Сотрудников на помещение"
    filtered_data = filtered_data.sort_values(by=y,ascending=False)  
    
    fig = px.bar(filtered_data, x="Корпус", y=y,text_auto=True)
    
    fig.add_hline(y=ppp_mean,line_dash="dash", line_color="black", annotation_text="Среднее = "+str(round(ppp_mean,2)   ), annotation_position="top right", annotation_font_size=18, annotation_font_color="black",opacity=0.75)    
    fig.update_layout(xaxis_title = 'Корпус', width = 900, height = 450)
    fig.update_traces(marker_color= "teal",textfont_size=20,textposition='outside', selector=dict(type='bar'))
    fig.update_yaxes(range=[0, filtered_data[y].max() * 1.2])
    st.plotly_chart(fig)

    y = "Площадь на сотрудника"
    filtered_data = filtered_data[filtered_data['Сотрудников'] > 0]
    filtered_data = filtered_data.sort_values(by=y,ascending=False)  
    
    fig = px.bar(filtered_data, x="Корпус", y=y,text_auto=True)
    
    fig.add_hline(y=spp_mean,line_dash="dash", line_color="black", annotation_text="Среднее = "+str(round(spp_mean,2)   ), annotation_position="top right", annotation_font_size=18, annotation_font_color="black",opacity=0.75)    
    fig.update_layout(xaxis_title = 'Корпус', width = 900, height = 450)
    fig.update_traces(marker_color= "teal",textfont_size=20,textposition='outside', selector=dict(type='bar'))
    fig.update_yaxes(range=[0, filtered_data[y].max() * 1.2])
    st.plotly_chart(fig)

    st.subheader("Анализ корпуса")
    building = st.selectbox('Корпус',buildings_data['Корпус'].unique())
    stacked_data = buildings_data.groupby(by=['Корпус','Адрес','Тип помещения']).sum().reset_index()
    filter_data = stacked_data[stacked_data['Корпус']== building].reset_index(drop=True)

    st.subheader(building)
    st.caption(filter_data.loc[0,'Адрес'])
    show = filter_data.drop(columns=['Корпус','Адрес']).sort_values(by='Площадь',ascending=False).reset_index(drop=True)
    show
    fig = px.pie(filter_data, values='Количество помещений', names='Тип помещения',title="Доля помещений разного типа")
    fig.update_traces(textinfo='percent', textfont_size=20)
    st.plotly_chart(fig)
    fig = px.pie(filter_data, values='Площадь', names='Тип помещения',title="Доля площадей разного типа")
    fig.update_traces(textinfo='percent', textfont_size=20)
    st.plotly_chart(fig)

# col1, col2, col3,col4 = st.columns(4)
# col1.metric("Помещений", filtered_data['Количество помещений'].sum()) 
# col2.metric("Площадь", filtered_data['Площадь'].sum()) 
# col3.metric("Сотрудников", filtered_data['Сотрудников'].sum())


if page == "Содержание имущества":
    st.subheader(page)
    st.subheader("По категориям зданий")
    year = st.selectbox('Год',money_data_melt['Год'].unique())
    filtered_data = money_data_melt.query("Год == @year")    
    type_data = filtered_data.groupby(by=['Категория','Год']).sum().sort_values(by='Расходы, руб.',ascending=False).reset_index()
    type_data['Расходы на 1 кв.м.'] = (type_data['Расходы, руб.'] / type_data['Площадь, кв.м.']).astype(int)
    type_data
    fig = px.pie(type_data, values='Расходы, руб.', names='Категория',title="Доля расходов по категориям")
    fig.update_traces(textinfo='percent', textfont_size=20)
    st.plotly_chart(fig)

    fig = px.bar(type_data, x="Категория", y='Расходы на 1 кв.м.',text_auto=True, color='Категория')
    fig.update_traces(textfont_size=20,textposition='outside', selector=dict(type='bar'))
    fig.update_yaxes(range=[0, type_data['Расходы на 1 кв.м.'].max() * 1.2])
    st.plotly_chart(fig)
    
    razv = st.checkbox('Показать развернутую диаграмму')
    if razv:
        fig = px.treemap(filtered_data, path=[px.Constant("Все"), 'Категория', 'Адрес', 'Тип расходов'], values='Расходы, руб.')
        fig.update_traces(root_color="lightgrey")
        fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        fig.show()

    
    st.subheader("По годам")
    all = pd.Series(['Все'])
    category = st.selectbox('Категория',np.concatenate([all,money_data_melt['Категория'].unique()]))
    if (category != 'Все'):
        filtered_data = money_data_melt.query("Категория == @category")    
    else:
        filtered_data = money_data_melt
    
    type_data = filtered_data.groupby(by=['Категория','Год']).sum().sort_values(by='Год',ascending=True).reset_index()
    type_data['Расходы на 1 кв.м.'] = (type_data['Расходы, руб.'] / type_data['Площадь, кв.м.']).astype(int)
    type_data['Расходы, руб.'] = type_data['Расходы, руб.'].astype('int')
    type_data
    fig = px.bar(type_data, x="Год", y="Расходы, руб.", color="Категория",barmode='group',text_auto='.0s')
    fig.update_traces(textfont_size=16, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_yaxes(range=[0, type_data['Расходы, руб.'].max() * 1.2])
    st.plotly_chart(fig)

    x = type_data['Год']
    fig = px.line(type_data, x=x, y="Расходы на 1 кв.м.", color='Категория', text="Расходы на 1 кв.м.")
    fig.update_traces(textfont_size=16, cliponaxis=False,textposition="top center")
    fig.update_yaxes(range=[0, type_data['Расходы на 1 кв.м.'].max() * 1.2])
    fig.update_xaxes(showgrid=True, dtick="1")
    st.plotly_chart(fig)

    st.subheader("По типам затрат")
    col1, col2, col3 = st.columns(3)

    with col1:
        year = st.selectbox('Год',money_data_melt['Год'].unique(),key='year2')
        filtered_data = money_data_melt.query("Год == @year")
    with col2:
        category = st.selectbox('Категория',np.concatenate([all,money_data_melt['Категория'].unique()]),key='category2')        
        if category != 'Все':
            filtered_data = filtered_data.query("Категория == @category")
    with col3:
        if category == 'Все':
            address = st.selectbox('Адрес',np.concatenate([all,money_data_melt['Адрес'].unique()]),key='address2')
        else:
            address = st.selectbox('Адрес',np.concatenate([all,money_data_melt.query("Категория == @category")['Адрес'].unique()]),key='address2')
        if address != 'Все':
           filtered_data = filtered_data.query("Адрес == @address") 
    
    # def rashod_type(type,summ):
    #     if (type * 100 / summ) >= 5:
    #         return type
    #     else:
    #         return "Другое"

    pie_data = filtered_data.groupby('Тип расходов').sum().drop(columns=['Площадь, кв.м.','Год']).sort_values(by='Расходы, руб.',ascending=False).reset_index()
    # pie_data['Тип  расходов'] = pie_data.apply(rashod_type, axis=1)
    # fig = px.pie(pie_data, values='Расходы, руб.', names='Тип расходов',title="Доля расходов по типам")
    # fig.update_traces(textinfo='percent', textfont_size=20)
    # st.plotly_chart(fig)
    pie_data

if page == "Расписание РОАТ":
    roat = pd.read_csv('roat.csv')
    roat["Дата"] = pd.to_datetime(roat["Дата"])
    roat["Время начала"] = pd.to_datetime(roat["Время начала"])
    roat["Время окончания"] = pd.to_datetime(roat["Время окончания"])
    
    roat = roat.drop_duplicates()
    #work = roat[['Дата','Время начала','Время окончания','Помещение','Корпус']]
    #work = work.drop_duplicates()
    #st.write(work.duplicated().sum())
    #work = roat.groupby(['Дата','Время начала','Время окончания','Помещение','Корпус'],as_index=False)['Корпус'].count()
    #work = work[work['Корпус'] > 1]
    #st.write(work['Корпус'].sum() - work.shape[0])
    st.subheader('Анализ расписания РОАТ за 2021-2022 учебный год')
    st.subheader('Количество задействованных аудиторий по корпусам')
    places = roat.groupby('Корпус',as_index=False)['Помещение'].nunique()
    places = places.rename(columns={"Помещение":"Задействовано аудиторий"})
    places
    st.subheader('Количество проводимых занятий по корпусам')
    lessons = roat.groupby('Корпус',as_index=False)['Помещение'].count()
    lessons = lessons.rename(columns={"Помещение":"Количество занятий"})
    lessons
    fig = px.pie(lessons, values='Количество занятий', names='Корпус',title="Количество проводимых занятий по корпусам")
    fig.update_traces(textinfo='percent', textfont_size=20)
    st.plotly_chart(fig)

    filtered = roat
    buildings = st.multiselect('Корпуса',places['Корпус'].unique(),places['Корпус'].unique())
    start_date = st.date_input("Начало периода",datetime.date(2021, 9, 1))
    end_date = st.date_input("Конец периода",datetime.date(2022, 7, 30))
    week_days = st.multiselect('Дни недели',roat['День недели'].unique(),roat['День недели'].unique())
    start_time, end_time = st.select_slider(
     'Фильтр по времени проведения занятий',
     options=[8,9,10,11,12,13,14,15,16,17,18,19,20,21,22],
     value=(8, 22))
     
    st.write('Отображаются данные для занятий с ', start_time, 'по', end_time,'часов')
    start_time = pd.to_datetime(start_time,format="%H")
    end_time = pd.to_datetime(end_time,format="%H")
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    filtered = roat[roat['Дата'] >= start_date]
    filtered = filtered[filtered['Дата'] <= end_date]
    filtered = filtered[filtered["День недели"].isin(week_days) ]
    filtered = filtered[filtered["Время начала"] >= start_time ]
    filtered = filtered[filtered["Время окончания"] <= end_time ]
    filtered = filtered[filtered["Корпус"].isin(buildings) ]
    st.subheader('Количество занятий по дням')
    day_bins = abs((filtered['Дата'].max() - filtered['Дата'].min()).days)+1
    fig = px.histogram(filtered, x="Дата",nbins=day_bins)
    st.plotly_chart(fig)

    max_lessons_1 = math.floor((end_time.hour - start_time.hour)*60/105)
    max_lessons = places[places['Корпус'].isin(buildings)]["Задействовано аудиторий"].sum() * max_lessons_1
    max_lessons
    
    place_load_df = filtered.groupby('Дата',as_index=False)['Корпус'].count().rename(columns={"Корпус":"Занятий"}).sort_values(by='Дата')
    place_load_df['% загрузки'] = (place_load_df['Занятий']/max_lessons)*100
    fig = px.bar(place_load_df, x='Дата', y='% загрузки')
    #fig.update_yaxes(range=[0, 100])
    st.plotly_chart(fig)
    st.write(place_load_df['% загрузки'].describe())

    filtered['Час'] = filtered['Время начала'].apply(lambda x: x.hour)
    place_time_load = filtered.groupby(['Дата','Час'],as_index=False)['Корпус'].count().rename(columns={"Корпус":"Занятий"}).sort_values(by=['Дата','Час'])
    fig = px.density_heatmap(place_time_load, x="Дата", y="Час", z='Занятий', histfunc="sum")
    st.plotly_chart(fig)

if page == "Расписание РУТ":
    week1 = pd.read_csv('week2.csv')
    week2 = pd.read_csv('week1.csv')
    miit = pd.concat([week1,week2])
    miit = miit.rename(columns={"Unnamed: 0":"Пара"})
    miit = miit.drop(columns=['Понедельник','Вторник','Среда','Четверг','Пятница'   ])

    value_vars = ['Понедельник 25 апреля','Вторник 26 апреля','Вторник 26 апреля','Среда 27 апреля','Четверг 28 апреля','Пятница 29 апреля','Суббота 30 апреля','Понедельник 2 мая','Вторник 3 мая','Среда 4 мая','Четверг 5 мая','Пятница 6 мая','Суббота 7 мая']
    miit = pd.melt(miit, id_vars=['Пара'],var_name='Дата', value_name='Занятие')
    miit = miit.replace('<NA>', np.NaN)
    miit = miit.dropna(subset=['Занятие']).reset_index(drop=True)
    miit["День недели"] = miit['Дата'].str.split(" ").apply(lambda x: x[0])
    replaces = ['Понедельник','Вторник','Среда','Четверг','Пятница','Суббота']
    for rep in replaces:
        miit['Дата'] = miit['Дата'].apply(lambda x: x.replace(rep,""))
    miit['Дата'] = miit['Дата'].apply(lambda x: x.replace(" апреля",".04.2022"))
    miit['Дата'] = miit['Дата'].apply(lambda x: x.replace(" мая",".05.2022"))
    miit['Дата'] = pd.to_datetime(miit['Дата'], dayfirst=True) - pd.DateOffset(days=14)
    #miit['Дата'] = miit['Дата'].dt.strftime('%d.%m.%Y')
    miit['Время начала'] = miit['Пара'].str.split("—").apply(lambda x: x[0])
    miit['Время окончания'] = miit['Пара'].str.split("—").apply(lambda x: x[1])
    replaces = ["1 пара","2 пара","3 пара","4 пара","5 пара","6 пара","7 пара","8 пара"," "]
    for rep in replaces:
        miit['Время начала'] = miit['Время начала'].apply(lambda x: x.replace(rep,""))
    miit['Время окончания'] = miit['Время окончания'].apply(lambda x: x.replace(" ",""))
    miit['Время начала'] = pd.to_datetime(miit['Время начала'],format= '%H:%M' )
    miit['Время окончания'] = pd.to_datetime(miit['Время окончания'],format= '%H:%M' )

    miit = miit[miit["Занятие"].str.contains("Аудитория")].reset_index(drop=True)
    miit['Аудитория'] = miit['Занятие'].str.split("Аудитория ").apply(lambda x: x[1])
    miit['Аудитория'] = miit['Аудитория'].str.split(" ").apply(lambda x: x[0])
    miit['Корпус'] = miit['Аудитория'].apply(lambda x: x[0] if len(x)==4 else x[:2])
    def repair_building(building):
        try:
            building = int(building)
            if building <13 or building == 14:
                return str(building)
            return str(building)[0]
        except:
            return str(building)[0]
    #miit['Корпус'] = miit['Корпус'].astype('int32',errors='ignore')
    miit['Корпус'] = miit['Корпус'].apply(repair_building)
    miit = miit.drop(columns=['Пара','Занятие'])
    st.write(miit.shape)
    miit = miit.drop_duplicates()
    st.subheader('Анализ расписания РУТ за 2-ой семестр 2021-2022 учебного года')
    st.subheader('Количество задействованных аудиторий по корпусам')
    places = miit.groupby('Корпус',as_index=False)['Аудитория'].nunique()
    places = places.rename(columns={"Аудитория":"Задействовано аудиторий"})
    places
    st.subheader('Количество проводимых занятий по корпусам за 2 недели')
    lessons = miit.groupby('Корпус',as_index=False)['Аудитория'].count()
    lessons = lessons.rename(columns={"Аудитория":"Количество занятий"})
    lessons
    fig = px.pie(lessons, values='Количество занятий', names='Корпус',title="Количество проводимых занятий по корпусам")
    fig.update_traces(textinfo='percent', textfont_size=20)
    st.plotly_chart(fig)

    buildings = st.multiselect('Корпуса',places['Корпус'].unique(),places['Корпус'].unique())
    start_date = st.date_input("Начало периода",miit['Дата'].min())
    end_date = st.date_input("Конец периода",miit['Дата'].max())
    week_days = st.multiselect('Дни недели',miit['День недели'].unique(),miit['День недели'].unique())
    times = ["8:00","9:40","11:20","13:20","15:00","16:40","18:20","20:00","21:30"]
    start_time_str, end_time_str = st.select_slider(
     'Фильтр по времени проведения занятий',
     options=times,
     value=("8:00", "21:30"))
     
    st.write('Отображаются данные для занятий с ', start_time_str, 'по', end_time_str,'часов')
    start_time = pd.to_datetime(start_time_str,format="%H:%M")
    end_time = pd.to_datetime(end_time_str,format="%H:%M")
    st.write(start_time)
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    filtered = miit[miit['Дата'] >= start_date]
    filtered = filtered[filtered['Дата'] <= end_date]
    filtered = filtered[filtered["День недели"].isin(week_days) ]
    filtered = filtered[filtered["Время начала"] >= start_time ]
    filtered = filtered[filtered["Время окончания"] <= end_time ]
    filtered = filtered[filtered["Корпус"].isin(buildings) ]

    st.subheader('Количество занятий по дням')
    day_bins = abs((filtered['Дата'].max() - filtered['Дата'].min()).days)+1
    fig = px.histogram(filtered, x="Дата",nbins=day_bins)
    st.plotly_chart(fig)

    #max_lessons_1 = math.floor((end_time.hour - start_time.hour)*60/105)
    max_lessons_1 = times.index(end_time_str) - times.index(start_time_str)
    st.write(max_lessons_1)
    max_lessons = places[places['Корпус'].isin(buildings)]["Задействовано аудиторий"].sum() * max_lessons_1
    max_lessons
    
    place_load_df = filtered.groupby('Дата',as_index=False)['Корпус'].count().rename(columns={"Корпус":"Занятий"}).sort_values(by='Дата')
    place_load_df['% загрузки'] = (place_load_df['Занятий']/max_lessons)*100
    fig = px.bar(place_load_df, x='Дата', y='% загрузки')
    #fig.update_yaxes(range=[0, 100])
    st.plotly_chart(fig)
    st.write(place_load_df['% загрузки'].describe())

    filtered['Час'] = filtered['Время начала'].apply(lambda x: x.hour)
    place_time_load = filtered.groupby(['Дата','Час'],as_index=False)['Корпус'].count().rename(columns={"Корпус":"Занятий"}).sort_values(by=['Дата','Час'])
    fig = px.density_heatmap(place_time_load, x="Дата", y="Час", z='Занятий', nbinsy=20, nbinsx=14, histfunc="sum")
    st.plotly_chart(fig)

    st.subheader("Средняя загрузка аудиторий по корпусам за двухнедельный период")
    #lessons['Корпус'] = lessons['Корпус'].astype('str')
    #places['Корпус'] = places['Корпус'].astype('str')
    
    total_df = miit.groupby('Корпус',as_index=False).agg({'Аудитория': 'nunique','Дата':'count'})
    total_df = total_df.rename(columns={"Аудитория":"Количество аудиторий","Дата":"Количество занятий"})
    total_df["% загрузки"] = total_df["Количество занятий"] * 100 / (total_df["Количество аудиторий"] * max_lessons_1 * len(week_days) * 2)
    total_df
