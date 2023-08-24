from array import array
from re import T
import pygame
import math
import random
from turtle import right, title
from multipledispatch import dispatch
import time
start_time = time.time()
pygame.init()

class DrawInfo:
    BLACK = (0, 0, 0)
    WHITE = (255, 255 ,255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    MAGENTA = (255, 0, 255)
    CYAN = (0, 255, 255)
    BLUE = (0, 0, 255)
    BACKGROUND_COLOR = WHITE

    GREYS = [ (128, 128, 128),
              (160, 160, 160),
              (192, 192, 192) ]
                             
    FONT = pygame.font.SysFont('tahoma', 30)
    LARGE_FONT = pygame.font.SysFont('tahoma', 40)
    
    SIDE_PAD = 100
    TOP_PAD = 150
    
    DELAY = 0.03

    def __init__(self, width, height, arr):
        self.width = width
        self.height = height

        self.window = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Sorting Visualizer")
        self.set_arr(arr)
 
    def set_arr(self, arr):
        self.arr = arr
        self.max_val = max(arr)
        self.min_val = min(arr)

        self.block_width = round((self.width - self.SIDE_PAD) / len(arr))
        self.block_height = (self.height - self.TOP_PAD) / (self.max_val - self.min_val)
        self.start_x = self.SIDE_PAD // 2

def draw(draw_info, algo_name, ascending):
     draw_info.window.fill(draw_info.BACKGROUND_COLOR)
     
     title = draw_info.LARGE_FONT.render(f"{algo_name} - {'Ascending' if ascending else 'Descending'}", 1, draw_info.RED)
     draw_info.window.blit(title, (draw_info.width/2 - title.get_width()/2 , 0))
     
     controls = draw_info.FONT.render("R - Reset | SPACE - Start Sorting | A - Ascending | D - Decending", 1, draw_info.BLACK)
     draw_info.window.blit(controls, (draw_info.width/2 - controls.get_width()/2 , 50))
     
     sorting = draw_info.FONT.render("B - Bubble Sort | Q - QuickSort | M - MergeSort | H - HeapSort", 1, draw_info.BLACK)
     draw_info.window.blit(sorting, (draw_info.width/2 - sorting.get_width()/2 , 80))
     
     draw_array(draw_info)
     pygame.display.update()

def draw_array(draw_info, color_positions = {}, clear_bg = False):
    arr = draw_info.arr
    
    if clear_bg:
        clear_rect = (draw_info.SIDE_PAD // 2, 7 * draw_info.TOP_PAD // 8,
                      draw_info.width - draw_info.SIDE_PAD, draw_info.height)
        pygame.draw.rect(draw_info.window, draw_info.BACKGROUND_COLOR, clear_rect)
        
    for i, val in enumerate(arr):
        x = draw_info.start_x + (i * draw_info.block_width)
        y = draw_info.height - ((val - draw_info.min_val) * draw_info.block_height)
        color = draw_info.GREYS[i % 3]
        if i in color_positions:
            color = color_positions[i]
        pygame.draw.rect(draw_info.window, color, (x, y, draw_info.block_width, draw_info.height))
        
    if clear_bg:
        pygame.display.update()
        

def generate_starting_array(n, min_val, max_val):
     arr = [0] * n   
     for i in range(n):
        val = random.randint(min_val, max_val) 
        arr[i] = val    
     return arr

def perform_chosen_algo(chosen_sorting_algo, draw_info, ascending, arr):
    if chosen_sorting_algo is bubbleSort: 
        while(True):
            try:
                next(bubbleSort(draw_info, ascending, arr, 0, len(arr) - 1))
            except StopIteration:
                break
    else: 
        chosen_sorting_algo(draw_info, ascending, arr, 0 , len(arr) - 1)
    yield True

@dispatch(list)
def quickSort(arr):
    quickSort(arr, 0, len(arr)-1)
    

@dispatch(DrawInfo, bool, list, int, int)
def quickSort(draw_info, ascending, arr, p, r):
    if p < r:
        #yield True
        partition_generator = partition(arr, p, r, draw_info, ascending)
        while True:
            try:
                next(partition_generator) 
            except StopIteration as pivot:
                q = pivot.value
                break   
        quickSort(draw_info, ascending, arr, p, q-1)  
        quickSort(draw_info, ascending, arr, q+1, r)
        

def partition(arr, p, r, draw_info, ascending):
    x = arr[r]  # pivot      
    i = p - 1
    for j in range(p,r):
        if (arr[j] <= x and ascending) or (arr[j] >= x and not ascending):
            i += 1
            swap(arr, i, j)
            draw_array(draw_info, {i: draw_info.MAGENTA, j: draw_info.CYAN}, True)
            time.sleep(draw_info.DELAY)
            yield True

    swap(arr, i+1, r)
    return i+1

def swap(arr, i, j):
    temp = arr[j]
    arr[j] = arr[i]
    arr[i] = temp  


@dispatch(list)
def mergeSort(arr):
    mergeSort(arr, 0, len(arr)-1)

@dispatch(DrawInfo, bool, list, int, int)
def mergeSort(draw_info, ascending, arr, p, r):
    if p < r:
        mid = (p+r) // 2 
        mergeSort(draw_info, ascending, arr, mid+1, r)
        mergeSort(draw_info, ascending, arr, p, mid)
        merge_generator = merge(draw_info, ascending, arr, p, mid, r)
        partition_generator = partition(arr, p, r, draw_info, ascending)
        while True:
            try:
                next(merge_generator) 
            except StopIteration as pivot:
                #q = pivot.value
                break   

def merge(draw_info, ascending, arr, p, mid, r):
    inf = float('inf') if ascending else float('-inf')
    n1 = mid - p + 1; n2 = r - mid
    left = [0] * (n1+1)
    right = [0] * (n2+1)
    left[n1] = inf; right[n2] = inf
    for t in range(p, r+1):
        if t <= mid:
            left[t-p] = arr[t]
        else:
            right[t-mid-1] = arr[t]
    i = 0; j = 0; idx = 0
    for k in range(p, r+1):
        if left[i] <= right[j] and ascending or left[i] >= right[j] and not ascending:
            idx = i
            arr[k] = left[i]
            i += 1
        else:
            idx = j
            arr[k] = right[j]
            j += 1   
        draw_array(draw_info, {k: draw_info.MAGENTA, idx: draw_info.CYAN}, True)
        time.sleep(draw_info.DELAY)
        yield True    
    
@dispatch(DrawInfo, bool, list)
def bubbleSort(draw_info, ascending, arr):
    bubbleSort(draw_info, ascending, arr, 0, len(arr) - 1)

@dispatch(DrawInfo, bool, list, int, int)
def bubbleSort(draw_info, ascending, arr, p , r):
    n = r - p + 1
    for i in range(1, n):
        swapped = False
        for j in range(p, r - i + 1):
            if (arr[j] > arr[j+1] and ascending) or (arr[j] < arr [j+1] and not ascending):
                swap(arr, j, j+1)
                draw_array(draw_info, {j: draw_info.MAGENTA, j + 1: draw_info.CYAN}, True)
                time.sleep(draw_info.DELAY)
                swapped = True
                yield True
        if not swapped: 
            return;        

def is_sorted(arr, ascending):
    return (all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1)) if ascending
            else all(arr[i] >= arr[i + 1] for i in range(len(arr) - 1)))

