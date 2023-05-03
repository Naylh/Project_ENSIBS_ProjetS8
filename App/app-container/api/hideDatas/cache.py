''' Censor class '''
__name__                = "cache.py"
__date__                = "29.03.23"
__version__             = "1.0.0"
__license__             = "ENSIBS - Cyberlog4"
__copyright__           = "Copyright 2023, S8 Project"
__referent_professor__  = "M. Salah SADOU"
__client__              = "M. Maykel MATTAR"
__credits__             = ["CHAPRON Lucas", "MARCHAND Robin"]

#-----------------------------------#
#                                   #
#              Imports              #
#                                   #
# ----------------------------------#

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import sys, argparse, random

#-----------------------------------#
#                                   #
#            Variables              #
#                                   #
# ----------------------------------# 

EOF_MARKER = '$eof!'
confs = {'RGB':[0,3], 'RGBA':[1,4]}

#-----------------------------------#
#                                   #
#            Functions              #
#                                   #
# ----------------------------------#

def calculate_min_size(number_of_bits):
    """ Calculate the minimum number of pixels needed to store the specified number of bits.

    Args:
        number_of_bits (int): The number of bits to be stored. (1 bit = 1 pixel

    Returns:
        int: The minimum number of pixels needed to store the specified number of bits.
    """
    min_pxls = number_of_bits//3 # 1 pixel = 3 bits stored
    return min_pxls

def get_num_rand(used_pixels, num_of_pixels):
    """ Get a random number between 0 and num_of_pixels, that is not in used_pixels.

    Args:
        used_pixels (set) : The set of numbers that cannot be returned.
        num_of_pixels (int) : The maximum number that can be returned.

    Returns:
        int: A random number between 0 and num_of_pixels, that is not in used_pixels.
    """
    n = random.randint(0, num_of_pixels)
    while n in used_pixels:
        n = random.randint(0, num_of_pixels)
    used_pixels.add(n)
    return n

def hide_data(seed, input_data, output_file, carrier):
    """ hide the input_data inside the carrier image, using the seed as passphrase.
    
    Args:
        seed (int): The passphrase.
        input_data ( str): The data to be hidden.
        output_file (str): The name of the output file.
        carrier (str): The name of the image that will carry the hidden data.
    """
    byte_written = 0
    img = Image.open(carrier, 'r')
    width, height = img.size
    matrix = np.array(list(img.getdata()))
    generator = random.seed(seed)
    used_pixels = set()
    conf = confs[img.mode]
    num_of_pixels = matrix.size//conf[1]
    print("Hiding: ",input_data)
    input_data += EOF_MARKER
    binary_enc = "".join([format(ord(ch), "08b") for ch in input_data])
    min_size = calculate_min_size(len(binary_enc))
    print("Minimum size needed is {} pixels and the carrier has: {}".format(min_size, num_of_pixels))
    if min_size >= num_of_pixels:
        print("ERROR: The image is not big enough to carry the data with the specified passphrase")
        sys.exit(1)
    start_pixel = get_num_rand(used_pixels, num_of_pixels)
    while byte_written != len(input_data):
        bit_i = 0
        while bit_i != 8:
            px = matrix[start_pixel]
            for c in range(conf[0], conf[1]):
                if bit_i == 8:
                    break
                color = matrix[start_pixel][c]
                lsb = color&1
                if lsb != int(binary_enc[(byte_written*8)+bit_i]):
                    color = color>>1 
                    color = color<<1 
                    if lsb == 0: 
                        color = color|1
                    matrix[start_pixel][c] = color
                bit_i += 1
            start_pixel = get_num_rand(used_pixels, num_of_pixels)
        byte_written += 1
        bit_i = 0
        start_pixel = get_num_rand(used_pixels, num_of_pixels)

    out_img = Image.fromarray(np.uint8(matrix.reshape(height, width, conf[1])), img.mode)
    out_img.save(output_file)
    print("All done!")

