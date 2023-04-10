''' Main class '''
__name__                = "app.py"
__date__                = "29.03.23"
__version__             = "1.0.0"
__license__             = "ENSIBS - Cyberlog4"
__copyright__           = "Copyright 2023, S8 Project"
__referent_professor__  = "M. Salah SADOU"
__client__              = "M. Maykel MATTAR"
__credits__             = ["CHAPRON Lucas", "COUTAND Bastien", "MARCHAND Robin"]

#-----------------------------------#
#                                   #
#              Imports              #
#                                   #
# ----------------------------------#   

from fastapi import FastAPI, HTTPException, Request, File, UploadFile, Form
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from PIL import Image, ImageDraw

from .hideDatas.cache import hide_data, retrieve_data

import fitz
import hashlib
import json
import os
import shutil

#-----------------------------------#
#                                   #
#            Variables              #
#                                   #
# ----------------------------------#   

templates = Jinja2Templates(directory="api/templates")
app = FastAPI(title=__name__, docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory="static"), name="static")

BASE_DIR = os.path.dirname((os.path.abspath(__file__)))
DOWNLOAD_DIR = os.path.join(BASE_DIR, r"../download")
UPLOAD_DIR = os.path.join(BASE_DIR, r"../upload")

global list_roles
list_roles = []
global dict_words_with_roles
dict_words_with_roles = {}

#-----------------------------------#
#                                   #
#              Routes               #
#                                   #
# ----------------------------------#

@app.get("/")
async def index(request:Request):
    """Route which allows to access the index page

    Args:
        request (Request): request

    Returns:
        templates.TemplateResponse: the index page
    """
    dict_words_with_roles.clear()
    list_roles.clear()
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/obfuscation")
async def obfuscation(request:Request):
    """Route which allows to access the obfuscation page

    Args:
        request (Request): request

    Returns:
        templates.TemplateResponse: the obfuscation page 
    """
    dict_words_with_roles.clear()
    list_roles.clear()
    return templates.TemplateResponse("obfuscation.html", {"request": request})


@app.get("/help")
async def help(request:Request):
    """Route which allows to access the help page

    Args:
        request (Request): request

    Returns:
        templates.TemplateResponse: the help page
    """
    dict_words_with_roles.clear()
    list_roles.clear()
    return templates.TemplateResponse("help.html", {"request": request})


@app.get("/{path:path}")
async def redirect(request: Request, path: str):
    """Other routes redirect to the index
    
    Args:
        request (Request): request
        
    Returns:
        RedirectResponse: redirect to the index or to the obfuscation page
    """
    if os.path.exists("download"):
        for file in os.listdir("download"):
            os.remove(f'download/{file}')
    if os.path.exists("upload"):
        for file in os.listdir("upload"):
            os.remove(f'upload/{file}')
    dict_words_with_roles.clear()
    list_roles.clear()
    if path == "index":
        return RedirectResponse(url = "/")
    elif path == "obfuscation":
        return RedirectResponse(url = "/obfuscation")
    else:
        return RedirectResponse(url = "/")

#-----------------------------------#
#                                   #
#          Index's routes           #
#                                   #
# ----------------------------------#

#check taille fichier
@app.post("/uploadfile_index")
async def create_upload_file_index(input_file: UploadFile = File(...)):
    """Route which allows to upload a file and save it in the upload folder
    
    Args:
        input_file (UploadFile): file to put in the upload folder

    Raises:
        HTTPException: if there is no file
        HTTPException: if the file is not a png
        HTTPException: if there is a problem when reading the file
        HTTPException: if the file is too big
        HTTPException: if it is not possible to put the file in the upload folder
    """
    if input_file == None:
        raise HTTPException(status_code = 400, detail = "Fichier non fourni, uploadez un fichier")
    if input_file.content_type != "image/png":
        raise HTTPException(status_code = 400, detail = "Fichier fourni non pris en charge, utilisez uniquement un fichier png")
    # try :
    #     fs = await input_file.read()
    # except :
    #     raise HTTPException(status_code = 500, detail = "Quelque chose s'est mal passé lors de la lecture du fichier, veuillez réessayer")
    # if len(fs) > 20000000:
    #     raise HTTPException(status_code = 400, detail = "Fichier fourni trop volumineux, utilisez un fichier de moins de 20Mo")
    try: 
        if not os.path.exists("upload"):
            os.makedirs("upload")
        if os.listdir("upload"):
            for file in os.listdir("upload"):
                os.remove(f'upload/{file}')
        with open(f'{input_file.filename}', 'wb') as buffer:
            shutil.copyfileobj(input_file.file, buffer)
        buffer.close()
        shutil.move(f'{input_file.filename}', f'upload/{input_file.filename}')
    except :
        raise HTTPException(status_code = 500, detail = "Quelque chose s'est mal passé lors de l'upload du fichier, veuillez réessayer")
    
