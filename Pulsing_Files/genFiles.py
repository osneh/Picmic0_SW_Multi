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
##filename="cfg_DiscP123_Yellow_213.txt"
##filename="cfg_DiscP123_Yellow_426.txt"
##filename="cfg_DiscP123_Yellow_639.txt"
filename="cfg_DiscP123_Yellow_852.txt"
cfg_write(filename=filename)


tab=cfg_read(filename=filename)


#pixels=[[15,6],[35,103],[28,68]]
# RISSING
#list0= [[10, 18], [3, 52], [11, 14], [4, 48], [12, 10], [8, 29], [5, 44], [6, 40], [7, 33], [9, 25], [1, 63], [7, 36], [4, 51], [2, 59], [13, 6], [11, 17], [12, 13], [13, 9], [8, 32], [10, 24], [6, 43], [9, 28], [14, 5], [3, 58], [4, 54], [12, 16], [2, 65], [11, 20], [15, 1], [3, 61], [5, 50], [7, 42], [14, 8], [9, 31], [8, 38], [4, 57], [11, 23], [9, 34], [5, 53], [12, 19], [2, 68], [10, 30], [6, 49], [14, 11], [13, 15], [8, 41], [9, 37], [12, 22], [6, 52], [15, 7], [14, 14], [13, 18], [16, 3], [11, 29], [7, 48], [3, 67], [4, 63], [6, 55], [15, 10], [17, 2], [13, 21], [11, 32], [5, 59], [3, 70], [4, 66], [16, 9], [7, 51], [12, 28], [15, 13], [13, 24], [14, 20], [4, 69], [17, 5], [9, 43], [12, 31], [8, 50], [18, 1], [13, 27], [17, 8], [5, 65], [15, 16], [7, 57], [10, 42], [16, 12], [6, 61], [8, 53], [16, 15], [6, 64], [15, 19], [18, 4], [10, 45], [5, 68], [17, 11], [8, 56], [19, 3], [11, 41], [14, 26], [4, 75], [13, 33], [9, 52], [7, 63], [11, 44], [10, 48], [4, 78], [8, 59], [12, 40], [18, 10], [20, 2], [13, 36], [16, 21], [14, 32], [15, 25], [6, 70], [7, 66], [15, 28], [11, 47], [18, 13], [12, 43], [13, 39], [10, 54], [16, 24], [9, 58], [21, 1], [20, 5], [15, 31], [17, 20], [14, 35], [5, 80], [10, 57], [20, 8], [19, 12], [14, 38], [6, 76], [18, 19], [15, 34], [21, 4], [9, 64], [6, 79], [10, 60], [8, 68], [20, 11], [18, 22], [7, 75], [17, 26], [19, 18], [16, 33], [12, 52], [6, 82], [20, 14], [13, 48], [17, 29], [9, 67], [10, 63], [7, 78], [11, 59], [21, 10], [12, 55], [19, 21], [14, 44], [20, 17], [6, 85], [18, 28], [9, 70], [8, 77], [11, 62], [7, 81], [12, 58], [21, 13], [24, 1], [16, 39], [19, 24], [15, 43], [10, 69], [17, 35], [22, 12], [7, 84], [14, 50], [19, 27], [12, 61], [9, 76], [8, 80], [7, 87], [10, 72], [8, 83], [20, 23], [16, 45], [24, 4], [15, 49], [14, 53], [17, 41], [19, 30], [10, 75], [14, 56], [21, 22], [9, 79], [13, 60], [18, 37], [25, 3], [10, 78], [19, 33], [21, 25], [13, 63], [11, 74], [14, 59], [24, 10], [17, 44], [18, 40], [23, 17], [10, 81], [22, 21], [16, 51], [14, 62], [25, 9]]

