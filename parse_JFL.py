import numpy as np
import matplotlib.pyplot as plt
import re
import copy

def parse_line_to_coords_refactored(line):
    # Regular expression to match the format of the coordinates (including the optional W coordinate)
    match = re.search(r'X\s*([\d.]+)\s*Z\s*([\d.]+)(?:\s*W\s*([\d.-]+))?', line)
    if match:
        x = float(match.group(1))
        z = float(match.group(2))
        # Check if W coordinate is present
        w = float(match.group(3)) if match.group(3) else None
        return (x, z, w) if w is not None else (x, z)
    else:
        return None
    
def parse_line_to_coords(line):
    # Regular expression to match the format of the coordinates (including the optional W coordinate)
    match = re.search(r'X\s*([\d.]+)\s*Z\s*([\d.]+)(?:\s*W\s*([\d.-]+))?', line)
    if match:
        x = float(match.group(1))
        z = float(match.group(2))
        # Check if W coordinate is present
        w = float(match.group(3)) if match.group(3) else None
        return (x, z, w) if w is not None else (x, z)
    else:
        return None
    
def parse_jfl_file_refactored(file_path):
    with open(file_path, 'r') as file:
        file_contents = file.readlines()

    segments = {}
    current_segment = None
    is_three_coordinate_data = False

    for line in file_contents:
        line = line.strip()
        if line.startswith("*"):  # Check for the three-coordinate data marker
            is_three_coordinate_data = True
        elif line.isalpha():  # New segment
            current_segment = line
            segments[current_segment + "_XZ"] = []  # Initialize two-coordinate data list
            segments[current_segment + "_XZW"] = []  # Initialize three-coordinate data list
            is_three_coordinate_data = False
        else:
            coords = parse_line_to_coords_refactored(line)
            if coords and current_segment:
                if is_three_coordinate_data and len(coords) == 3:  # Three-coordinate data
                    segments[current_segment + "_XZW"].append(coords)
                elif len(coords) == 2:  # Two-coordinate data
                    segments[current_segment + "_XZ"].append(coords)

    # Convert lists to numpy arrays and remove empty segments
    for segment in list(segments.keys()):
        if len(segments[segment]) > 0:
            segments[segment] = np.array(segments[segment])
        else:
            del segments[segment]

    return segments


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

def plot_zoom_jfl_segments(segments,segment_name,x_min,x_max):
    fig=plt.figure()
    segment_data=segments[segment_name]
    index=np.where(np.logical_and(segment_data[:,0]>=x_min,segment_data[:,0]<=x_max))[0]
    plt.plot(segment_data[index, 0], segment_data[index, 1], label=f'{segment_name} Segment')
    plt.xlim(x_min,x_max)
    # plt.ylim(-0.5,0.5)

    # Adding labels and title
    plt.xlabel('X Coordinate')
    plt.ylabel('Z Coordinate (Inverted)')
    plt.title(f'Segment zoom in {segment_name}')
    plt.legend()
    # Inverting the y-axis
    plt.gca().invert_yaxis()
    # Showing the plot
    # plt.show()
    return fig 


def plot_jfl_segments_with_arrows(segments, n_arrows=10):
    fig=plt.figure()

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

    # plt.show()

    return fig 

