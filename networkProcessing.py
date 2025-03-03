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
    docs = []
    for entry in os.scandir(root_folder):
        if entry.is_dir():
            folder_name = os.path.basename(entry.path.rstrip(os.sep))
            psx_name = folder_name + '.psx'
            psx_path = os.path.join(entry.path, psx_name)
            if not os.path.exists(psx_path):
                print(f'Processing folder: {entry.path}')
                doc = setUpPhotos(entry.path, psx_path)
                docs.append(doc)
            else:
                print(
                    f'Skipping folder {entry.path}, Metashape file already exists.')
    return docs


def process_doc(doc: Metashape.Document):
    resolution = 5e-6
    doc.save()
    file_path = doc.path
    name = os.path.splitext(file_path)[0]
    chunk = doc.chunks[0]
    chunk.detectMarkers(tolerance=100)

    doc.save()

    markerLocation = {
        'target 1': Metashape.Vector((0.01, 0, 0)),
        'target 2': Metashape.Vector((0.11, 0, 0)),
        'target 3': Metashape.Vector((0.21, 0, 0)),
        'target 4': Metashape.Vector((0.31, 0, 0)),
        'target 5': Metashape.Vector((0.41, 0, 0)),
        'target 6': Metashape.Vector((0.51, 0, 0)),
        'target 7': Metashape.Vector((0.61, 0, 0))
    }
    for marker in chunk.markers:
        print(f'Maker label is {marker.label}')
        for key in markerLocation.keys():
            if marker.label in markerLocation and marker.label == key:
                print(f'{marker.label} is in markerLocation dictionary.')
                marker.reference.location = markerLocation[key]
                marker.reference.accuracy = Metashape.Vector(
                    (0.00001, 0.00001, 0.00001))
    for camera in chunk.cameras:
        camera.reference.rotation = Metashape.Vector([0.0, 0.0, 0.0])
        camera.reference.rotation_accuracy = Metashape.Vector(
            [0.01, 0.01, 0.01])

    doc.save()

    # Network processing
    network_client = Metashape.NetworkClient()
    # Replace with your network server address
    network_client.connect('seesalsdo1p')

    tasks = []

    task = Metashape.Tasks.MatchPhotos()
    tasks.append(task)

    task = Metashape.Tasks.AlignCameras()
    tasks.append(task)

    task = Metashape.Tasks.OptimizeCameras()
    tasks.append(task)

    task = Metashape.Tasks.BuildModel()
    task.source_data = Metashape.TiePointsData
    tasks.append(task)

    task = Metashape.Tasks.BuildOrthomosaic()
    task.resolution = resolution
    tasks.append(task)
    network_tasks = []
    for task in tasks:
        if task.target == Metashape.Tasks.DocumentTarget:
            network_tasks.append(task.toNetworkTask(doc))
        else:
            for chunk in doc.chunks:
                network_tasks.append(task.toNetworkTask(chunk))

    batch_id = network_client.createBatch(file_path, network_tasks)
    network_client.setBatchPaused(batch_id, False)

    doc.save()

    try:
        chunk.exportRaster(path=name + '.tif', resolution=resolution)
    except Exception as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    root_folder = '\\\\file\\Shared\\SEESPhotoDatabase\\Active Work\\Kamen Engel\\For Sophie Newsham\\2. Giles or Jonathan_Metashape Fix\\test1'
    docs = process_folders(root_folder)
    while docs:
        doc = docs.pop(0)
        print(f'Processing {doc.path}')
        process_doc(doc)
        print("All done.")
