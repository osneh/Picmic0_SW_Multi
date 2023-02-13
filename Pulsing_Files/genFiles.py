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
##filename="cfg_DiscP123_9R-9B-30H.txt"
#filename="cfg_DiscP123_Yellow_213.txt"
#filename="cfg_DiscP123_Yellow_426.txt"
#filename="cfg_DiscP123_Yellow_639.txt"
#filename="cfg_DiscP123_Yellow_852.txt"
#filename="cfg_DiscP123_Rissing_213.txt"
#filename="cfg_DiscP123_Rissing_426.txt"
#filename="cfg_DiscP123_Rissing_639.txt"
filename="cfg_DiscP123_Rissing_852.txt"
cfg_write(filename=filename)


tab=cfg_read(filename=filename)


#pixels=[[15,6],[35,103],[28,68]]
# #### BENDING #### #
#list0= [[10, 18], [3, 52], [11, 14], [4, 48], [12, 10], [8, 29], [5, 44], [6, 40], [7, 33], [9, 25], [1, 63], [7, 36], [4, 51], [2, 59], [13, 6], [11, 17], [12, 13], [13, 9], [8, 32], [10, 24], [6, 43], [9, 28], [14, 5], [3, 58], [4, 54], [12, 16], [2, 65], [11, 20], [15, 1], [3, 61], [5, 50], [7, 42], [14, 8], [9, 31], [8, 38], [4, 57], [11, 23], [9, 34], [5, 53], [12, 19], [2, 68], [10, 30], [6, 49], [14, 11], [13, 15], [8, 41], [9, 37], [12, 22], [6, 52], [15, 7], [14, 14], [13, 18], [16, 3], [11, 29], [7, 48], [3, 67], [4, 63], [6, 55], [15, 10], [17, 2], [13, 21], [11, 32], [5, 59], [3, 70], [4, 66], [16, 9], [7, 51], [12, 28], [15, 13], [13, 24], [14, 20], [4, 69], [17, 5], [9, 43], [12, 31], [8, 50], [18, 1], [13, 27], [17, 8], [5, 65], [15, 16], [7, 57], [10, 42], [16, 12], [6, 61], [8, 53], [16, 15], [6, 64], [15, 19], [18, 4], [10, 45], [5, 68], [17, 11], [8, 56], [19, 3], [11, 41], [14, 26], [4, 75], [13, 33], [9, 52], [7, 63], [11, 44], [10, 48], [4, 78], [8, 59], [12, 40], [18, 10], [20, 2], [13, 36], [16, 21], [14, 32], [15, 25], [6, 70], [7, 66], [15, 28], [11, 47], [18, 13], [12, 43], [13, 39], [10, 54], [16, 24], [9, 58], [21, 1], [20, 5], [15, 31], [17, 20], [14, 35], [5, 80], [10, 57], [20, 8], [19, 12], [14, 38], [6, 76], [18, 19], [15, 34], [21, 4], [9, 64], [6, 79], [10, 60], [8, 68], [20, 11], [18, 22], [7, 75], [17, 26], [19, 18], [16, 33], [12, 52], [6, 82], [20, 14], [13, 48], [17, 29], [9, 67], [10, 63], [7, 78], [11, 59], [21, 10], [12, 55], [19, 21], [14, 44], [20, 17], [6, 85], [18, 28], [9, 70], [8, 77], [11, 62], [7, 81], [12, 58], [21, 13], [24, 1], [16, 39], [19, 24], [15, 43], [10, 69], [17, 35], [22, 12], [7, 84], [14, 50], [19, 27], [12, 61], [9, 76], [8, 80], [7, 87], [10, 72], [8, 83], [20, 23], [16, 45], [24, 4], [15, 49], [14, 53], [17, 41], [19, 30], [10, 75], [14, 56], [21, 22], [9, 79], [13, 60], [18, 37], [25, 3], [10, 78], [19, 33], [21, 25], [13, 63], [11, 74], [14, 59], [24, 10], [17, 44], [18, 40], [23, 17], [10, 81], [22, 21], [16, 51], [14, 62], [25, 9]]