def translate_segment(segments, segment_name, x_min, x_max, target_Z, head="max"):
    '''
    Translate a specified segment along the Z-axis.

    Args:
    segments (dict): Dictionary of segments with coordinates.
    segment_name (str): Name of the segment to edit.
    x_min, x_max (float): Range of X coordinates to apply the translation.
    target_Z (float): Target Z coordinate for translation.    
    '''
    if segment_name not in segments:
        print(f"Segment {segment_name} not found.")
        return
    segments_copy = copy.deepcopy(segments)
    segment=segments_copy[segment_name]
    if head=="max":
        index=np.where(np.logical_and(segment[:,0]>=x_min,segment[:,0]<=x_max))[0][-2]
    elif head=="min":
        index=np.where(np.logical_and(segment[:,0]>=x_min,segment[:,0]<=x_max))[0][0]
    delta_Z=target_Z-segment[index][1]
    # print(f"index={index}")
    # print(f"delta_Z={delta_Z}")

    change_point_count=0
    for i, (x, z) in enumerate(segment):
        if head=="max":
            if x_min < x <= x_max:
                segment[i] = (x, z + delta_Z)            
                change_point_count+=1
        elif head=="min":
            if x_min <= x < x_max:
                segment[i] = (x, z + delta_Z)            
                change_point_count+=1
    print(f"Segment {segment_name} translated successfully.")
    return segments_copy

def replace_segment(segments, segment_name, x_min, x_max, new_Z):
    '''
    Replace the Z-coordinate of a specified segment without altering the original segments.

    Args:
    segments (dict): Dictionary of segments with coordinates.
    segment_name (str): Name of the segment to edit.
    x_min, x_max (float): Range of X coordinates to apply the replacement.
    new_Z (list or numpy array): New values for Z coordinate for replacement.
    '''
    # Create a deep copy of the segments to avoid modifying the original
    segments_copy = copy.deepcopy(segments)

    if segment_name not in segments_copy:
        print(f"Segment {segment_name} not found.")
        return

    # Ensure new_Z is iterable and has the right number of elements
    if not hasattr(new_Z, '__iter__'):
        print("new_Z must be a list or numpy array.")
        return

    segment = segments_copy[segment_name]
    replace_indices = [i for i, (x, _) in enumerate(segment) if x_min <= x <= x_max]

    if len(replace_indices) != len(new_Z):
        print("Length of new_Z does not match the number of points in the segment to be replaced.")
        return

    for i, new_z in zip(replace_indices, new_Z):
        segment[i] = (segment[i][0], new_z)

    print(f"Segment {segment_name} replaced successfully.")
    return segments_copy

def find_x_in_range(segments, segment_name, x_min, x_max):
    if segment_name not in segments:
        print(f"Segment {segment_name} not found.")
        return
    else:
        segment = segments[segment_name]

    x = np.array(segment)[:, 0]
    x_filtered = x[(x >= x_min) & (x <= x_max)]
    return x_filtered


def build_jfl_string(segments, three_coord_marker="*S015A000"):
    header = """MCG
GSH003
Jobnumber
8/29/2023 2:34:15 PM
1
C:
L1021
L1021
MY_OK
OK1
Chuck1
1
2
FC
AC
"""
    footer = 'Q'
    content = header
    for segment_name, coords in segments.items():
        # Determine if the segment is for two-coordinate or three-coordinate data
        if segment_name.endswith("_XZ"):
            # Two-coordinate data (XZ)
            content += segment_name[:-3] + '\n'  # Remove '_XZ' from segment name
            for x, z in coords:
                content += f'X {x:012.9f} Z {z:012.9f}\n'
        elif segment_name.endswith("_XZW"):
            # Three-coordinate data (XZW)
            content += three_coord_marker + '\n'
            # content += segment_name[:-4] + '\n'  # Remove '_XZW' from segment name
            for x, z, w in coords:
                content += f'X {x:012.9f} Z {z:012.9f} W {w:012.9f}\n'
        else: 
            content += segment_name + '\n' 
            for x, z in coords:
                content += f'X {x:012.9f} Z {z:012.9f}\n'

    content += footer
    return content


def save_jfl_file(segments, file_path,three_coord_marker="*S015A000"):
    '''
    Save the modified segments back into a JFL file in the specified format.
    
    Args:
    segments (dict): Dictionary of segments with coordinates.
    file_path (str): Path to save the modified JFL file.
    '''
    with open(file_path, 'w') as file:
        file.write(build_jfl_string(segments,three_coord_marker=three_coord_marker))
    print(f"File saved successfully to {file_path}")
