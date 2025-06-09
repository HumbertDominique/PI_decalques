
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk


def polynomial_mask(data, mask, grid, order=4):
    '''------------------------------------------------------------------------------------
        polynomial_mask(data, mask_radius,order=4)
        in:
          data : image to interpolate from
          mask : mask boolean mask. True means to be removed
          Order : Order of the appoximation. Default = 4
        out: 
          approximated image
          error flag
         
        to do:
        ------------------------------------------------------------------------------------'''
    # From "Caractérisation du télescope de l'observatoire solaire IRSOL (Tessin)", Dominique Humbert, HEIG-VD, 2022 
    error_flag = False
    nmodes = int(((order+1)**2-(order+1))/2+(order+1))
    mask_dbl = np.zeros(mask.shape)
    mask_dbl[mask==False] = 1.   # met des 1. là ou le masque n'est pas présent
    height, width = data.shape
    model = np.zeros(mask.shape)
    basis = np.zeros((height,width,nmodes))

    j_mode = -1
    for i in range(order+1):
        for j in range(i+1):
            j_mode +=1
            basis[:,:,j_mode] =grid[0]**(i-j)*grid[1]**j
    A = np.zeros((nmodes,nmodes)).astype(np.double)

    for i in range(0,nmodes):
        for j in range(0,i+1): 
            A[i,j] = np.sum(basis[:,:,i]*basis[:,:,j]*mask_dbl)

    b = np.zeros(nmodes)
    for i in range(nmodes):
         b[i]=np.sum(data*basis[:,:,i]*mask_dbl)

    try:
        a = np.dot(np.linalg.inv(A),b)
    except np.linalg.LinAlgError:
        error_flag = True
        print('Linear algorithm error, model not build')

    if not error_flag:
        model = np.zeros((height,width))
        for i in range(0,nmodes):
            model += a[i]*basis[:,:,i] 

    return model, error_flag

def build_mask(width, height, radius, center=[None,None]):
    '''#------------------------------------------------------------------------------------
        buid_maks(data,center=None)
        in:
            shape : shape tuple. limited to 2^16x2^16 pixels
            radius : mask radius
            center (optional) : x,y coordinate of the mask's center relative to the image centre

        out:
            mask : boolean array with True in the mask circle
        ------------------------------------------------------------------------------------
    '''
    # if radius > Mshape[0] or radius > Mshape[1]:
    #   raise ValueError("Radius is too large")
    if (center[0]==None or center[1]==None):
        center = np.zeros((2))
        center[0] = 0
        center[1] = 0
    print(center)
    pxR = np.linspace(-width//2 -center[0],width//2 -center[0],width)
    pyR = np.linspace(-height//2 -center[1],height//2 -center[1],height)
    xx, yy = np.meshgrid(pxR,pyR)
    R = np.sqrt(xx**2 + yy**2)  # Pupil radius in pixel

    return R >= radius


def pick_color_from_image():
    '''#------------------------------------------------------------------------------------
        pick_color_from_image()
        in:
            -

        out:
            rgb : list of the RGB value picked
        ------------------------------------------------------------------------------------
    '''
    zoom = 1.0  # Scale factor for resizing the image to fit the window
    selected_rgb = [None]  # Use list for mutability in nested functions

    def load_image():
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.bmp")])
        if path:
            nonlocal img, zoom
            img = Image.open(path).convert("RGB")
            fit_to_window()

    def fit_to_window():
        nonlocal zoom, tk_img
        if img:
            w, h = img.width, img.height
            cw, ch = canvas.winfo_width(), canvas.winfo_height()
            zoom = min(cw/w, ch/h)
            update_image()

    def update_image():
        nonlocal tk_img
        resized = img.resize((int(img.width*zoom), int(img.height*zoom)), Image.LANCZOS)
        tk_img = ImageTk.PhotoImage(resized)
        canvas.delete("IMG")
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_img, tags="IMG")

    def get_color(event):
        x, y = int(event.x / zoom), int(event.y / zoom)
        if 0 <= x < img.width and 0 <= y < img.height:
            selected_rgb[0] = img.getpixel((x, y))
            rgb = selected_rgb[0]
            color_label.config(text=f"RGB: {rgb} | HEX: #{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}")

    def on_resize(event):
        fit_to_window()

    def on_close():
        root.destroy()

    root = tk.Tk()
    root.title("Simple Color Picker")
    root.protocol("WM_DELETE_WINDOW", on_close)

    canvas = tk.Canvas(root, bg="gray")
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.bind("<Button-1>", get_color)
    canvas.bind("<Configure>", on_resize)

    btn = tk.Button(root, text="Load Image", command=load_image)
    btn.pack(pady=5)

    color_label = tk.Label(root, text="Click on the image", bg="white")
    color_label.pack(pady=5)

    img = None
    tk_img = None

    root.mainloop()
    return selected_rgb[0]  # Return selected RGB after GUI is closed