#list1= [[21, 28], [26, 5], [8, 92], [16, 54], [11, 77], [9, 88], [17, 50], [15, 58], [10, 84], [27, 1], [20, 35], [25, 12], [15, 61], [8, 95], [14, 65], [23, 23], [27, 4], [12, 76], [17, 53], [22, 30], [15, 64], [8, 98], [13, 72], [9, 94], [13, 75], [12, 79], [18, 49], [19, 45], [16, 60], [10, 90], [25, 18], [21, 37], [26, 14], [28, 3], [23, 29], [27, 10], [11, 86], [17, 59], [24, 25], [29, 2], [18, 55], [21, 40], [16, 66], [11, 89], [23, 32], [24, 28], [9, 100], [28, 9], [12, 85], [27, 13], [15, 73], [11, 92], [12, 88], [16, 69], [20, 50], [10, 99], [9, 103], [14, 80], [11, 95], [18, 61], [21, 46], [17, 65], [27, 16], [15, 76], [12, 91], [13, 87], [20, 53], [14, 83], [21, 49], [10, 102], [18, 64], [29, 11], [17, 68], [28, 15], [26, 26], [11, 98], [19, 60], [10, 105], [28, 18], [25, 33], [30, 7], [12, 97], [14, 86], [24, 37], [11, 101], [22, 48], [13, 93], [17, 74], [16, 78], [32, 2], [14, 89], [31, 6], [12, 100], [21, 55], [29, 17], [20, 62], [18, 70], [14, 92], [15, 85], [28, 24], [24, 43], [18, 73], [27, 28], [22, 54], [21, 58], [13, 99], [15, 88], [31, 12], [28, 27], [33, 1], [18, 76], [14, 95], [26, 38], [21, 61], [30, 19], [12, 106], [27, 34], [28, 30], [31, 15], [23, 53], [24, 49], [33, 7], [12, 109], [17, 83], [32, 11], [21, 64], [34, 3], [21, 67], [30, 22], [13, 105], [23, 56], [31, 18], [26, 44], [32, 14], [27, 40], [33, 10], [35, 2], [17, 89], [14, 104], [16, 93], [18, 85], [32, 17], [20, 74], [12, 115], [20, 77], [34, 9], [28, 39], [27, 43], [26, 47], [18, 88], [32, 20], [15, 103], [30, 31], [26, 50], [22, 69], [19, 84], [12, 118], [16, 99], [24, 61], [36, 4], [28, 42], [20, 80], [19, 87], [17, 95], [20, 83], [23, 68], [25, 57], [30, 34], [33, 19], [28, 45], [33, 22], [35, 11], [17, 98], [32, 26], [29, 41], [31, 33], [17, 101], [34, 18], [16, 105], [18, 97], [36, 10], [29, 44], [26, 59], [32, 29], [30, 40], [31, 36], [25, 63], [15, 112], [35, 17], [22, 81], [25, 66], [27, 55], [21, 85], [23, 77], [28, 51], [29, 47], [33, 28], [34, 24], [18, 103], [24, 73], [28, 54], [27, 58], [38, 5], [21, 88], [34, 27], [36, 16], [24, 76], [31, 42], [28, 57], [39, 4], [37, 12], [26, 68], [19, 102]]

#list2= [[22, 87], [33, 34], [31, 45], [16, 117], [29, 53], [38, 11], [18, 109], [20, 98], [19, 105], [21, 94], [29, 56], [28, 60], [25, 75], [31, 48], [37, 18], [32, 44], [38, 14], [27, 67], [18, 112], [25, 78], [36, 25], [20, 104], [33, 40], [40, 6], [24, 85], [27, 70], [25, 81], [35, 32], [22, 96], [36, 28], [31, 51], [28, 66], [23, 92], [39, 13], [33, 43], [34, 39], [41, 5], [31, 54], [17, 122], [32, 50], [28, 69], [25, 84], [23, 95], [41, 8], [30, 61], [17, 125], [19, 114], [37, 27], [19, 117], [21, 106], [32, 53], [30, 64], [22, 102], [20, 113], [36, 34], [31, 60], [32, 56], [18, 124], [38, 26], [28, 75], [26, 86], [20, 116], [39, 22], [23, 101], [24, 97], [25, 93], [18, 127], [33, 55], [27, 82], [42, 10], [39, 25], [21, 112], [30, 70], [22, 108], [31, 66], [38, 32], [21, 115], [23, 104], [22, 111], [29, 77], [30, 73], [34, 54], [31, 69], [20, 122], [23, 107], [19, 126], [24, 103], [28, 84], [38, 35], [35, 50], [37, 42], [26, 95], [27, 91], [39, 31], [22, 114], [38, 38], [30, 76], [29, 83], [41, 23], [28, 87], [25, 102], [27, 94], [22, 117], [34, 60], [37, 45], [33, 64], [24, 109], [33, 67], [39, 37], [23, 116], [41, 29], [32, 71], [21, 124], [35, 59], [42, 25], [25, 108], [26, 101], [33, 70], [40, 36], [36, 55], [22, 123], [23, 119], [41, 32], [35, 62], [28, 96], [32, 77], [36, 58], [43, 24], [25, 111], [30, 88], [29, 92], [33, 73], [26, 107], [35, 65], [31, 84], [39, 46], [27, 103], [33, 76], [38, 50], [40, 42], [30, 91], [25, 114], [32, 80], [26, 110], [34, 72], [25, 117], [32, 83], [37, 57], [39, 49], [43, 30], [30, 94], [28, 102], [38, 56], [24, 124], [39, 52], [44, 26], [29, 101], [31, 90], [25, 120], [44, 29], [41, 44], [30, 97], [34, 78], [35, 74], [31, 93], [26, 116], [37, 63], [32, 89], [38, 59], [39, 55], [40, 51], [29, 104], [30, 100], [38, 62], [28, 111], [32, 92], [44, 32], [37, 66], [25, 126], [44, 35], [33, 88], [29, 107], [40, 54], [36, 73], [27, 118], [38, 65], [32, 95], [31, 99], [28, 114], [42, 46], [41, 53], [45, 34], [38, 68], [34, 87], [30, 106], [46, 30], [43, 45], [44, 38], [39, 64], [29, 113], [37, 75], [45, 37], [30, 109], [31, 105], [27, 124], [44, 41], [41, 56], [33, 97], [28, 120], [43, 48], [34, 93], [41, 59], [36, 82]]


