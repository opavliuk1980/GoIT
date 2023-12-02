import os
import sys
import shutil
import zipfile
import gzip
import tarfile

FILES_CATEGORIES = {
        "Images" : ('.jpeg', '.png', '.jpg', '.svg'),
        "Videos" : ('.avi', '.mp4', '.mov', '.mkv'),
        "Documents" : ('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx', ".epub"),
        "Musics" : ('.mp3', '.ogg', '.wav', '.amr'),
        "Archives" : ('.zip', '.gz', '.tar'),
};


CYRILLIC_SYMBOLS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ"
ILLEGAL_SYMBOLS = ':<>|"?* !\'/\\';
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")
    
TRANS = {ord(c):t for c, t in zip(CYRILLIC_SYMBOLS, TRANSLATION)};
TRANS.update({ord(c.upper()):t.upper() for c, t in zip(CYRILLIC_SYMBOLS, TRANSLATION)});

illegals_table = str.maketrans(ILLEGAL_SYMBOLS, '_' * len(ILLEGAL_SYMBOLS))
TRANS.update(illegals_table)


def translate(name):
    return name.translate(TRANS);


def list_folders_and_files(folder_path, ignore_hidden = False):
    files = [];
    folders = [];
    for item in os.listdir(folder_path):
        if ignore_hidden and item.startswith('.'): continue; 
        item_path = os.path.join(folder_path, item)
        if os.path.isfile(item_path):
            files.append(item_path);
        elif os.path.isdir(item_path):
            folders.append(item_path);
    return folders, files


def group_files_by_extensions(files_list:list) -> dict:
    res = {};
    for file_path in files_list:
        _, ext = os.path.splitext(file_path);
        files = res.get(ext, []);
        files.append(file_path);
        res.update({ext: files});            
    return res;


def group_files_by_categories(files_list: list) -> dict:
    res = {};
    files_by_exts = group_files_by_extensions(files_list);
    for category, file_extensions in FILES_CATEGORIES.items():
        for ext in file_extensions:
            try:
                ext_files = files_by_exts.pop(ext);
                category_groups = res.get(category, {});
                category_groups.update({ext: ext_files});
                res.update({category: category_groups});
            except KeyError:
                continue 
    if files_by_exts:
        res.update({"Unknown": files_by_exts});
    return res;


def merge_files_catorories(c1:dict, c2:dict) -> dict:
    for category, group2 in c2.items():
        group1 = c1.get(category, {});
        for ext, files2 in group2.items():
            files1 = group1.get(ext, []);
            files1.extend(files2);
            group1.update({ext: files1});
        c1.update({category: group1});
    return c1;


def move_file_to_group(file_path, group_folder):
    if not os.path.exists(group_folder):
        os.makedirs(group_folder);
    _, f_name = os.path.split(file_path);
    destination_path = os.path.join(group_folder, translate(f_name));
    print(f'Moving the "{file_path}" to the "{destination_path}"');
    shutil.move(file_path, destination_path);
    return destination_path;


def extract_archive(file_path):
    extraction_path, extension, = os.path.splitext(file_path);
    os.makedirs(extraction_path);
    match extension:
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
    return extraction_path;


def extract_archives(archives_groups : dict) -> list:
    etractions_folders = []; 
    for ext, archives in archives_groups.items():
        for archive_path in archives:
            etractions_folders.append(extract_archive(archive_path));
            os.remove(archive_path);
    return etractions_folders;


def organize_files_by_cathegory(folder_path, destination_folder_path = None):
    print(f"Опрацювання вмісту '{folder_path}' папки");
    if not destination_folder_path: 
        destination_folder_path = folder_path;        
    
    folders, files = list_folders_and_files(folder_path, ignore_hidden=True)
    categories_files = group_files_by_categories(files);
    try:
        folders.extend(extract_archives(categories_files["Archives"]));
    except:
        None;
    
    for cat, cat_files_groups in categories_files.items():
        if cat == "Archives" : continue;
        cat_path = os.path.join(destination_folder_path, cat);
        for ext, file_paths in cat_files_groups.items():
            for file_path in file_paths:
                try: 
                    destination_path = move_file_to_group(file_path, cat_path);
                except Exception as e:
                    print(f"Cannot move file '{file_path}' to the '{cat_path}' folder: ", e);
    
    for folder in folders:
        folder_cat_files = organize_files_by_cathegory(folder, destination_folder_path);
        shutil.rmtree(folder);
        categories_files = merge_files_catorories(categories_files, folder_cat_files);
    
    return categories_files;


def print_report(categories_files_groups):
    for cat, files_ext_group in categories_files_groups.items():
        l = list(files_ext_group.keys());
        print(f"\n{cat:=>10s} : {len(l):^4} file types : {l}");
        for ext, files in files_ext_group.items():
            file_names = [os.path.split(f)[1] for f in files];
            print(" - " + "\n - ".join(file_names));

if not __name__ == "__main__" :
    c1 = {
        "Executables": {
            ".exe" : [f"exec-{n}.exe" for n in range(0,2)],
            ".com" : [f"exec-{n}.com" for n in range(0,2)],
            },
        "Images": {
            ".jpg" : [f"img-{n}.jpg" for n in range(0,2)],
            ".png" : [f"img-{n}.png" for n in range(0,2)],
            },        
        };

    c2 = {
        "Archives": {
            ".zip" : [f"arc-{n}.exe" for n in range(2,4)],
            ".tar" : [f"arc-{n}.com" for n in range(2,4)],
            },
        "Images": {
            ".jpg" : [f"img-{n}.jpg" for n in range(2,4)],
            ".bmp" : [f"img-{n}.png" for n in range(2,4)],
            },        
        };
    
    print_report(merge_files_catorories(c2, c1));
    

else:
    # Приклад виклику функції для папки на робочому столі
    folder_path = os.path.join(os.path.expanduser("~"), "ParseMe", "F-2")
    folder_dest = os.path.join(os.path.expanduser("~"), "ParseMe", "F-1")
    if len(sys.argv) > 2:
        folder_dest = sys.argv[2];
    if len(sys.argv) > 1:
        folder_path = sys.argv[1];

    print("Start")
    categories_files_groups = organize_files_by_cathegory(folder_path, folder_dest);
    print_report(categories_files_groups)