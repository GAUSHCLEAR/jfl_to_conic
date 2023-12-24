import streamlit as st
from microlens_on_RGP import * 
from parse_JFL import *

def conic_input(c,id):
    col1,col2,col3=c.columns(3)
    R=col1.number_input("R",value=7.8,key=f"conic_R_{id}")
    Q=col2.number_input("Q",value=0.0,key=f"conic_Q_{id}")
    semi_diameter=col3.number_input("semiDiameter",value=7.8,key=f"conic_semi_diameter_{id}")
    return R,Q,semi_diameter
def odd_asphere_input(c,id):
    col1,col2,col3=c.columns(3)
    R=col1.number_input("",value=0.0,key=f"odd_asphere_R_{id}")
    Q=col2.number_input("",value=0.0,key=f"odd_asphere_Q_{id}")
    semi_diameter=col3.number_input("",value=0.0,key=f"odd_asphere_semi_diameter_{id}")
    N=c.number_input("N",value=3,key=f"odd_asphere_N_{id}")
    col=c.columns(N)
    a_list=[]
    for i in range(N):
        a=col[i].number_input("",value=0.0,key=f"odd_asphere_a_{id}_{i}")
        a_list.append(a)

    return R,Q,semi_diameter,N,a_list
def horizontal_line_input(c,id):
    semi_diameter=c.number_input("",value=0.0,key=f"horizontal_line_semi_diameter_{id}")
    return semi_diameter   

def cirle_input(c,id):
    col1,col2,col3=c.columns(3)
    R=col1.number_input("R",value=1,key=f"circle_R_{id}")
    semi_diameter=col3.number_input("semiDiameter",value=7.8,key=f"circle_semi_diameter_{id}")
    return R,semi_diameter 

function_list=[
    "conic",
    "odd asphere",
    "horizontal line"
    ]

st.markdown("# RGP design")
st.markdown("## lens parameters") 
lens_diameter=st.number_input("镜片直径",value=14.0,key="lens_diameter")
center_thickness=st.number_input("中心厚度",value=0.2,key="center_thickness") 
front_seg_num=st.number_input("前表面有多少段弧？",min_value=1,max_value=10,value=2,step=1,key="front_seg_num")
back_seg_num=st.number_input("后表面有多少段弧？",min_value=1,max_value=10,value=2,step=1,key="back_seg_num")

st.markdown("## 前表面")
for i in range(front_seg_num):
    front_seg_type=st.selectbox("前表面第"+str(i+1)+"段弧的类型",function_list,key="front_seg_type"+str(i))
    if front_seg_type=="conic":
        id="front_seg"+str(i)
        R,Q,semi_diameter=conic_input(st,id)
    elif front_seg_type=="odd asphere":
        id="front_seg"+str(i)
        R,Q,semi_diameter,N,a_list=odd_asphere_input(st,id)
    elif front_seg_type=="horizontal line":
        id="front_seg"+str(i)
        semi_diameter=horizontal_line_input(st,id)
st.markdown("### 前表面进退刀")


st.markdown("## 后表面")
for i in range(back_seg_num):
    back_seg_type=st.selectbox("后表面第"+str(i+1)+"段弧的类型",function_list,key="back_seg_type"+str(i))
    if back_seg_type=="conic":
        id="back_seg"+str(i)
        R,Q,semi_diameter=conic_input(st,id)
    elif back_seg_type=="odd asphere":
        id="back_seg"+str(i)
        R,Q,semi_diameter,N,a_list=odd_asphere_input(st,id)
    elif back_seg_type=="horizontal line":
        id="back_seg"+str(i)
        semi_diameter=horizontal_line_input(st,id)
