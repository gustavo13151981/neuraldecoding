import pickle
from pathlib import Path
import tensorflow as tf
import neo
import numpy as np
# from sklearn.metrics import confusion_matrix
# import matplotlib.pyplot as plt
# import seaborn as sns
# from numba import njit, prange
# import time
from sklearn.model_selection import train_test_split, StratifiedKFold
from tqdm import tqdm
from keras import backend as K
from viziphant.rasterplot import rasterplot

from sklearn.utils import resample
import astropy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.ticker import MaxNLocator
import seaborn as sns
from datetime import datetime
from astropy.stats import bootstrap
import sklearn
from instruments.helpers.util import simple_xy_axes, set_font_axes
from instruments.helpers.neural_analysis_helpers import get_soundonset_alignedraster, split_cluster_base_on_segment
from instruments.helpers.euclidean_classification_minimal_function import classify_sweeps
# Import standard packages
import numpy as np
from scipy import io
from scipy import stats
import pickle

# If you would prefer to load the '.h5' example file rather than the '.pickle' example file. You need the deepdish package
# import deepdish as dd

# Import function to get the covariate matrix that includes spike history from previous bins
from Neural_Decoding.preprocessing_funcs import get_spikes_with_history
import Neural_Decoding
# Import metrics
from Neural_Decoding.metrics import get_R2
from Neural_Decoding.metrics import get_rho

# Import decoder functions
from Neural_Decoding.decoders import LSTMDecoder, LSTMClassification


def sound_onset_raster(blocks, stream ='BB_3'):

    tarDir = Path(f'E:/rastersms4spikesortinginter/F1815_Cruella/figsonset/')
    saveDir = tarDir
    saveDir.mkdir(exist_ok=True, parents=True)

    binsize = 0.01
    window = [0, 0.6]

    clust_ids = [st.annotations['cluster_id'] for st in blocks[0].segments[0].spiketrains if
                 st.annotations['group'] != 'noise']

    cluster_id_droplist = np.empty([])
    # for cluster_id in clust_ids:
    #     print('now starting cluster')
    #     print(cluster_id)
    #
    #     filter = ['No Level Cue']  # , 'Non Correction Trials']
    #
    #     # try:
    #     new_blocks = split_cluster_base_on_segment(blocks, cluster_id)

    # #print the cluster ids in new_blocks and blocks
    # for block in blocks:
    #     for segment in block.segments:
    #         for st in segment.spiketrains:
    #             print(st.annotations['cluster_id'])
    # for block in new_blocks:
    #     for segment in block.segments:
    #         for st in segment.spiketrains:
    #             print(st.annotations['cluster_id'])

    for cluster_id in clust_ids:
        print('now starting cluster')
        print(cluster_id)

        filter = ['No Level Cue']  # , 'Non Correction Trials']

        try:
            # new_blocks = split_cluster_base_on_segment(blocks, cluster_id)
            raster_target = get_soundonset_alignedraster(blocks, cluster_id, df_filter=filter)

        # plt.hist(raster_target, bins=100)
        #for each time in the raster target (second in the tuple, plot a dot at the time and the trial number)
        # for time in raster_target:
        #     plt.scatter(time[1], time[0], s=0.5)
        #plot the distribution of times, the second tuple in the list

            raster_target = raster_target.reshape(raster_target.shape[0], )
        except:
            print('No relevant target firing')
            cluster_id_droplist = np.append(cluster_id_droplist, cluster_id)
            continue

        bins = np.arange(window[0], window[1], binsize)


        unique_trials_targ = np.unique(raster_target['trial_num'])
        raster_targ_reshaped = np.empty([len(unique_trials_targ), len(bins) - 1])
        count = 0
        for trial in (unique_trials_targ):
            raster_targ_reshaped[count, :] = \
            np.histogram(raster_target['spike_time'][raster_target['trial_num'] == trial], bins=bins,
                         range=(window[0], window[1]))[0]
            count += 1

        spiketrains = []
        for trial_id in unique_trials_targ:
            selected_trials = raster_target[raster_target['trial_num'] == trial_id]
            spiketrain = neo.SpikeTrain(selected_trials['spike_time'], units='s', t_start=min(selected_trials['spike_time']), t_stop=max(selected_trials['spike_time']))
            spiketrains.append(spiketrain)

        print(spiketrains)
        try:
        #print the distribution of times
        # fig, ax = plt.figure()
        # plt.hist(raster_target['spike_time'], bins=100, ax = ax)
        # plt.suptitle(f'distribution firings for cruella,  clus id '+ str(cluster_id) +'stream:'+ f'{stream}', fontsize = 12)
        #
        # plt.show()

            fig,ax = plt.subplots(2, figsize=(10, 5))
            #ax.scatter(raster_target['spike_time'], np.ones_like(raster_target['spike_time']))
            rasterplot(spiketrains, c='black', histogram_bins=100, axes=ax, s=0.5 )

            ax[0].set_ylabel('trial')
            ax[0].set_xlabel('Time relative to word presentation (s)')
            custom_xlim = (-0.1, 0.6)

            plt.setp(ax, xlim=custom_xlim)

            plt.suptitle(f'Sound onset firings for cruella,  clus id '+ str(cluster_id) +'stream:'+ f'{stream}', fontsize = 12)
            plt.savefig(
                str(saveDir) + f'/soundonset_clusterid_{stream}_' + str(cluster_id)+ '.png')
            plt.show()
        except:
            print('no spikes')
            continue



    return



def generate_rasters(dir):
    datapath = Path(f'E:\ms4output2\F1815_Cruella\BB4BB5_cruella_26092023\BB4BB5_cruella_26092023_BB4BB5_cruella_26092023_BB_4\mountainsort4\phy/')
    stream = str(datapath).split('\\')[-3]
    stream = stream[-4:]
    print(stream)
    with open(datapath / 'blocks.pkl', 'rb') as f:
        blocks = pickle.load(f)
    scores = {}
    probewords_list = [(2,2),]


    for probeword in probewords_list:
        print('now starting')
        print(probeword)
        for talker in [1]:

            # target_vs_probe_with_raster(blocks, talker=talker,probewords=probeword,pitchshift=False)
            sound_onset_raster(blocks,stream = stream)




def main():

    directories = ['zola_2022']  # , 'Trifle_July_2022']
    for dir in directories:
        generate_rasters(dir)


if __name__ == '__main__':
    main()
