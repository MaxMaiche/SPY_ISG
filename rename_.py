
import os

dir = "Assets/StreamingAssets/Levels/Desamorceur/"
for filename in os.listdir(dir):
    if filename.startswith("desamorceur_"):
        new_filename = filename[12].upper() + filename[13:]
        filename = os.path.join(dir, filename)
        new_filename = os.path.join(dir, new_filename)
        os.rename(filename, new_filename)
        print("Renommage de", filename, "en", new_filename)
    else:
        print("Le fichier", filename, "n'a pas été renommé")

