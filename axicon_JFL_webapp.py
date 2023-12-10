import PySimpleGUIWeb as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
import base64
from microlens_on_RGP import build_JFL
from parse_JFL import *

def get_img_data(fig, **kwargs):
    """Generate image data using matplotlib's Figure."""
    img = BytesIO()
    fig.savefig(img, format='png', **kwargs)
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode()

# Parse JFL file
base_file_path = 'MCOK001OS.JFL'
segments = parse_jfl_file(base_file_path)

# Define layout
sg.theme('SystemDefault1')
text_size=(25,1)
input_size=(10,1)

layout = [
    [sg.Text('Axicon Height in um',size=text_size), 
     sg.InputText('2.5', key='axicon_height',size=input_size)],
    [sg.Text('Microlens Diameter in mm',size=text_size), 
     sg.InputText('1.1', key='microlens_diameter',size=input_size)],
    [sg.Text('Microlens Radius in mm',size=text_size), 
     sg.InputText('107.4545', key='microlens_R',size=input_size)],
    [sg.Text('Base Lens Front Radius in mm',size=text_size), 
     sg.InputText('236.4', key='base_lens_R',size=input_size)],
    [sg.Text('Base Lens Back Radius in mm',size=text_size), 
     sg.InputText('107.4545', key='base_lens_back_R',size=input_size)],
    [sg.Text('Center Thickness in mm',size=text_size), 
     sg.InputText('0.2', key='center_thickness',size=input_size)],
    [sg.Text('Base Lens Diameter in mm',size=text_size), 
     sg.InputText('10.3', key='base_lens_diameter',size=input_size)],
    [sg.Text('Base Lens Back Diameter in mm',size=text_size), 
     sg.InputText('10.24', key='base_lens_back_diameter',size=input_size)],
    [sg.Button('Plot'), sg.Button('Download JFL File')],
    [sg.Image(key='image_zoom')],
    [sg.Image(key='image_whole')],
]

# Create the Window
window = sg.Window('Microlens App', layout, web_start_browser=True, web_port=8080)

# Event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == 'Plot':
        axicon_height = float(values['axicon_height']) if values['axicon_height'] else 2.5
        microlens_diameter = float(values['microlens_diameter']) if values['microlens_diameter'] else 1.1
        microlens_semi_diameter = microlens_diameter / 2
        microlens_R = float(values['microlens_R']) if values['microlens_R'] else 107.4545
        base_lens_R = float(values['base_lens_R']) if values['base_lens_R'] else 236.4
        base_lens_back_R = float(values['base_lens_back_R']) if values['base_lens_back_R'] else 107.4545
        center_thickness = float(values['center_thickness']) if values['center_thickness'] else 0.2
        base_lens_diameter = float(values['base_lens_diameter']) if values['base_lens_diameter'] else 10.3
        base_lens_semi_diameter=base_lens_diameter/2 
        base_lens_back_diameter = float(values['base_lens_back_diameter'])/2 if values['base_lens_back_diameter'] else 10.24
        base_lens_back_semi_diameter=base_lens_back_diameter/2

        # More parameters...
        base_lens_Q = 0.0
        base_lens_back_Q = 0.0
        whole_lens_semi_diameter = 8
        microlens_Q = 0

        segments_result = build_JFL(
            segments, axicon_height, microlens_semi_diameter, microlens_R,
            base_lens_semi_diameter, base_lens_R, base_lens_Q, center_thickness,
            base_lens_back_semi_diameter, base_lens_back_R, base_lens_back_Q,
            whole_lens_semi_diameter
        )

        # fig, _ = plt.subplots()
        # plot_zoom_jfl_segments(segments_result, 'F', 0, microlens_semi_diameter * 2)
        # 使用您的函数生成图像
        fig_zoom = plot_zoom_jfl_segments(segments_result, 'F', 0, microlens_semi_diameter * 2)
        img_zoom_data = get_img_data(fig_zoom)
        fig_whole=plot_jfl_segments_with_arrows(segments_result, n_arrows=10)
        img_whole_data=get_img_data(fig_whole)

        window['image_zoom'].update(data=img_zoom_data)
        window['image_whole'].update(data=img_whole_data)


        # img_data = get_img_data(fig)
        # window['image'].update(data=img_data)

    elif event == 'Download JFL File':
        JFL_string = build_jfl_string(segments_result)
        with open('axicon.JFL', 'w') as file:
            file.write(JFL_string)
        sg.popup('File Saved', 'The JFL file has been saved as axicon.JFL')

window.close()
