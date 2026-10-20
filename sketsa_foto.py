import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import turtle
import numpy as np
from PIL import Image, ImageGrab  # ImageGrab untuk fungsi Simpan
from rembg import remove
import threading
import time

# ================================
# FUNGSI PROSES SKETSA
# ================================
def proses_sketsa(file_path):
    print("1. Menghapus background...")
    time.sleep(0.1)

    # Hapus Background
    gambar_asli = Image.open(file_path).convert('RGB')
    gambar_tanpa_bg = remove(gambar_asli)
    
    print("2. Memotong (crop) area kosong agar objek lebih besar...")
    img_array = np.array(gambar_tanpa_bg)
    
    # Ambil nilai Alpha (transparansi) untuk mencari tahu di mana objek utamanya
    alpha = img_array[:, :, 3]
    koordinat = cv2.findNonZero(alpha)
    
    # Crop (potong) gambar persis di tepi objek
    if koordinat is not None:
        x, y, w_box, h_box = cv2.boundingRect(koordinat)
        img_cropped = img_array[y:y+h_box, x:x+w_box]
    else:
        img_cropped = img_array

    # Konversi ke Grayscale
    img_gray = cv2.cvtColor(img_cropped, cv2.COLOR_RGBA2GRAY)
    
    # Resize agar maksimal menyesuaikan ukuran kanvas baru (550px)
    h, w = img_gray.shape
    rasio = 550 / max(h, w)
    lebar_baru, tinggi_baru = int(w * rasio), int(h * rasio)
    img_resized = cv2.resize(img_gray, (lebar_baru, tinggi_baru))
    
    print("3. Deteksi garis tepi...")
    edges = cv2.Canny(img_resized, threshold1=80, threshold2=150)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    print("4. Mulai menggambar!")
    pen.clear()
    pen.color("black")
    
    offset_x = -lebar_baru // 2
    offset_y = tinggi_baru // 2

    # Tracer disetel ke 2 agar gambar cukup cepat
    turtle_screen.tracer(1) 
    
    for contour in contours:
        pen.penup()
        for i, point in enumerate(contour):
            x, y = point[0]
            t_x = x + offset_x
            t_y = offset_y - y 
            
            pen.goto(t_x, t_y)
            if i == 0:
                pen.pendown()
    
    turtle_screen.update()
    print("Selesai!")
    
    # Menggunakan root.after agar tidak error saat update UI dari Thread lain
    root.after(0, lambda: btn_pilih.config(state=tk.NORMAL))
    root.after(0, lambda: btn_simpan.config(state=tk.NORMAL))

# ================================
# FUNGSI TOMBOL PILIH FOTO
# ================================
def pilih_dan_gambar():
    file_path = filedialog.askopenfilename(
        title="Pilih Foto", 
        filetypes=[("File Gambar", "*.jpg *.jpeg *.png")]
    )
    if not file_path:
        return

    btn_pilih.config(state=tk.DISABLED)
    btn_simpan.config(state=tk.DISABLED)
    pen.clear()

    t = threading.Thread(target=proses_sketsa, args=(file_path,))
    t.start()

# ================================
# FUNGSI TOMBOL SIMPAN
# ================================
def simpan_sketsa():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")],
        title="Simpan Hasil Sketsa"
    )
    if not file_path:
        return
    
    # Cari tahu titik koordinat kanvas di layar laptopmu
    x = root.winfo_rootx() + kanvas.winfo_x() + frame.winfo_x()
    y = root.winfo_rooty() + kanvas.winfo_y() + frame.winfo_y()
    x1 = x + kanvas.winfo_width()
    y1 = y + kanvas.winfo_height()
    
    try:
        # Mengambil screenshot khusus pada kotak kanvas
        gambar_simpan = ImageGrab.grab(bbox=(x, y, x1, y1))
        gambar_simpan.save(file_path)
        messagebox.showinfo("Berhasil", "Sketsa kerenmu berhasil disimpan!")
    except Exception as e:
        messagebox.showerror("Error", f"Gagal menyimpan gambar: {e}")

# ================================
# SETUP UI & TURTLE
# ================================
root = tk.Tk()
root.title("Animasi Sketsa Pena + Hapus Latar Belakang")
root.geometry("700x800") # Ukuran aplikasi diperbesar
root.configure(bg="#2C3E50")

# Frame untuk meletakkan tombol secara berdampingan
frame_btn = tk.Frame(root, bg="#2C3E50")
frame_btn.pack(pady=20)

btn_pilih = tk.Button(frame_btn, text="Pilih Foto & Gambar", font=("Arial", 12, "bold"), 
                      bg="#E74C3C", fg="white", cursor="hand2", command=pilih_dan_gambar)
btn_pilih.grid(row=0, column=0, padx=10)

btn_simpan = tk.Button(frame_btn, text="Simpan Sketsa", font=("Arial", 12, "bold"), 
                       bg="#2ECC71", fg="white", cursor="hand2", state=tk.DISABLED, command=simpan_sketsa)
btn_simpan.grid(row=0, column=1, padx=10)

# Frame & Kanvas Turtle diperbesar (600x600)
frame = tk.Frame(root, width=600, height=600, relief=tk.SUNKEN, bd=3)
frame.pack()
kanvas = tk.Canvas(frame, width=600, height=600)
kanvas.pack()

# Setup Turtle
turtle_screen = turtle.TurtleScreen(kanvas)
turtle_screen.bgcolor("white")
pen = turtle.RawTurtle(turtle_screen)
pen.shape("circle")
pen.shapesize(0.2, 0.2) # Ukuran kursor kecil
pen.speed(0) 
pen.pensize(1)

root.mainloop()