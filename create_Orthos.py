import os
import Metashape

# A helper to create orthomosaics from all .psx files in a folder. Used when orthomosaics are needed for a large number of projects.
# The function process_document() opens a .psx file, builds an orthomosaic with the specified resolution, saves the document and exports the orthomosaic as a .tif file.


def process_document(doc_path, resolution):
    doc = Metashape.Document()
    doc.open(doc_path)
    chunk = doc.chunk

    chunk.buildOrthomosaic(resolution=resolution)
    doc.save()

    try:
        chunk.exportRaster(path=f"{doc_path}.tif", resolution=resolution)
    except Exception as error:
        print(f"An error occurred: {error}")


def find_and_process_docs(root_folder, resolution):
    for subdir, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.psx'):
                doc_path = os.path.join(subdir, file)
                process_document(doc_path, resolution)


# Example usage
root_folder = '\\\\file\\Shared\\SEESPhotoDatabase\\Active Work\\Kamen Engel\\For Sophie Newsham\\1. For Sophie to Check\\needs ortho'
resolution = 5e-6
find_and_process_docs(root_folder, resolution)