#list1= [[21, 28], [26, 5], [8, 92], [16, 54], [11, 77], [9, 88], [17, 50], [15, 58], [10, 84], [27, 1], [20, 35], [25, 12], [15, 61], [8, 95], [14, 65], [23, 23], [27, 4], [12, 76], [17, 53], [22, 30], [15, 64], [8, 98], [13, 72], [9, 94], [13, 75], [12, 79], [18, 49], [19, 45], [16, 60], [10, 90], [25, 18], [21, 37], [26, 14], [28, 3], [23, 29], [27, 10], [11, 86], [17, 59], [24, 25], [29, 2], [18, 55], [21, 40], [16, 66], [11, 89], [23, 32], [24, 28], [9, 100], [28, 9], [12, 85], [27, 13], [15, 73], [11, 92], [12, 88], [16, 69], [20, 50], [10, 99], [9, 103], [14, 80], [11, 95], [18, 61], [21, 46], [17, 65], [27, 16], [15, 76], [12, 91], [13, 87], [20, 53], [14, 83], [21, 49], [10, 102], [18, 64], [29, 11], [17, 68], [28, 15], [26, 26], [11, 98], [19, 60], [10, 105], [28, 18], [25, 33], [30, 7], [12, 97], [14, 86], [24, 37], [11, 101], [22, 48], [13, 93], [17, 74], [16, 78], [32, 2], [14, 89], [31, 6], [12, 100], [21, 55], [29, 17], [20, 62], [18, 70], [14, 92], [15, 85], [28, 24], [24, 43], [18, 73], [27, 28], [22, 54], [21, 58], [13, 99], [15, 88], [31, 12], [28, 27], [33, 1], [18, 76], [14, 95], [26, 38], [21, 61], [30, 19], [12, 106], [27, 34], [28, 30], [31, 15], [23, 53], [24, 49], [33, 7], [12, 109], [17, 83], [32, 11], [21, 64], [34, 3], [21, 67], [30, 22], [13, 105], [23, 56], [31, 18], [26, 44], [32, 14], [27, 40], [33, 10], [35, 2], [17, 89], [14, 104], [16, 93], [18, 85], [32, 17], [20, 74], [12, 115], [20, 77], [34, 9], [28, 39], [27, 43], [26, 47], [18, 88], [32, 20], [15, 103], [30, 31], [26, 50], [22, 69], [19, 84], [12, 118], [16, 99], [24, 61], [36, 4], [28, 42], [20, 80], [19, 87], [17, 95], [20, 83], [23, 68], [25, 57], [30, 34], [33, 19], [28, 45], [33, 22], [35, 11], [17, 98], [32, 26], [29, 41], [31, 33], [17, 101], [34, 18], [16, 105], [18, 97], [36, 10], [29, 44], [26, 59], [32, 29], [30, 40], [31, 36], [25, 63], [15, 112], [35, 17], [22, 81], [25, 66], [27, 55], [21, 85], [23, 77], [28, 51], [29, 47], [33, 28], [34, 24], [18, 103], [24, 73], [28, 54], [27, 58], [38, 5], [21, 88], [34, 27], [36, 16], [24, 76], [31, 42], [28, 57], [39, 4], [37, 12], [26, 68], [19, 102]]

#list2= [[22, 87], [33, 34], [31, 45], [16, 117], [29, 53], [38, 11], [18, 109], [20, 98], [19, 105], [21, 94], [29, 56], [28, 60], [25, 75], [31, 48], [37, 18], [32, 44], [38, 14], [27, 67], [18, 112], [25, 78], [36, 25], [20, 104], [33, 40], [40, 6], [24, 85], [27, 70], [25, 81], [35, 32], [22, 96], [36, 28], [31, 51], [28, 66], [23, 92], [39, 13], [33, 43], [34, 39], [41, 5], [31, 54], [17, 122], [32, 50], [28, 69], [25, 84], [23, 95], [41, 8], [30, 61], [17, 125], [19, 114], [37, 27], [19, 117], [21, 106], [32, 53], [30, 64], [22, 102], [20, 113], [36, 34], [31, 60], [32, 56], [18, 124], [38, 26], [28, 75], [26, 86], [20, 116], [39, 22], [23, 101], [24, 97], [25, 93], [18, 127], [33, 55], [27, 82], [42, 10], [39, 25], [21, 112], [30, 70], [22, 108], [31, 66], [38, 32], [21, 115], [23, 104], [22, 111], [29, 77], [30, 73], [34, 54], [31, 69], [20, 122], [23, 107], [19, 126], [24, 103], [28, 84], [38, 35], [35, 50], [37, 42], [26, 95], [27, 91], [39, 31], [22, 114], [38, 38], [30, 76], [29, 83], [41, 23], [28, 87], [25, 102], [27, 94], [22, 117], [34, 60], [37, 45], [33, 64], [24, 109], [33, 67], [39, 37], [23, 116], [41, 29], [32, 71], [21, 124], [35, 59], [42, 25], [25, 108], [26, 101], [33, 70], [40, 36], [36, 55], [22, 123], [23, 119], [41, 32], [35, 62], [28, 96], [32, 77], [36, 58], [43, 24], [25, 111], [30, 88], [29, 92], [33, 73], [26, 107], [35, 65], [31, 84], [39, 46], [27, 103], [33, 76], [38, 50], [40, 42], [30, 91], [25, 114], [32, 80], [26, 110], [34, 72], [25, 117], [32, 83], [37, 57], [39, 49], [43, 30], [30, 94], [28, 102], [38, 56], [24, 124], [39, 52], [44, 26], [29, 101], [31, 90], [25, 120], [44, 29], [41, 44], [30, 97], [34, 78], [35, 74], [31, 93], [26, 116], [37, 63], [32, 89], [38, 59], [39, 55], [40, 51], [29, 104], [30, 100], [38, 62], [28, 111], [32, 92], [44, 32], [37, 66], [25, 126], [44, 35], [33, 88], [29, 107], [40, 54], [36, 73], [27, 118], [38, 65], [32, 95], [31, 99], [28, 114], [42, 46], [41, 53], [45, 34], [38, 68], [34, 87], [30, 106], [46, 30], [43, 45], [44, 38], [39, 64], [29, 113], [37, 75], [45, 37], [30, 109], [31, 105], [27, 124], [44, 41], [41, 56], [33, 97], [28, 120], [43, 48], [34, 93], [41, 59], [36, 82]]

