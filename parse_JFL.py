import numpy as np
import matplotlib.pyplot as plt
import re

# Function to parse a line into coordinates
# def parse_line_to_coords(line):
#     try:
#         parts = line.split()
#         x = float(parts[1])
#         z = float(parts[3])
#         return (x, z)
#     except (ValueError, IndexError):
#         return None
    
def parse_line_to_coords(line):
    # Regular expression to match both formats of the coordinates
    match = re.search(r'X\s*([\d.]+)\s*Z\s*([\d.]+)', line)
    if match:
        x = float(match.group(1))
        z = float(match.group(2))
        return (x, z)
    else:
        return None

def parse_jfl_file(file_path, streamlit=False):
    if streamlit:
        file_contents = file_path.getvalue().decode('utf-8').splitlines()
    else:
        with open(file_path, 'r') as file:
            file_contents = file.readlines()

    segments = {}
    current_segment = None

    for line in file_contents:
        line = line.strip()
        if line.isalpha():
            current_segment = line
            segments[current_segment] = []
        else:
            coords = parse_line_to_coords(line)
            if coords and current_segment:
                segments[current_segment].append(coords)

    for segment in segments:
        if len(segments[segment]) > 0:
            segments[segment] = np.array(segments[segment])
        # else:
        #     del segments[segment]
    # 删掉空的segment
    segments = {k: v for k, v in segments.items() if len(v) > 0}
    return segments

def plot_jfl_segments_generic(segments):
    plt.figure()

    # Colors for different segments, randomly chosen for each segment
    colors = ['blue', 'green', 'red', 'purple', 'orange', 'pink', 'brown', 'gray', 'olive', 'cyan']

    for i, (segment_label, segment_data) in enumerate(segments.items()):
        if len(segment_data) > 0:  # Plot only if there is data in the segment
            color = colors[i % len(colors)]  # Cycle through colors
            plt.plot(segment_data[:, 0], segment_data[:, 1], c=color, label=f'{segment_label} Segment')

    # Adding labels and title
    plt.xlabel('X Coordinate')
    plt.ylabel('Z Coordinate (Inverted)')
    plt.title('JFL File Segments Visualization')
    plt.legend()
    # Inverting the y-axis
    plt.gca().invert_yaxis()
    # Showing the plot
    plt.show()

def plot_jfl_segments_with_arrows(segments, n_arrows=10):
    plt.figure(figsize=(10, 6))

    colors = ['blue', 'green', 'red', 'purple', 'orange', 'pink', 'brown', 'gray', 'olive', 'cyan']

    for i, (segment_label, segment_data) in enumerate(segments.items()):
        if len(segment_data) > 0:
            color = colors[i % len(colors)]
            plt.plot(segment_data[:, 0], segment_data[:, 1], c=color, label=f'{segment_label} Segment')

            # Adding arrows to the plot
            num_points = len(segment_data)
            if num_points > 1:
                for j in range(1, n_arrows + 1):
                    idx = j * num_points // (n_arrows + 1)  # Calculating the index for the arrow
                    start_point = segment_data[idx - 1]
                    end_point = segment_data[idx]
                    plt.annotate('', xy=(end_point[0], end_point[1]), xytext=(start_point[0], start_point[1]),
                                 arrowprops=dict(arrowstyle="->", color=color))

    plt.xlabel('X Coordinate')
    plt.ylabel('Z Coordinate')
    plt.title('JFL File Segments Visualization with Direction Arrows')
    plt.legend()

    # Inverting the y-axis
    plt.gca().invert_yaxis()

    plt.show()

    return plt 