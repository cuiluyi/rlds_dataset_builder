import h5py
import glob

folders = glob.glob("/data/cuiluyi/resources/datasets/LIBERO/*")
for folder in folders:
    files = glob.glob(folder + "/*.hdf5")
    if files:
        with h5py.File(files[0], "r") as F:
            key = list(F['data'].keys())[0]
            images = F['data'][key]["obs"]["agentview_rgb"][()]
            print(folder, "agentview_rgb shape:", images.shape)