#list3= [[44, 44], [31, 108], [27, 127], [32, 104], [35, 89], [45, 40], [38, 74], [44, 47], [39, 70], [38, 77], [36, 85], [31, 111], [39, 73], [33, 100], [36, 88], [43, 54], [28, 126], [33, 103], [35, 92], [29, 122], [41, 65], [42, 61], [32, 110], [30, 118], [33, 106], [45, 46], [37, 87], [30, 121], [41, 68], [34, 102], [43, 57], [45, 49], [46, 45], [42, 64], [39, 79], [43, 60], [35, 98], [40, 75], [41, 71], [31, 120], [42, 67], [37, 90], [34, 105], [44, 56], [40, 78], [36, 97], [44, 59], [33, 112], [45, 55], [41, 74], [39, 82], [47, 44], [38, 89], [43, 66], [37, 93], [35, 104], [40, 81], [32, 119], [48, 43], [38, 92], [39, 85], [41, 77], [33, 115], [31, 126], [45, 58], [43, 69], [33, 118], [40, 84], [34, 114], [38, 95], [42, 76], [48, 46], [41, 80], [39, 91], [35, 110], [43, 72], [49, 42], [34, 117], [44, 68], [47, 53], [45, 64], [41, 83], [42, 79], [48, 49], [40, 90], [47, 56], [37, 105], [35, 113], [36, 109], [46, 60], [43, 75], [46, 63], [39, 97], [34, 120], [38, 101], [36, 112], [49, 48], [40, 93], [41, 89], [45, 70], [38, 104], [49, 51], [48, 55], [42, 85], [37, 108], [47, 62], [37, 111], [48, 58], [35, 119], [39, 100], [38, 107], [49, 54], [42, 88], [35, 122], [43, 84], [47, 65], [50, 50], [36, 118], [41, 95], [46, 69], [40, 99], [38, 110], [42, 91], [45, 76], [35, 125], [50, 53], [37, 117], [44, 83], [39, 106], [36, 121], [38, 113], [39, 109], [48, 64], [49, 60], [41, 98], [50, 56], [44, 86], [37, 120], [48, 67], [38, 116], [36, 124], [42, 97], [45, 82], [49, 63], [46, 78], [40, 108], [50, 59], [48, 70], [41, 104], [37, 123], [45, 85], [43, 93], [44, 89], [50, 62], [40, 111], [43, 96], [38, 119], [41, 107], [51, 58], [38, 122], [39, 115], [48, 73], [45, 88], [50, 65], [44, 92], [42, 103], [39, 118], [40, 114], [47, 80], [48, 76], [42, 106], [44, 95], [38, 125], [46, 87], [51, 61], [40, 117], [39, 121], [51, 64], [43, 102], [47, 83], [45, 94], [42, 109], [48, 79], [50, 71], [43, 105], [41, 113], [44, 101], [49, 75], [51, 67], [52, 63], [39, 124], [48, 82], [49, 78], [43, 108], [45, 97], [50, 74], [42, 112], [46, 93], [39, 127], [45, 100], [51, 70], [46, 96], [52, 66], [41, 119], [47, 92], [51, 73], [44, 107], [40, 126], [45, 103], [53, 62], [42, 118], [48, 88], [53, 65]]

