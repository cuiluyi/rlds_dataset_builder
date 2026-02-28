# RLDS Dataset Conversion

This repo demonstrates how to convert an existing dataset into RLDS format for X-embodiment experiment integration.
It provides an example for converting a dummy dataset to RLDS. To convert your own dataset, **fork** this repo and
modify the example code for your dataset following the steps below.

## Installation

First create a conda environment using the provided environment.yml file (use `environment_ubuntu.yml` or `environment_macos.yml` depending on the operating system you're using):

```
conda env create -f environment_ubuntu.yml
```

Then activate the environment using:

```
conda activate rlds_env
```

If you want to manually create an environment, the key packages to install are `tensorflow`,
`tensorflow_datasets`, `tensorflow_hub`, `apache_beam`, `matplotlib`, `plotly` and `wandb`.

## Run Example RLDS Dataset Creation

Before modifying the code to convert your own dataset, run the provided example dataset creation script to ensure
everything is installed correctly. Run the following lines to create some dummy data and convert it to RLDS.

```
cd example_dataset
python3 create_example_data.py
proxy_on
tfds build
```

This should create a new dataset in `~/tensorflow_datasets/example_dataset`. Please verify that the example
conversion worked before moving on.

## Converting your Own Dataset to RLDS

Now we can modify the provided example to convert your own data. Follow the steps below:

1. **Rename Dataset**: Change the name of the dataset folder from `example_dataset` to the name of your dataset (e.g. robo_net_v2),
   also change the name of `example_dataset_dataset_builder.py` by replacing `example_dataset` with your dataset's name (e.g. robo_net_v2_dataset_builder.py)
   and change the class name `ExampleDataset` in the same file to match your dataset's name, using camel case instead of underlines (e.g. RoboNetV2).

2. **Modify Features**: Modify the data fields you plan to store in the dataset. You can find them in the `_info()` method
   of the `ExampleDataset` class. Please add **all** data fields your raw data contains, i.e. please add additional features for
   additional cameras, audio, tactile features etc. If your type of feature is not demonstrated in the example (e.g. audio),
   you can find a list of all supported feature types [here](https://www.tensorflow.org/datasets/api_docs/python/tfds/features?hl=en#classes).
   You can store step-wise info like camera images, actions etc in `'steps'` and episode-wise info like `collector_id` in `episode_metadata`.
   Please don't remove any of the existing features in the example (except for `wrist_image` and `state`), since they are required for RLDS compliance.
   Please add detailed documentation what each feature consists of (e.g. what are the dimensions of the action space etc.).
   Note that we store `language_instruction` in every step even though it is episode-wide information for easier downstream usage (if your dataset
   does not define language instructions, you can fill in a dummy string like `pick up something`).

3. **Modify Dataset Splits**: The function `_split_generator()` determines the splits of the generated dataset (e.g. training, validation etc.).
   If your dataset defines a train vs validation split, please provide the corresponding information to `_generate_examples()`, e.g.
   by pointing to the corresponding folders (like in the example) or file IDs etc. If your dataset does not define splits,
   remove the `val` split and only include the `train` split. You can then remove all arguments to `_generate_examples()`.

4. **Modify Dataset Conversion Code**: Next, modify the function `_generate_examples()`. Here, your own raw data should be
   loaded, filled into the episode steps and then yielded as a packaged example. Note that the value of the first return argument,
   `episode_path` in the example, is only used as a sample ID in the dataset and can be set to any value that is connected to the
   particular stored episode, or any other random value. Just ensure to avoid using the same ID twice.

5. **Provide Dataset Description**: Next, add a bibtex citation for your dataset in `CITATIONS.bib` and add a short description
   of your dataset in `README.md` inside the dataset folder. You can also provide a link to the dataset website and please add a
   few example trajectory images from the dataset for visualization.

6. **Add Appropriate License**: Please add an appropriate license to the repository.
   Most common is the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license --
   you can copy it from [here](https://github.com/teamdigitale/licenses/blob/master/CC-BY-4.0).

That's it! You're all set to run dataset conversion. Inside the dataset directory, run:

```
proxy_on
tfds build --overwrite
```

The command line output should finish with a summary of the generated dataset (including size and number of samples).
Please verify that this output looks as expected and that you can find the generated `tfrecord` files in `~/tensorflow_datasets/<name_of_your_dataset>`.

### Parallelizing Data Processing

By default, dataset conversion is single-threaded. If you are parsing a large dataset, you can use parallel processing.
For this, replace the last two lines of `_generate_examples()` with the commented-out `beam` commands. This will use
Apache Beam to parallelize data processing. Before starting the processing, you need to install your dataset package
by filling in the name of your dataset into `setup.py` and running `pip install -e .`

Then, make sure that no GPUs are used during data processing (`export CUDA_VISIBLE_DEVICES=`) and run:

```
proxy_on
tfds build --overwrite --beam_pipeline_options="direct_running_mode=multi_processing,direct_num_workers=10"
```

You can specify the desired number of workers with the `direct_num_workers` argument.

## Visualize Converted Dataset

To verify that the data is converted correctly, please run the data visualization script from the base directory:

```
python3 visualize_dataset.py <name_of_your_dataset>
```

This will display a few random episodes from the dataset with language commands and visualize action and state histograms per dimension.
Note, if you are running on a headless server you can modify `WANDB_ENTITY` at the top of `visualize_dataset.py` and
add your own WandB entity -- then the script will log all visualizations to WandB.

## Add Transform for Target Spec

For X-embodiment training we are using specific inputs / outputs for the model: input is a single RGB camera, output
is an 8-dimensional action, consisting of end-effector position and orientation, gripper open/close and a episode termination
action.

The final step in adding your dataset to the training mix is to provide a transform function, that transforms a step
from your original dataset above to the required training spec. Please follow the two simple steps below:

1. **Modify Step Transform**: Modify the function `transform_step()` in `example_transform/transform.py`. The function
   takes in a step from your dataset above and is supposed to map it to the desired output spec. The file contains a detailed
   description of the desired output spec.

2. **Test Transform**: We provide a script to verify that the resulting **transformed** dataset outputs match the desired
   output spec. Please run the following command: `python3 test_dataset_transform.py <name_of_your_dataset>`

If the test passes successfully, you are ready to upload your dataset!

## Upload Your Data

We provide a Google Cloud bucket that you can upload your data to. First, install `gsutil`, the Google cloud command
line tool. You can follow the installation instructions [here](https://cloud.google.com/storage/docs/gsutil_install).

Next, authenticate your Google account with:

```
gcloud auth login
```

This will open a browser window that allows you to log into your Google account (if you're on a headless server,
you can add the `--no-launch-browser` flag). Ideally, use the email address that
you used to communicate with Karl, since he will automatically grant permission to the bucket for this email address.
If you want to upload data with a different email address / google account, please shoot Karl a quick email to ask
to grant permissions to that Google account!

After logging in with a Google account that has access permissions, you can upload your data with the following
command:

```
gsutil -m cp -r ~/tensorflow_datasets/<name_of_your_dataset> gs://xembodiment_data
```

This will upload all data using multiple threads. If your internet connection gets interrupted anytime during the upload
you can just rerun the command and it will resume the upload where it was interrupted. You can verify that the upload
was successful by inspecting the bucket [here](https://console.cloud.google.com/storage/browser/xembodiment_data).

The last step is to commit all changes to this repo and send Karl the link to the repo.

**Thanks a lot for contributing your data! :)**

## Errors

### Error executing an HTTP request: libcurl code 6 meaning 'Couldn't resolve host name'
```
(rlds_env) cuiluyi@h800-1:~/rlds_dataset_builder/LIBERO_10$ tfds build
INFO[build.py]: Loading dataset  from path: /data/cuiluyi/rlds_dataset_builder/LIBERO_10/LIBERO_10_dataset_builder.py
2026-02-28 04:48:02.928779: I tensorflow/core/util/port.cc:110] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
2026-02-28 04:48:02.930564: I tensorflow/tsl/cuda/cudart_stub.cc:28] Could not find cuda drivers on your machine, GPU will not be used.
2026-02-28 04:48:02.976166: I tensorflow/tsl/cuda/cudart_stub.cc:28] Could not find cuda drivers on your machine, GPU will not be used.
2026-02-28 04:48:02.976655: I tensorflow/core/platform/cpu_feature_guard.cc:182] This TensorFlow binary is optimized to use available CPU instructions in performance-critical operations.
To enable the following instructions: AVX2 AVX512F AVX512_VNNI AVX512_BF16 AVX_VNNI AMX_TILE AMX_INT8 AMX_BF16 FMA, in other operations, rebuild TensorFlow with the appropriate compiler flags.
2026-02-28 04:48:03.557551: W tensorflow/compiler/tf2tensorrt/utils/py_utils.cc:38] TF-TRT Warning: Could not find TensorRT
2026-02-28 04:48:03.975736: W tensorflow/core/common_runtime/gpu/gpu_device.cc:1960] Cannot dlopen some GPU libraries. Please make sure the missing libraries mentioned above are installed properly if you would like to use GPU. Follow the guide at https://www.tensorflow.org/install/gpu for how to download and setup the required libraries for your platform.
Skipping registering GPU devices...
2026-02-28 04:48:04.344264: W tensorflow/tsl/platform/cloud/google_auth_provider.cc:184] All attempts to get a Google authentication bearer token failed, returning an empty token. Retrieving token from files failed with "NOT_FOUND: Could not locate the credentials file.". Retrieving token from GCE failed with "FAILED_PRECONDITION: Error executing an HTTP request: libcurl code 6 meaning 'Couldn't resolve host name', error details: Could not resolve host: metadata.google.internal".
2026-02-28 04:49:05.349720: E tensorflow/tsl/platform/cloud/curl_http_request.cc:610] The transmission  of request 0x5a84a30dc010 (URI: https://www.googleapis.com/storage/v1/b/tfds-data/o/dataset_info%2Flibero10%2F1.0.0?fields=size%2Cgeneration%2Cupdated) has been stuck at 0 of 0 bytes for 61 seconds and will be aborted. CURL timing information: lookup time: 0.007674 (No error), connect time: 0 (No error), pre-transfer time: 0 (No error), start-transfer time: 0 (No error)
2026-02-28 04:50:07.687723: E tensorflow/tsl/platform/cloud/curl_http_request.cc:610] The transmission  of request 0x5a84a30dc010 (URI: https://www.googleapis.com/storage/v1/b/tfds-data/o/dataset_info%2Flibero10%2F1.0.0?fields=size%2Cgeneration%2Cupdated) has been stuck at 0 of 0 bytes for 61 seconds and will be aborted. CURL timing information: lookup time: 0.006134 (No error), connect time: 0 (No error), pre-transfer time: 0 (No error), start-transfer time: 0 (No error)
```
**解决办法**
It request google for datainfo and a error msg should be returned and then it build the datainfo from _info() method.

so just
```
proxy_on
```
to let the request be sent to google maybe it works