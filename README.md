# 📷 ZaBir HaSan | Image Editor

A desktop-based image editing application built with **Python, Tkinter, Pillow, and NumPy**. It provides an intuitive graphical interface for viewing, adjusting, transforming, cropping, and saving images.

The application features a clean cream-white interface, customizable image adjustments, a movable image preview, and essential editing tools.

## ✨ Features

### 🖼️ Image Management
- Open images in multiple formats, including PNG, JPG, JPEG, BMP, GIF, TIFF, and WebP.
- Preview images inside the application.
- Save edited images in PNG, JPEG, WebP, TIFF, and BMP formats.
- Display image dimensions and filenames.

### 🎨 Image Adjustments
Adjust your images using the following controls:

- **Brightness** — Adjust image brightness.
- **Contrast** — Control tonal differences.
- **Exposure** — Adjust overall exposure.
- **Highlights** — Modify bright areas.
- **Shadows** — Adjust darker areas.
- **Saturation** — Control color intensity.
- **Temperature** — Make colors warmer or cooler.
- **Vibrance** — Enhance color intensity.
- **Sharpness** — Adjust image sharpness.
- **Clarity** — Enhance local image details.
- **Vignette** — Add a darkening effect around image edges.

### 🔄 Image Transformation
- Rotate images left or right.
- Flip images horizontally or vertically.
- Crop images by selecting an area in the preview.
- Move images around the preview area using the mouse.

### 🔍 Preview Controls
- Zoom in and out using the mouse wheel.
- View images against a neutral background.
- Drag images to reposition them inside the preview.
- Automatically resize the preview when the application window changes size.

### ↩️ Editing Controls
- Undo previous image transformations.
- Redo undone transformations.
- Reset adjustment sliders.
- Restore the original image and default adjustment values.

### 🎨 User Interface
- Modern cream-white color theme.
- Organized editing panel with scrollable controls.
- Custom-styled scrollbar.
- Responsive desktop layout.
- Confirmation dialog before exiting the application.

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Tkinter | Graphical user interface |
| Pillow (PIL) | Image loading, processing, and saving |
| NumPy | Efficient numerical image processing |
| ttk | Styled interface components and scrollbar |

## 📋 Requirements

Before running the application, ensure that you have:

- Python 3.10 or newer recommended.
- Pillow
- NumPy

Tkinter is included with most standard Python installations.

## 📖 How to Use

1. Launch the application.
2. Click **Open Image** to select an image from your computer.
3. Adjust brightness, contrast, exposure, colors, and other image properties using the sliders.
4. Drag the image to reposition it inside the preview area.
5. Use the mouse wheel to zoom in or out.
6. Use the transformation buttons to rotate, flip, or crop the image.
7. Use Undo and Redo to navigate between previous image transformations.
8. Click **Save Image** or **Save** to export your edited image.
9. Click **Reset Edits** to restore the adjustment sliders to their default values.
10. Click **Reset All** to restore the original image and default adjustments.

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl + O` | Open an image |
| `Ctrl + S` | Save an edited image |
| `Escape` | Cancel crop mode |


## ⚡ Performance

The application uses NumPy for numerical image operations and limits the preview processing dimensions to improve responsiveness when working with large images.

Final image adjustments are processed at the current image's full resolution when saving.

Performance may vary depending on image dimensions, applied adjustments, and available system resources.

## 👨‍💻 Author

**ZaBir HaSan**

Project: ZaBir HaSan | Image Editor

Built with Python ❤️
