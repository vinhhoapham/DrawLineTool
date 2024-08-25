# Draw Line Tool

# Table of Contents

1. [Draw Line Tool](#draw-line-tool)
2. [How to Use the Program](#how-to-use-the-program)
3. [File Structure](#file-structure)
4. [Installation](#installation)
5. [Running the Program](#running-the-program)
6. [Troubleshooting](#troubleshooting)
7. [Technical Details](#technical-details)
   1. [Line Detection Algorithm](#line-detection-algorithm)
   2. [Blurriness Measurement](#blurriness-measurement)
      1. [Edge Spread Function (ESF) Fitting](#edge-spread-function-esf-fitting)

## How to Use the Program

The Draw Line Tool is a Python application for analyzing images, particularly useful for examining the contrast and angle of lines in circular samples. Here's how to use it:

1. **Load a Folder**: Click the "Load Folder" button to select a directory containing your images (.JPG or .jpeg).

2. **Auto Detection**: If enabled in settings, the program will automatically process all images in the folder, detecting lines and calculating angles and contrast.

3. **Manual Line Drawing**: If auto-detection is disabled or you want to manually specify a line:
   - Click on the image to set the first point of the line.
   - Click again to set the second point and complete the line.
   - The program will calculate the angle and contrast based on your drawn line.

4. **Navigate Images**: Use the left and right arrow buttons (or keyboard arrows) to cycle through images in the folder.

5. **Export Analysis**: Click "Export Analysis" to save the results in the format(s) specified in settings (CSV, Excel, MAT).

6. **Adjust Settings**: Click the "Settings" button to modify export options, auto-detection, and export paths.

## File Structure

The project is structured as follows:

```
Draw-Line-Tool/
│
├── App.py                     # Main application entry point
├── View/
│   ├── DrawLineToolView.py    # Main view controller
│   ├── BottomMenu.py          # Bottom navigation menu
│   ├── ControlPanelComponent.py # Top control panel
│   ├── ImageCanvas.py         # Canvas for displaying images
│   └── SettingsPopupComponent.py # Settings popup window
│
├── Model/
│   ├── DrawLineToolModel.py   # Main model for data and logic
│   ├── Export.py              # Handles exporting analysis results
│   ├── ImageAnalysis/
│   │   ├── AutoAnalysis.py    # Automatic line detection and analysis
│   │   ├── SingleImageAnalysis.py # Analysis for a single image
│   │   └── RiseDistance.py    # Calculates rise distance for blurriness
│   └── Settings.py            # Manages application settings
│
├── ViewModel/
│   └── DrawLineToolViewModel.py # ViewModel for MVVM architecture
│
└── requirements.txt           # List of required Python packages
```

## Installation

1. Ensure you have Python 3.7+ installed on your system.

2. Clone the repository or download the source code.

3. Navigate to the project directory in your terminal.

4. Install the required packages using pip:

   ```
   pip install -r requirements.txt
   ```

   This will install the following packages:
   - numpy
   - opencv-python
   - openpyxl
   - Pillow
   - scikit-learn
   - scipy

## Running the Program

To run the Draw Line Tool:

1. Open a terminal or command prompt.

2. Navigate to the project directory.

3. Run the following command in the folder/directory where you install this repo:

   ```
   python src/App.py
   ```

4. The application window should open, and you can begin using the Draw Line Tool.

## Troubleshooting

- If you encounter any issues with package installation, try updating pip:
  ```
  pip install --upgrade pip
  ```
  Then attempt to install the requirements again.

- Make sure your Python environment matches the version requirements of the packages.

- If you face any runtime errors, check that all files are in their correct locations according to the file structure.

For any additional issues or feature requests, please open an issue on the project's repository.

## Technical Details

### Line Detection Algorithm

The automatic line detection algorithm comprises of the following steps: 

1. **Preprocessing**: 
   - The image is converted to grayscale and blurred using Gaussian blur to reduce noise.
   - The circular region of interest is cropped from the image.

2. **K-means Clustering**:
   - The pixels in the circular region are clustered into two groups using K-means clustering. 
   - One group is assigned to have pixel value of 0, while the other has value of 255

3. **Edge Detection**:
   - Canny edge detection is applied to the binarized image to identify edges.

4. **Hough Transform**:
   - The Hough transform is used to detect lines in the edge image.

5. **Line Selection**:
   - The detected lines are filtered and the line closest to the center of the circle is selected.

### Blurriness Measurement

The blurriness measurement in this tool is based on the concept of the Edge Spread Function (ESF) and is implemented in the `RiseDistance.py` file. Here's how it works:

1. **Edge Spread Function (ESF)**:
   - The ESF is created by plotting the intensity values of pixels perpendicular to the detected line.
   - This function represents the transition between two regions across the edge.

2. **Line Fitting**:
   - An error function (erf) is fitted to the ESF using curve fitting techniques.
   - The error function is a good model for the intensity transition across an edge.

3. **Sigma Calculation**:
   - The sigma (σ) parameter of the fitted error function is used as a measure of blurriness.
   - A larger sigma indicates a more gradual transition, which corresponds to a blurrier edge.

4. **Rise Distance**:
   - The rise distance is proportional to the sigma value.
   - It represents the distance over which the intensity changes from its minimum to maximum value across the edge.

5. **Interpretation**:
   - A smaller rise distance indicates a sharper, less blurry edge.
   - A larger rise distance suggests a more blurry or out-of-focus edge.

This method provides a quantitative measure of image sharpness, allowing for objective comparison of blurriness across different images or different regions within the same image.

#### Edge Spread Function (ESF) Fitting

The blurriness measurement uses a specific mathematical function to fit the Edge Spread Function. The form of this fitting function in LaTeX notation is:


$$ f(x) = a_1 \cdot \text{erf}\left(\frac{x - a_3}{\sigma\sqrt{2}}\right) + a_2 $$


Where:
- $f(x)$ is the intensity value at position $x$
- $\text{erf}$ is the error function
- $a_1$ is the amplitude of the edge transition
- $a_2$ is the offset (baseline intensity)
- $a_3$ is the position of the edge center
- $\sigma$ (sigma) is the standard deviation of the edge spread, which is used as the measure of blurriness

The $\sigma$ parameter is particularly important:
- A smaller $\sigma$ indicates a sharper edge (less blurry)
- A larger $\sigma$ indicates a more gradual transition (more blurry)

This function is fitted to the observed edge data using curve fitting techniques (specifically, the `curve_fit` function from SciPy). The resulting $\sigma$ value provides a quantitative measure of the edge sharpness, and thus, the image blurriness.

In the code, this is implemented in the `edge_model` function within `RiseDistance.py`:

```python
def edge_model(x, a1, a3, sigma, a2):
    return a1 * erf((x - a3) / (sigma * np.sqrt(2))) + a2
```

Understanding this function can help users interpret the blurriness measurements more accurately and potentially customize the analysis for specific types of images or edge characteristics.

The error function $\text{erf}(x)$ used in this equation is defined as:


$$ \text{erf}(x) = \frac{2}{\sqrt{\pi}} \int_0^x e^{-t^2} dt $$


This integral form of the error function represents the cumulative distribution function of a Gaussian distribution, which closely models the intensity transition across an edge in an image.
