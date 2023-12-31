import cv2
import numpy as np
import math
from scipy import fftpack
from scipy.signal import find_peaks
from skimage.draw import line as sk_line

from matplotlib import pyplot as plt

def crop_image(img_path):
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    img_norm = np.uint8(img / np.max(img) * 255)

    th2 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 2)
    th3 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15,2)

    contours, hierarchy = cv2.findContours(~th2, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    outer_contour = max(contours, key=cv2.contourArea)

    # Find the bounding rectangle of the outermost contour
    x, y, w, h = cv2.boundingRect(outer_contour)

    # Crop the image
    cropped_img = img_norm[y:y + h, x:x + w]

    return cropped_img

def band_pass(cropped_img, low_cut=3, high_cut=40, angle_tol=5):
    # Convert to 8-bit
    img_8bit = np.uint8(cropped_img / np.max(cropped_img) * 255)

    # Apply FFT
    img_fft = fftpack.fft2(img_8bit)

    # Shift the zero-frequency component to the center of the spectrum
    img_fft_shift = fftpack.fftshift(img_fft)

    # Create the bandpass filter
    cy, cx = np.indices(cropped_img.shape)
    r = np.sqrt((cx - cx.mean()) ** 2 + (cy - cy.mean()) ** 2)

    # Add x% direction tolerance
    theta = np.arctan2(cy - cy.mean(), cx - cx.mean())
    theta_deg = np.degrees(theta)
    bandpass = np.logical_and(r > low_cut, r < high_cut)
    for angle in range(-angle_tol, angle_tol + 1):
        bandpass |= np.logical_and(theta_deg > angle * 18 - angle_tol, theta_deg < angle * 18 + angle_tol)

    # Autoscale the result
    img_fft_shift_filt = img_fft_shift * bandpass
    img_fft_filt = fftpack.ifftshift(img_fft_shift_filt)
    img_filt = np.real(fftpack.ifft2(img_fft_filt))
    img_filt -= np.min(img_filt)
    img_filt /= np.max(img_filt)
    img_filt = np.uint8(img_filt * 255)

    return img_filt


def hpf_blur(cropped_img):
    hpf = cropped_img - cv2.GaussianBlur(cropped_img, (21, 21), 3)
    hpf = np.uint8(hpf / np.max(hpf) * 255)

    blur_hpf = cv2.GaussianBlur(hpf, (21, 21), 0)
    blur_hpf = np.uint8(blur_hpf / np.max(blur_hpf) * 255)

    return blur_hpf


def sobel_filter(cropped_img, apply_blur=True):
    if apply_blur:
        blur = cv2.GaussianBlur(cropped_img, (7,7), 0)
    else:
        blur = cropped_img

    sobelxy = cv2.Sobel(src=blur, ddepth=cv2.CV_8U, dx=1, dy=1, ksize=5) # Combined X and Y Sobel Edge Detection

    sobelxy_norm = np.uint8(sobelxy / np.max(sobelxy) * 255)

    return sobelxy_norm


def edge_detection(cropped_img, lthresh=100, hthresh=140):
    edges = cv2.Canny(image=cropped_img, threshold1=lthresh, threshold2=hthresh)

    return edges


def estimate_depth(edges, percentile=50):
    # Get image dimensions and center coordinates
    height, width = edges.shape
    center_x, center_y = width // 2, height // 2

    # Define the number of lines and angle step
    num_lines = 360
    angle_step = 2 * np.pi / num_lines

    # Create an array to store the profiles
    profiles = []
    diffs_list = []

    # Loop over the angles of each line
    for i in range(num_lines):
        # Define the angle of the line
        angle = i * angle_step

        # Define the coordinates of the line
        x1 = center_x + int(width * np.cos(angle) / 2)
        y1 = center_y + int(height * np.sin(angle) / 2)

        # Define the line
        line = np.linspace([x1, y1], [center_x, center_y], num=int(np.sqrt(width * 2 + height * 2 / 2.0)))

        # Plot the line
        # plt.plot(line[:, 0], line[:, 1], color='red')

        # Get the gray intensity profile of the line
        profile = []
        for x, y in line:
            if x >= 0 and x < width and y >= 0 and y < height:
                pixel_value = edges[int(y), int(x)]
                if pixel_value != 0:
                    profile.append(math.ceil(pixel_value))

        profile = np.array(profile)
        profiles.append(profile)

        # find peaks and valleys
        peaks, _ = find_peaks(profile)
        valleys, _ = find_peaks(-profile)

        # combine peaks and valleys and sort the array
        pv = np.sort(np.concatenate([peaks, valleys]))

        # calculate absolute difference between consecutive values
        diffs = (np.diff(profile[pv]))

        diffs_list.append(diffs)

    count_list = []
    for diffs in diffs_list:
        #count if the drop is more than 10 gray lives
        count = np.count_nonzero(diffs <=int(0))
        count_list.append(count)
        #Calculate the median of the global minima
        median = np.percentile(count_list, percentile)

    # Get the estimated depth
    depth = math.ceil(median)

    return depth


def estimate_depth_edges(edges, percentile=50):
    # Get image dimensions and center coordinates
    height, width = edges.shape
    center_x, center_y = width // 2, height // 2

    # Define the number of lines and angle step
    num_lines = 360
    angle_step = 2 * np.pi / num_lines

    # Create an array to store the profiles
    count_list = []

    # Loop over the angles of each line
    for i in range(num_lines):
        # Define the angle of the line
        angle = i * angle_step
        ll = np.sqrt((width / 2.0) ** 2 + (height / 2.0) ** 2)

        # Define the coordinates of the line
        x1 = center_x + int(ll * np.cos(angle))
        y1 = center_y + int(ll * np.sin(angle))
        
        if x1 < 0:
            x1 = 0
        elif x1 > width:
            x1 = width
            
        if y1 < 0:
            y1 = 0
        elif y1 > height:
            y1 = height


        # Define the line
        rr, cc = sk_line(y1, x1, center_y, center_x)

        # Get the gray intensity profile of the line 1
        profile = []
        count = 0
        for x, y in zip(cc, rr):
            if x >= 0 and x < width and y >= 0 and y < height:
                pixel_value = edges[int(y), int(x)]
                if pixel_value != 0:
                    count += 1 
        count_list.append(count)

        
    median = np.percentile(count_list, percentile)

    # Get the estimated depth
    depth = math.ceil(median)

    return depth


def complete_depth(img_path, bandpass=True, sobel=False, edge=False, low_cut=3, high_cut=40, angle_tol=5, 
                   lthresh=100, hthresh=140, percentile=60):
    cropped_img = crop_image(img_path)

    if bandpass:
        cropped_img = band_pass(cropped_img, low_cut=low_cut, high_cut=high_cut, angle_tol=angle_tol)
    else:
        cropped_img = hpf_blur(cropped_img)

    if sobel:
        cropped_img = sobel_filter(cropped_img, apply_blur=~bandpass)

    if edge:
        edges = edge_detection(cropped_img, lthresh=lthresh, hthresh=hthresh)
        depth = estimate_depth_edges(edges, percentile)
    else:
        depth = estimate_depth(cropped_img, percentile)

    return depth
