import Metashape
import sticksOrthoPhotos
import remove_pitch

# Checking compatibility
compatible_major_version = "2.2"
found_major_version = ".".join(Metashape.app.version.split('.')[:2])
if found_major_version != compatible_major_version:
    raise Exception("Incompatible Metashape version: {} != {}".format(
        found_major_version, compatible_major_version))


def stitch_photos():
    doc = Metashape.app.document
    if not len(doc.chunks):
        raise Exception("No chunks!")
    sticksOrthoPhotos.process_doc(doc, False)


def remove_average_pitch():
    doc = Metashape.app.document
    if not len(doc.chunks):
        raise Exception("No chunks!")
    remove_pitch.remove_average_pitch(doc.chunk)


label_stitch = "Scripts/Stitch Photos"
Metashape.app.addMenuItem(label_stitch, stitch_photos)
print("To execute this script press {}".format(label_stitch))

label_remove_pitch = "Scripts/Remove Average Pitch"
Metashape.app.addMenuItem(label_remove_pitch, remove_average_pitch)
print("To execute this script press {}".format(label_remove_pitch))
