import h5py
import glob

folders = glob.glob("/data/cuiluyi/resources/datasets/LIBERO/*")
for folder in folders:
    files = glob.glob(folder + "/*.hdf5")
    if files:
        with h5py.File(files[0], "r") as F:
            key = list(F['data'].keys())[0]
            # print all shapes
            print(folder)
            print("actions shape:", F['data'][key]["actions"][()].shape)
            print("ee_states shape:", F['data'][key]["obs"]["ee_states"][()].shape)
            print("gripper_states shape:", F['data'][key]["obs"]["gripper_states"][()].shape)
            print("joint_states shape:", F['data'][key]["obs"]["joint_states"][()].shape)
