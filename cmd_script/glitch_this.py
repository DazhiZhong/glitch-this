from PIL import Image
from random import randint
import numpy as np

def glitch_left(start_copy_x, start_copy_y, width, height, start_paste_x, start_paste_y):
    # Grabs a rectange of given width and height from inputarr and shifts it leftwards
    # Any lost pixel data is wrapped back to the right
    """
    Consider an array like so-
    [[ 0,  1,  2,  3],
    [ 4,  5,  6,  7],
    [ 8,  9, 10, 11],
    [12, 13, 14, 15]]
    If we were to left shift the first row only, starting from the 1st index; 
    i.e a rectangle of width = 3, height = 1, start_copy_x = 1, start_copy_y = 0
    We'd grab [1, 2, 3] and left shift it until the start of row
    so it'd look like [[1, 2, 3, 3]]
    Now we wrap around the lost values, i.e 0
    now it'd look like [[1, 2, 3, 0]]
    That's the end result!
    """
    left_chunk = inputarr[start_copy_y : start_copy_y + height, start_copy_x : start_copy_x + width]
    wrap_chunk = inputarr[start_copy_y : start_copy_y + height, 0 : start_copy_x]
    outputarr[start_paste_y : start_paste_y + height, start_paste_x : start_paste_x + width] = left_chunk
    outputarr[start_paste_y : start_paste_y + height, start_paste_x + width : img_width] = wrap_chunk

def glitch_right(start_copy_x, start_copy_y, width, height, paste_x, paste_y):
    # Grabs a rectange of given width and height from inputarr and shifts it leftwards
    # Any lost pixel data is wrapped back to the right
    """ 
    Consider an array like so-
    [[ 0,  1,  2,  3],
    [ 4,  5,  6,  7],
    [ 8,  9, 10, 11],
    [12, 13, 14, 15]]
    If we were to right shift the first row only, starting from the 0th index; 
    i.e a rectangle of width = 3, height = 1, start_copy_x = 0, start_copy_y = 0
    We'd grab [0, 1, 2] and right shift it until the end of row
    so it'd look like [[0, 0, 1, 2]]
    Now we wrap around the lost values, i.e 3
    now it'd look like [[3, 0, 1, 2]]
    That's the end result!
    """
    right_chunk = inputarr[start_copy_y : start_copy_y + height, start_copy_x : start_copy_x + width]
    wrap_chunk = inputarr[start_copy_y : start_copy_y + height, start_copy_x + width : img_width]
    outputarr[paste_y : paste_y + height, paste_x : paste_x + width] = right_chunk
    outputarr[paste_y : paste_y + height, 0 : paste_x] = wrap_chunk

def get_random_channel():
    # Returns a random index from 0 to pixel_tuple_len
    # For an RGB image, a 0th index represents the RED channel
    return randint(0, pixel_tuple_len - 1)

def copy_channel(start_copy_x, start_copy_y, width, height, channel_index):
    # Grabs the specified color channel from a rectangle of given width and height
    """
    Forms a rectangle of given height and width

    Steps through the values in each row, taking only the given channel values

    If channel index was 0 and the image was RGB, only the RED values will 
    be taken
    """
    start_y = start_copy_y
    stop_y = start_y + height
    start_x = (start_copy_x - 1) * pixel_tuple_len + channel_index
    stop_x = start_x + width * pixel_tuple_len
    step_x = pixel_tuple_len
    return inputarr[start_y : stop_y, start_x : stop_x : step_x]

def paste_channel(start_paste_x, start_paste_y, width, height, channel_index, channel_chunk):
    # Pastes the given color channel chunk in a rectangle of given width and height
    """
    Forms a rectangle of given height and width

    Steps through the values in each row, putting only the given channel values 
    from channel_chunk

    If channel index was 0 and the image was RGB, only the RED values will 
    be modified
    """
    start_y = start_paste_y
    stop_y = start_y + height
    start_x = (start_paste_x - 1) * pixel_tuple_len + channel_index
    stop_x = start_x + width * pixel_tuple_len
    step_x = pixel_tuple_len
    outputarr[start_y : stop_y, start_x : stop_x : step_x] = channel_chunk

src_img = Image.open('test.png')
# Fetching image attributes
pixel_tuple_len = len(src_img.getbands())
img_filename = src_img.filename
img_width, img_height = src_img.size
img_mode = src_img.mode

# Creating 3D arrays with pixel data
inputarr = np.asarray(src_img)
outputarr = np.array(src_img)

# Glitching begins here

glitch_amount = 2
max_offset = int((glitch_amount ** 2 / 100) * img_width)
for i in range(0, glitch_amount * 2):
    # Setting up values needed for the randomized glitching
    start_y = randint(0, img_height)
    chunk_height = randint(1, int(img_height / 4))
    chunk_height = min(chunk_height, img_height - start_y)
    current_offset = randint(-max_offset, max_offset)

    if current_offset is 0:
        # Can't wrap left OR right when offset is 0, End of Array
        continue
    if current_offset < 0: 
        # Grab a rectangle of specific width and height and shift it left by a specified offset
        # Wrap around the lost pixel data from the right
        glitch_left(-current_offset, start_y, img_width + current_offset, chunk_height, 0, start_y)
    else:
        # Grab a rectangle of specific width and height and shift it right by a specified offset
        # Wrap around the lost pixel data from the left
        glitch_right(0, start_y, img_width - current_offset, chunk_height, current_offset, start_y)

# Converting 3D array to 2D array, Ex - breaking down [[[R, G, B]....]] to [[R, G, B...]]
inputarr = inputarr.reshape(img_height, -1)
outputarr = outputarr.reshape(img_height, -1)
# row length represents number of elements in each row in the 2D array
row_length = img_width * pixel_tuple_len

# Channel offset for glitched colors
# The start point (x, y) is randomized and the end point is always (img_width, img_height)
channel_chunk_start_x = randint(0, int(img_width / 4))
channel_chunk_width = img_width - channel_chunk_start_x
channel_chunk_start_y = randint(0, int(img_height / 4))
channel_chunk_height = img_height - channel_chunk_start_y

channel_index = get_random_channel()
channel_chunk = copy_channel(channel_chunk_start_x, channel_chunk_start_y, channel_chunk_width, channel_chunk_height, channel_index)
# To ensure that the paste_channel has the same width and height, the start point must not be
# greater than (channel_chunk_start_x, channel_chunk_y) or we will end up running out of slots 
paste_channel(randint(0, channel_chunk_start_x), randint(0, channel_chunk_start_y), channel_chunk_width, channel_chunk_height, channel_index, channel_chunk)

# Converting 2D array back to original 3D array
outputarr = np.reshape(outputarr, (img_height, img_width, pixel_tuple_len))

# Creating glitched image from output array
glitch_img = Image.fromarray(outputarr, img_mode)
glitch_img.save('glitched_{}'.format(img_filename))