@app.post("/createunlockfile_index")
async def create_download_file_index(passphrase_file : str = Form(...)):
    """Route which try to find and write the hidden data if the passphrase is correct

    Args:
        passphrase_file (str, optional): The passphrase to find the hidden data.

    Raises:
        HTTPException: if the passphrase is empty
        HTTPException: if there is not hidden data to find

    Returns:
        FileResponse: the file which is in the download folder
    """
    if not os.path.exists("download"):
        os.makedirs("download")
    if os.listdir("download"):
        for file in os.listdir("download"):
            os.remove(f'download/{file}')
    if passphrase_file == "":
        raise HTTPException(status_code = 400, detail = "Passphrase vide, entrez une passphrase")
    try :
        file = os.path.join(UPLOAD_DIR, os.listdir("upload")[0])
        output = os.path.join(DOWNLOAD_DIR, os.listdir("upload")[0][:-4] + '_unhidden.png')
        retrieve_data(passphrase_file, file, output)
        file_path = os.path.join(DOWNLOAD_DIR, os.listdir("download")[0])
        filename = os.listdir("download")[0]
        headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    except :
        raise HTTPException(status_code = 404, detail = "Pas de fichier à déchiffrer, uploadez un fichier")
    return FileResponse(path = file_path, media_type = 'image/png', headers = headers)

@app.post("/downloadfile_index")
async def download_file_index():
    """Route which allows to download the file which is in the download folder
    Args:
        None

    Raises:
        HTTPException: if there is no file in the download folder
            
    Returns:
        FileResponse: the file which is in the download folder
    """
    try:
        file_path = os.path.join(DOWNLOAD_DIR, os.listdir("download")[0])
        filename = os.listdir("download")[0]
    except :
        raise HTTPException(status_code = 404, detail = "Pas de fichier à télécharger, uploadez un fichier et entrez une passphrase")
    headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    return FileResponse(path = file_path, media_type = 'image/png', headers = headers)

#-----------------------------------#
#                                   #
#       Obfuscation's routes        #
#                                   #
# ----------------------------------#

#check taille fichier
@app.post("/uploadfile_obfuscation")
async def create_upload_file_obfuscation(input_file: UploadFile = File(...)):
    """Route which allows to upload a file and save it in the upload folder
    
    Args:
        input_file (UploadFile): file to put in the upload folder

    Raises:
        HTTPException: if there is no file
        HTTPException: if the file is not a png, jpeg, jpg or pdf
        HTTPException: if there is a problem when reading the file
        HTTPException: if the file is too big
        HTTPException: if it is not possible to put the file in the upload folder
                
    Returns:
        FileResponse: file in the upload folder
    """
    # clear all the variables
    dict_words_with_roles.clear()
    list_roles.clear()
    if input_file == None:
        raise HTTPException(status_code = 400, detail = "Fichier non fourni, uploadez un fichier")
    if input_file.content_type != "image/png" and input_file.content_type != "image/jpeg" and input_file.content_type != "image/jpg" and input_file.content_type != "application/pdf":
        raise HTTPException(status_code = 400, detail = "Fichier fourni non pris en charge, utilisez uniquement un fichier png, jpeg, jpg ou pdf")
    # try :
    #     fs = await input_file.read()
    # except :
    #     raise HTTPException(status_code = 500, detail = "Quelque chose s'est mal passé lors de la lecture du fichier, veuillez réessayer")
    # if len(fs) > 20000000:
    #     raise HTTPException(status_code = 400, detail = "Fichier fourni trop volumineux, utilisez un fichier de moins de 20Mo")    
    try :
        if not os.path.exists("upload"):
            os.makedirs("upload")
        if os.listdir("upload"):
            for file in os.listdir("upload"):
                os.remove(f'upload/{file}')
        with open(f'{input_file.filename}', 'wb') as buffer:
            shutil.copyfileobj(input_file.file, buffer)
        buffer.close() 
        shutil.move(f'{input_file.filename}', f'upload/{input_file.filename}')
        
        file_path = os.path.join(UPLOAD_DIR, os.listdir("upload")[0])
        filename = os.listdir("upload")[0]
        
        if input_file.content_type == "application/pdf":
            pdf_to_png(file_path)
            file_path = os.path.join(UPLOAD_DIR, os.listdir("upload")[1])
            filename = os.listdir("upload")[1]
        headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    except :
        raise HTTPException(status_code = 500, detail = "Quelque chose s'est mal passé lors de l'upload du fichier, veuillez réessayer")
    return FileResponse(path = file_path, media_type = 'image/png', headers = headers)

