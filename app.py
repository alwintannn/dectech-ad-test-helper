import numpy as np
import cv2
import streamlit as st
import math
import io
import base64
import shutil
import os
from os import listdir
from os.path import isfile, join
from PIL import Image
from PIL import ImageFilter
from shapely.geometry import Point
from shapely.geometry import Polygon


def take_screenshots(filename, screenshot_n):
    # capture video with opencv
    cap = cv2.VideoCapture(filename)

    # capture details of the video
    frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    # fps = frames / video_in_sec
    video_in_sec = frames/fps
    st.text("Video Duration: " + str(video_in_sec))
    screenshot_frame = math.ceil(video_in_sec / screenshot_n * fps)

    # take screenshots
    # success,image = cap.read()
    count = 0
    success = True
    black_frame_this = False
    black_frame_last = False

    while success:
        # vidObj object calls read
        # function extract frames
        success, image = cap.read()

        if success:
            if image.mean() < 1:
                black_frame_this = True
            else:
                black_frame_this = False

            # print(count, count%screenshot_frame == 0)

            if black_frame_last is False:

                if count % screenshot_frame == 0 and black_frame_this is False:
                    cv2.imwrite('screenshots_temp/' + f'{count:05}_' + '.jpg', image)
                    # st.text('successfully wrote a frame:' + str(count))

                elif black_frame_this is True:
                    black_frame_last = True

            if black_frame_last is True:
                if black_frame_this is False:
                    cv2.imwrite('screenshots_temp/' + f'{count:05}_' + '.jpg', image)
                    # st.text('successfully wrote a frame:' + str(count))
                    black_frame_last = False

                elif black_frame_this is True:
                    black_frame_last = True

            count += 1


def combine_screenshots():
    # get all screenshot files
    list_im = [f for f in listdir('screenshots_temp') if isfile(join('screenshots_temp', f))]
    list_im.sort()
    imgs = [Image.open('screenshots_temp/'+i) for i in list_im]

    # pick the image which is the smallest, and resize the others to match it
    # (can be arbitrary image shape here)
    min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
    imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))

    # shrink and save the combined image
    imgs_comb = Image.fromarray(imgs_comb)
    # width, height = imgs_comb.size
    imgs_comb.thumbnail((1600, 60), Image.ANTIALIAS)
    imgs_comb.save('screenshots_combined/' + output_filename + '.jpg')

    # for a vertical stacking it is simple: use vstack
    # imgs_comb = np.vstack( (np.asarray( i.resize(min_shape) ) for i in imgs))
    # imgs_comb = PIL.Image.fromarray( imgs_comb)
    # imgs_comb.save( 'Trifecta_vertical.jpg')


def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href


def cut_image(region, im):
    pixels = np.array(im)
    im_copy = np.array(im)

    for index, pixel in np.ndenumerate(pixels):
        # Unpack the index.
        row, col, channel = index
        # We only need to look at spatial pixel data for one of the four channels.
        if channel != 0:
            continue
        point = Point(row, col)
        if not region.contains(point):
            im_copy[(row, col, 0)] = 255
            im_copy[(row, col, 1)] = 255
            im_copy[(row, col, 2)] = 255
            im_copy[(row, col, 3)] = 0

    cut_im = Image.fromarray(im_copy)

    return(cut_im)


def blur(img, blur_radius=0.1):
    blurred = img.copy().filter(ImageFilter.GaussianBlur(radius=blur_radius))
    blurred = np.asarray(blurred)

    return blurred


def dectech_blur(im, l, section):

    # set greyed out section ratio
    ratio_grey = 0.18

    # set up points
    o = (l/2, l/2)
    a = (0, 0)
    b = (0, l/2)
    c = (0, l)
    d = (l, l)
    e = (l, 0)
    f = ((1+math.tan(math.radians(30))) * l/2, l)
    g = (l, (1-math.tan(math.radians(20))) * l/2)
    h = ((1+math.tan(math.radians(10))) * l/2, 0)
    i = (0, (1-math.tan(math.radians(40))) * l/2)

    path = {
        "lm": ([o, b, c, f], [b, o, f, d, e, a]),
        "em": ([o, f, d, g], [o, g, e, a, c, f]),
        "in": ([o, g, e, a, i],  [o, i, c, d, g]),
        "im": ([o, i, b], [o, b, c, d, e, a, i])
    }

    rotation_angle = {
        "lm": 60,
        "em": 160,
        "in": 260,
        "im": 340
    }

    region1 = Polygon(path[section][0])
    region2 = Polygon(path[section][1])

    # cut images into focus and greyed out sections
    im_focus = cut_image(region1, im)
    im_grey = cut_image(region2, im)

    # shrink and blur greyed out section
    size = l*ratio_grey, l*ratio_grey
    im_grey.thumbnail(size, Image.ANTIALIAS)
    im_grey_bl = im_grey.filter(ImageFilter.GaussianBlur(radius=3))

    # combine two sections together
    im_new = Image.new('RGBA', (l, l), (255, 255, 255, 0))
    im_new.paste(im_grey_bl, (int(l/2*(1-ratio_grey)), int(l/2*(1-ratio_grey)))) # need to shift the greyout chart so they match
    im_new.paste(im_focus, (0, 0), im_focus)

    # rotate image
    output_im = im_new.rotate(rotation_angle[section], resample=Image.BICUBIC, expand=True)

    # crop image
    image_data = np.asarray(output_im)
    image_data_bw = image_data.max(axis=2)
    non_empty_columns = np.where(image_data_bw.max(axis=0) > 0)[0]
    non_empty_rows = np.where(image_data_bw.max(axis=1) > 0)[0]
    cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))
    image_data_new = image_data[cropBox[0]:cropBox[1]+1, cropBox[2]:cropBox[3]+1, :]
    output_im_crop = Image.fromarray(image_data_new)

    return(output_im_crop)


