import Metashape


def remove_average_pitch(chunk):
    pitch = get_average_pitch(chunk)
    rotation_matrix = Metashape.Utils.ypr2mat(Metashape.Vector((0, pitch, 0)))
    inverse_rotation_matrix = rotation_matrix.inv()
    T = chunk.transform.matrix
    # Apply the inverse rotation to remove the pitch
    chunk.transform.matrix = Metashape.Matrix.Rotation(
        inverse_rotation_matrix) * T


def get_average_pitch(chunk):
    pitch_sum = 0
    count = 0
    T = chunk.transform.matrix

    for camera in chunk.cameras:
        if camera.center is None:
            continue

        m = chunk.crs.localframe(T.mulp(camera.center))
        R = (m * T * camera.transform *
             Metashape.Matrix().Diag([1, -1, -1, 1])).rotation()
        estimated_ypr = Metashape.utils.mat2ypr(R)

        if estimated_ypr is None:
            continue

        pitch = estimated_ypr[1]
        pitch_sum += pitch
        count += 1

    if count == 0:
        return None

    return pitch_sum / count
