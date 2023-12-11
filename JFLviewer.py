import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from parse_JFL import *
import re

# Function to parse JFL file
# def parse_jfl_file(file_path):
#     with open(file_path, 'r') as file:
#         file_contents = file.readlines()

#     segments = {}
#     current_segment = None

#     for line in file_contents:
#         line = line.strip()
#         if line.isalpha():
#             current_segment = line
#             segments[current_segment] = []
#         else:
#             coords = parse_line_to_coords(line)
#             if coords and current_segment:
#                 segments[current_segment].append(coords)

#     for segment in segments:
#         if len(segments[segment]) > 0:
#             segments[segment] = np.array(segments[segment])
#     return segments

# # Function to parse a line to coordinates
# def parse_line_to_coords(line):
#     match = re.search(r'X\s*([\d.]+)\s*Z\s*([\d.]+)', line)
#     if match:
#         x = float(match.group(1))
#         z = float(match.group(2))
#         return (x, z)
#     else:
#         return None

# # Function to plot JFL file with arrows (needs to be defined based on your requirement)
# def plot_jfl_segments_with_arrows(segments):
#     plt.figure()
#     colors = ['blue', 'green', 'red', 'purple', 'orange', 'pink', 'brown', 'gray', 'olive', 'cyan']
#     for i, (segment_label, segment_data) in enumerate(segments.items()):
#         if len(segment_data) > 0:
#             color = colors[i % len(colors)]
#             plt.plot(segment_data[:, 0], segment_data[:, 1], c=color, label=f'{segment_label} Segment')
#             # Add arrows here as per the requirements
#             # Example: plt.arrow(...)
#     plt.xlabel('X Coordinate')
#     plt.ylabel('Z Coordinate')
#     plt.title('JFL File Visualization with Arrows')
#     plt.legend()
#     return plt.gcf()

# GUI Layout
layout = [
    [sg.Text('Select JFL File'), sg.Input(), sg.FileBrowse(key='file')],
    [sg.Button('Plot'), sg.Button('Exit')]
]

# Create the Window
window = sg.Window('JFL Viewer', layout)

# Event Loop
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == 'Plot':
        file_path = values['file']
        if file_path:
            segments = parse_jfl_file(file_path)
            fig = plot_jfl_segments_with_arrows(segments)
            # Display the plot
            plt.show()

window.close()