# App
# Suppress deprecation reminder
st.set_option('deprecation.showfileUploaderEncoding', False)
# Title
st.title("Ad Test Deck Helper")
st.info("Version 1.0")
st.info("Please follow the instructions in the sidebar to use the helper app.")

# Sidebar (Storyboard Generator)
st.sidebar.title("Storyboard Generator")
uploaded_video = st.sidebar.file_uploader("Select video...", type=["mp4"])
if st.sidebar.button("Preview video"):
    video_file = open('video_temp/temp.mp4', 'rb')
    video_bytes = video_file.read()
    st.video(video_bytes)
screenshot_n = st.sidebar.slider("Number of screenshots:", 1, 50, 30)
output_filename = st.sidebar.text_input("Output filename (e.g. JustEat_Storyboard):")
if output_filename == "":
    output_filename = "Unnamed"

# Temporarily store the uploaded video
temporary_location = False

if uploaded_video is not None:
    g = io.BytesIO(uploaded_video.read())  # BytesIO Object
    temporary_location = "video_temp/temp.mp4"

    with open(temporary_location, 'wb') as out:  # Open temporary file as bytes
        out.write(g.read())  # Read bytes into file

    # close file
    out.close()

# Run code that generate the storyboard
if st.sidebar.button("Generate storyboard"):

    st.info("Processing video...")
    st.info("Generating " + str(screenshot_n) + " screenshots...")
    st.spinner('Wait for it...')

    # Remove the previous images in the screenshots_temp folder
    folder = 'screenshots_temp'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    # Take screenshots
    take_screenshots("video_temp/temp.mp4", screenshot_n)
    # Combine screenshots to generate storyboard
    combine_screenshots()

    st.success('Done!')
    st.balloons()

    # Download the storyboard
    st.markdown(get_binary_file_downloader_html('screenshots_combined/' + output_filename + '.jpg', "Storyboard"), unsafe_allow_html=True)

# Sidebar (Radial Bar Chart)
st.sidebar.title("Radial Bar Chart Generator")
uploaded_chart = st.sidebar.file_uploader("Select the full radial bar chart...", type=["png", "jpg"])
output_filename_chart = st.sidebar.text_input("Output filename (e.g. JustEat):")
if output_filename_chart == "":
    output_filename_chart = "Unnamed"

# Temporarily store the uploaded video
temporary_location = False

if uploaded_chart is not None:
    g = io.BytesIO(uploaded_chart.read())  # BytesIO Object
    temporary_location = "chart_temp/temp.png"

    with open(temporary_location, 'wb') as out:  # Open temporary file as bytes
        out.write(g.read())  # Read bytes into file

    # close file
    out.close()

# Run code that generate the bar charts
if st.sidebar.button("Generate separate bar charts"):
    st.info("Processing bar chart... This may take a minute.")
    metrics = ["lm", "em", "in", "im"]

    percent_complete = 0
    my_bar = st.progress(percent_complete)
    for metric in metrics:
        percent_complete += 25
        my_bar.progress(percent_complete)
        im = Image.open("chart_temp/" + "temp.png").convert('RGBA')  # read the overall chart
        im_new = dectech_blur(im, 600, metric)  # do the Dectech Blur
        im_new.save("chart_temp/" + output_filename_chart + metric + ".png")  # save the output chart for each section

    st.success('Done!')
    st.balloons()

    # Download the separate bar charts
    st.markdown(get_binary_file_downloader_html('chart_temp/' + output_filename_chart + 'lm.png', "Lasting Impression"), unsafe_allow_html=True)
    st.markdown(get_binary_file_downloader_html('chart_temp/' + output_filename_chart + 'em.png', "Emotion"), unsafe_allow_html=True)
    st.markdown(get_binary_file_downloader_html('chart_temp/' + output_filename_chart + 'in.png', "Information"), unsafe_allow_html=True)
    st.markdown(get_binary_file_downloader_html('chart_temp/' + output_filename_chart + 'im.png', "Impact"), unsafe_allow_html=True)
