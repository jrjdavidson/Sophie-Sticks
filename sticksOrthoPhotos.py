import Metashape
import os

def find_files(folder, types):
    return [entry.path for entry in os.scandir(folder) if (entry.is_file() and os.path.splitext(entry.name)[1].upper().lstrip('.') in types)]

def setUpPhotos(image_folder, project_path, types=['JPG']):
    photos = find_files(image_folder, types)

    doc = Metashape.Document()
    doc.save(project_path)

    
    chunk = doc.addChunk()
    chunk.addPhotos(photos)
    print(str(len(chunk.cameras)) + " images loaded")

    doc.save()
    return doc

def process_folders(root_folder):
    # for every folder(entry) in the root
    docs=[]
    for entry in os.scandir(root_folder):
        #if the entry is a directory
        if entry.is_dir():
            #define the folder name
            folder_name = os.path.basename(entry.path.rstrip(os.sep))
            psx_name = folder_name + '.psx'
            psx_path = os.path.join(entry.path, psx_name)
            #if the psx file doesn't exist then create one
            if not os.path.exists(psx_path):
                print(f'Processing folder: {entry.path}')
                doc = setUpPhotos(entry.path, psx_path)
                # Add marker detection and assignment if needed
                docs.append(doc)
                #skips setting up folder
            else:
                # doc= Metashape.Document()
                # doc.open(psx_path,read_only=False)
                # docs.append(doc)
                print(f'Skipping folder {entry.path}, Metashape file already exists.')
    return docs

def process_doc(doc:Metashape.Document):
    resolution = 1e-5 # 1 micrometer!
    doc.save()
    file_path = doc.path
    name = os.path.splitext(file_path)[0]
    chunk = doc.chunks[0]
    chunk.detectMarkers()
    markerLocation={
        'target 1': Metashape.Vector((100,0,0)),
        'target 2': Metashape.Vector((200,0,0)),
        'target 3': Metashape.Vector((300,0,0)),
        'target 4': Metashape.Vector((400,0,0)),
        'target 5': Metashape.Vector((500,0,0)),
        'target 6': Metashape.Vector((600,0,0)),
        'target 7': Metashape.Vector((700,0,0)),
        'target 8': Metashape.Vector((800,0,0))
    }
    for marker in chunk.markers:
        print(f'Maker label is {marker.label}')
        for key in markerLocation.keys():
            print(f'Key is: {key}')
            if marker.label in markerLocation and marker.label == key:
                print(f'{marker.label} is in markerLocation dictonary and the key and marker label are equal.')
                marker.reference.location= markerLocation[key]
                
    doc.save()

    chunk.matchPhotos()
    chunk.alignCameras()
    doc.save()

    chunk.buildDepthMaps()
    chunk.buildModel(source_data=Metashape.DepthMapsData)
    chunk.buildOrthomosaic(resolution=resolution)
    doc.save()

    try:
        chunk.exportRaster(path=name + '.tif',resolution=resolution)
    except Exception as error:
        print(f'An error occured: {error}')

if __name__ == '__main__':
    root_folder = '\\\\file\\Shared\\SEESPhotoDatabase\\Active Work\\Kamen Engel\\For Sophie Newsham\\Working Files'
    docs =  process_folders(root_folder)
    for doc in docs:
        print(f'Processing {doc.path}')
        process_doc(doc)
        # Close the document explicitly
        del doc
          
        
    




