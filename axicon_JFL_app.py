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
layout = [
    [sg.Text('Axicon Height in um'), sg.InputText('2.5', key='axicon_height')],
    [sg.Text('Microlens Diameter in mm'), sg.InputText('1.1', key='microlens_diameter')],
    [sg.Text('Microlens Radius in mm'), sg.InputText('107.4545', key='microlens_R')],
    [sg.Text('Base Lens Front Radius in mm'), sg.InputText('236.4', key='base_lens_R')],
    [sg.Text('Base Lens Back Radius in mm'), sg.InputText('107.4545', key='base_lens_back_R')],
    [sg.Text('Center Thickness in mm'), sg.InputText('0.2', key='center_thickness')],
    [sg.Text('Base Lens Semi Diameter in mm'), sg.InputText('10.3', key='base_lens_semi_diameter')],
    [sg.Text('Base Lens Back Semi Diameter in mm'), sg.InputText('5.12', key='base_lens_back_semi_diameter')],
    [sg.Image(key='image_zoom')],
    [sg.Image(key='image_whole')],
    [sg.Button('Plot'), sg.Button('Download JFL File')]
]

# Create the Window
window = sg.Window('Microlens App', layout, web_start_browser=True, web_port=8080)

# Event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == 'Plot':
        axicon_height = float(values['axicon_height'])
        microlens_diameter = float(values['microlens_diameter'])
        microlens_semi_diameter = microlens_diameter / 2
        microlens_R = float(values['microlens_R'])
        base_lens_R = float(values['base_lens_R'])
        base_lens_back_R = float(values['base_lens_back_R'])
        center_thickness = float(values['center_thickness'])
        base_lens_semi_diameter = float(values['base_lens_semi_diameter']) / 2
        base_lens_back_semi_diameter = float(values['base_lens_back_semi_diameter'])

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
        fig_whole=plot_jfl_segments_with_arrows(segments, n_arrows=10)
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
