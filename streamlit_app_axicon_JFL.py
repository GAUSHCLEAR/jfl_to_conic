import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from microlens_on_RGP import build_JFL
from parse_JFL import * 

base_file_path = 'MCOK001OS.JFL'  
segments = parse_jfl_file(base_file_path)

col1,col2=st.columns(2)
axicon_hight_in_um=col1.number_input('axicon hight in um',value=2.5)
microlens_diameter=col1.number_input('microlens diameter in mm',value=1.1)
microlens_semi_diameter = microlens_diameter/2
microlens_R=col1.number_input('microlens Radius in mm',value=107.4545)
base_lens_R=col2.number_input('base lens front Radius in mm',value=236.4)
base_lens_back_R=col2.number_input('base lens back Radius in mm',value=107.4545)
center_thickness=col2.number_input('center thickness in mm',value=0.2)

with st.expander('other parameters'):

    base_lens_diameter=st.number_input('base lens semi diameter in mm',value=5.15*2)
    base_lens_semi_diameter=base_lens_diameter/2
    base_lens_Q=st.number_input('base lens Q',value=0.0)
    base_lens_back_semi_diameter=st.number_input('base lens back semi diameter in mm',value=5.12)
    base_lens_back_Q=st.number_input('base lens back Q',value=0.0)

    microlens_Q=0
    whole_lens_semi_diameter=8

segments_result=build_JFL(segments,
        axicon_hight_in_um,
        microlens_semi_diameter,
        microlens_R,
        base_lens_semi_diameter,
        base_lens_R,
        base_lens_Q,
        center_thickness,
        base_lens_back_semi_diameter,
        base_lens_back_R,
        base_lens_back_Q,
        whole_lens_semi_diameter
        )
JFL_string=build_jfl_string(segments_result)
st.pyplot(plot_zoom_jfl_segments(segments_result,'F',0,microlens_semi_diameter*2))
st.pyplot(plot_jfl_segments_with_arrows(segments_result))
download=st.download_button('Download JFL file',data=JFL_string,file_name='axicon.JFL',mime='text/plain')