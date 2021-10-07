from heapq import merge 

def mergePathBundles(pathBundle1, pathBundle2):
    greatBundle = []

    if not pathBundle1 and not pathBundle2:
       return greatBundle

    elif pathBundle1 and not pathBundle2:
       return greatBundle + pathBundle1

    elif not pathBundle1 and pathBundle2:
       return greatBundle + pathBundle2

    elif pathBundle1 and pathBundle2:
       if (len(pathBundle1[0]) < len(pathBundle2[0])) or (len(pathBundle1[0]) == len(pathBundle2[0]) and pathBundle1[0] < pathBundle2[0]):
          greatBundle.append(pathBundle1[0])
          greatBundle = greatBundle +  mergePathBundles(pathBundle1[1:], pathBundle2)

       else:
          greatBundle.append(pathBundle2[0])
          greatBundle = greatBundle +  mergePathBundles(pathBundle1, pathBundle2[1:])


    return greatBundle

def main():
    list1 = ["ABC"]
    list2 = ["AC", "ABD"]

    print("list 1: {0} | list 2: {1} | merged list: {2}".format(list1, list2, list(merge(list1, list2, key=lambda i: (len(i), i))))) # mergePathBundles(list1, list2)

# Calling main function, start of script
if __name__ == "__main__":
    main()