## #### YELLOW #### ##  
#list0= [[2, 0], [5, 0], [8, 0], [11, 0], [14, 0], [17, 0], [19, 1], [22, 1], [25, 1], [28, 1], [31, 1], [34, 1], [37, 1], [39, 2], [42, 2], [45, 2], [48, 2], [51, 2], [3, 2], [6, 2], [8, 3], [11, 3], [14, 3], [17, 3], [20, 3], [23, 3], [25, 4], [28, 4], [31, 4], [34, 4], [37, 4], [40, 4], [43, 4], [45, 5], [48, 5], [51, 5], [3, 5], [6, 5], [9, 5], [12, 5], [14, 6], [17, 6], [20, 6], [23, 6], [26, 6], [29, 6], [31, 7], [34, 7], [37, 7], [40, 7], [43, 7], [46, 7], [49, 7], [51, 8], [3, 8], [6, 8], [9, 8], [12, 8], [15, 8], [18, 8], [20, 9], [23, 9], [26, 9], [29, 9], [32, 9], [35, 9], [37, 10], [40, 10], [43, 10], [46, 10], [49, 10], [1, 10], [4, 10], [6, 11], [9, 11], [12, 11], [15, 11], [18, 11], [21, 11], [24, 11], [26, 12], [29, 12], [32, 12], [35, 12], [38, 12], [41, 12], [43, 13], [46, 13], [49, 13], [1, 13], [4, 13], [7, 13], [10, 13], [12, 14], [15, 14], [18, 14], [21, 14], [24, 14], [27, 14], [30, 14], [32, 15], [35, 15], [38, 15], [41, 15], [44, 15], [47, 15], [49, 16], [1, 16], [4, 16], [7, 16], [10, 16], [13, 16], [16, 16], [18, 17], [21, 17], [24, 17], [27, 17], [30, 17], [33, 17], [36, 17], [38, 18], [41, 18], [44, 18], [47, 18], [50, 18], [2, 18], [4, 19], [7, 19], [10, 19], [13, 19], [16, 19], [19, 19], [22, 19], [24, 20], [27, 20], [30, 20], [33, 20], [36, 20], [39, 20], [42, 20], [44, 21], [47, 21], [50, 21], [2, 21], [5, 21], [8, 21], [10, 22], [13, 22], [16, 22], [19, 22], [22, 22], [25, 22], [28, 22], [30, 23], [33, 23], [36, 23], [39, 23], [42, 23], [45, 23], [48, 23], [50, 24], [2, 24], [5, 24], [8, 24], [11, 24], [14, 24], [16, 25], [19, 25], [22, 25], [25, 25], [28, 25], [31, 25], [34, 25], [36, 26], [39, 26], [42, 26], [45, 26], [48, 26], [51, 26], [3, 26], [5, 27], [8, 27], [11, 27], [14, 27], [17, 27], [20, 27], [22, 28], [25, 28], [28, 28], [31, 28], [34, 28], [37, 28], [40, 28], [42, 29], [45, 29], [48, 29], [51, 29], [3, 29], [6, 29], [9, 29], [11, 30], [14, 30], [17, 30], [20, 30], [23, 30], [26, 30], [28, 31], [31, 31], [34, 31], [37, 31], [40, 31], [43, 31], [46, 31]]

#list1= [[48, 32], [51, 32], [3, 32], [6, 32], [9, 32], [12, 32], [15, 32], [17, 33], [20, 33], [23, 33], [26, 33], [29, 33], [32, 33], [34, 34], [37, 34], [40, 34], [43, 34], [46, 34], [49, 34], [1, 34], [3, 35], [6, 35], [9, 35], [12, 35], [15, 35], [18, 35], [21, 35], [23, 36], [26, 36], [29, 36], [32, 36], [35, 36], [38, 36], [40, 37], [43, 37], [46, 37], [49, 37], [1, 37], [4, 37], [7, 37], [9, 38], [12, 38], [15, 38], [18, 38], [21, 38], [24, 38], [27, 38], [29, 39], [32, 39], [35, 39], [38, 39], [41, 39], [44, 39], [46, 40], [49, 40], [1, 40], [4, 40], [7, 40], [10, 40], [13, 40], [15, 41], [18, 41], [21, 41], [24, 41], [27, 41], [30, 41], [33, 41], [35, 42], [38, 42], [41, 42], [44, 42], [47, 42], [50, 42], [1, 43], [4, 43], [7, 43], [10, 43], [13, 43], [16, 43], [19, 43], [21, 44], [24, 44], [27, 44], [30, 44], [33, 44], [36, 44], [39, 44], [41, 45], [44, 45], [47, 45], [50, 45], [2, 45], [5, 45], [7, 46], [10, 46], [13, 46], [16, 46], [19, 46], [22, 46], [25, 46], [27, 47], [30, 47], [33, 47], [36, 47], [39, 47], [42, 47], [45, 47], [47, 48], [50, 48], [2, 48], [5, 48], [8, 48], [11, 48], [13, 49], [16, 49], [19, 49], [22, 49], [25, 49], [28, 49], [31, 49], [33, 50], [36, 50], [39, 50], [42, 50], [45, 50], [48, 50], [51, 50], [2, 51], [5, 51], [8, 51], [11, 51], [14, 51], [17, 51], [19, 52], [22, 52], [25, 52], [28, 52], [31, 52], [34, 52], [37, 52], [39, 53], [42, 53], [45, 53], [48, 53], [51, 53], [3, 53], [6, 53], [8, 54], [11, 54], [14, 54], [17, 54], [20, 54], [23, 54], [25, 55], [28, 55], [31, 55], [34, 55], [37, 55], [40, 55], [43, 55], [45, 56], [48, 56], [51, 56], [3, 56], [6, 56], [9, 56], [12, 56], [14, 57], [17, 57], [20, 57], [23, 57], [26, 57], [29, 57], [31, 58], [34, 58], [37, 58], [40, 58], [43, 58], [46, 58], [49, 58], [51, 59], [3, 59], [6, 59], [9, 59], [12, 59], [15, 59], [18, 59], [20, 60], [23, 60], [26, 60], [29, 60], [32, 60], [35, 60], [37, 61], [40, 61], [43, 61], [46, 61], [49, 61], [1, 61], [4, 61], [6, 62], [9, 62], [12, 62], [15, 62], [18, 62], [21, 62], [24, 62], [26, 63], [29, 63], [32, 63], [35, 63], [38, 63], [41, 63]]

