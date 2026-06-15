[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/AktWbCri)
# assignment-04-CV-Sensor-Fusion

# Perspective Transformation
usage ```python image_extractor.py [-i input_path] [-o output_path] [-r width height]```
- If a parameter is missing the program refuses to start
- Alternative to the shortcuts you can use --input,--output and --resolution
- After the program started you can select the 4 points in a clockwise order
- You can press s to save the image when you selected the corners or q to quit

# Ar Game
## How to play
- If you have no game board you can generate one using ```genBoard.py```. By default this gives you a DIN-A4 field easy to print
- If you want a different field feel free to change the parameters or bring your own. The order of the markers is not important because it is getting ordered anyways XD
## Gameplay
- Simply hit the blue dots with your finger and get points
- Your finger is displayed as a red dot
- If you want to stop at any time just press q
  
# Sensor Fusion
The choice of the alpha weight determines the extent to which data from the accelerometer or the camera tracking influence the prediction. If the weight is set too low, the high latency of the camera will cause jitter and delays in the prediction. If, on the other hand, it is set too high, the tracking prediction deviates too much from the actual values and sometimes even goes completely out of bounds. With an optimal setting, therefore, the advantages of the accelerometer’s low latency and the camera’s more accurate prediction can be combined.
