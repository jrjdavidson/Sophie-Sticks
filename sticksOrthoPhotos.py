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
    docs = []
    for entry in os.scandir(root_folder):
        # if the entry is a directory
        if entry.is_dir():
            # define the folder name
            folder_name = os.path.basename(entry.path.rstrip(os.sep))
            psx_name = folder_name + '.psx'
            psx_path = os.path.join(entry.path, psx_name)
            # if the psx file doesn't exist then create one
            if not os.path.exists(psx_path):
                print(f'Processing folder: {entry.path}')
                doc = setUpPhotos(entry.path, psx_path)
                # Add marker detection and assignment if needed
                docs.append(doc)
                # skips setting up folder
            else:
                # doc= Metashape.Document()
                # doc.open(psx_path,read_only=False)
                # docs.append(doc)
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
                print(
                    f'{marker.label} is in markerLocation dictonary.')
                marker.reference.location = markerLocation[key]
                marker.reference.accuracy = Metashape.Vector(
                    (0.00001, 0.00001, 0.00001))
    for camera in chunk.cameras:
        # Set yaw, pitch, and roll to 0
        camera.reference.rotation = Metashape.Vector([0.0, 0.0, 0.0])
        # Set accuracy to 0.01 degrees
        camera.reference.rotation_accuracy = Metashape.Vector(
            [0.1, 0.1, 0.1])

    # Save the changes
    doc.save()

    chunk.matchPhotos()

    batch_size = 20
    total_cameras = len(chunk.cameras)
    for i in range(0, total_cameras, batch_size):
        end_index = min(i + batch_size, total_cameras)
        chunk.alignCameras(chunk.cameras[i:end_index])
    doc.save()

    # chunk.optimizeCameras()
    if check_camera_rotation(chunk):
        print("Camera rotation exceeds threshold, skipping orthomosaic generation for this chunk. This chunk will have to be checked manually.")
        return
    chunk.buildModel(source_data=Metashape.TiePointsData)
    pitch = get_average_pitch(chunk)
    rotation_matrix = Metashape.Utils.ypr2mat(Metashape.Vector((0, pitch, 0)))
    inverse_rotation_matrix = rotation_matrix.inv()
    T = chunk.transform.matrix
    # Apply the inverse rotation to remove the pitch
    chunk.transform.matrix = Metashape.Matrix.Rotation(
        inverse_rotation_matrix) * T

    print(f'Chunk rotation: {chunk.transform.matrix}')
    if get_average_pitch(chunk) > 2:
        print("Pitch exceeds threshold, skipping orthomosaic generation for this chunk. This chunk will have to be checked manually.")
        return
    # chunk.buildOrthomosaic(resolution=resolution)
    doc.save()

    try:
        chunk.exportRaster(path=name + '.tif', resolution=resolution)
    except Exception as error:
        print(f'An error occured: {error}')


def get_average_pitch(chunk):
    pitch_sum = 0
    count = 0
    T = chunk.transform.matrix

    for camera in chunk.cameras:
        m = chunk.crs.localframe(T.mulp(camera.center))
        R = (m * T * camera.transform *
             Metashape.Matrix().Diag([1, -1, -1, 1])).rotation()
        estimated_ypr = Metashape.utils.mat2ypr(R)
        if estimated_ypr:
            pitch = estimated_ypr[1]
            pitch_sum += pitch
            count += 1

    if count == 0:
        return None

    return pitch_sum / count


def check_camera_rotation(chunk: Metashape.Chunk):
    threshold = 5  # degrees
    yaw_sum, pitch_sum, roll_sum = 0, 0, 0
    count = 0
    T = chunk.transform.matrix

    # Calculate the sum of yaw, pitch, and roll
    for camera in chunk.cameras:
        m = chunk.crs.localframe(T.mulp(camera.center))
        R = (m * T * camera.transform *
             Metashape.Matrix().Diag([1, -1, -1, 1])).rotation()
        estimated_ypr = Metashape.utils.mat2ypr(R)
        if estimated_ypr:
            yaw, pitch, roll = estimated_ypr
            yaw_sum += yaw
            pitch_sum += pitch
            roll_sum += roll
            count += 1

    # Calculate the averages
    if count == 0:
        print('No camera rotations found.')
        return False

    yaw_avg = yaw_sum / count
    pitch_avg = pitch_sum / count
    roll_avg = roll_sum / count

    # Check if each rotation is within the threshold
    for camera in chunk.cameras:
        m = chunk.crs.localframe(T.mulp(camera.center))
        R = (m * T * camera.transform *
             Metashape.Matrix().Diag([1, -1, -1, 1])).rotation()
        estimated_ypr = Metashape.utils.mat2ypr(R)
        if estimated_ypr:
            yaw, pitch, roll = estimated_ypr
            if (abs(yaw - yaw_avg) > threshold or
                abs(pitch - pitch_avg) > threshold or
                    abs(roll - roll_avg) > threshold):
                return True

    print('All camera rotations are within threshold.')
    return False


if __name__ == '__main__':
    root_folder = '\\\\file\\Shared\\SEESPhotoDatabase\\Active Work\\Kamen Engel\\For Sophie Newsham\\2. Giles or Jonathan_Metashape Fix\\test1'
    docs = process_folders(root_folder)
    while docs:  # instead of a "for" loop, pop the doc off the array, to ensure that the docuemnt is closed when done processing. An empty array will evaluate to False.
        doc = docs.pop(0)  # Pop the first document from the list
        print(f'Processing {doc.path}')
        process_doc(doc)
        print("All done.")