#list2= [[43, 64], [46, 64], [49, 64], [1, 64], [4, 64], [7, 64], [10, 64], [12, 65], [15, 65], [18, 65], [21, 65], [24, 65], [27, 65], [30, 65], [32, 66], [35, 66], [38, 66], [41, 66], [44, 66], [47, 66], [49, 67], [1, 67], [4, 67], [7, 67], [10, 67], [13, 67], [16, 67], [18, 68], [21, 68], [24, 68], [27, 68], [30, 68], [33, 68], [36, 68], [38, 69], [41, 69], [44, 69], [47, 69], [50, 69], [2, 69], [4, 70], [7, 70], [10, 70], [13, 70], [16, 70], [19, 70], [22, 70], [24, 71], [27, 71], [30, 71], [33, 71], [36, 71], [39, 71], [42, 71], [44, 72], [47, 72], [50, 72], [2, 72], [5, 72], [8, 72], [10, 73], [13, 73], [16, 73], [19, 73], [22, 73], [25, 73], [28, 73], [30, 74], [33, 74], [36, 74], [39, 74], [42, 74], [45, 74], [48, 74], [50, 75], [2, 75], [5, 75], [8, 75], [11, 75], [14, 75], [16, 76], [19, 76], [22, 76], [25, 76], [28, 76], [31, 76], [34, 76], [36, 77], [39, 77], [42, 77], [45, 77], [48, 77], [51, 77], [3, 77], [5, 78], [8, 78], [11, 78], [14, 78], [17, 78], [20, 78], [22, 79], [25, 79], [28, 79], [31, 79], [34, 79], [37, 79], [40, 79], [42, 80], [45, 80], [48, 80], [51, 80], [3, 80], [6, 80], [9, 80], [11, 81], [14, 81], [17, 81], [20, 81], [23, 81], [26, 81], [28, 82], [31, 82], [34, 82], [37, 82], [40, 82], [43, 82], [46, 82], [48, 83], [51, 83], [3, 83], [6, 83], [9, 83], [12, 83], [15, 83], [17, 84], [20, 84], [23, 84], [26, 84], [29, 84], [32, 84], [34, 85], [37, 85], [40, 85], [43, 85], [46, 85], [49, 85], [1, 85], [3, 86], [6, 86], [9, 86], [12, 86], [15, 86], [18, 86], [21, 86], [23, 87], [26, 87], [29, 87], [32, 87], [35, 87], [38, 87], [40, 88], [43, 88], [46, 88], [49, 88], [1, 88], [4, 88], [7, 88], [9, 89], [12, 89], [15, 89], [18, 89], [21, 89], [24, 89], [27, 89], [29, 90], [32, 90], [35, 90], [38, 90], [41, 90], [44, 90], [46, 91], [49, 91], [1, 91], [4, 91], [7, 91], [10, 91], [13, 91], [15, 92], [18, 92], [21, 92], [24, 92], [27, 92], [30, 92], [33, 92], [35, 93], [38, 93], [41, 93], [44, 93], [47, 93], [50, 93], [1, 94], [4, 94], [7, 94], [10, 94], [13, 94], [16, 94], [19, 94], [21, 95], [24, 95], [27, 95], [30, 95], [33, 95], [36, 95]]

#list3= [[39, 95], [41, 96], [44, 96], [47, 96], [50, 96], [2, 96], [5, 96], [7, 97], [10, 97], [13, 97], [16, 97], [19, 97], [22, 97], [25, 97], [27, 98], [30, 98], [33, 98], [36, 98], [39, 98], [42, 98], [45, 98], [47, 99], [50, 99], [2, 99], [5, 99], [8, 99], [11, 99], [13, 100], [16, 100], [19, 100], [22, 100], [25, 100], [28, 100], [31, 100], [33, 101], [36, 101], [39, 101], [42, 101], [45, 101], [48, 101], [51, 101], [2, 102], [5, 102], [8, 102], [11, 102], [14, 102], [17, 102], [19, 103], [22, 103], [25, 103], [28, 103], [31, 103], [34, 103], [37, 103], [39, 104], [42, 104], [45, 104], [48, 104], [51, 104], [3, 104], [6, 104], [8, 105], [11, 105], [14, 105], [17, 105], [20, 105], [23, 105], [25, 106], [28, 106], [31, 106], [34, 106], [37, 106], [40, 106], [43, 106], [45, 107], [48, 107], [51, 107], [3, 107], [6, 107], [9, 107], [12, 107], [14, 108], [17, 108], [20, 108], [23, 108], [26, 108], [29, 108], [31, 109], [34, 109], [37, 109], [40, 109], [43, 109], [46, 109], [49, 109], [51, 110], [3, 110], [6, 110], [9, 110], [12, 110], [15, 110], [18, 110], [20, 111], [23, 111], [26, 111], [29, 111], [32, 111], [35, 111], [37, 112], [40, 112], [43, 112], [46, 112], [49, 112], [1, 112], [4, 112], [6, 113], [9, 113], [12, 113], [15, 113], [18, 113], [21, 113], [24, 113], [26, 114], [29, 114], [32, 114], [35, 114], [38, 114], [41, 114], [43, 115], [46, 115], [49, 115], [1, 115], [4, 115], [7, 115], [10, 115], [12, 116], [15, 116], [18, 116], [21, 116], [24, 116], [27, 116], [30, 116], [32, 117], [35, 117], [38, 117], [41, 117], [44, 117], [47, 117], [49, 118], [1, 118], [4, 118], [7, 118], [10, 118], [13, 118], [16, 118], [18, 119], [21, 119], [24, 119], [27, 119], [30, 119], [33, 119], [36, 119], [38, 120], [41, 120], [44, 120], [47, 120], [50, 120], [2, 120], [4, 121], [7, 121], [10, 121], [13, 121], [16, 121], [19, 121], [22, 121], [24, 122], [27, 122], [30, 122], [33, 122], [36, 122], [39, 122], [42, 122], [44, 123], [47, 123], [50, 123], [2, 123], [5, 123], [8, 123], [10, 124], [13, 124], [16, 124], [19, 124], [22, 124], [25, 124], [28, 124], [30, 125], [33, 125], [36, 125], [39, 125], [42, 125], [45, 125], [48, 125], [50, 126], [2, 126], [5, 126], [8, 126], [11, 126], [14, 126], [16, 127], [19, 127], [22, 127], [25, 127], [28, 127], [31, 127]]

