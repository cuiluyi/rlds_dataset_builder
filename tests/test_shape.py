import h5py
import glob

files = glob.glob("/data/cuiluyi/resources/datasets/LIBERO/libero_spatial/*.hdf5")
if files:
    with h5py.File(files[0], "r") as F:
        key = list(F['data'].keys())[0]
        images = F['data'][key]["obs"]["agentview_rgb"][()]
        wrist_images = F['data'][key]["obs"]["eye_in_hand_rgb"][()]
        print("agentview_rgb shape:", images.shape)
        print("eye_in_hand_rgb shape:", wrist_images.shape)
