import os
import sys
import shutil
import zipfile
import gzip
import tarfile

ARCHIVES = "archives"
DOCUMENTS = "documents"
IMAGES = "images"
MUSICS = "musics"
UNKNOWN = "others"
VIDEOS = "videos"

FILES_CATEGORIES = {
        ARCHIVES : ('.zip', '.gz', '.tar'),
        DOCUMENTS : ('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx', ".epub"),
        IMAGES : ('.jpeg', '.png', '.jpg', '.svg'),
        MUSICS : ('.mp3', '.ogg', '.wav', '.amr'),
        VIDEOS : ('.avi', '.mp4', '.mov', '.mkv'),  
        UNKNOWN : (),      
}


def illegal_ords(legals = ((1, ord('0')), (ord('9')+1, ord('A')), (ord('Z')+1, ord('a')), (ord('z')+1, 0x80))):
    res = []
    for f,t in legals:
        res.extend(list(range(f,t)))
    return res
    
ILLEGAL_SYMBOLS = illegal_ords()
TRANS = {k:"_" for k in ILLEGAL_SYMBOLS}
CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")    
TRANS.update({ord(c):t for c, t in zip(CYRILLIC_SYMBOLS, TRANSLATION)})
TRANS.update({ord(c.upper()):t.upper() for c, t in zip(CYRILLIC_SYMBOLS, TRANSLATION)})

def normalize(name):
    return name.translate(TRANS)


def list_folders_and_files(folder_path, ignore_hidden = False):
    files = []
    folders = []
    for item in os.listdir(folder_path):
        if ignore_hidden and item.startswith('.'): continue 
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            files.append(item_path)
        elif os.path.isdir(item_path):
            folders.append(item_path)
    return folders, files


def group_files_by_extensions(files_list:list) -> dict:
    res = {}
    for file_path in files_list:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        files = res.get(ext, [])
        files.append(file_path)
        res.update({ext: files})            
    return res


def group_files_by_categories(files_list: list) -> dict:
    res = {}
    files_by_exts = group_files_by_extensions(files_list)
    for category, file_extensions in FILES_CATEGORIES.items():
        for ext in file_extensions:
            try:
                ext_files = files_by_exts.pop(ext)
                category_groups = res.get(category, {})
                category_groups.update({ext: ext_files})
                res.update({category: category_groups})
            except KeyError:
                continue 
    if files_by_exts:
        res.update({UNKNOWN: files_by_exts})
    return res


def merge_files_catorories(c1:dict, c2:dict) -> dict:
    for category, group2 in c2.items():
        group1 = c1.get(category, {})
        for ext, files2 in group2.items():
            files1 = group1.get(ext, [])
            files1.extend(files2)
            group1.update({ext: files1})
        c1.update({category: group1})
    return c1


def move_file_to_group(file_path, group_folder):
    if not os.path.exists(group_folder):
        os.makedirs(group_folder)
    _, f_name = os.path.split(file_path)
    f_name, ext = os.path.splitext(f_name)
    destination_path = os.path.join(group_folder, normalize(f_name) + ext)
    print(f'Moving the "{file_path}" to the "{destination_path}"')
    if os.path.exists(destination_path): raise FileExistsError(f'The "{destination_path}" path exists already')
    shutil.move(file_path, destination_path)
    return destination_path

def get_extraction_path(file_path, dest_path):
    no_ext_file_path, extension = os.path.splitext(file_path)
    soutce_folder_path, extraction_folder_name = os.path.split(no_ext_file_path)
    extraction_folder_name = normalize(extraction_folder_name)
    return os.path.join(dest_path, ARCHIVES, extraction_folder_name), extension  

def extract_archive(file_path, extraction_path : str, extension):
    os.makedirs(extraction_path)
    match extension.lower():
        case ".zip":
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(extraction_path)
        case '.gz':
            with gzip.open(file_path, 'rb') as gz_file:
                with open(extraction_path, 'wb') as extracted_file:
                    shutil.copyfileobj(gz_file, extracted_file)
        case '.tar':
            with tarfile.open(file_path, 'r') as tar_ref:
                tar_ref.extractall(extraction_path)
    return extraction_path


def extract_archives(archives_groups : dict, extract_archive_to : str = None) -> list:
    etractions_folders = [] 
    for ext, archives in archives_groups.items():
        for archive_path in archives:
            try:
                extraction_path, extension = get_extraction_path(archive_path, extract_archive_to);
                etractions_folders.append(extract_archive(archive_path, extraction_path, extension))
            except Exception as e:
                print(f'Error at to extract the "{archive_path}" archive: ', e, "\nDeleting ...")
                if os.path.exists(extract_archive_to): shutil.rmtree(extraction_path)
            finally:
                os.remove(archive_path)
    return etractions_folders


def organize_files_by_cathegory(folder_path: str, destination_folder_path:str = None, organize_archives = True) -> dict:
    print(f"Опрацювання вмісту '{folder_path}' папки")
    is_empty = True
    if not destination_folder_path: 
        destination_folder_path = folder_path        
    
    folders, files = list_folders_and_files(folder_path, ignore_hidden=True)
    categories_files = group_files_by_categories(files)
    try:
        extractions_paths = extract_archives(categories_files[ARCHIVES], destination_folder_path)
        if organize_archives:
            folders.extend(extractions_paths)
    except:
        None
        # is_empty = False
    
    for cat, cat_files_groups in categories_files.items():
        if cat == ARCHIVES : continue
        cat_path = os.path.join(destination_folder_path, cat)
        for ext, file_paths in cat_files_groups.items():
            for file_path in file_paths:
                try: 
                    destination_path = move_file_to_group(file_path, cat_path)
                except Exception as e:
                    print(f"The '{folder_path}' folder will not be deleted due to the error: ", e)
                    is_empty = False
    
    for folder in folders:
        _, foler_name = os.path.split(folder)
        if foler_name in FILES_CATEGORIES.keys(): 
            is_empty = False
            continue
        folder_cat_files, is_all_subfolders_empty = organize_files_by_cathegory(folder, destination_folder_path, organize_archives)
        is_empty = is_empty and is_all_subfolders_empty
        if is_all_subfolders_empty: shutil.rmtree(folder)
        categories_files = merge_files_catorories(categories_files, folder_cat_files)
    
    return categories_files, is_empty


def print_report(categories_files_groups):
    for cat, files_ext_group in categories_files_groups.items():
        l = list(files_ext_group.keys())
        print(f"\n{cat:=>10s} : {len(l):^4} file types : {l}")
        for ext, files in files_ext_group.items():
            file_names = [os.path.split(f)[1] for f in files]
            print(" - " + "\n - ".join(file_names))

if  __name__ == "__main__" :
    folder_path = os.path.join(os.path.expanduser("~"), "Desktop", "Мотлох")
    folder_dest = folder_path
    if len(sys.argv) > 2:
        folder_dest = sys.argv[2]
        folder_path = sys.argv[1]
    elif len(sys.argv) > 1:
        folder_path = sys.argv[1]
        folder_dest = folder_path

    print("Start")
    categories_files_groups, is_all_subfolders_empty = organize_files_by_cathegory(folder_path, folder_dest, organize_archives=False)
    print_report(categories_files_groups)