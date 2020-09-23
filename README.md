# Style Transfer Snipping Tool

This Python run lightweight GUI allows you to apply a number of style transfer models on a screenshot taken from your computer screen. The screenshot is taken just like the windows Snipping Tool, and can be used across multiple monitors. The Style Transfer Models can be cycled between and final image can be saved. 

### Installation

Please run `pip install -r requirements.txt` to get required modules

### How to run and use

In command line, run `python style_transfer_snip` 
Once the GUI is open, press "New" in order to create your first screenshot. Your screen (or screens if you have multiple monitors) will turn slighlty opaque, and by clicking and dragging your mouse, you can create a rectangular area which will become your input image. The style transfer model applied to the input can then be changed and the output is shown on the right. "Save" will then allow you to save the output.

### How it works

This work is essentially the combination of the Style Transfer project from https://www.pyimagesearch.com/2018/08/27/neural-style-transfer-with-opencv/ and the screenshot project from https://github.com/harupy/snipping-tool 

#### Style Transfer

The Style Transfer Algorithm combines the "content" of one image and the "style" of another image to create a new image that tries to minimise the loss function for both the "content" and "style". One can then take famous art pieces, such as starry night and the scream, and apply the style of that image to completely new photographs or paintings. 

![Example Style Transfer](ForGithub.jpg)
{Cute Dog Image Source: https://www.pexels.com/photo/white-long-coated-dog-3722196/}

### Why create it?

I found the process of applying Style Transfer to images quite tedious and long winded. I wanted an interface that allowed me to apply different style transfer models quickly for ideation when looking at source images. Now when I come across different pictures on the internet, I can use this tool to create a screenshot of it and apply different style transfer models to get inspiration 