def retrieve_data(seed, input_file, output_file):
    """Takes a passhprase and an image. Outputs the hidden data inside the image, if any.
    
    Args:
        seed (int): The passphrase.
        input_file (str): The name of the image that contains the hidden data.
        output_file (str): The name of the output file.
    """
    image_file = Image.open(input_file) # Create a new image object from the image file
    img = Image.open(input_file, 'r')
    width, height = img.size
    matrix = np.array(list(img.getdata()))
    conf = confs[img.mode]
    num_of_pixels = matrix.size//conf[1]
    generator = random.seed(seed)
    used_pixels = set()
    start_pixel = get_num_rand(used_pixels, num_of_pixels)
    bit_i = 7
    byte = 0
    message = ""
    end = False
    while (end == False):
        while (bit_i >= 0):
            px = matrix[start_pixel]
            for c in range(conf[0], conf[1]):
                if bit_i >= 0:
                    byte += (px[c]&1)<<bit_i
                    bit_i -= 1
                else:
                    break
            start_pixel = get_num_rand(used_pixels, num_of_pixels)
        if start_pixel>=num_of_pixels:
            break
        message += chr(byte)
        if message[-len(EOF_MARKER):] == EOF_MARKER:
            end = True
        byte = 0
        bit_i = 7
        start_pixel = get_num_rand(used_pixels, num_of_pixels)
    
    if end == False:
        print("Nothing found in this image")
    else:
        print("All done!")
        print("The hidden message is: [{}]".format(message[:len(message)-len(EOF_MARKER)]))
        messages = message[:len(message)-len(EOF_MARKER)].split(";")
        # Print the number of messages
        print("There are {} messages".format(len(messages)))
        
        for m in messages:
            # Print number of messages in the decoded message
            # 50,50,ABC means that the first letter is at 50,50 and the word is ABC
            # Split the message by comma
            m = m.split(",")
            # Get the coordinates
            x_coord = float(m[0])
            y_coord = float(m[1])
            # Get the word
            word = m[2]
            print("\n")
            print("----------------------------------")
            print("The word is: {}".format(word))
            print("----------------------------------")
            print("\n")

            # Print the coordinates
            print("----------------------------------")
            print("The X and Y coordinates are: {}, {}".format(x_coord, y_coord))
            print("----------------------------------")
            # Write each words on the image at the X, Y coordinates retrieved from the message
            # Retrieve the file given in argument after --input_image
            # Open the image and write each words at the X, Y coordinates retrieved from the message
            # Save the image

            draw = ImageDraw.Draw(image_file)
            # Write the word at the X, Y coordinates but we want to center the word
            # Get the width of the word
            width, height = draw.textsize(word)
            # Get the X and Y coordinates of the center of the word
            # I have zoom_x and zoom_y by 3
            # The word is 3 times bigger than the original word
            # Adapt the coordinates to the zoom
            x_coord = x_coord - (width/2)
            y_coord = y_coord - (height/2)
            font = ImageFont.truetype("arial.ttf", 27)

            # Moove the word while the word is not fully contained into a black rectangle behind it
            # The word is not fully contained into a black rectangle behind it
            # then center the word into the rectangle
            while True:
                # Get the coordinates of the rectangle
                # The rectangle is 3 times bigger than the word
                # So we have to divide the coordinates by 3
                # The rectangle is centered on the word
                padding_x = 2
                padding_y = 2
                x1 = x_coord - 3 - padding_x
                y1 = y_coord - 3 - padding_y
                x2 = x_coord + width + 3 + padding_x
                y2 = y_coord + height + 3 + padding_y
                # Get the pixels of the rectangle
                # The rectangle is 3 times bigger than the word
                # So we have to divide the coordinates by 3
                # The rectangle is centered on the word
                pixels = image_file.crop((x1, y1, x2, y2))
                # Get the pixels of the rectangle as a list
                pixels = list(pixels.getdata())
                # Get the number of black pixels in the rectangle
                black_pixels = pixels.count((0, 0, 0))
                # Get the number of pixels in the rectangle
                total_pixels = len(pixels)
                # If the number of black pixels is equal to the number of pixels in the rectangle
                # The word is fully contained into a black rectangle behind it
                if black_pixels == total_pixels:
                    # We can write the word
                    break
                # If the word is not fully contained into a black rectangle behind it
                # We have to moove the word
                # Moove the word to the right
                x_coord += 2
                # Moove the word to the bottom
                y_coord += 2
                # Center the word into the rectangle
            # Write the word
            x_coord += padding_x
            y_coord += padding_y
            draw.text((x_coord-2, y_coord-15), word, (255, 255, 255), font=font)

            image_file.save(output_file) # Save the image
            print("\n")
            print("Création de l'image {}...".format(output_file))
            print("\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="Le mode dans lequel vous voulez exécuter le programme : enc ou dec")
    parser.add_argument("seed", help="La graine utilisée pour coder/décoder les données.")
    parser.add_argument("--input_data", help="Le nom de chemin des données que vous voulez cacher. Doit être ASCII.")
    parser.add_argument("--input_image", help="Le nom de chemin de l'image qui contient les données cachées")
    parser.add_argument("--output", help="Nom du fichier de sortie")
    parser.add_argument("--carrier", help="Le nom de chemin de l'image qui sera utilisée comme support")
    args = parser.parse_args()
    if args.mode == 'enc':
        if args.input_data == None or args.output == None or args.carrier == None:
            print("ERREUR: Argument manquant!")
            print(parser.print_help())
            sys.exit(1)
        hide_data(args.seed, args.input_data, args.output, args.carrier)
    elif args.mode == 'dec':
        if args.input_image == None or args.output == None:
            print("ERREUR: Argument manquant!")
            print(parser.print_help())
            sys.exit(1)
        retrieve_data(args.seed, args.input_image, args.output)
