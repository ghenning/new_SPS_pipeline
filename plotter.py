import matplotlib.pyplot as plt
import numpy as np
import os

def plotstuff(ALL_SPS,GOOD_SPS,WF_CANDS):

    # path to dir
    plot_dir = os.path.dirname(ALL_SPS)

    # interactive mode off
    plt.ioff() 
    plt.close()

    # check if txt files exist
    is_all = os.path.isfile(ALL_SPS)
    is_good = os.path.isfile(GOOD_SPS)
    is_wf = os.path.isfile(WF_CANDS)

    # grab data to plot

    # all cands
    if is_all:
        all_dat = np.loadtxt(ALL_SPS)
        if np.ndim(all_dat)==1: all_dat = np.zeros((1,5))
        all_DM = all_dat[:,0]
        all_SN = all_dat[:,1]
        all_T = all_dat[:,2]

    # good cands
    if is_good:
        good_dat = np.loadtxt(GOOD_SPS)
        if np.ndim(good_dat)==1: good_dat = np.zeros((1,5))
        good_DM = good_dat[:,0]
        good_SN = good_dat[:,1]
        good_T = good_dat[:,2]

    # wf cands
    if is_wf:
        wf_dat = np.loadtxt(WF_CANDS)
        if np.ndim(wf_dat)==1: wf_dat = np.zeros((1,5))
        wf_DM = wf_dat[:,0]
        wf_SN = wf_dat[:,1]
        wf_T = wf_dat[:,2]
    
    # plot DM vs T, color coded and SN weighted
    fig = plt.figure(1)
    ax = fig.add_subplot(1,1,1)

    # plot all cands
    if is_all:
        ax.scatter(all_T,all_DM,marker='o',color='black',linewidth=.5,
            facecolor='none',s=all_SN+.5)#,label='All events')

    # plot good cands
    if is_good and np.count_nonzero(good_dat)>0:
        good_SN[good_SN>40] = 40
        ax.scatter(good_T,good_DM,marker='o',color='blue',linewidth=.5,
            facecolor='none',s=2.*good_SN+.5)#,(sn-5)**2+.5,label='High SN')

    # plot wf cands
    if is_wf and np.count_nonzero(wf_dat)>0:
        ax.scatter(wf_T,wf_DM,marker='x',color='red',linewdith=.5,
            s=2)#,label='waterfall cands')

    # save plot
    ax.set_xlabel(r"$T$",fontsize=18)
    ax.set_ylabel("DM",fontsize=18)
    #ax.legend(loc='upper center',ncol=3,frameon=False)
    plot_out = os.path.join(plot_dir,"DM_SN_T_COLORS.png")
    plt.tight_layout()
    plt.savefig(plot_out,format='png',dpi=200)
    plt.close(fig)
    plt.close('all')
    
    # plot modified single pulse search plot
    fig = plt.figure(2)
    ax = fig.add_subplot(1,1,1)
    ax.axis('off')
    
    # SN histogram
    ax2 = fig.add_subplot(3,3,1)
    if is_good:
        ax2.hist(good_SN,lw=1,color='blue')
    ax2.set_xlabel("SN",fontsize=10)
    ax2.set_ylabel("#Pulses",fontsize=10)

    # DM histogram
    ax3 = fig.add_subplot(3,3,2)
    if is_good:
        ax3.hist(good_DM,lw=1,color='blue')
    ax3.set_xlabel("DM",fontsize=10)
    ax3.set_ylabel("#Pulses",fontsize=10)

    # DM vs SN
    ax4 = fig.add_subplot(3,3,3)
    if is_all:
        ax4.plot(all_DM,all_SN,'k.',ms=1)
    if is_good:
        ax4.plot(good_DM,good_SN,'b.',ms=1)
    ax4.set_xlabel("DM",fontsize=10)
    ax4.set_ylabel("SN",fontsize=10)

    # DM vs Time
    ax5 = fig.add_subplot(3,3,(4,9))
    if is_good and np.count_nonzero(good_dat)>0:
        good_SN[good_SN>40] = 40
        ax5.scatter(good_T,good_DM,color='blue',linewidth=.5,
            facecolor='none',s=2.*good_SN+.5)
    if is_wf and np.count_nonzero(wf_dat)>0:
        ax5.scatter(wf_T,wf_DM,marker='x',color='red',linewidth=.5,
            s=2)
    ax5.set_xlabel(r"$T$",fontsize=14)
    ax5.set_ylabel("DM",fontsize=14)
    fig.subplots_adjust(wspace=.7,hspace=.7)

    # save plot
    out = os.path.join(plot_dir,"SPS_plot.png")
    plt.tight_layout()
    plt.savefig(out,format='png',dpi=200)
    plt.close(fig)
    plt.close('all')
    
   
        
        



    

    