list3= [[39, 95], [41, 96], [44, 96], [47, 96], [50, 96], [2, 96], [5, 96], [7, 97], [10, 97], [13, 97], [16, 97], [19, 97], [22, 97], [25, 97], [27, 98], [30, 98], [33, 98], [36, 98], [39, 98], [42, 98], [45, 98], [47, 99], [50, 99], [2, 99], [5, 99], [8, 99], [11, 99], [13, 100], [16, 100], [19, 100], [22, 100], [25, 100], [28, 100], [31, 100], [33, 101], [36, 101], [39, 101], [42, 101], [45, 101], [48, 101], [51, 101], [2, 102], [5, 102], [8, 102], [11, 102], [14, 102], [17, 102], [19, 103], [22, 103], [25, 103], [28, 103], [31, 103], [34, 103], [37, 103], [39, 104], [42, 104], [45, 104], [48, 104], [51, 104], [3, 104], [6, 104], [8, 105], [11, 105], [14, 105], [17, 105], [20, 105], [23, 105], [25, 106], [28, 106], [31, 106], [34, 106], [37, 106], [40, 106], [43, 106], [45, 107], [48, 107], [51, 107], [3, 107], [6, 107], [9, 107], [12, 107], [14, 108], [17, 108], [20, 108], [23, 108], [26, 108], [29, 108], [31, 109], [34, 109], [37, 109], [40, 109], [43, 109], [46, 109], [49, 109], [51, 110], [3, 110], [6, 110], [9, 110], [12, 110], [15, 110], [18, 110], [20, 111], [23, 111], [26, 111], [29, 111], [32, 111], [35, 111], [37, 112], [40, 112], [43, 112], [46, 112], [49, 112], [1, 112], [4, 112], [6, 113], [9, 113], [12, 113], [15, 113], [18, 113], [21, 113], [24, 113], [26, 114], [29, 114], [32, 114], [35, 114], [38, 114], [41, 114], [43, 115], [46, 115], [49, 115], [1, 115], [4, 115], [7, 115], [10, 115], [12, 116], [15, 116], [18, 116], [21, 116], [24, 116], [27, 116], [30, 116], [32, 117], [35, 117], [38, 117], [41, 117], [44, 117], [47, 117], [49, 118], [1, 118], [4, 118], [7, 118], [10, 118], [13, 118], [16, 118], [18, 119], [21, 119], [24, 119], [27, 119], [30, 119], [33, 119], [36, 119], [38, 120], [41, 120], [44, 120], [47, 120], [50, 120], [2, 120], [4, 121], [7, 121], [10, 121], [13, 121], [16, 121], [19, 121], [22, 121], [24, 122], [27, 122], [30, 122], [33, 122], [36, 122], [39, 122], [42, 122], [44, 123], [47, 123], [50, 123], [2, 123], [5, 123], [8, 123], [10, 124], [13, 124], [16, 124], [19, 124], [22, 124], [25, 124], [28, 124], [30, 125], [33, 125], [36, 125], [39, 125], [42, 125], [45, 125], [48, 125], [50, 126], [2, 126], [5, 126], [8, 126], [11, 126], [14, 126], [16, 127], [19, 127], [22, 127], [25, 127], [28, 127], [31, 127]]

#B = [[24,76],[31,42],[28,57],[39,4],[37,12],[26,68],[19,102],[22,87],[33,34]]
#Y = [[37,61],[40,61],[43,61],[46,61],[49,61],[1,61],[4,61],[6,62],[9,62],[12,62],[15,62],[18,62],[21,62],[24,62],[26,63],[29,63],[32,63],[35,63],[38,63],[41,63],[43,64],[46,64],[49,64],[1,64],[4,64],[7,64],[10,64],[12,65],[15,65],[18,65],[21,65]]
#pixels=list0
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