@app.post("/createroles_obfuscation")
async def add_role_obfuscation(roles_input : str = Form(...)):
    """Route which allows to add a role in the list of roles

    Args:
        roles_input (str, optional): the role to add

    Raises:
        HTTPException: if the role send is empty
        HTTPException: if the role send is already in the list of roles
    """
    if roles_input == "":
        raise HTTPException(status_code = 400, detail = "Rôle vide, entrez un rôle")
    for role in list_roles:
        if role == roles_input:
            raise HTTPException(status_code = 400, detail = "Rôle déjà présent, entrez un rôle différent")
    list_roles.append(roles_input)
    
@app.post("/deleteroles_obfuscation")
async def delete_role_obfuscation(role_name : str = Form(...)):
    """Route which allows to delete a role in the list of roles

    Args:
        role_name (str, optional): the role to delete

    Raises:
        HTTPException: if the role send isn't in the list of roles
    """
    if role_name in list_roles:
        list_roles.remove(role_name)
    else:
        raise HTTPException(status_code = 400, detail = "Rôle non présent, entrez un rôle présent")

@app.post("/createwords_obfuscation")
async def add_word_obfuscation(words_input : str = Form(...)):
    """Route which allows to add a word in the dictionary

    Args:
        words_input (str, optional): the word to add

    Raises:
        HTTPException: if the word send is empty
    """
    global dict_words_with_roles
    if words_input == "":
        raise HTTPException(status_code = 400, detail = "Mot vide, entrez un mot")
    dict_words_with_roles = json.loads(words_input)
    
@app.post("/deletewords_obfuscation")
async def delete_word_obfuscation(word_name : str = Form(...)):
    """Route which allows to delete a word in the dictionary

    Args:
        word_name (str, optional): the word to delete

    Raises:
        HTTPException: if the word is not in the dictionary
    """
    key = word_name.split("{")[0]
    for word,role in dict_words_with_roles.items():
        if word == key:
            del dict_words_with_roles[word]
            break
    else:
        raise HTTPException(status_code = 400, detail = "Mot non présent, entrez un mot présent")

@app.post("/downloadfile_obfuscation")
async def download_file_obfuscation():
    """Route which create the hidden file and which allows to download the file which is in the download folder
    
    Args:
        None

    Raises:
        HTTPException: if it's impossible to create the hidden file
            
    Returns:
        FileResponse: the file which is in the download folder
    """
    if not os.path.exists("download"):
        os.makedirs("download")
    if os.listdir("download"):
        for file in os.listdir("download"):
            os.remove(f'download/{file}')
    try:
        if len(os.listdir("upload")) == 2:
            if os.listdir("upload")[0][-3:] == "pdf":
                os.remove(os.path.join(UPLOAD_DIR, os.listdir("upload")[0]))
            else:
                os.remove(os.path.join(UPLOAD_DIR, os.listdir("upload")[1]))
            
        list_position, dict_role2 = convertdict(dict_words_with_roles, list_roles)
        fileinputpath = os.path.join(UPLOAD_DIR, os.listdir("upload")[0])
        fileoutputpath = os.path.join(DOWNLOAD_DIR, os.listdir("upload")[0])
        
        change_pixels_to_black(fileinputpath, list_position, fileoutputpath)
        
        fileinputpath = os.path.join(DOWNLOAD_DIR, os.listdir("download")[0]) #the png file
        finalfile = os.path.join(DOWNLOAD_DIR, os.listdir("download")[0][:-4] + "_hidden.png")
        
        list_hash = {}
        for role,words in dict_role2.items():
            data = ''
            for word in words:
                data += word + ';'
            data = data[:-1]
            hash = create_a_hash(role)
            list_hash["{}".format(role)] = "{}".format(hash)
            hide_data(hash, data, finalfile, fileinputpath)
            fileinputpath = os.path.join(DOWNLOAD_DIR, os.listdir("download")[0][:-4] + "_hidden.png")

        json_data = json.dumps(list_hash)
        filename = f"{os.listdir('download')[1]}?list_hash={json_data}"
        headers = {'Content-Disposition': f'attachment; filename="{filename}"'}
    except:
        raise HTTPException(status_code = 500, detail = "Quelque chose s'est mal passé lors de la génération du fichier, veuillez réessayer")
    return FileResponse(path = finalfile, media_type = 'image/png', headers = headers)

