import numpy as np
import matplotlib.pyplot as plt
import os
from pathlib import Path


def run_scores_and_plot(file_path, pitchshift, output_folder, ferretname,  stringprobewordindex=str(2), talker='female', totalcount = 0):
    if talker == 'female':
        talker_string = 'onlyfemaletalker'
        talkerinput = 'talker1'
    else:
        talker_string = 'onlymaletalker'
        talkerinput = 'talker2'
        # scores_2022_cruella_2_cruella_probe_bs
    try:
        scores = np.load(
            str(file_path) + '/' + r'scores_2022_' + ferretname + '_' + stringprobewordindex + '_' + ferretname + '_probe_bs.npy',
            allow_pickle=True)[()]
    except:
        print('error loading scores: ' + str(file_path) + '/' + r'scores_2022_' + ferretname + '_' + stringprobewordindex + '_' + ferretname + '_probe_bs.npy')
        return
    rec_name = file_path.parts[-2]
    stream = file_path.parts[-1]
    probeword = int(stringprobewordindex)
    if pitchshift == 'nopitchshiftvspitchshift':
        pitchshift_option = False
    elif pitchshift == 'pitchshift':
        pitchshift_option = True

    if probeword == 4 and pitchshift_option == False:
        probeword_text = 'when a'
        color_option = 'green'
    elif probeword == 4 and pitchshift_option == True:
        probeword_text = 'when a'
        color_option = 'lightgreen'

    elif probeword == 1 and pitchshift_option == False:
        probeword_text = 'instruments'
        color_option = 'black'
    elif probeword == 1 and pitchshift_option == True:
        probeword_text = 'instruments'
        color_option = 'black'

    elif probeword == 2 and pitchshift_option == False:
        probeword_text = 'craft'
        color_option = 'deeppink'
    elif probeword == 2 and pitchshift_option == True:
        probeword_text = 'craft'
        color_option = 'pink'

    elif probeword == 3 and pitchshift_option == False:
        probeword_text = 'in contrast'
        color_option = 'mediumpurple'
    elif probeword == 3 and pitchshift_option == True:
        probeword_text = 'in contrast'
        color_option = 'purple'

    elif probeword == 5 and pitchshift_option == False:
        probeword_text = 'accurate'
        color_option = 'olivedrab'

    elif probeword == 5 and pitchshift_option == True:
        probeword_text = 'accurate'
        color_option = 'limegreen'
    elif probeword == 6 and pitchshift_option == False:
        probeword_text = 'pink noise'
        color_option = 'navy'
    elif probeword == 6 and pitchshift_option == True:
        probeword_text = 'pink noise'
        color_option = 'lightblue'
    elif probeword == 7 and pitchshift_option == False:
        probeword_text = 'of science'
        color_option = 'coral'
    elif probeword == 7 and pitchshift_option == True:
        probeword_text = 'of science'
        color_option = 'orange'
    elif probeword == 8 and pitchshift_option == False:
        probeword_text = 'rev. instruments'
        color_option = 'plum'
    elif probeword == 8 and pitchshift_option == True:
        probeword_text = 'rev. instruments'
        color_option = 'darkorchid'
    elif probeword == 9 and pitchshift_option == False:
        probeword_text = 'boats'
        color_option = 'cornflowerblue'
    elif probeword == 9 and pitchshift_option == True:
        probeword_text = 'boats'
        color_option = 'royalblue'
    elif probeword == 10 and pitchshift_option == False:
        probeword_text = 'today'
        color_option = 'gold'
    elif probeword == 10 and pitchshift_option == True:
        probeword_text = 'today'
        color_option = 'yellow'

    #for each cluster plot their scores over time
    num_clusters = len(scores[talkerinput]['target_vs_probe'][pitchshift]['cluster_id'])
    num_cols = int(num_clusters / 2) + 1  # Calculate the number of columns
    if len (scores[talkerinput]['target_vs_probe'][pitchshift]['cluster_id']) == 1:
        fig, axs = plt.subplots( figsize=(50, 15))
    else:
        fig, axs = plt.subplots(2, num_cols, figsize=(50, 15))

    index = -1  # Initialize index here

    color_list = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
    # fig, axs = plt.subplots(2, int(len(scores[talkerinput]['target_vs_probe'][pitchshift]['cluster_id'])/2)+1, figsize=(50,15))
    for cluster in scores[talkerinput]['target_vs_probe'][pitchshift]['cluster_id']:
        #get the scores
        index += 1

        cluster_scores = scores[talkerinput]['target_vs_probe'][pitchshift]['lstm_balancedaccuracylist'][index]
        #generate the timepoints based on the bin width of 4ms
        timepoints = np.arange(0, (len(cluster_scores) / 100)*4, 0.04)
        if len (scores[talkerinput]['target_vs_probe'][pitchshift]['cluster_id']) == 1:
            ax = axs
        else:
            row = index // num_cols
            col = index % num_cols
            # Assign ax based on row and column
            ax = axs[row, col]

        ax.plot(timepoints, cluster_scores, c = color_option)
        # ax.set(xlabel='time since target word (s)', ylabel='balanced accuracy',
        #     title=f'unit: {cluster}_{rec_name}_{stream}')
        ax.set_ylim([0, 1])
        ax.set_title('unit: ' + str(cluster) + ' ' + rec_name + ' ' + stream, fontsize = 20)

        ax.set_xlabel('time (s)', fontsize = 20)
        ax.set_ylabel('balanced accuracy', fontsize = 20)
        plt.xticks(fontsize = 20)
        plt.yticks(fontsize = 20)

        ax.grid()
    if pitchshift_option == True:
        pitchshift_text = 'inter-roved F0'
    else:
        pitchshift_text = 'control F0'
    plt.suptitle('LSTM balanced accuracy for ' + ferretname + ' ' + pitchshift_text + ' ' + talker+ ' target vs. ' + probeword_text, fontsize = 30)
    output_folder2 = output_folder + '/' + rec_name + '/' + stream + '/'
    if not os.path.exists(output_folder2):
        os.makedirs(output_folder2)
    fig.savefig(output_folder2 + '/' +ferretname+ 'multipanel' +pitchshift+ stringprobewordindex +'_'+probeword_text+'talker_'+talker+ '.png', bbox_inches='tight')


    return scores








if __name__ == '__main__':
    print('hello')

    big_folder = Path('G:/results_decodingovertime_17112023/F1815_Cruella/')
    animal = big_folder.parts[-1]
    # file_path = 'D:\decodingresults_overtime\F1815_Cruella\lstm_kfold_balac_01092023_cruella/'
    output_folder = f'G:/decodingovertime_figures/{animal}/'
    #make the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    ferretname = 'cruella'
    #typo in my myriad code, this should really be relabelled as nopitchshift
    pitchshift = 'nopitchshiftvspitchshift'
    stringprobewordlist = [2,3,4,5,6,7,8,9,10]
    # probewordlist = [ (5, 6),(2, 2), (42, 49), (32, 38), (20, 22)]
    totalcount = 0
    talkerlist = ['female']
    #find all the subfolders, all the folders that contain the data

    subfolders = [f for f in big_folder.glob('**/BB*/') if f.is_dir()]



    for file_path in subfolders:
        #get the subfolders
        print(file_path)
        #get the talke
        for talker in talkerlist:
            for probeword in stringprobewordlist:

                print(probeword)
                run_scores_and_plot(file_path, pitchshift, output_folder, ferretname, stringprobewordindex=str(probeword), talker = talker, totalcount = totalcount )
                totalcount = totalcount + 1

