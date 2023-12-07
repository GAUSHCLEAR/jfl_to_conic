import streamlit as st 
from parse_JFL import parse_jfl_file,plot_jfl_segments_with_arrows
from fit import fit_sag_with_multi_standard_surface,sag_of_standard_surface, show_fit_result
import matplotlib.pyplot as plt
import numpy as np

st.markdown("# JFL to Conic Arc")
jfl_file=st.file_uploader("Upload JFL file",type=['jfl'])
if jfl_file is not None:
    jfl_segments=parse_jfl_file(jfl_file,streamlit=True)

    # jfl_plot=plot_jfl_segments_with_arrows(jfl_segments)
    # st.pyplot(jfl_plot)

    # 显示出jfl_segments中的keys，作为选择项
    segment_list=list(jfl_segments.keys())
    segment_list.insert(0,"All")
    segment=st.selectbox("Select segment",segment_list,index=0)
    if segment=="All":
        segment_plot=plot_jfl_segments_with_arrows(jfl_segments)
    else:
        segment_data=jfl_segments[segment]
        segment_plot=plot_jfl_segments_with_arrows({segment:segment_data})
    st.pyplot(segment_plot)



    if segment != "All":
        x_data=jfl_segments[segment][:,0]
        sag_data=jfl_segments[segment][:,1]
        # 按x_data的升序，排序x_data和sag_data
        sort_index=np.argsort(x_data)
        x_data=x_data[sort_index]
        sag_data=sag_data[sort_index]


        N=st.number_input("Number of segments",value=5)
        x_data_min=st.number_input("x min",value=x_data.min())
        x_data_max=st.number_input("x max",value=x_data.max())
        asphere=st.checkbox("Asphere",value=True)

        mask=(x_data>=x_data_min)&(x_data<=x_data_max)

        R_list, conic_list, z0_list,part_x,part_sag=fit_sag_with_multi_standard_surface(x_data[mask],sag_data[mask],N,asphere=asphere,weight_list=[10,8,5])

        for i, r,conic,z0,x in zip(range(N),R_list,conic_list,z0_list,part_x):
            x_min=x.min()
            x_max=x.max()
            ecc=-np.sign(conic)*np.sqrt(np.abs(conic))
            st.write(f"arc {i+1}: \tR=\t{r:.4f},\tecc=\t{ecc:.4f}\tz0=\t{z0:.4f},\tx:\t{x_min:.4f}\t→\t{x_max:.4f},\tconic=\t{conic:.4f}")

        fit_plot=show_fit_result(R_list,conic_list,z0_list,part_x,part_sag,N)
        st.pyplot(fit_plot)
        
