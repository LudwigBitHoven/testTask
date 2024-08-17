from os import listdir
from os.path import join, isfile
import zipfile


PATH = "../заливка"
paths = [join(PATH, f) for f in listdir(PATH) if isfile(join(PATH, f))]
try:
    for path in paths:
        """
            renames 'xl/SharedStrings.xml' into 'xl/sharedStrings.xml' inside xlsx file,
            works without extracting files, new files have names like "file_name.modified.xlsx"
        """
        with zipfile.ZipFile(path, mode="r") as archive:
            if not "_temp.xlsx" in path:
                filename = path.replace(".xlsx", "")
                with zipfile.ZipFile(filename + "_temp.xlsx", 'w') as temp_zip:
                    for item in archive.infolist():
                        if item.filename == 'xl/SharedStrings.xml':
                            temp_zip.writestr('xl/sharedStrings.xml', archive.read(item.filename))
                        else:
                            temp_zip.writestr(item.filename, archive.read(item.filename))
    print("Script finished successfully")
except Exception as E:
    print(f"Error occured:\n{E}")
