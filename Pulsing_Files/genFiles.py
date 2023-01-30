import numpy as np
import pandas as pd


#filename="Pulsing_Files/cfg_mat128x54_00.txt"
filename="cfg_mat128x54_01_R424.txt"

def cfg_read(filename="cfg_mat128x54_01_R424.txt"):
    sf = pd.read_csv(filename, dtype=str, sep=' ', comment=":",header = None)
    nf=sf.apply(lambda x: "".join(x), axis =1)
    bitmap=nf.str.split('', expand=True)
    table=np.asarray(bitmap)[:,1:-1]
    tab=table.astype(int)
    result=np.where(tab==1)
    print([(i,j) for i,j in list(zip(result[0], result[1]))])
    return tab

#np.zeros((128,54))
def list_to_8bit(line=[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]):
    res=''
    for i,bit in enumerate(line):
        res+=str(bit)
        if (i+1)%8==0:
            res+=' '
    return res

filename="cfg.txt"
def cfg_write(tab=np.zeros((128,54),dtype=int), filename="cfg.txt"):
    lstr=[list_to_8bit(line) for line in tab]
    file=open(filename, 'w')
    result=np.where(tab==1)
    file.write(":cfg_write {}\n:".format(len(result[0])))
    file.write("".join(["({},{})".format(i,j) for i,j in list(zip(result[0], result[1]))])+('\n'))
    file.write("\n".join(lstr))
    file.close()

# from which one easier to filter ?    
# picmic_adress_table.csv
# ROnb_xyp1.txt

#print(res)
filename="cfg_DiscP123_9x9.txt"
cfg_write(filename=filename)


tab=cfg_read(filename=filename)


#pixels=[[15,6],[35,103],[28,68]]
R = [[37,113],[14,1],[31,83],[28,68],[35,103],[15,6],[21,36],[28,71],[35,106]]
B = [[24,76],[31,42],[28,57],[39,4],[37,12],[26,68],[19,102],[22,87],[33,34]]
Y = [[18,62],[21,62],[24,62],[26,63],[29,63],[32,63],[35,63],[38,63],[41,63]]
pixels=R+B+Y
#print(pixels)

for row,col in pixels:
    print("{}".format((row,col)))
    tab[col,row]=1

# for i,j in pixels:
#     tab[j,i]=1
cfg_write(tab, filename) #<= write tab with activated values
cfg_read( filename) #<= check back
#cfg_read("Pulsing_Files/cfg_mat128x54_01_R424.txt")