## #### RISING #### ##
#list0= [[45, 24], [50, 49], [52, 59], [41, 7], [47, 34], [40, 2], [53, 64], [42, 12], [47, 37], [46, 32], [48, 42], [52, 62], [41, 10], [49, 47], [42, 15], [43, 20], [46, 35], [40, 5], [45, 30], [50, 55], [52, 65], [48, 45], [51, 60], [49, 50], [40, 8], [44, 28], [45, 33], [42, 18], [41, 13], [39, 3], [43, 23], [47, 43], [39, 6], [43, 26], [49, 53], [46, 41], [52, 68], [40, 11], [50, 61], [42, 21], [44, 31], [49, 56], [45, 36], [42, 24], [40, 14], [52, 71], [38, 4], [43, 29], [44, 34], [49, 59], [45, 39], [50, 64], [41, 22], [39, 12], [38, 7], [47, 52], [46, 47], [45, 42], [50, 67], [49, 62], [37, 5], [42, 27], [43, 32], [42, 30], [43, 35], [46, 50], [45, 45], [50, 70], [39, 15], [48, 60], [40, 20], [51, 75], [36, 3], [39, 18], [41, 28], [46, 53], [48, 63], [40, 23], [37, 8], [47, 58], [36, 6], [49, 68], [41, 31], [42, 36], [37, 11], [46, 56], [40, 26], [49, 71], [45, 51], [50, 76], [47, 61], [36, 9], [43, 41], [39, 24], [43, 44], [47, 64], [37, 14], [40, 29], [50, 79], [34, 2], [48, 69], [35, 7], [46, 59], [45, 54], [41, 37], [42, 42], [47, 67], [44, 52], [45, 57], [49, 77], [35, 10], [38, 25], [37, 20], [40, 35], [48, 72], [45, 60], [47, 70], [39, 30], [48, 75], [49, 80], [41, 40], [43, 50], [36, 18], [35, 13], [43, 53], [33, 3], [37, 23], [48, 78], [40, 38], [46, 68], [37, 26], [45, 63], [38, 31], [47, 73], [43, 56], [41, 46], [36, 21], [47, 76], [42, 51], [32, 4], [46, 71], [44, 61], [36, 24], [38, 34], [42, 54], [41, 49], [40, 44], [39, 39], [32, 7], [34, 17], [37, 32], [46, 74], [31, 2], [40, 47], [45, 72], [41, 52], [33, 12], [47, 82], [36, 27], [32, 10], [36, 30], [31, 5], [46, 77], [37, 35], [35, 25], [47, 85], [45, 75], [46, 80], [39, 45], [40, 50], [36, 33], [48, 90], [40, 53], [32, 13], [42, 63], [39, 48], [34, 23], [45, 78], [44, 73], [31, 11], [34, 26], [37, 41], [32, 16], [41, 61], [30, 6], [40, 56], [39, 51], [29, 4], [43, 71], [31, 14], [42, 66], [39, 54], [32, 19], [40, 59], [36, 39], [35, 34], [38, 49], [30, 12], [31, 17], [46, 89], [37, 47], [41, 64], [40, 62], [32, 22], [28, 2], [43, 77], [39, 57], [31, 20], [36, 42], [33, 30], [46, 92], [39, 60], [28, 5]]

