import Metashape
import sticksOrthoPhotos
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
    sticksOrthoPhotos.process_doc(doc)


label = "Scripts/Stitch Photos"
Metashape.app.addMenuItem(label, stitch_photos)
print("To execute this script press {}".format(label))