def main():
    run = True
    clock = pygame.time.Clock()
    n = 70; min_val = 1; max_val = 100
    arr = generate_starting_array(n, min_val, max_val)
    draw_info = DrawInfo(1000, 600, arr)
    sorting = False
    ascending = True
    sorting_algo = bubbleSort
    sorting_algo_name = "Bubble Sort"
    sorting_algo_generator = None

    while run:
        clock.tick(60)
        if sorting:
            try:
                next(sorting_algo_generator)
            except StopIteration:
                sorting = False  
        else: 
            draw(draw_info, sorting_algo_name, ascending)
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_r:
                arr = generate_starting_array(n, min_val, max_val)
                draw_info.set_arr(arr)  
                sorting = False  
            elif event.key == pygame.K_SPACE and sorting == False:
                if not is_sorted(arr, ascending):
                    sorting = True 
                    sorting_algo_generator = perform_chosen_algo(sorting_algo, draw_info, ascending, arr)
            elif event.key == pygame.K_a and not sorting:
                ascending = True
            elif event.key == pygame.K_d and not sorting:
                ascending = False 
            elif event.key == pygame.K_q and not sorting:
                sorting_algo = quickSort
                sorting_algo_name = "QuickSort" 
            elif event.key == pygame.K_m and not sorting:
                sorting_algo = mergeSort
                sorting_algo_name = "MergeSort" 
            elif event.key == pygame.K_b and not sorting:
                sorting_algo = bubbleSort
                sorting_algo_name = "Bubble Sort"       
                                 


    pygame.quit() 

if __name__ == "__main__":
    main()
    




arr = [34,2,7,2,9,29,-14,16,89,76,35,104,32,18,1203,156,1367,1785,352,573, 10000, 10000000, 999999,10000000,19030303,10339,20193,5256,2672]
#mergeSort(arr)
quickSort(arr)
#bubbleSort(arr)
print(arr)
duration = round((time.time() - start_time)*1000,3)
print("Process finished in %sms" %duration)