#list1= [[34, 35], [42, 75], [30, 15], [27, 3], [31, 23], [33, 33], [46, 95], [35, 43], [38, 58], [34, 38], [45, 90], [28, 8], [32, 28], [46, 98], [43, 83], [42, 78], [35, 46], [44, 88], [45, 93], [41, 76], [43, 86], [44, 91], [45, 96], [42, 81], [29, 19], [30, 24], [33, 39], [39, 66], [32, 34], [28, 14], [41, 79], [35, 49], [45, 99], [43, 89], [42, 84], [38, 64], [35, 52], [28, 17], [26, 7], [27, 12], [32, 37], [44, 97], [41, 82], [40, 77], [42, 87], [31, 35], [38, 67], [30, 30], [43, 92], [27, 15], [33, 45], [36, 60], [41, 85], [44, 100], [24, 3], [28, 23], [35, 58], [45, 105], [43, 95], [30, 33], [41, 88], [33, 48], [24, 6], [43, 98], [31, 41], [27, 21], [40, 83], [34, 56], [36, 66], [30, 36], [41, 91], [23, 4], [33, 51], [40, 86], [26, 19], [24, 9], [25, 14], [44, 106], [39, 84], [35, 64], [31, 44], [24, 12], [33, 54], [25, 17], [42, 99], [43, 104], [38, 79], [30, 42], [37, 77], [34, 62], [31, 47], [41, 97], [29, 37], [32, 52], [43, 107], [25, 20], [34, 65], [31, 50], [28, 35], [35, 70], [39, 90], [23, 13], [25, 23], [22, 8], [41, 100], [38, 85], [24, 18], [42, 105], [35, 73], [29, 43], [42, 108], [23, 16], [41, 103], [33, 63], [28, 41], [20, 1], [43, 113], [34, 71], [35, 76], [20, 4], [40, 101], [42, 111], [29, 46], [36, 81], [37, 86], [24, 24], [34, 74], [27, 39], [26, 34], [36, 84], [29, 49], [33, 69], [22, 17], [35, 79], [25, 32], [32, 67], [41, 109], [33, 72], [38, 97], [40, 107], [39, 102], [30, 57], [35, 82], [23, 25], [27, 45], [31, 65], [34, 80], [20, 10], [28, 50], [36, 90], [38, 100], [19, 8], [41, 115], [32, 70], [40, 110], [25, 38], [39, 105], [31, 68], [38, 103], [41, 118], [34, 83], [17, 1], [23, 31], [32, 73], [31, 71], [25, 41], [33, 81], [28, 56], [27, 51], [37, 101], [22, 29], [18, 9], [34, 86], [28, 59], [21, 24], [41, 121], [20, 19], [26, 49], [32, 79], [24, 39], [27, 54], [30, 69], [18, 12], [31, 74], [27, 57], [22, 32], [24, 42], [41, 124], [28, 62], [19, 20], [39, 117], [33, 87], [20, 25], [27, 60], [29, 70], [22, 35], [24, 45], [33, 90], [17, 13], [15, 3], [38, 115], [37, 110], [21, 33], [24, 48], [34, 95], [23, 43], [22, 38], [16, 11], [37, 113], [14, 1], [31, 83], [28, 68], [35, 103]]

#list2= [[15, 6], [21, 36], [28, 71], [35, 106], [26, 61], [15, 9], [36, 111], [17, 19], [34, 101], [18, 24], [37, 116], [22, 44], [25, 59], [38, 121], [17, 22], [37, 119], [24, 54], [21, 42], [20, 37], [16, 17], [22, 47], [19, 32], [38, 124], [14, 10], [34, 107], [15, 15], [38, 127], [23, 55], [20, 40], [33, 102], [29, 85], [19, 35], [17, 25], [32, 100], [13, 8], [26, 70], [35, 115], [30, 90], [28, 80], [24, 63], [29, 88], [17, 28], [37, 125], [19, 38], [17, 31], [33, 108], [15, 21], [20, 46], [21, 51], [30, 93], [22, 56], [23, 61], [33, 111], [26, 76], [13, 14], [18, 39], [12, 9], [20, 49], [36, 126], [30, 96], [35, 121], [15, 24], [30, 99], [15, 27], [12, 12], [31, 104], [29, 94], [26, 79], [19, 47], [32, 109], [24, 72], [26, 82], [33, 117], [21, 57], [12, 15], [19, 50], [31, 107], [15, 30], [21, 60], [14, 25], [17, 40], [28, 95], [16, 35], [31, 110], [33, 120], [19, 53], [13, 23], [32, 115], [34, 125], [18, 48], [16, 38], [30, 108], [28, 98], [15, 36], [24, 78], [13, 26], [33, 123], [21, 66], [14, 31], [27, 96], [28, 101], [30, 111], [18, 51], [25, 86], [23, 76], [33, 126], [15, 39], [17, 49], [25, 89], [31, 116], [24, 84], [18, 54], [30, 114], [15, 42], [22, 74], [11, 22], [29, 109], [19, 62], [32, 124], [25, 92], [26, 97], [16, 47], [12, 30], [30, 117], [20, 67], [11, 25], [15, 45], [19, 65], [10, 20], [18, 60], [16, 50], [27, 105], [30, 120], [28, 110], [15, 48], [18, 63], [16, 53], [23, 88], [19, 68], [12, 33], [17, 58], [27, 108], [25, 98], [21, 78], [15, 51], [10, 26], [29, 118], [13, 41], [19, 71], [26, 106], [18, 66], [9, 24], [27, 111], [30, 126], [11, 34], [14, 49], [16, 59], [22, 89], [20, 79], [17, 64], [18, 69], [23, 94], [29, 124], [28, 119], [11, 37], [25, 104], [21, 87], [14, 52], [18, 72], [25, 107], [29, 127], [15, 57], [16, 62], [13, 50], [14, 55], [23, 97], [24, 102], [27, 117], [20, 85], [22, 95], [18, 75], [10, 38], [19, 80], [23, 100], [9, 33], [25, 110], [17, 73], [22, 98], [25, 113], [26, 118], [27, 123], [24, 108], [23, 103], [21, 93], [20, 88], [15, 66], [14, 61], [21, 96], [19, 86], [25, 116], [24, 111], [22, 101], [20, 91], [12, 54], [17, 79], [26, 121], [14, 64], [21, 99], [13, 59], [16, 74], [18, 84], [26, 124], [10, 47]]