#-----------------------------------#
#                                   #
#            Functions              #
#                                   #
# ----------------------------------#

def pdf_to_png(pdf_file_path):
    """Function which converts a PDF file to a PNG file.
    
    Args:
        pdf_file_path (str): path to the PDF file

    Returns:
        None
    """
    with fitz.open(pdf_file_path) as pdf:
        if len(pdf) != 1:
            print("Le fichier PDF doit contenir une seule page.")
            return
    
    filename = os.path.splitext(os.path.basename(pdf_file_path))[0] + ".png"
    output_file_path = os.path.join(os.path.dirname(pdf_file_path), filename)
    with fitz.open(pdf_file_path) as pdf, open(output_file_path, "wb") as png:
        page = pdf.load_page(0)
        zoom_x = 3
        zoom_y = 3
        mat = fitz.Matrix(zoom_x, zoom_y)
        pix = page.get_pixmap(matrix = mat)
        png.write(pix.tobytes())
        png.close()

def create_a_hash(role):
    """Function which creates a hash from a role.
    
    Args:
        role (str): role

    Returns:
        hash (str): hash of the role
    """
    hash_object = hashlib.sha256(role.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig[:16]

def get_the_top_left(coordinates):
    """Get the top left coordinates of the rectangle
    
    Args:
        list_positions (list): list of positions of the words

    Returns:
        text (str): string of the top left coordinates
    """
    coorStartX = coordinates[0][0] 
    coorStartY = coordinates[0][1]
    coorEndX = coordinates[1][0]
    coorEndY = coordinates[1][1]
    #get the one which is on the top left
    if coorStartX > coorEndX:
        coorStartX = coordinates[1][0]
        coorEndX = coordinates[0][0]
    if coorStartY > coorEndY:
        coorStartY = coordinates[1][1]
        coorEndY = coordinates[0][1]
    return '{coorStartX},{coorStartY}'.format(coorStartX = coorStartX, coorStartY = coorStartY)

def convertdict(dict, list_roles):
    """Convert the dictionary of roles and words to be read by the hide_data function and get the positions of the words

    Args:
        dict (dict): dictionary of roles and words
        list_roles (list): list of roles

    Returns:
        list_positions (list): list of positions of the words
        list_role2 (dict): dictionary of roles and words to be read by the hide_data function
    """
    list_role2 = {}
    list_positions = []
    for role in list_roles:
        list_role2[role] = []
    for word, data in dict.items():
        for i in data:
            list_positions.append([i[1], i[2]])
            for role in i[0]:
                list_role2[role].append(get_the_top_left([i[1], i[2]]) + ',' + word)
    return list_positions, list_role2

def change_pixels_to_black(file_path, positions, output_path):
    """Change the pixels of the image to black

    Args:
        file_path (str): input file path
        positions (list): list of positions of the words
        output_path (str): output file path
    """
    with Image.open(file_path) as img:
        draw = ImageDraw.Draw(img)
        for pos in positions:
            x1, y1, x2, y2 = pos[0][0], pos[0][1], pos[1][0], pos[1][1]
            draw.rectangle([(x1, y1), (x2, y2)], fill="black")
        img.save(output_path)
