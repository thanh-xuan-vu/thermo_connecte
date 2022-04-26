import streamlit as st
from src import get_temperature
from src import send_email
import datetime
import time

st.set_page_config(layout="wide")
st.header('Température du réfrigérateur - La coop sur mer')
area_1 = st.empty()
area_2 = st.empty() 
area_3 = st.empty() 


while True :
    import random
    t1 = random.choice((1,2,3,5,12))
    alert1 = 10
    unit = '°C'

    if t1 - alert1 < 0 :
        area_1.success('Tout va bien !')
    else :
        area_1.error('Température trop élévée !')

    cols = area_2.columns(4)

    with cols[0] : 
        st.metric(label='Frigo 1', value=str(t1)+unit, 
                    delta=str(t1-alert1)+unit, delta_color='inverse')
        st.metric(label='Frigo 1', value=str(t1)+unit, 
                    delta=str(t1-alert1)+unit, delta_color='inverse')
        st.metric(label='Frigo 1', value=str(t1)+unit, 
                    delta=str(t1-alert1)+unit, delta_color='inverse')

    with cols[2] : 
        st.metric(label='Frigo 1', value=str(t1)+unit, 
                    delta=str(t1-alert1)+unit, delta_color='inverse')
        st.metric(label='Frigo 1', value=str(t1)+unit, 
                    delta=str(t1-alert1)+unit, delta_color='inverse')
        st.metric(label='Frigo 1', value=str(t1)+unit, 
                    delta=str(t1-alert1)+unit, delta_color='inverse')


    with cols[1] : 
        st.metric(label='Frigo 1', value=str(t1)+unit, 
                    delta=str(t1-alert1)+unit, delta_color='inverse')
        st.metric(label='Frigo 1', value=str(t1)+unit, 
                    delta=str(t1-alert1)+unit, delta_color='inverse')
        st.metric(label='Frigo 1', value=str(t1)+unit, 
                    delta=str(t1-alert1)+unit, delta_color='inverse')

    with cols[3] : 
        st.metric(label='Frigo 1', value=str(t1)+unit, 
                    delta=str(t1-alert1)+unit, delta_color='inverse')
        st.metric(label='Frigo 1', value=str(t1)+unit, 
                    delta=str(t1-alert1)+unit, delta_color='inverse')
        st.metric(label='Frigo 1', value=str(t1)+unit, 
                    delta=str(t1-alert1)+unit, delta_color='inverse')
    with area_3.expander(f"Dernière mise-à-jour à {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}. \
            Cliquez ici pour en savoir plus"):
        st.text(
        '''
        La température mesurée par le thermomètre connecté. En dessous de chaque frigo, nous avons la température la plus récente 
        et son écart par rapport aux valeurs d'alerte. Si la couleur de l'écart devient rouge, c.à.d., la température est trop élevée, 
        il faut chercher à le résoudre dès que possible.
        '''
    )
    time.sleep(3)