list3= [[23, 109], [11, 52], [25, 119], [24, 114], [8, 37], [9, 42], [7, 35], [13, 62], [10, 50], [17, 82], [24, 117], [25, 122], [22, 107], [13, 65], [16, 80], [22, 110], [14, 70], [25, 125], [21, 105], [17, 85], [12, 63], [14, 73], [10, 53], [18, 93], [7, 38], [22, 113], [24, 123], [7, 41], [21, 108], [12, 66], [9, 51], [16, 86], [14, 76], [13, 71], [18, 96], [22, 116], [11, 61], [15, 81], [19, 101], [9, 54], [6, 39], [23, 121], [17, 94], [10, 59], [8, 49], [21, 114], [22, 119], [7, 47], [11, 67], [23, 124], [15, 87], [10, 62], [19, 107], [17, 97], [13, 77], [16, 92], [20, 112], [14, 82], [11, 70], [22, 122], [8, 55], [21, 117], [18, 105], [10, 65], [21, 120], [5, 43], [6, 48], [14, 85], [11, 73], [22, 125], [13, 83], [10, 68], [18, 108], [20, 118], [17, 103], [16, 98], [7, 56], [19, 113], [9, 66], [8, 61], [5, 46], [12, 81], [6, 51], [21, 126], [18, 111], [16, 101], [13, 86], [7, 59], [8, 64], [5, 49], [6, 54], [15, 99], [18, 114], [14, 94], [11, 79], [20, 124], [19, 119], [12, 84], [16, 104], [8, 67], [7, 62], [14, 97], [9, 72], [15, 102], [11, 82], [13, 92], [5, 55], [9, 75], [16, 107], [6, 60], [11, 85], [10, 80], [17, 115], [15, 105], [14, 100], [18, 120], [5, 58], [9, 78], [10, 83], [12, 93], [8, 73], [4, 53], [16, 113], [15, 108], [13, 98], [18, 123], [17, 118], [5, 61], [14, 103], [12, 96], [6, 66], [9, 81], [11, 91], [17, 121], [16, 116], [4, 59], [14, 106], [6, 69], [7, 74], [13, 104], [9, 84], [14, 109], [15, 114], [11, 94], [8, 79], [5, 67], [6, 72], [9, 87], [7, 77], [13, 107], [12, 102], [4, 62], [11, 97], [16, 122], [15, 117], [10, 92], [7, 80], [14, 112], [9, 90], [8, 85], [11, 100], [6, 75], [10, 95], [4, 65], [3, 63], [4, 68], [16, 125], [9, 93], [6, 78], [5, 73], [8, 88], [11, 103], [14, 118], [12, 108], [3, 66], [2, 61], [4, 71], [5, 76], [15, 123], [9, 96], [10, 101], [15, 126], [12, 111], [7, 86], [6, 81], [5, 79], [3, 69], [8, 94], [4, 74], [13, 119], [6, 84], [12, 114], [9, 99], [7, 89], [14, 124], [11, 109], [5, 82], [8, 97], [9, 102], [6, 87], [12, 117], [1, 62], [2, 67], [4, 77], [3, 75], [14, 127], [7, 95], [4, 80], [10, 110], [1, 65], [9, 105], [5, 85], [6, 90]]

#B = [[24,76],[31,42],[28,57],[39,4],[37,12],[26,68],[19,102],[22,87],[33,34]]
#Y = [[37,61],[40,61],[43,61],[46,61],[49,61],[1,61],[4,61],[6,62],[9,62],[12,62],[15,62],[18,62],[21,62],[24,62],[26,63],[29,63],[32,63],[35,63],[38,63],[41,63],[43,64],[46,64],[49,64],[1,64],[4,64],[7,64],[10,64],[12,65],[15,65],[18,65],[21,65]]
#pixels=list2
pixels=list3
#print(pixels)

for row,col in pixels:
    print("{}".format((row,col)))
    tab[col,row]=1

# for i,j in pixels:
#     tab[j,i]=1
cfg_write(tab, filename) #<= write tab with activated values
cfg_read( filename) #<= check back
#cfg_read("Pulsing_Files/cfg_mat128x54_01_R424.txt")
